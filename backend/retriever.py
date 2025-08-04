from haystack import Pipeline
from haystack_integrations.components.embedders.ollama.text_embedder import OllamaTextEmbedder
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

# Initialize the retriever pipeline once
document_store = QdrantDocumentStore(
    path="./qdrant_store",
    index="wellbot_index",
    recreate_index=False,  # Set to False to avoid deleting your index every time
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
