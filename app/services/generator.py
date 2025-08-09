#a app/services/generator.py

from __future__ import annotations

from typing import Callable, Optional, Dict, Any, List

from haystack.dataclasses import ChatMessage

from app.config import settings
from app.services.ollama_client import DirectOllamaClient


def _to_ollama_messages(hs_msgs: List[ChatMessage]) -> List[Dict[str, str]]:
    """
    Convert Haystack ChatMessage list -> Ollama /api/chat messages.
    """
    out: List[Dict[str, str]] = []
    for m in hs_msgs:
        # ChatMessage has .role and .text in Haystack 2.x objects
        role = getattr(m, "role", "user").lower()
        text = getattr(m, "text", "") or ""
        if role not in ("system", "user", "assistant", "tool"):
            role = "user"
        out.append({"role": role, "content": text})
    return out


class LLMGenerator:
    """
    Generation via direct Ollama /api/chat (stream: false).
    We simulate streaming by chunking the final text to on_token.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        url: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.model = model or settings.ollama_chat_model
        self.url = url or settings.ollama_url
        # Configure options for Ollama (temperature/top_p map to "options" in /api/chat)
        self.options = {
            "temperature": 0.8,
            "top_p": 0.9,
            **(generation_kwargs or {}),
        }
        self.client = DirectOllamaClient(base_url=self.url, model=self.model)

    def _chunk_text(self, text: str, max_len: int = 40) -> List[str]:
        chunks: List[str] = []
        buf, cur = [], 0
        for tok in text.split(" "):  # explicit split on spaces
            if cur + len(tok) + (1 if buf else 0) > max_len:
                chunks.append(" ".join(buf) + " ")  # <-- add trailing space
                buf, cur = [tok], len(tok)
            else:
                buf.append(tok)
                cur += len(tok) + (1 if buf and len(buf) > 1 else 0)
        if buf:
            chunks.append(" ".join(buf) + " ")
        return chunks or ([text] if text else [])


    def stream_chat(
        self,
        messages: List[ChatMessage],
        on_token: Optional[Callable[[str], None]] = None,
    ) -> tuple[str, dict]:
        # Convert to Ollama’s expected shape
        ollama_msgs = _to_ollama_messages(messages)
        # Non-streaming call (robust)
        final_text = self.client.chat(ollama_msgs, options=self.options)

        # Faux streaming: emit slices to on_token
        if on_token and final_text:
            for chunk in self._chunk_text(final_text, max_len=40):
                try:
                    on_token(chunk)
                except Exception:
                    pass

        usage = {"model": self.model}
        return final_text, usage
