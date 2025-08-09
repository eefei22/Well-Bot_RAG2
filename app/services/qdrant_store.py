# app/services/qdrant_store.py

from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

def ensure_collection(name: str):
    client = QdrantClient(url=settings.qdrant_url)
    if name not in [c.name for c in client.get_collections().collections]:
        logger.info(f"Creating Qdrant collection: {name}")
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(
                size=settings.embedding_dim,
                distance=models.Distance.COSINE
            )
        )

    # Payload indexes
    for field in ["session_id", "user_id", "timestamp"]:
        try:
            client.create_payload_index(
                collection_name=name,
                field_name=field,
                field_schema=models.PayloadSchemaType.KEYWORD
            )
        except Exception as e:
            logger.debug(f"Index for {field} may already exist: {e}")

def bootstrap_qdrant():
    ensure_collection(settings.qdrant_collection_docs)
    ensure_collection(settings.qdrant_collection_memory)
    logger.info("Qdrant bootstrap complete.")
