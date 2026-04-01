"""
Memory Manager — Strict short-term vs long-term memory management for agents.
Controls context window usage, memory consolidation, and retrieval strategies.
"""

import json
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

MAX_SHORT_TERM_ITEMS = 20
MAX_SHORT_TERM_TOKENS = 4000


@dataclass
class MemoryEntry:
    """A single memory item with metadata."""
    content: str
    memory_type: str  # "short_term" | "long_term"
    timestamp: datetime
    importance: float  # 0.0–1.0
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "memory_type": self.memory_type,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "tags": self.tags,
        }


class MemoryManager:
    """
    Manages agent memory with strict separation between short-term
    (in-context, fast) and long-term (vector-persisted, comprehensive) memory.
    """

    def __init__(self) -> None:
        # Short-term: recent conversation context (FIFO with capacity limit)
        self._short_term: deque[MemoryEntry] = deque(maxlen=MAX_SHORT_TERM_ITEMS)
        # Long-term: persistent facts stored in Milvus (indexed by embedding)
        self._long_term: list[MemoryEntry] = []

    def add_short_term(self, content: str, importance: float = 0.5,
                       tags: list[str] | None = None) -> None:
        """Add an item to short-term memory."""
        entry = MemoryEntry(
            content=content,
            memory_type="short_term",
            timestamp=datetime.now(tz=timezone.utc),
            importance=importance,
            tags=tags or [],
        )
        self._short_term.append(entry)
        logger.debug("Added to short-term memory: %s", content[:80])

        # Auto-consolidate high-importance items to long-term
        if importance >= 0.8:
            self._consolidate_to_long_term(entry)

    def add_long_term(self, content: str, importance: float = 0.7,
                      tags: list[str] | None = None,
                      embedding: list[float] | None = None) -> None:
        """Persist an item to long-term memory."""
        entry = MemoryEntry(
            content=content,
            memory_type="long_term",
            timestamp=datetime.now(tz=timezone.utc),
            importance=importance,
            tags=tags or [],
            embedding=embedding,
        )
        self._long_term.append(entry)
        logger.info("Added to long-term memory: %s", content[:80])

    def _consolidate_to_long_term(self, entry: MemoryEntry) -> None:
        """Consolidate a high-importance short-term entry to long-term memory."""
        lt_entry = MemoryEntry(
            content=entry.content,
            memory_type="long_term",
            timestamp=entry.timestamp,
            importance=entry.importance,
            tags=entry.tags + ["consolidated"],
        )
        self._long_term.append(lt_entry)

    def get_short_term_context(self, max_tokens: int = MAX_SHORT_TERM_TOKENS) -> str:
        """Get the short-term memory as a formatted context string."""
        items = list(self._short_term)
        context_parts = []
        total_chars = 0
        for item in reversed(items):
            text = f"[{item.timestamp.strftime('%H:%M:%S')}] {item.content}"
            if total_chars + len(text) > max_tokens * 4:  # rough char→token ratio
                break
            context_parts.insert(0, text)
            total_chars += len(text)
        return "\n".join(context_parts)

    def search_long_term(self, query_tags: list[str],
                          limit: int = 10) -> list[MemoryEntry]:
        """Search long-term memory by tag matching."""
        results = []
        for entry in self._long_term:
            if any(tag in entry.tags for tag in query_tags):
                results.append(entry)
        results.sort(key=lambda e: e.importance, reverse=True)
        return results[:limit]

    def clear_short_term(self) -> None:
        """Clear short-term memory (start new conversation context)."""
        self._short_term.clear()
        logger.info("Short-term memory cleared")

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of current memory state."""
        return {
            "short_term_count": len(self._short_term),
            "long_term_count": len(self._long_term),
            "oldest_short_term": (
                self._short_term[0].timestamp.isoformat()
                if self._short_term else None
            ),
        }
