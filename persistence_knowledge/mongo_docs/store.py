"""
MongoDB Document Store — Persistence for enriched events and configurations.
Manages car setups, session configurations, fault reports and enriched events.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

DB_NAME = "aspar_hub"


class MongoDocStore:
    """Manages document storage in MongoDB for events and configurations."""

    def __init__(self, uri: str = "mongodb://localhost:27017") -> None:
        self.client = MongoClient(uri)
        self.db = self.client[DB_NAME]
        self._ensure_indexes()

    def _ensure_indexes(self) -> None:
        """Create required indexes for efficient queries."""
        self.db.setups.create_index([("track", 1), ("conditions", 1)])
        self.db.events.create_index([("timestamp", DESCENDING)])
        self.db.events.create_index([("vehicle_id", 1), ("event_type", 1)])
        self.db.fault_reports.create_index([("timestamp", DESCENDING)])

    # --- Car Setup Management ---

    def save_setup(self, setup: dict[str, Any]) -> str:
        """Save a car setup configuration."""
        setup["created_at"] = datetime.now(tz=timezone.utc)
        result = self.db.setups.insert_one(setup)
        return str(result.inserted_id)

    def get_setup(self, track: str, conditions: str) -> dict[str, Any] | None:
        """Retrieve the latest setup for a track and conditions."""
        return self.db.setups.find_one(
            {"track": track, "conditions": conditions},
            sort=[("created_at", DESCENDING)],
            projection={"_id": 0},
        )

    def list_setups(self, track: str | None = None) -> list[dict[str, Any]]:
        """List all available setups, optionally filtered by track."""
        query = {"track": track} if track else {}
        return list(self.db.setups.find(query, projection={"_id": 0}))

    # --- Enriched Event Storage ---

    def store_event(self, event: dict[str, Any]) -> str:
        """Store an enriched telemetry or correlation event."""
        event["stored_at"] = datetime.now(tz=timezone.utc)
        result = self.db.events.insert_one(event)
        return str(result.inserted_id)

    def get_events(self, vehicle_id: str, event_type: str | None = None,
                   limit: int = 100) -> list[dict[str, Any]]:
        """Retrieve recent events for a vehicle."""
        query: dict[str, Any] = {"vehicle_id": vehicle_id}
        if event_type:
            query["event_type"] = event_type
        docs = self.db.events.find(
            query,
            sort=[("timestamp", DESCENDING)],
            limit=limit,
            projection={"_id": 0},
        )
        return list(docs)

    # --- Fault Reports ---

    def save_fault_report(self, report: dict[str, Any]) -> str:
        """Save a fault diagnosis report."""
        report["created_at"] = datetime.now(tz=timezone.utc)
        result = self.db.fault_reports.insert_one(report)
        return str(result.inserted_id)

    def get_fault_reports(self, vehicle_id: str,
                           limit: int = 50) -> list[dict[str, Any]]:
        """Get recent fault reports for a vehicle."""
        return list(
            self.db.fault_reports.find(
                {"vehicle_id": vehicle_id},
                sort=[("timestamp", DESCENDING)],
                limit=limit,
                projection={"_id": 0},
            )
        )

    def close(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()
