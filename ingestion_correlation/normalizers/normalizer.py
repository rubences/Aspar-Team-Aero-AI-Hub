"""
Normalizers — Transform raw ingestion events to a common schema.
Each normalizer converts a source-specific event format into a
standardized TelemetryEvent for downstream processing.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TelemetryEvent:
    """Common schema for all normalized telemetry events."""

    source: str
    event_type: str
    timestamp: datetime
    vehicle_id: str
    session_id: str
    values: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for storage."""
        return {
            "source": self.source,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "vehicle_id": self.vehicle_id,
            "session_id": self.session_id,
            "values": self.values,
            "metadata": self.metadata,
        }


class CANBusNormalizer:
    """Normalizes raw CAN bus messages from the vehicle ECU."""

    def normalize(self, raw: dict[str, Any]) -> TelemetryEvent:
        """Convert a CAN bus frame to a TelemetryEvent."""
        ts = datetime.fromtimestamp(raw.get("ts", 0), tz=timezone.utc)
        return TelemetryEvent(
            source="can_bus",
            event_type="vehicle_telemetry",
            timestamp=ts,
            vehicle_id=str(raw.get("vehicle_id", "unknown")),
            session_id=str(raw.get("session_id", "unknown")),
            values={
                "speed_kmh": float(raw.get("speed", 0.0)),
                "rpm": float(raw.get("rpm", 0.0)),
                "throttle_pct": float(raw.get("throttle", 0.0)),
                "brake_pct": float(raw.get("brake", 0.0)),
                "gear": float(raw.get("gear", 0)),
                "steering_angle_deg": float(raw.get("steering", 0.0)),
            },
            metadata={"raw_frame_id": raw.get("frame_id")},
        )


class AeroSensorNormalizer:
    """Normalizes aerodynamic pressure/force sensor readings."""

    def normalize(self, raw: dict[str, Any]) -> TelemetryEvent:
        """Convert aero sensor data to a TelemetryEvent."""
        ts = datetime.fromtimestamp(raw.get("ts", 0), tz=timezone.utc)
        return TelemetryEvent(
            source="aero_sensors",
            event_type="aero_telemetry",
            timestamp=ts,
            vehicle_id=str(raw.get("vehicle_id", "unknown")),
            session_id=str(raw.get("session_id", "unknown")),
            values={
                "downforce_n": float(raw.get("downforce", 0.0)),
                "drag_n": float(raw.get("drag", 0.0)),
                "front_wing_angle_deg": float(raw.get("fw_angle", 0.0)),
                "rear_wing_angle_deg": float(raw.get("rw_angle", 0.0)),
                "differential_pressure_pa": float(raw.get("diff_pressure", 0.0)),
            },
            metadata={"sensor_ids": raw.get("sensor_ids", [])},
        )


class GPSNormalizer:
    """Normalizes GPS/GNSS positional data."""

    def normalize(self, raw: dict[str, Any]) -> TelemetryEvent:
        """Convert GPS data to a TelemetryEvent."""
        ts = datetime.fromtimestamp(raw.get("ts", 0), tz=timezone.utc)
        return TelemetryEvent(
            source="gps",
            event_type="position",
            timestamp=ts,
            vehicle_id=str(raw.get("vehicle_id", "unknown")),
            session_id=str(raw.get("session_id", "unknown")),
            values={
                "latitude": float(raw.get("lat", 0.0)),
                "longitude": float(raw.get("lon", 0.0)),
                "altitude_m": float(raw.get("alt", 0.0)),
                "speed_ms": float(raw.get("speed_ms", 0.0)),
                "heading_deg": float(raw.get("heading", 0.0)),
            },
            metadata={"accuracy_m": raw.get("accuracy")},
        )
