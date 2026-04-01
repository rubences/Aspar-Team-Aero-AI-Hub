"""
AI Maintenance — Predictive maintenance and proactive degradation alerting.
Analyses historical telemetry trends and component usage to predict
component degradation and schedule proactive maintenance.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class ComponentStatus(str, Enum):
    """Component health status."""
    HEALTHY = "healthy"
    MONITOR = "monitor"
    SERVICE_SOON = "service_soon"
    SERVICE_NOW = "service_now"
    FAILED = "failed"


@dataclass
class ComponentHealth:
    """Health report for a vehicle component."""
    component_id: str
    component_name: str
    vehicle_id: str
    status: ComponentStatus
    health_score: float  # 0.0 = failed, 1.0 = perfect
    remaining_life_km: float | None
    last_service_km: float
    current_km: float
    degradation_rate: float  # health units lost per km
    next_service_due_km: float
    alerts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "vehicle_id": self.vehicle_id,
            "status": self.status.value,
            "health_score": self.health_score,
            "remaining_life_km": self.remaining_life_km,
            "last_service_km": self.last_service_km,
            "current_km": self.current_km,
            "degradation_rate": self.degradation_rate,
            "next_service_due_km": self.next_service_due_km,
            "alerts": self.alerts,
        }


# Component service intervals (km)
SERVICE_INTERVALS: dict[str, float] = {
    "engine": 2000.0,
    "gearbox": 1500.0,
    "brakes_front": 500.0,
    "brakes_rear": 500.0,
    "tyres": 150.0,
    "suspension_front": 3000.0,
    "suspension_rear": 3000.0,
    "hydraulics": 1000.0,
}


class MaintenancePredictor:
    """
    Predictive maintenance engine using telemetry trend analysis.

    Tracks component degradation rates using exponential smoothing of
    telemetry stress indicators and generates proactive service alerts.
    """

    def __init__(self, smoothing_alpha: float = 0.2) -> None:
        self.alpha = smoothing_alpha
        self._degradation_history: dict[str, list[float]] = {}

    def compute_health_score(self, component: str,
                              stress_readings: list[float]) -> float:
        """
        Compute health score from a sequence of stress readings.

        Uses exponential smoothing to estimate the current degradation level.
        Higher stress → faster degradation → lower health score.

        Args:
            component: Component identifier.
            stress_readings: List of normalised stress values (0.0–1.0).

        Returns:
            Health score between 0.0 (failed) and 1.0 (perfect).
        """
        if not stress_readings:
            return 1.0
        if component not in self._degradation_history:
            self._degradation_history[component] = []

        smoothed = stress_readings[0]
        for reading in stress_readings[1:]:
            smoothed = self.alpha * reading + (1 - self.alpha) * smoothed

        self._degradation_history[component].append(smoothed)
        health = max(0.0, 1.0 - smoothed)
        return health

    def predict_component_health(
        self,
        component: str,
        vehicle_id: str,
        current_km: float,
        last_service_km: float,
        stress_readings: list[float],
    ) -> ComponentHealth:
        """
        Generate a full health report for a vehicle component.

        Args:
            component: Component name (must be in SERVICE_INTERVALS).
            vehicle_id: Vehicle identifier.
            current_km: Total kilometres on the vehicle.
            last_service_km: Kilometres at last service.
            stress_readings: Recent normalised stress readings.

        Returns:
            ComponentHealth report.
        """
        health_score = self.compute_health_score(component, stress_readings)
        km_since_service = current_km - last_service_km
        interval = SERVICE_INTERVALS.get(component, 1000.0)
        degradation_rate = (1.0 - health_score) / max(km_since_service, 1.0)
        remaining_life_km = (health_score / max(degradation_rate, 1e-6)
                             if degradation_rate > 0 else None)
        next_service_km = last_service_km + interval

        # Determine status
        usage_ratio = km_since_service / interval
        if health_score < 0.2:
            status = ComponentStatus.FAILED
        elif health_score < 0.4 or usage_ratio > 0.95:
            status = ComponentStatus.SERVICE_NOW
        elif health_score < 0.6 or usage_ratio > 0.80:
            status = ComponentStatus.SERVICE_SOON
        elif health_score < 0.8 or usage_ratio > 0.60:
            status = ComponentStatus.MONITOR
        else:
            status = ComponentStatus.HEALTHY

        alerts = []
        if status in (ComponentStatus.SERVICE_NOW, ComponentStatus.FAILED):
            alerts.append(f"URGENT: {component} requires immediate attention")
        elif status == ComponentStatus.SERVICE_SOON:
            alerts.append(f"{component} service due within {interval - km_since_service:.0f} km")

        return ComponentHealth(
            component_id=f"{vehicle_id}_{component}",
            component_name=component,
            vehicle_id=vehicle_id,
            status=status,
            health_score=health_score,
            remaining_life_km=remaining_life_km,
            last_service_km=last_service_km,
            current_km=current_km,
            degradation_rate=degradation_rate,
            next_service_due_km=next_service_km,
            alerts=alerts,
        )

    def fleet_health_summary(
        self, components_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Generate a fleet-wide health summary.

        Args:
            components_data: List of component data dictionaries with
                keys: component, vehicle_id, current_km, last_service_km,
                stress_readings.

        Returns:
            Summary dictionary with overall fleet health.
        """
        reports = []
        for item in components_data:
            report = self.predict_component_health(
                component=item["component"],
                vehicle_id=item["vehicle_id"],
                current_km=item["current_km"],
                last_service_km=item["last_service_km"],
                stress_readings=item.get("stress_readings", []),
            )
            reports.append(report.to_dict())

        scores = [r["health_score"] for r in reports]
        urgent = [r for r in reports
                  if r["status"] in (ComponentStatus.SERVICE_NOW.value,
                                     ComponentStatus.FAILED.value)]

        return {
            "fleet_health_score": float(np.mean(scores)) if scores else 1.0,
            "components_analysed": len(reports),
            "urgent_count": len(urgent),
            "urgent_components": urgent,
            "all_reports": reports,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }
