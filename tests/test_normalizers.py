"""
Tests for the data normalizers (CAN bus, aero sensors, GPS).
"""

import pytest
from datetime import timezone

from ingestion_correlation.normalizers.normalizer import (
    AeroSensorNormalizer,
    CANBusNormalizer,
    GPSNormalizer,
    TelemetryEvent,
)


class TestCANBusNormalizer:
    """Test suite for the CAN bus normalizer."""

    def setup_method(self):
        self.normalizer = CANBusNormalizer()

    def test_normalize_returns_telemetry_event(self):
        raw = {
            "ts": 1700000000.0,
            "vehicle_id": "V44",
            "session_id": "S001",
            "speed": 220.5,
            "rpm": 12000.0,
            "throttle": 95.0,
            "brake": 0.0,
            "gear": 5,
            "steering": 3.2,
        }
        event = self.normalizer.normalize(raw)
        assert isinstance(event, TelemetryEvent)
        assert event.source == "can_bus"
        assert event.vehicle_id == "V44"
        assert event.values["speed_kmh"] == 220.5
        assert event.values["rpm"] == 12000.0
        assert event.values["gear"] == 5.0

    def test_normalize_missing_fields_use_defaults(self):
        event = self.normalizer.normalize({})
        assert event.values["speed_kmh"] == 0.0
        assert event.values["rpm"] == 0.0

    def test_to_dict_serializes_correctly(self):
        raw = {"ts": 0, "vehicle_id": "V1", "session_id": "S1"}
        event = self.normalizer.normalize(raw)
        d = event.to_dict()
        assert "source" in d
        assert "timestamp" in d
        assert "values" in d


class TestAeroSensorNormalizer:
    """Test suite for the aero sensor normalizer."""

    def setup_method(self):
        self.normalizer = AeroSensorNormalizer()

    def test_normalize_returns_aero_event(self):
        raw = {
            "ts": 1700000000.0,
            "vehicle_id": "V44",
            "session_id": "S002",
            "downforce": 1500.0,
            "drag": 250.0,
            "fw_angle": 22.5,
            "rw_angle": 35.0,
            "diff_pressure": 120.0,
        }
        event = self.normalizer.normalize(raw)
        assert event.event_type == "aero_telemetry"
        assert event.values["downforce_n"] == 1500.0
        assert event.values["front_wing_angle_deg"] == 22.5


class TestGPSNormalizer:
    """Test suite for the GPS normalizer."""

    def setup_method(self):
        self.normalizer = GPSNormalizer()

    def test_normalize_returns_position_event(self):
        raw = {
            "ts": 1700000000.0,
            "vehicle_id": "V44",
            "session_id": "S003",
            "lat": 40.4168,
            "lon": -3.7038,
            "alt": 667.0,
            "speed_ms": 55.5,
            "heading": 180.0,
        }
        event = self.normalizer.normalize(raw)
        assert event.event_type == "position"
        assert event.values["latitude"] == pytest.approx(40.4168)
        assert event.values["longitude"] == pytest.approx(-3.7038)

    def test_timestamp_is_timezone_aware(self):
        raw = {"ts": 1700000000.0, "vehicle_id": "V1", "session_id": "S1"}
        event = self.normalizer.normalize(raw)
        assert event.timestamp.tzinfo is not None
