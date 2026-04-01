"""
Kafka Consumer — Ingestion layer for telemetry and event streams.
Integrates asynchronously with Apache Kafka or RabbitMQ.
"""

import json
import logging
import threading
from typing import Any, Callable

from kafka import KafkaConsumer, KafkaProducer

logger = logging.getLogger(__name__)

TELEMETRY_TOPIC = "aspar.telemetry.raw"
AERO_EVENTS_TOPIC = "aspar.aero.events"
FAULT_EVENTS_TOPIC = "aspar.fault.events"


class TelemetryConsumer:
    """Asynchronous Kafka consumer for raw telemetry streams."""

    def __init__(self, brokers: list[str],
                 group_id: str = "aspar-ingestion") -> None:
        self.brokers = brokers
        self.group_id = group_id
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self, topics: list[str],
              handler: Callable[[dict[str, Any]], None]) -> None:
        """Start consuming messages asynchronously."""
        self._running = True
        self._thread = threading.Thread(
            target=self._consume_loop, args=(topics, handler), daemon=True
        )
        self._thread.start()
        logger.info("TelemetryConsumer started for topics: %s", topics)

    def stop(self) -> None:
        """Stop the consumer loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("TelemetryConsumer stopped")

    def _consume_loop(self, topics: list[str],
                      handler: Callable[[dict[str, Any]], None]) -> None:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.brokers,
            group_id=self.group_id,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=True,
        )
        try:
            for message in consumer:
                if not self._running:
                    break
                try:
                    handler(message.value)
                except Exception:
                    logger.exception("Error handling message from %s", message.topic)
        finally:
            consumer.close()


class EventProducer:
    """Kafka producer for publishing processed events."""

    def __init__(self, brokers: list[str]) -> None:
        self.producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            retries=3,
        )

    def publish(self, topic: str, event: dict[str, Any]) -> None:
        """Publish an event to a Kafka topic."""
        self.producer.send(topic, value=event)
        self.producer.flush()
        logger.debug("Published event to %s: %s", topic, event)

    def close(self) -> None:
        """Close the producer connection."""
        self.producer.close()
