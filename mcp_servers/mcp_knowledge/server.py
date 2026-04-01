"""
MCP Knowledge Server
Exposes Milvus vector DB (regulations) and MongoDB (setups) to agents via MCP.
"""

import logging
from typing import Any

from pymilvus import Collection, connections
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MCPKnowledgeServer:
    """Universal MCP connector for knowledge bases (Milvus + MongoDB)."""

    def __init__(self, milvus_host: str, milvus_port: int,
                 mongo_uri: str, mongo_db: str) -> None:
        connections.connect("default", host=milvus_host, port=milvus_port)
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db]

    def vector_search(self, collection_name: str, query_vector: list[float],
                      top_k: int = 5) -> list[dict[str, Any]]:
        """Perform a semantic similarity search in Milvus."""
        collection = Collection(collection_name)
        collection.load()
        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param={"metric_type": "L2", "params": {"nprobe": 10}},
            limit=top_k,
            output_fields=["text", "source", "category"],
        )
        hits = []
        for result in results[0]:
            hits.append({
                "id": result.id,
                "distance": result.distance,
                "text": result.entity.get("text"),
                "source": result.entity.get("source"),
                "category": result.entity.get("category"),
            })
        return hits

    def get_setup_config(self, track: str, conditions: str) -> dict[str, Any]:
        """Retrieve a car setup configuration from MongoDB."""
        doc = self.mongo_db.setups.find_one(
            {"track": track, "conditions": conditions},
            {"_id": 0},
        )
        return doc or {}

    def store_setup_config(self, config: dict[str, Any]) -> str:
        """Store a car setup configuration in MongoDB."""
        result = self.mongo_db.setups.insert_one(config)
        return str(result.inserted_id)

    def get_mcp_manifest(self) -> dict[str, Any]:
        """Return the MCP server manifest for agent discovery."""
        return {
            "name": "mcp_knowledge",
            "version": "1.0.0",
            "description": "Exposes Milvus (regulations) and MongoDB (setups) via MCP",
            "capabilities": ["vector_search", "get_setup_config", "store_setup_config"],
        }
