# app/services/memory_summarizer.py

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional

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

# More permissive: treat explicit preferences as durable unless claimed temporary.
_SUMMARY_SYSTEM_PROMPT = (
    "You summarize a single user turn into durable memory for personalization.\n"
    "Extract ONLY stable facts, preferences, habits, constraints, skills, goals, or recurring concerns.\n"
    "Treat explicit first-person preferences (e.g., 'I like mangoes') as durable unless marked temporary.\n"
    "Exclude one-off mood, chat logistics, or model/tool mentions.\n"
    "Output 1–3 bullet points, each ≤ 20 words. If nothing durable, output EXACTLY: NONE"
)

def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _utc_epoch() -> float:
    return datetime.now(timezone.utc).timestamp()


class MemorySummarizer:
    """
    Converts a (user_text, bot_text) turn into a compact memory snippet,
    embeds it, and upserts into the `user_memory` collection.
    """

    def __init__(self) -> None:
        self.generator = LLMGenerator()
        self.embedder = OllamaDocumentEmbedder(model=settings.ollama_embed_model)

        # <-- THIS was missing in your trace
        self.mem_store = QdrantDocumentStore(
            url=settings.qdrant_url,
            index=settings.qdrant_collection_memory,
            recreate_index=False,
            return_embedding=True,
            wait_result_from_api=True,
            embedding_dim=settings.embedding_dim,
            similarity=settings.embedding_similarity,
        )

    def _summarize_sync(self, user_text: str, bot_text: str) -> str:
        messages = [
            ChatMessage.from_system(_SUMMARY_SYSTEM_PROMPT),
            ChatMessage.from_user(f"User said: {user_text}"),
            ChatMessage.from_assistant(f"Assistant replied: {bot_text}"),
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
        # Use upsert so repeated memories get updated
        self.mem_store.write_documents([embedded_doc], policy="upsert")
        return embedded_doc.id

    async def process_turn(self, *, user_id: str, session_id: str, user_text: str, bot_text: str) -> None:
        try:
            summary = await asyncio.to_thread(self._summarize_sync, user_text, bot_text)
            logger.info(f"Memory summary: {summary!r}")
            upserted_id = await asyncio.to_thread(self._embed_and_upsert, summary, user_id, session_id)

            if upserted_id:
                logger.info(f"User memory upserted: {upserted_id} (user={user_id}, session={session_id})")
            else:
                logger.info("No durable memory extracted for this turn.")
        except Exception as e:
            logger.error(f"Memory summarization failed: {e}")


# Singleton used by ws_chat
memory_summarizer = MemorySummarizer()
