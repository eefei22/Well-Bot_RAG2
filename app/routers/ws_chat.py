# app/routers/ws_chat.py

from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.schemas import ChatIn, TokenOut, MetaOut, DoneOut, ErrorOut
from app.state.session_store import session_store
from app.utils.logging import get_logger
from app.services.RAG_pipeline import RAGPipeline
from app.services.memory_summarizer import memory_summarizer

router = APIRouter()
logger = get_logger(__name__)

# Single pipeline instance for the app lifetime
pipeline = RAGPipeline()


async def _safe_send_text(ws: WebSocket, data: str) -> None:
    """Send a text frame only if the socket is still open."""
    try:
        if ws.client_state == WebSocketState.CONNECTED:
            await ws.send_text(data)
    except Exception:
        # client may have already gone away; ignore
        pass


async def _safe_close(ws: WebSocket, code: int = 1000, reason: str = "") -> None:
    """Close the socket only if it hasn't been closed yet."""
    try:
        if ws.client_state == WebSocketState.CONNECTED:
            await ws.close(code=code, reason=reason)
    except Exception:
        pass


async def _finalize_session(user_id: Optional[str], session_id: Optional[str]) -> None:
    """
    End-of-session hook:
      - Read full in-memory history for the session
      - Call memory_summarizer.process_session(...) once
      - Clear the session state
    Safe to call multiple times; no-ops on missing ids/history.
    """
    if not user_id or not session_id:
        return

    state = session_store.get(session_id)
    history = state.get("history", [])
    try:
        if history:
            await memory_summarizer.process_session(
                user_id=user_id,
                session_id=session_id,
                history=history,
            )
    except Exception as e:
        logger.error(f"Final session summarization failed (user={user_id}, session={session_id}): {e}")
    finally:
        # Clear the session cache regardless
        session_store.delete(session_id)


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    last_user_id: Optional[str] = None
    last_session_id: Optional[str] = None

    # Optional greet (best-effort)
    await _safe_send_text(websocket, TokenOut(text="Hi! How can I help you today?").model_dump_json())

    try:
        while True:
            raw = await websocket.receive_text()

            # Parse inbound payload into ChatIn (fallback to plain text)
            try:
                data: dict[str, Any] = json.loads(raw)
                chat_in = ChatIn(**data)
            except Exception:
                chat_in = ChatIn(session_id="dev-session", user_id="dev-user", text=raw)

            # Assign ids + text BEFORE using them
            last_user_id = chat_in.user_id
            last_session_id = chat_in.session_id
            text = (chat_in.text or "").strip()
            if not text:
                continue

            # Exit signal: finalize, then best-effort notify & close, then return
            if text.lower() == "exit":
                await _finalize_session(last_user_id, last_session_id)
                await _safe_send_text(websocket, DoneOut().model_dump_json())
                await _safe_close(websocket, code=1000)
                logger.info("WebSocket closed by client request (exit).")
                return

            # Maintain a small rolling in-memory history (non-persistent)
            state = session_store.get(last_session_id)
            hist = state.get("history", [])
            hist.append({"role": "user", "content": text})
            session_store.set(last_session_id, {"history": hist})

            loop = asyncio.get_running_loop()

            # Bridge callback from a background thread to this async WS safely
            def on_token(tok: str) -> None:
                try:
                    if websocket.client_state == WebSocketState.CONNECTED:
                        frame = TokenOut(text=tok).model_dump_json()
                        asyncio.run_coroutine_threadsafe(websocket.send_text(frame), loop)
                except Exception as e:
                    logger.error(f"Failed to send token: {e}")

            # Run the blocking RAG call in a worker thread (include short-term history)
            final_text, meta = await asyncio.to_thread(
                pipeline.run_rag,
                user_id=last_user_id,
                session_id=last_session_id,
                query=text,
                history=hist,
                on_token=on_token,
            )

            # Send meta frame (retrieval, usage, latency) best-effort
            await _safe_send_text(websocket, MetaOut(**meta).model_dump_json())

            # Append assistant reply to in-memory history
            hist.append({"role": "assistant", "content": final_text})
            session_store.set(last_session_id, {"history": hist})

            # NOTE: Per-turn summarization removed — we now summarize only at end-of-session.

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        # Finalize on abrupt disconnect, then return (no more WS I/O)
        await _finalize_session(last_user_id, last_session_id)
        return
    except Exception as e:
        logger.exception("WebSocket error")
        # Finalize first; then try to notify client if still connected; then close
        await _finalize_session(last_user_id, last_session_id)
        await _safe_send_text(websocket, ErrorOut(message=str(e)).model_dump_json())
        await _safe_close(websocket, code=1011)
        return
