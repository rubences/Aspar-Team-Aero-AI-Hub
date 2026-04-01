"""
MCP Telemetry Server
Exposes InfluxDB time-series data and Kafka event streams to any agent
via the Model Context Protocol (MCP) standard.
"""

import json
import logging
from typing import Any

from influxdb_client import InfluxDBClient
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


class MCPTelemetryServer:
    """Universal MCP connector for telemetry data sources (InfluxDB + Kafka)."""

    def __init__(self, influx_url: str, influx_token: str, influx_org: str,
                 kafka_brokers: list[str]) -> None:
        self.influx_client = InfluxDBClient(
            url=influx_url, token=influx_token, org=influx_org
        )
        self.kafka_brokers = kafka_brokers
        self.query_api = self.influx_client.query_api()

    def query_timeseries(self, bucket: str, measurement: str,
                         start: str = "-1h") -> list[dict[str, Any]]:
        """Query InfluxDB and return records as MCP-compatible context objects."""
        flux_query = f'''
        from(bucket: "{bucket}")
          |> range(start: {start})
          |> filter(fn: (r) => r._measurement == "{measurement}")
        '''
        tables = self.query_api.query(flux_query)
        records = []
        for table in tables:
            for record in table.records:
                records.append({
                    "timestamp": record.get_time().isoformat(),
                    "measurement": record.get_measurement(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                    "tags": dict(record.values),
                })
        return records

    def consume_kafka_events(self, topic: str,
                              max_messages: int = 100) -> list[dict[str, Any]]:
        """Consume Kafka events and return as MCP context objects."""
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.kafka_brokers,
            auto_offset_reset="latest",
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        messages = []
        for message in consumer:
            messages.append({
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "timestamp": message.timestamp,
                "payload": message.value,
            })
            if len(messages) >= max_messages:
                break
        consumer.close()
        return messages

    def get_mcp_manifest(self) -> dict[str, Any]:
        """Return the MCP server manifest for agent discovery."""
        return {
            "name": "mcp_telemetry",
            "version": "1.0.0",
            "description": "Exposes InfluxDB and Kafka streams to agents via MCP",
            "capabilities": ["query_timeseries", "consume_kafka_events"],
            "schema": {
                "query_timeseries": {
                    "bucket": "string",
                    "measurement": "string",
                    "start": "string (optional, default=-1h)",
                },
                "consume_kafka_events": {
                    "topic": "string",
                    "max_messages": "int (optional, default=100)",
                },
            },
        }
