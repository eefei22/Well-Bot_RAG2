from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from datetime import datetime

# Connect to Qdrant chat history index
document_store = QdrantDocumentStore(
    url="http://localhost:6333",
    index="chat_history",
    embedding_dim=768
)

# Retrieve all stored documents
documents = document_store.filter_documents(filters={})

# Sort by timestamp
documents_sorted = sorted(
    documents,
    key=lambda doc: datetime.fromisoformat(doc.meta.get("timestamp"))
)

# Display sorted messages
for doc in documents_sorted:
    raw_ts = doc.meta.get("timestamp")
    dt = datetime.fromisoformat(raw_ts)
    formatted_ts = dt.strftime("%Y-%m-%d %I:%M %p %Z")
    print(f"[{formatted_ts}] [{doc.meta.get('role')}] {doc.content}")
