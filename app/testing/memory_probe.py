from app.services.memory_summarizer import memory_summarizer
from qdrant_client import QdrantClient
from app.config import settings

# Force a memory snippet without the LLM (bypass summarize step)
USER_ID = "alex"
SESSION_ID = "probe-session"
TEXT = "• Enjoys mangoes. • Trains 6 days a week."

if __name__ == "__main__":
    # Use the private method directly to isolate write path
    upserted_id = memory_summarizer._embed_and_upsert(TEXT, USER_ID, SESSION_ID)
    print("Upserted ID:", upserted_id)

    # Read back a couple of points
    c = QdrantClient(url=settings.qdrant_url)
    pts, _ = c.scroll(collection_name=settings.qdrant_collection_memory, limit=5, with_payload=True)
    print("\nuser_memory peek:")
    for p in pts:
        print("-", p.id, p.payload)
