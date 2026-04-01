"""
Milvus Vector Store — Semantic search and RAG support.
Manages vector embeddings for regulation documents and technical knowledge.
"""

import logging
from typing import Any

import numpy as np
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

logger = logging.getLogger(__name__)

REGULATIONS_COLLECTION = "aspar_regulations"
EMBEDDING_DIM = 1536  # OpenAI text-embedding-3-small


class MilvusVectorStore:
    """Manages vector collections in Milvus for semantic search and RAG."""

    def __init__(self, host: str = "localhost", port: int = 19530) -> None:
        connections.connect("default", host=host, port=port)
        self._ensure_collections()

    def _ensure_collections(self) -> None:
        """Create required collections if they don't exist."""
        if not utility.has_collection(REGULATIONS_COLLECTION):
            self._create_regulations_collection()

    def _create_regulations_collection(self) -> None:
        """Create the regulations document collection."""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        ]
        schema = CollectionSchema(fields, description="Aerodynamic regulations knowledge base")
        collection = Collection(REGULATIONS_COLLECTION, schema)
        collection.create_index(
            field_name="embedding",
            index_params={"index_type": "IVF_FLAT", "metric_type": "L2",
                          "params": {"nlist": 128}},
        )
        logger.info("Created Milvus collection: %s", REGULATIONS_COLLECTION)

    def insert_documents(self, texts: list[str], sources: list[str],
                         categories: list[str],
                         embeddings: list[list[float]]) -> list[int]:
        """Insert document embeddings into Milvus."""
        collection = Collection(REGULATIONS_COLLECTION)
        data = [texts, sources, categories, embeddings]
        result = collection.insert(data)
        collection.flush()
        return result.primary_keys

    def search(self, query_embedding: list[float], top_k: int = 5,
               category_filter: str | None = None) -> list[dict[str, Any]]:
        """Search for similar documents by embedding."""
        collection = Collection(REGULATIONS_COLLECTION)
        collection.load()
        expr = f'category == "{category_filter}"' if category_filter else ""
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            expr=expr or None,
            output_fields=["text", "source", "category"],
        )
        hits = []
        for r in results[0]:
            hits.append({
                "id": r.id,
                "distance": r.distance,
                "text": r.entity.get("text"),
                "source": r.entity.get("source"),
                "category": r.entity.get("category"),
            })
        return hits

    def delete_collection(self) -> None:
        """Drop the regulations collection."""
        utility.drop_collection(REGULATIONS_COLLECTION)
        logger.warning("Dropped Milvus collection: %s", REGULATIONS_COLLECTION)
