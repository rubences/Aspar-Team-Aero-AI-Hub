"""
InfluxDB Time-Series Store — Persistence for telemetry and metrics.
Handles write and query operations for all time-series data.
"""

import logging
from datetime import datetime
from typing import Any

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxTimeSeriesStore:
    """Manages time-series data in InfluxDB for telemetry and metrics."""

    def __init__(self, url: str, token: str, org: str,
                 bucket: str = "aspar_telemetry") -> None:
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.org = org
        self.bucket = bucket
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_telemetry(self, measurement: str, tags: dict[str, str],
                        fields: dict[str, float],
                        timestamp: datetime | None = None) -> None:
        """Write a telemetry data point to InfluxDB."""
        point = Point(measurement)
        for k, v in tags.items():
            point = point.tag(k, v)
        for k, v in fields.items():
            point = point.field(k, v)
        if timestamp:
            point = point.time(timestamp, WritePrecision.NANOSECONDS)
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        logger.debug("Written telemetry: %s %s %s", measurement, tags, fields)

    def query_last_n(self, measurement: str, n_minutes: int = 5,
                     vehicle_id: str | None = None) -> list[dict[str, Any]]:
        """Query the last N minutes of telemetry for a measurement."""
        filter_clause = ""
        if vehicle_id:
            filter_clause = f'|> filter(fn: (r) => r["vehicle_id"] == "{vehicle_id}")'

        flux = f"""
        from(bucket: "{self.bucket}")
          |> range(start: -{n_minutes}m)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          {filter_clause}
          |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
        tables = self.query_api.query(flux, org=self.org)
        records = []
        for table in tables:
            for record in table.records:
                records.append({
                    "time": record.get_time().isoformat(),
                    **{k: v for k, v in record.values.items()
                       if not k.startswith("_") and k != "result" and k != "table"},
                })
        return records

    def write_batch(self, points: list[dict[str, Any]]) -> None:
        """Write a batch of telemetry points."""
        influx_points = []
        for p in points:
            point = Point(p["measurement"])
            for k, v in p.get("tags", {}).items():
                point = point.tag(k, v)
            for k, v in p.get("fields", {}).items():
                point = point.field(k, v)
            if "timestamp" in p:
                point = point.time(p["timestamp"], WritePrecision.NANOSECONDS)
            influx_points.append(point)
        self.write_api.write(bucket=self.bucket, org=self.org, record=influx_points)
        logger.info("Written batch of %d points", len(influx_points))

    def close(self) -> None:
        """Close the InfluxDB client."""
        self.client.close()
