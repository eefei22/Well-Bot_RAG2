# app/routers/ws_chat.py

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas import ChatIn, TokenOut, MetaOut, DoneOut, ErrorOut
from app.state.session_store import session_store
from app.utils.logging import get_logger
from app.services.RAG_pipeline import RAGPipeline
from app.services.memory_summarizer import memory_summarizer

router = APIRouter()
logger = get_logger(__name__)

# Create a single pipeline instance for the app lifetime
pipeline = RAGPipeline()


@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    # Optional: greet immediately so clients see the stream is alive
    try:
        await websocket.send_text(TokenOut(text="Hi! How can I help you today?").model_dump_json())
    except Exception:
        # greet is best-effort; continue either way
        pass

    try:
        while True:
            raw = await websocket.receive_text()

            # Expect JSON from client; friendly fallback if it's just plain text
            try:
                data: dict[str, Any] = json.loads(raw)
                chat_in = ChatIn(**data)
            except Exception:
                # If plain text, fabricate a minimal payload (dev convenience)
                chat_in = ChatIn(session_id="dev-session", user_id="dev-user", text=raw)

            text = chat_in.text.strip()

            if text.lower() == "exit":
                await websocket.send_text(DoneOut().model_dump_json())
                await websocket.close()
                logger.info("WebSocket closed by client request (exit).")
                break

            # Maintain a tiny rolling window in memory (optional, non-persistent)
            state = session_store.get(chat_in.session_id)
            hist = state.get("history", [])
            hist.append({"role": "user", "content": text})
            session_store.set(chat_in.session_id, {"history": hist})

            loop = asyncio.get_running_loop()

            # Bridge callback from a background thread to this async WS safely
            def on_token(tok: str) -> None:
                try:
                    frame = TokenOut(text=tok).model_dump_json()
                    asyncio.run_coroutine_threadsafe(websocket.send_text(frame), loop)
                except Exception as e:
                    logger.error(f"Failed to send token: {e}")

            # Run the blocking RAG call in a worker thread so we don't block the event loop
            # NOTE: RAGPipeline.run_rag now accepts a `history` parameter (list of {"role","content"}).
            final_text, meta = await asyncio.to_thread(
                pipeline.run_rag,
                user_id=chat_in.user_id,
                session_id=chat_in.session_id,
                query=text,
                history=hist,  # <-- include short-term conversation window
                on_token=on_token,
            )

            # Send meta frame (retrieval, usage, latency)
            await websocket.send_text(MetaOut(**meta).model_dump_json())

            # Update in-memory conversation window
            hist.append({"role": "assistant", "content": final_text})
            session_store.set(chat_in.session_id, {"history": hist})

            # Fire-and-forget: distill user memory and upsert to Qdrant
            asyncio.create_task(
                memory_summarizer.process_turn(
                    user_id=chat_in.user_id,
                    session_id=chat_in.session_id,
                    user_text=text,
                    bot_text=final_text,
                )
            )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.exception("WebSocket error")
        try:
            await websocket.send_text(ErrorOut(message=str(e)).model_dump_json())
        finally:
            await websocket.close()
