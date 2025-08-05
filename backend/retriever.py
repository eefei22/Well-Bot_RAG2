from haystack import Pipeline
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

# Initialize the retriever pipeline once
document_store = QdrantDocumentStore(
    path="./qdrant_store",
    index="wellbot_index",
    recreate_index=False,  #do not change 
    return_embedding=True,
    wait_result_from_api=True,
    embedding_dim=768,
    similarity="cosine"
)

text_embedder = OllamaTextEmbedder()
retriever = QdrantEmbeddingRetriever(document_store=document_store)

query_pipeline = Pipeline()
query_pipeline.add_component("text_embedder", text_embedder)
query_pipeline.add_component("retriever", retriever)
query_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")

# Function to call externally
def retrieve_top_document(user_query: str) -> str:
    result = query_pipeline.run({"text_embedder": {"text": user_query}})
    top_doc = result["retriever"]["documents"][0]
    return top_doc.content


# ================================================================
# DEPENDENCIES REQUIRED:
# ================================================================
# haystack
# haystack-integrations: Ollama, qdrant
#   ollama (Ollama server for embedding: localhost:11434)
#   qdrant (Qdrant vector database)
#
# ================================================================
# WORKFLOW SUMMARY:
# ================================================================
# 1. Initializes QdrantDocumentStore to connect to the local Qdrant vector DB.
# 2. Uses OllamaTextEmbedder to embed user queries.
# 3. Retrieves top matching document from Qdrant using QdrantEmbeddingRetriever.
# 4. Exposes `retrieve_top_document` to return the content of the most relevant document for a given query.
