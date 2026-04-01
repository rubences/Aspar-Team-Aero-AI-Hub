"""
Tests for the Edge RAG engine (in-memory vector retrieval).
"""

import numpy as np
import pytest

from genai_agents.edge_rag_engine.engine import EdgeRAGEngine, RAGResult


class TestEdgeRAGEngine:
    """Test suite for the in-memory Edge RAG engine."""

    def _make_engine(self, dim: int = 8) -> EdgeRAGEngine:
        return EdgeRAGEngine(embedding_dim=dim)

    def _random_embedding(self, dim: int = 8) -> list[float]:
        v = np.random.rand(dim).astype(np.float32)
        return (v / np.linalg.norm(v)).tolist()

    def test_add_and_retrieve_single_document(self):
        """Adding one document and querying should return it as the top result."""
        engine = self._make_engine(dim=4)
        emb = [1.0, 0.0, 0.0, 0.0]
        engine.add_document("doc1", "FIA regulation article 1", emb)
        results = engine.retrieve(emb, top_k=1)
        assert len(results) == 1
        assert results[0].doc_id == "doc1"
        assert results[0].score > 0.99  # should be near-perfect match

    def test_retrieve_top_k_ordering(self):
        """Results should be returned in descending similarity order."""
        engine = self._make_engine(dim=4)
        engine.add_document("far", "far document", [0.0, 0.0, 0.0, 1.0])
        engine.add_document("near", "near document", [1.0, 0.0, 0.0, 0.0])
        engine.add_document("mid", "mid document", [0.7, 0.7, 0.0, 0.0])

        query = [1.0, 0.0, 0.0, 0.0]
        results = engine.retrieve(query, top_k=3)
        assert results[0].doc_id == "near"
        assert results[0].score >= results[1].score
        assert results[1].score >= results[2].score

    def test_category_filter(self):
        """Category filter should exclude documents not matching the category."""
        engine = self._make_engine(dim=4)
        engine.add_document("reg1", "Regulation 1", [1.0, 0.0, 0.0, 0.0], category="regulation")
        engine.add_document("setup1", "Setup 1", [1.0, 0.0, 0.0, 0.0], category="setup")

        results = engine.retrieve([1.0, 0.0, 0.0, 0.0], top_k=5, category_filter="regulation")
        assert all(r.category == "regulation" for r in results)

    def test_empty_engine_returns_empty_list(self):
        """Querying an empty engine should return an empty list."""
        engine = self._make_engine()
        results = engine.retrieve(self._random_embedding(), top_k=5)
        assert results == []

    def test_batch_add_and_stats(self):
        """Batch-adding documents should update engine stats correctly."""
        engine = self._make_engine(dim=4)
        docs = [
            {"doc_id": f"d{i}", "content": f"Content {i}",
             "embedding": [1.0, 0.0, 0.0, 0.0], "category": "test"}
            for i in range(5)
        ]
        engine.add_documents_batch(docs)
        stats = engine.get_stats()
        assert stats["document_count"] == 5
        assert stats["matrix_ready"] is True

    def test_clear(self):
        """Clearing the engine should remove all documents."""
        engine = self._make_engine(dim=4)
        engine.add_document("doc1", "Content", [1.0, 0.0, 0.0, 0.0])
        engine.clear()
        assert engine.get_stats()["document_count"] == 0
        assert engine.retrieve([1.0, 0.0, 0.0, 0.0]) == []

    def test_l2_normalisation_of_query(self):
        """Unnormalised query should produce same ranking as normalised query."""
        engine = self._make_engine(dim=3)
        engine.add_document("a", "doc a", [1.0, 0.0, 0.0])
        engine.add_document("b", "doc b", [0.0, 1.0, 0.0])

        query_normalised = [1.0, 0.0, 0.0]
        query_unnormalised = [5.0, 0.0, 0.0]

        r1 = engine.retrieve(query_normalised, top_k=2)
        r2 = engine.retrieve(query_unnormalised, top_k=2)

        assert [r.doc_id for r in r1] == [r.doc_id for r in r2]

    def test_retrieve_and_format(self):
        """retrieve_and_format should return a non-empty string."""
        engine = self._make_engine(dim=4)
        engine.add_document("r1", "Front wing regulation", [1.0, 0.0, 0.0, 0.0])
        text = engine.retrieve_and_format([1.0, 0.0, 0.0, 0.0], top_k=1)
        assert "Front wing regulation" in text

    def test_retrieve_and_format_empty(self):
        """retrieve_and_format on empty engine should return fallback message."""
        engine = self._make_engine(dim=4)
        text = engine.retrieve_and_format([1.0, 0.0, 0.0, 0.0])
        assert text == "No relevant context found."
