# app/services/embedder.py

from haystack import Document
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.config import settings


def load_documents_from_folder(folder_path: str):
    docs = []
    for fn in os.listdir(folder_path):
        if fn.endswith(".txt"):
            p = os.path.join(folder_path, fn)
            with open(p, "r", encoding="utf-8") as f:
                docs.append(Document(content=f.read(), meta={"name": fn, "source": fn}))
    return docs

store = QdrantDocumentStore(
    url=settings.qdrant_url,
    index=settings.qdrant_collection_docs,  # <- kb_docs
    recreate_index=False,
    return_embedding=True,
    wait_result_from_api=True,
    embedding_dim=settings.embedding_dim,
    similarity=settings.embedding_similarity,
)

docs = load_documents_from_folder("./context_doc")
embedder = OllamaDocumentEmbedder(model=settings.ollama_embed_model)  # 768-dim
embedded = embedder.run(docs)["documents"]
store.write_documents(embedded, policy="upsert")
print(f"Indexed {len(embedded)} docs into {settings.qdrant_collection_docs}")
