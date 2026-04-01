"""
Edge RAG Engine — In-memory vector retrieval in microseconds.
Provides ultra-fast Retrieval-Augmented Generation (RAG) for critical
real-time decisions during races, without relying on external services.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


@dataclass
class RAGDocument:
    """A document stored in the Edge RAG engine."""
    doc_id: str
    content: str
    metadata: dict[str, Any]
    embedding: NDArray[np.float32]
    category: str = "general"


@dataclass
class RAGResult:
    """A single retrieval result."""
    doc_id: str
    content: str
    metadata: dict[str, Any]
    score: float
    category: str


class EdgeRAGEngine:
    """
    In-memory vector RAG engine for sub-millisecond retrieval.

    Uses a flat FAISS-style brute-force search over numpy arrays for
    microsecond-latency retrieval of technical regulations, setup guides,
    and operational procedures during live race sessions.
    """

    def __init__(self, embedding_dim: int = 1536) -> None:
        self.embedding_dim = embedding_dim
        self._documents: list[RAGDocument] = []
        self._embedding_matrix: NDArray[np.float32] | None = None
        self._matrix_dirty = True

    def add_document(self, doc_id: str, content: str,
                     embedding: list[float] | NDArray[np.float32],
                     metadata: dict[str, Any] | None = None,
                     category: str = "general") -> None:
        """Add a document to the in-memory index."""
        emb = np.array(embedding, dtype=np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-12)  # L2 normalise
        doc = RAGDocument(
            doc_id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=emb,
            category=category,
        )
        self._documents.append(doc)
        self._matrix_dirty = True
        logger.debug("Added document to EdgeRAG: %s", doc_id)

    def add_documents_batch(self, documents: list[dict[str, Any]]) -> None:
        """Batch-add documents for efficient index loading."""
        for doc in documents:
            self.add_document(
                doc_id=doc["doc_id"],
                content=doc["content"],
                embedding=doc["embedding"],
                metadata=doc.get("metadata", {}),
                category=doc.get("category", "general"),
            )
        self._rebuild_matrix()

    def _rebuild_matrix(self) -> None:
        """Rebuild the embedding matrix for batch similarity search."""
        if not self._documents:
            self._embedding_matrix = None
            return
        self._embedding_matrix = np.stack(
            [doc.embedding for doc in self._documents], axis=0
        ).astype(np.float32)
        self._matrix_dirty = False
        logger.debug("EdgeRAG matrix rebuilt: %d documents", len(self._documents))

    def retrieve(self, query_embedding: list[float] | NDArray[np.float32],
                 top_k: int = 5,
                 category_filter: str | None = None) -> list[RAGResult]:
        """
        Retrieve the top-k most similar documents to a query embedding.

        This operation runs entirely in memory using matrix multiplication,
        achieving sub-millisecond latency for collections up to ~100k documents.

        Args:
            query_embedding: Query vector (will be L2 normalised).
            top_k: Number of results to return.
            category_filter: Optional category to restrict results.

        Returns:
            List of RAGResult sorted by similarity score (descending).
        """
        if not self._documents:
            return []

        if self._matrix_dirty:
            self._rebuild_matrix()

        t0 = time.perf_counter()
        query = np.array(query_embedding, dtype=np.float32)
        query = query / (np.linalg.norm(query) + 1e-12)

        # Cosine similarity via dot product (embeddings are L2-normalised)
        scores = self._embedding_matrix @ query  # shape: (n_docs,)

        # Apply category filter
        if category_filter:
            mask = np.array(
                [doc.category == category_filter for doc in self._documents],
                dtype=bool,
            )
            scores = np.where(mask, scores, -np.inf)

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] == -np.inf:
                continue
            doc = self._documents[idx]
            results.append(RAGResult(
                doc_id=doc.doc_id,
                content=doc.content,
                metadata=doc.metadata,
                score=float(scores[idx]),
                category=doc.category,
            ))

        elapsed_us = (time.perf_counter() - t0) * 1e6
        logger.debug("EdgeRAG retrieve: %d results in %.1f µs", len(results), elapsed_us)
        return results

    def retrieve_and_format(self, query_embedding: list[float],
                             top_k: int = 3,
                             category_filter: str | None = None) -> str:
        """Retrieve and format results as a prompt-ready context string."""
        results = self.retrieve(query_embedding, top_k=top_k,
                                category_filter=category_filter)
        if not results:
            return "No relevant context found."
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] (score={r.score:.3f}) {r.content}")
        return "\n\n".join(parts)

    def get_stats(self) -> dict[str, Any]:
        """Return engine statistics."""
        return {
            "document_count": len(self._documents),
            "embedding_dim": self.embedding_dim,
            "categories": list({d.category for d in self._documents}),
            "matrix_ready": not self._matrix_dirty,
        }

    def clear(self) -> None:
        """Clear all documents from the engine."""
        self._documents.clear()
        self._embedding_matrix = None
        self._matrix_dirty = True
        logger.info("EdgeRAG engine cleared")
