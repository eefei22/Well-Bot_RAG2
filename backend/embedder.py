from haystack import Document, Pipeline
from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

import os
# need to run: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

def load_documents_from_folder(folder_path: str):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(Document(content=content, meta={"name": filename}))
    return documents


# 1: Initialize Qdrant Document Store
document_store = QdrantDocumentStore(
    path="./qdrant_store",        # Local folder to persist vectors
    index="wellbot_index",        
    recreate_index=True,          
    return_embedding=True,
    wait_result_from_api=True,
    embedding_dim=768,            
    similarity="cosine"
)

# 2: Create sample documents
documents = load_documents_from_folder("./context_doc")
for doc in documents:
    print(f"Loaded: {doc.meta['name']} ({len(doc.content)} chars)")


# 3: Embed documents using Ollama
document_embedder = OllamaDocumentEmbedder()
embedded_docs = document_embedder.run(documents)["documents"]

# 4: Write embedded docs to Qdrant
document_store.write_documents(embedded_docs, policy="overwrite")   #TODO: CHANGE THIS POLICY




# ================================================================
# TESTING:
# ================================================================

# 5: Build retrieval pipeline
query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", OllamaTextEmbedder())
query_pipeline.add_component("retriever", QdrantEmbeddingRetriever(document_store=document_store))
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

# 6: Query the index
query = "what does Jason like to eat?"
result = query_pipeline.run({"text_embedder": {"text": query}})

# 7: Print best match
top_doc = result["retriever"]["documents"][0]
print("Top result:", top_doc.content)








# ================================================================
# DEPENDENCIES REQUIRED:
# ================================================================
# pip install haystack-ai
# pip install haystack-integrations[qdrant]
# pip install haystack-integrations[ollama]
# 
# External Services:
# - Docker: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
# - Ollama: Local LLM service for embeddings
#
# ================================================================
# WORKFLOW SUMMARY:
# ================================================================
# Load → Read text documents from folder
# Embed → Convert documents to vector embeddings using Ollama
# Store → Save embeddings in Qdrant vector database
# Query → Accept natural language questions
# Retrieve → Find and return most relevant document content
