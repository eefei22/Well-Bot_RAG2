# app/main.py

from __future__ import annotations

import asyncio
from fastapi import FastAPI

from app.routers import ws_chat
from app.services.qdrant_store import bootstrap_qdrant
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Well-Bot Realtime RAG")

    # Routers
    app.include_router(ws_chat.router)

    async def _bootstrap_qdrant_non_blocking() -> None:
        """
        Run Qdrant bootstrap in the background so app startup doesn't block.
        Times out quickly in dev; app continues to serve WS routes regardless.
        """
        try:
            # Run the (likely blocking) bootstrap in a thread with a short timeout.
            await asyncio.wait_for(asyncio.to_thread(bootstrap_qdrant), timeout=5.0)
            logger.info("Qdrant bootstrap completed.")
        except asyncio.TimeoutError:
            logger.warning("Qdrant bootstrap timed out (continuing without blocking app).")
        except Exception as e:
            logger.error(f"Qdrant bootstrap failed (continuing): {e}")

    @app.on_event("startup")
    async def startup_event():
        logger.info("App startup: scheduling non-blocking Qdrant bootstrap.")
        # Fire-and-forget task; the app becomes ready immediately.
        asyncio.create_task(_bootstrap_qdrant_non_blocking())

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
