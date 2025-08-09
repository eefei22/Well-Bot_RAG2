#app/services/haystack_pipeline.py

from __future__ import annotations

import time
from datetime import datetime, timezone, timedelta
from typing import Callable, Dict, List, Tuple

from haystack.dataclasses import ChatMessage
from haystack import Document
from datetime import datetime, timezone, timedelta

from app.config import settings
from app.utils.logging import get_logger
from app.services.generator import LLMGenerator
from app.services.retriever import (
    DualRetriever,
    RetrieverConfig,
    build_filters,
)
from app.utils.prompts import build_system
# add at top
from typing import Sequence, TypedDict, Optional

class HistMsg(TypedDict):
    role: str  # "user" | "assistant"
    content: str

def _history_to_messages(history: Sequence[HistMsg], max_chars: int = 1200) -> list[ChatMessage]:
    msgs: list[ChatMessage] = []
    used = 0
    for h in history[-10:]:  # last 10 turns (user/assistant = ~20 msgs)
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


logger = get_logger(__name__)

def _epoch_now() -> float:
    return datetime.now(timezone.utc).timestamp()

def _epoch_minutes_back(minutes: int) -> float:
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes)).timestamp()

def _format_context(docs: List[Document], max_chars: int = 1800) -> str:
    """
    Join snippets from retrieved docs into a compact context block for the prompt.
    Trim aggressively to keep LLM focused (real UIs can show full context separately).
    """
    parts = []
    used = 0
    for d in docs:
        src = d.meta.get("source") or d.meta.get("name") or d.id[:8]
        chunk = (d.content or "").strip()
        if not chunk:
            continue
        # prefer shorter, dense chunks
        chunk = chunk[:600]
        line = f"[{src}] {chunk}"
        if used + len(line) > max_chars:
            break
        used += len(line)
        parts.append(line)
    return "\n".join(parts)

def _system_prompt() -> str:
    """
    Lightweight system prompt; we’ll move this to utils/prompts.py later.
    """
    return (
        "You are Well‑Bot, a friendly, precise assistant. "
        "Use the provided CONTEXT when it is relevant. "
        "Be concise (<=200 words), empathetic, and avoid emojis."
    )


class RAGPipeline:
    """
    Orchestrates two-stage retrieval (KB + user memory) and chat generation with streaming.
    This object is long-lived (create once at app startup).
    """

    def __init__(
        self,
        *,
        kb_top_k: int = 4,
        mem_top_k: int = 4,
        mem_time_window_min: int | None = 7 * 24 * 60,  # last 7 days default
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
        session_id: str,
        query: str,
        history: Optional[Sequence[HistMsg]] = None,   # <— NEW
        on_token: Callable[[str], None] | None = None,
    ) -> Tuple[str, Dict]:
        """
        Execute retrieval + generation. Streams tokens via on_token.
        Returns:
            final_text, meta (retrieval list + usage)
        """
        t0 = time.perf_counter()

        # --- Build filters ---
        min_ts_epoch = _epoch_minutes_back(self.mem_time_window_min) if self.mem_time_window_min else None
        mem_filters = build_filters(
            user_id=user_id,
            session_id=session_id,
            min_timestamp_epoch=min_ts_epoch,
        )
        kb_filters = None

        # --- Retrieve ---
        kb_docs, mem_docs = self.dual_ret.retrieve(
            query=query, user_filters=mem_filters, kb_filters=kb_filters
        )
        all_docs = self.dual_ret.combine_results(kb_docs, mem_docs, cap_total=8)

        # --- Build prompt ---
        ctx_block = _format_context(all_docs)
        sys = _system_prompt()
        messages: List[ChatMessage] = [ChatMessage.from_system(f"{sys}\n\nCONTEXT:\n{ctx_block}" if ctx_block else sys)]

        if history:
            messages.extend(_history_to_messages(history))

        messages.append(ChatMessage.from_user(query))

        # --- Generate with streaming ---
        final_text, usage = self.generator.stream_chat(messages, on_token=on_token)

        latency_ms = int((time.perf_counter() - t0) * 1000)
        # --- Meta to report back to client ---
        retrieval_meta = []
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
                # token counts can be added later once exposed
            },
        }

        return final_text, meta
