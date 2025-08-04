from haystack import Document, Pipeline
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

import os

def load_documents_from_folder(folder_path: str):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(Document(content=content, meta={"name": filename}))
    return documents


# STEP 1: Initialize Qdrant Document Store
document_store = QdrantDocumentStore(
    path="./qdrant_data",         # Local folder to persist vectors
    index="wellbot_index",        # Name of collection
    recreate_index=True,          # Clear on each run (disable in production)
    return_embedding=True,
    wait_result_from_api=True,
    embedding_dim=768,            # Must match Ollama's output
    similarity="cosine"
)

# STEP 2: Create sample documents
documents = load_documents_from_folder("./context_doc")
for doc in documents:
    print(f"Loaded: {doc.meta['name']} ({len(doc.content)} chars)")


# STEP 3: Embed documents using Ollama
document_embedder = OllamaDocumentEmbedder()
embedded_docs = document_embedder.run(documents)["documents"]

# STEP 4: Write embedded docs to Qdrant
document_store.write_documents(embedded_docs, policy="overwrite")


# STEP 5: Build retrieval pipeline
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", OllamaTextEmbedder())
query_pipeline.add_component("retriever", QdrantEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

# STEP 6: Query the index
query = "what does Jason like to eat?"
result = query_pipeline.run({"text_embedder": {"text": query}})

# STEP 7: Print best match
top_doc = result["retriever"]["documents"][0]
print("Top result:", top_doc.content)
