from fastapi import FastAPI
from app.routers import ws_chat
from app.services.qdrant_store import bootstrap_qdrant
from app.utils.logging import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="Well-Bot Realtime RAG")

    # Routers
    app.include_router(ws_chat.router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Bootstrapping Qdrant collections")
        bootstrap_qdrant()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()
