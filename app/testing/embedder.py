from haystack_integrations.components.embedders.ollama.document_embedder import OllamaDocumentEmbedder
from haystack import Document

embedder = OllamaDocumentEmbedder()
docs = [Document(content="test")]
embedded = embedder.run(docs)["documents"]
print(len(embedded[0].embedding))
