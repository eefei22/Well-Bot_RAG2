# app/services/retriever.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from haystack import Document
from haystack_integrations.components.embedders.ollama.text_embedder import (
    OllamaTextEmbedder,
)
from haystack_integrations.components.retrievers.qdrant import (
    QdrantEmbeddingRetriever,
)
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from app.config import settings
from app.utils.logging import get_logger
from typing import Optional, Dict, Any, List

logger = get_logger(__name__)


def _build_qdrant_store(collection: str) -> QdrantDocumentStore:
    """HTTP mode Qdrant store for a specific collection."""
    return QdrantDocumentStore(
        url=settings.qdrant_url,
        index=collection,
        recreate_index=False,
        return_embedding=False,
        wait_result_from_api=True,
        embedding_dim=settings.embedding_dim,
        similarity=settings.embedding_similarity,
    )


def build_filters(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    min_timestamp_epoch: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Return a Haystack-format filter:
    {
      "operator": "AND",
      "conditions": [
        {"field": "meta.user_id", "operator": "==", "value": "..."},
        {"field": "meta.session_id", "operator": "==", "value": "..."},
        {"field": "meta.timestamp_epoch", "operator": ">=", "value": 1723180800.0},
      ]
    }
    Return None if no conditions (avoid passing {})
    """
    conditions: List[Dict[str, Any]] = []
    if user_id:
        conditions.append({"field": "meta.user_id", "operator": "==", "value": user_id})
    if session_id:
        conditions.append({"field": "meta.session_id", "operator": "==", "value": session_id})
    if min_timestamp_epoch is not None:
        conditions.append({"field": "meta.timestamp_epoch", "operator": ">=", "value": float(min_timestamp_epoch)})

    if not conditions:
        return None
    return {"operator": "AND", "conditions": conditions}



@dataclass
class RetrieverConfig:
    collection: str
    top_k: int = 4


class DualRetriever:
    """
    Two-stage retrieval:
      - Long-term knowledge (kb_docs)
      - User memory (user_memory)
    Embeds the query once, then calls both retrievers directly.
    """

    def __init__(
        self,
        kb_cfg: RetrieverConfig,
        mem_cfg: RetrieverConfig,
    ) -> None:
        self.kb_store = _build_qdrant_store(kb_cfg.collection)
        self.mem_store = _build_qdrant_store(mem_cfg.collection)
        self.kb_cfg = kb_cfg
        self.mem_cfg = mem_cfg

        # Components (not mounted into Pipelines)
        self.text_embedder = OllamaTextEmbedder(model=settings.ollama_embed_model)
        self.kb_retriever = QdrantEmbeddingRetriever(document_store=self.kb_store)
        self.mem_retriever = QdrantEmbeddingRetriever(document_store=self.mem_store)

    def _embed_query(self, query: str) -> list[float]:
        out = self.text_embedder.run(text=query)
        emb = out.get("embedding")
        if not emb:
            raise RuntimeError("Failed to compute query embedding.")
        return emb

    def _retrieve_direct(
        self,
        retriever: QdrantEmbeddingRetriever,
        *,
        query_embedding: List[float],
        top_k: int,
        filters: Dict,
    ) -> List[Document]:
        out = retriever.run(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )
        return out.get("documents", [])

    def retrieve(
        self,
        *,
        query: str,
        user_filters: Dict,
        kb_filters: Optional[Dict] = None,
    ) -> Tuple[List[Document], List[Document]]:
        """Run both retrievers and return (kb_docs, user_memory_docs)."""
        kb_filters = kb_filters or {}
        q_emb = self._embed_query(query)

        kb_docs = self._retrieve_direct(
            self.kb_retriever,
            query_embedding=q_emb,
            top_k=self.kb_cfg.top_k,
            filters=kb_filters,
        )
        mem_docs = self._retrieve_direct(
            self.mem_retriever,
            query_embedding=q_emb,
            top_k=self.mem_cfg.top_k,
            filters=user_filters,
        )
        return kb_docs, mem_docs

    @staticmethod
    def combine_results(
        kb_docs: List[Document],
        mem_docs: List[Document],
        *,
        cap_total: int = 8,
    ) -> List[Document]:
        """Merge results preferring memory first, then KB, dedup by id."""
        seen = set()
        ordered: List[Document] = []
        for group in (mem_docs, kb_docs):
            for d in group:
                if d.id not in seen:
                    seen.add(d.id)
                    ordered.append(d)
                if len(ordered) >= cap_total:
                    return ordered
        return ordered
