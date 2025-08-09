#app/schemas.py

from __future__ import annotations

from typing import Any, Literal, Optional
from typing import Annotated
from pydantic import BaseModel, Field


# ---------- Inbound (client -> server) ----------

Str1 = Annotated[str, Field(min_length=1)]
NonEmpty = Annotated[str, Field(min_length=1, strip_whitespace=True)]

class ChatIn(BaseModel):
    session_id: NonEmpty
    user_id: NonEmpty
    text: Str1


# ---------- Outbound (server -> client, streamed) ----------

class TokenOut(BaseModel):
    """A single streamed token/chunk from the LLM."""
    type: Literal["token"] = "token"
    text: str


class RetrievalDocMeta(BaseModel):
    """Metadata for a retrieved document that grounded the answer."""
    collection: str = Field(..., description="e.g., kb_docs or user_memory")
    doc_id: str
    score: Optional[float] = None
    source: Optional[str] = None  # e.g., filename/url
    meta: Optional[dict[str, Any]] = None  # user_id/session_id/timestamp etc.


class UsageMeta(BaseModel):
    """Lightweight usage/telemetry for observability."""
    latency_ms: Optional[int] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    model: Optional[str] = None


class MetaOut(BaseModel):
    """Sent once per turn after streaming finishes."""
    type: Literal["meta"] = "meta"
    retrieval: list[RetrievalDocMeta] = Field(default_factory=list)
    usage: UsageMeta = UsageMeta()


class DoneOut(BaseModel):
    """Signals end of stream for this turn."""
    type: Literal["done"] = "done"


class ErrorOut(BaseModel):
    """Error frame (non-fatal unless the server closes)."""
    type: Literal["error"] = "error"
    message: str
    detail: Optional[dict[str, Any]] = None
