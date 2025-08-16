# app/services/memory_summarizer.py

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional, Sequence, TypedDict

from haystack import Document
from haystack.dataclasses import ChatMessage
from haystack_integrations.components.embedders.ollama.document_embedder import (
    OllamaDocumentEmbedder,
)
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from app.config import settings
from app.services.generator import LLMGenerator
from app.utils.logging import get_logger

logger = get_logger(__name__)


class HistMsg(TypedDict):
    role: str   # "user" | "assistant"
    content: str


# System prompt for end-of-session durable memory extraction
# (Now explicitly states that ONLY user utterances are provided.)
_SESSION_SUMMARY_SYSTEM_PROMPT = (
    "You are extracting durable, long-term memories from a chat session.\n"
    "You will be given ONLY the USER'S utterances (no assistant replies).\n"
    "Extract ONLY stable facts, preferences, habits, persistent constraints, skills, goals,\n"
    "or recurring concerns that will remain useful in future conversations.\n"
    "Ignore transient mood, logistics, or tool/model mentions.\n"
    "Be concise and specific. Output 1–8 bullet points, each ≤ 20 words.\n"
    "If there is nothing durable, output EXACTLY: NONE"
)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_epoch() -> float:
    return datetime.now(timezone.utc).timestamp()


def _user_history_to_block(history: Sequence[HistMsg], cap_chars: int = 8000) -> str:
    """
    Build a text block from ONLY user messages in the session history.
    Caps total characters for safety.
    """
    parts: list[str] = []
    used = 0
    for h in history:
        if (h.get("role") or "").strip().lower() != "user":
            continue
        content = (h.get("content") or "").strip()
        if not content:
            continue
        line = f"USER: {content}"
        if used + len(line) > cap_chars:
            break
        parts.append(line)
        used += len(line)
    return "\n".join(parts)


class MemorySummarizer:
    """
    End-of-session summarizer:
    - Takes the full session history
    - Filters to USER-ONLY utterances
    - Extracts durable memory bullets
    - Embeds & upserts into Qdrant `user_memory`
    """

    def __init__(self) -> None:
        self.generator = LLMGenerator()
        self.embedder = OllamaDocumentEmbedder(model=settings.ollama_embed_model)
        self.mem_store = QdrantDocumentStore(
            url=settings.qdrant_url,
            index=settings.qdrant_collection_memory,
            recreate_index=False,
            return_embedding=True,
            wait_result_from_api=True,
            embedding_dim=settings.embedding_dim,
            similarity=settings.embedding_similarity,
        )

    def _summarize_session_sync(self, history: Sequence[HistMsg]) -> str:
        user_block = _user_history_to_block(history)
        if not user_block:
            return "NONE"

        messages = [
            ChatMessage.from_system(_SESSION_SUMMARY_SYSTEM_PROMPT),
            ChatMessage.from_user(
                "Here are ONLY the USER'S lines from the session (role-tagged):\n\n" + user_block
            ),
            ChatMessage.from_user("Now extract durable memory bullets."),
        ]
        summary, _ = self.generator.stream_chat(messages, on_token=None)
        return (summary or "").strip()

    def _embed_and_upsert(self, text: str, user_id: str, session_id: str) -> Optional[str]:
        if not text or text.upper() == "NONE":
            return None

        doc = Document(
            content=text,
            meta={
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": _utc_iso(),
                "timestamp_epoch": _utc_epoch(),
                "source": "memory_summarizer",
            },
        )
        embedded_doc = self.embedder.run([doc])["documents"][0]
        self.mem_store.write_documents([embedded_doc], policy="upsert")
        return embedded_doc.id

    async def process_session(self, *, user_id: str, session_id: str, history: Sequence[HistMsg]) -> None:
        """
        Public entrypoint: summarize ONLY the user's utterances from the entire session and persist durable memory.
        """
        try:
            summary = await asyncio.to_thread(self._summarize_session_sync, history)
            logger.info(f"[memory] Session summary for user={user_id} session={session_id}: {summary!r}")

            upserted_id = await asyncio.to_thread(self._embed_and_upsert, summary, user_id, session_id)
            if upserted_id:
                logger.info(f"[memory] Upserted session memory: {upserted_id} (user={user_id}, session={session_id})")
            else:
                logger.info("[memory] No durable memory extracted for this session.")
        except Exception as e:
            logger.error(f"[memory] End-of-session summarization failed: {e}")


# Singleton used by ws_chat
memory_summarizer = MemorySummarizer()
