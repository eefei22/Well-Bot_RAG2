# app/utils/prompts.py
SYSTEM_RAG = (
  "You are Well‑Bot. Be concise (≤200 words), accurate, and empathetic. "
  "Use CONTEXT only if relevant. Never invent facts."
)

def build_system(ctx: str) -> str:
    return f"{SYSTEM_RAG}\n\nCONTEXT:\n{ctx}" if ctx else SYSTEM_RAG
