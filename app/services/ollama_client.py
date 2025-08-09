from __future__ import annotations

from typing import List, Dict, Any
import httpx

from app.config import settings


class DirectOllamaClient:
    """
    Minimal client for Ollama /api/chat (non-streaming).
    We keep stream=False and chunk the final text ourselves.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_chat_model

    def chat(self, messages: List[Dict[str, str]], options: Dict[str, Any] | None = None) -> str:
        """
        messages = [{"role": "system"|"user"|"assistant", "content": "..."}, ...]
        returns full assistant text (no streaming)
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,  # critical: avoid unstable streaming shapes
        }
        if options:
            payload["options"] = options

        url = f"{self.base_url}/api/chat"
        with httpx.Client(timeout=120) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            # Ollama /api/chat (non-stream) returns {"message": {"role":"assistant","content":"..."} , ...}
            msg = data.get("message") or {}
            return msg.get("content", "") or ""
