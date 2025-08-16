# app/services/generator.py

from __future__ import annotations

import json
from typing import Callable, Optional, Dict, Any, List, Sequence, Tuple

import requests
from haystack.dataclasses import ChatMessage

from app.config import settings
from app.services.ollama_client import DirectOllamaClient
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _to_ollama_messages(hs_msgs: Sequence[ChatMessage]) -> List[Dict[str, str]]:
    """
    Convert Haystack ChatMessage list -> Ollama /api/chat messages.
    IMPORTANT: Use .text (your project’s field), not .content.
    """
    out: List[Dict[str, str]] = []
    for m in hs_msgs:
        role = getattr(m, "role", "user")
        # role might be an enum; normalize to lowercase string
        role = getattr(role, "value", role)
        role = (role or "user").lower()
        text = getattr(m, "text", "") or ""
        if role not in ("system", "user", "assistant", "tool"):
            role = "user"
        out.append({"role": role, "content": text})
    return out


class LLMGenerator:
    """
    Generation via Ollama.
    - If `on_token` is provided, we first try TRUE streaming via /api/chat (stream=True).
    - If streaming fails, we fall back to a single non-streaming call and "faux" stream chunks.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        url: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.model = model or settings.ollama_chat_model
        self.url = (url or settings.ollama_url).rstrip("/")
        # Options for Ollama (map to "options" in /api/chat)
        self.options: Dict[str, Any] = {
            "temperature": 0.8,
            "top_p": 0.9,
            **(generation_kwargs or {}),
        }
        self.client = DirectOllamaClient(base_url=self.url, model=self.model)

    # --- Faux streaming for the non-streaming fallback ---
    def _chunk_text(self, text: str, max_len: int = 40) -> List[str]:
        chunks: List[str] = []
        buf, cur = [], 0
        for tok in text.split(" "):  # explicit split on spaces
            if cur + len(tok) + (1 if buf else 0) > max_len:
                chunks.append(" ".join(buf) + " ")
                buf, cur = [tok], len(tok)
            else:
                buf.append(tok)
                cur += len(tok) + (1 if len(buf) > 1 else 0)
        if buf:
            chunks.append(" ".join(buf) + " ")
        return chunks or ([text] if text else [])

    # --- True streaming via Ollama HTTP API ---
    def _stream_via_http(
        self,
        messages: List[Dict[str, str]],
        on_token: Callable[[str], None],
    ) -> str:
        """
        Connects to /api/chat with stream=True and yields deltas to on_token.
        Returns the final concatenated text.
        """
        endpoint = f"{self.url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "options": self.options or None,
            "stream": True,
        }

        final_parts: List[str] = []
        # Reasonable timeouts: (connect, read)
        with requests.post(endpoint, json=payload, stream=True, timeout=(10, 300)) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True, chunk_size=1):
                if not line:
                    continue
                # Each line is JSON with partial content
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message") or {}
                delta = msg.get("content") or ""
                if delta:
                    final_parts.append(delta)
                    try:
                        on_token(delta)
                    except Exception as cb_err:
                        logger.error(f"on_token callback failed: {cb_err}")
                # stop when ollama indicates completion
                if obj.get("done") is True:
                    break

        return "".join(final_parts)

    def stream_chat(
        self,
        messages: List[ChatMessage],
        on_token: Optional[Callable[[str], None]] = None,
    ) -> Tuple[str, Dict]:
        # Convert to Ollama’s expected shape
        ollama_msgs = _to_ollama_messages(messages)

        # Try TRUE streaming when a callback is provided
        if on_token is not None:
            try:
                final_text = self._stream_via_http(ollama_msgs, on_token)
                usage = {"model": self.model}
                return final_text, usage
            except Exception as e:
                logger.warning(f"Ollama HTTP streaming failed; falling back to non-streaming. Error: {e}")

        # Non-streaming fallback (previous behavior)
        final_text = self.client.chat(ollama_msgs, options=self.options)

        # Faux streaming: emit slices to on_token if provided
        if on_token and final_text:
            for chunk in self._chunk_text(final_text, max_len=40):
                try:
                    on_token(chunk)
                except Exception:
                    pass

        usage = {"model": self.model}
        return final_text, usage
