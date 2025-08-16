# app/services/RAG_pipeline.py

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from typing import Callable, Dict, List, Tuple, Sequence, TypedDict, Optional

from haystack.dataclasses import ChatMessage
from haystack import Document

from app.config import settings
from app.utils.logging import get_logger
from app.services.generator import LLMGenerator
from app.services.retriever import (
    DualRetriever,
    RetrieverConfig,
    build_filters,
)

logger = get_logger(__name__)

class HistMsg(TypedDict):
    role: str  # "user" | "assistant"
    content: str

def _history_to_messages(history: Sequence[HistMsg], max_chars: int = 1200) -> list[ChatMessage]:
    msgs: list[ChatMessage] = []
    used = 0
    # Take last ~10 messages worth of turns, capped to ~1200 chars
    for h in history[-10:]:
        txt = (h.get("content") or "").strip()
        if not txt:
            continue
        if used + len(txt) > max_chars:
            break
        used += len(txt)
        role = (h.get("role") or "user").lower()
        if role == "assistant":
            msgs.append(ChatMessage.from_assistant(txt))
        else:
            msgs.append(ChatMessage.from_user(txt))
    return msgs

def _epoch_minutes_back(minutes: int) -> float:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).timestamp()

def _format_context(docs: List[Document], max_chars: int = 1800) -> str:
    """
    Join snippets from retrieved docs into a compact context block for the prompt.
    """
    parts: List[str] = []
    used = 0
    for d in docs:
        src = d.meta.get("source") or d.meta.get("name") or d.id[:8]
        chunk = (d.content or "").strip()
        if not chunk:
            continue
        chunk = chunk[:600]  # prefer shorter, dense chunks
        line = f"[{src}] {chunk}"
        if used + len(line) > max_chars:
            break
        used += len(line)
        parts.append(line)
    return "\n".join(parts)

def _system_prompt() -> str:
    return (
        "You are Well-Bot, a friendly, empathetic Pet Robot, you are talking to your owner Alex. "
        "Use the provided CONTEXT when it is relevant. "
        "Be concise (<=200 words), empathetic, never ever use emojis."
    )

class RAGPipeline:
    """
    Two-stage retrieval (KB + user memory) + chat generation with token streaming.
    """

    def __init__(
        self,
        *,
        kb_top_k: int = 4,
        mem_top_k: int = 4,
        mem_time_window_min: int | None = 7 * 24 * 60,  # last 7 days by default; set None for no limit
    ) -> None:
        self.dual_ret = DualRetriever(
            kb_cfg=RetrieverConfig(collection=settings.qdrant_collection_docs, top_k=kb_top_k),
            mem_cfg=RetrieverConfig(collection=settings.qdrant_collection_memory, top_k=mem_top_k),
        )
        self.generator = LLMGenerator()
        self.mem_time_window_min = mem_time_window_min

    def run_rag(
        self,
        *,
        user_id: str,
        session_id: str,  # still passed for telemetry/meta, but not used for memory filtering anymore
        query: str,
        history: Optional[Sequence[HistMsg]] = None,
        on_token: Callable[[str], None] | None = None,
    ) -> Tuple[str, Dict]:
        """
        Execute retrieval + generation. Streams tokens via on_token.
        Returns: (final_text, meta)
        """
        t0 = time.perf_counter()

        # --- Build filters ---
        # Cross-session recall: filter persistent user memory by user_id (+ optional recency), NOT session_id.
        min_ts_epoch = (
            _epoch_minutes_back(self.mem_time_window_min)
            if self.mem_time_window_min is not None
            else None
        )
        mem_filters = build_filters(
            user_id=user_id,
            # session_id=session_id,  # intentionally omitted for cross-session recall
            min_timestamp_epoch=min_ts_epoch,
        )
        kb_filters = None  # widen as needed

        # --- Retrieve ---
        kb_docs, mem_docs = self.dual_ret.retrieve(
            query=query, user_filters=mem_filters, kb_filters=kb_filters
        )
        all_docs = self.dual_ret.combine_results(kb_docs, mem_docs, cap_total=8)

        # --- Build prompt ---
        ctx_block = _format_context(all_docs)
        sys = _system_prompt()
        messages: List[ChatMessage] = [
            ChatMessage.from_system(f"{sys}\n\nCONTEXT:\n{ctx_block}" if ctx_block else sys)
        ]

        if history:
            messages.extend(_history_to_messages(history))

        messages.append(ChatMessage.from_user(query))

        # --- Generate with streaming ---
        final_text, usage = self.generator.stream_chat(messages, on_token=on_token)

        latency_ms = int((time.perf_counter() - t0) * 1000)

        # --- Meta (observability) ---
        retrieval_meta: List[Dict] = []
        for d in mem_docs:
            retrieval_meta.append(
                {
                    "collection": settings.qdrant_collection_memory,
                    "doc_id": d.id,
                    "score": d.score if hasattr(d, "score") else None,
                    "source": d.meta.get("source") or d.meta.get("name"),
                    "meta": {
                        k: v
                        for k, v in d.meta.items()
                        if k in ("user_id", "session_id", "timestamp")
                    },
                }
            )
        for d in kb_docs:
            retrieval_meta.append(
                {
                    "collection": settings.qdrant_collection_docs,
                    "doc_id": d.id,
                    "score": d.score if hasattr(d, "score") else None,
                    "source": d.meta.get("source") or d.meta.get("name"),
                    "meta": d.meta,
                }
            )

        meta = {
            "retrieval": retrieval_meta,
            "usage": {
                "model": usage.get("model"),
                "latency_ms": latency_ms,
            },
        }

        return final_text, meta
