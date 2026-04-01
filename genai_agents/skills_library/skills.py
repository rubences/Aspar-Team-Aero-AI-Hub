"""
Skills Library — Injectable skills for GenAI agents.
Provides reusable, composable skill functions that agents can call
to perform specific domain actions.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AeroSkills:
    """Aerodynamic analysis skills for injection into agents."""

    def analyse_wing_balance(self, telemetry: dict[str, float]) -> dict[str, Any]:
        """Analyse front/rear wing balance from telemetry data."""
        front_downforce = telemetry.get("front_downforce_n", 0.0)
        rear_downforce = telemetry.get("rear_downforce_n", 0.0)
        total = front_downforce + rear_downforce
        balance = front_downforce / total if total > 0 else 0.5
        return {
            "front_balance_pct": round(balance * 100, 1),
            "rear_balance_pct": round((1 - balance) * 100, 1),
            "recommendation": (
                "Understeer tendency — increase front wing"
                if balance < 0.44
                else "Oversteer tendency — increase rear wing"
                if balance > 0.50
                else "Balance is optimal"
            ),
        }

    def compute_aero_efficiency(self, downforce: float, drag: float) -> dict[str, Any]:
        """Compute aerodynamic efficiency (downforce/drag ratio)."""
        efficiency = downforce / drag if drag > 0 else 0.0
        return {
            "efficiency_ratio": round(efficiency, 3),
            "interpretation": (
                "Excellent" if efficiency > 6.0
                else "Good" if efficiency > 4.5
                else "Acceptable" if efficiency > 3.0
                else "Needs improvement"
            ),
        }


class DiagnosticSkills:
    """Fault diagnostic skills for injection into agents."""

    def interpret_fault_codes(self, codes: list[str]) -> list[dict[str, str]]:
        """Interpret fault codes and provide human-readable descriptions."""
        fault_db: dict[str, str] = {
            "E001": "Oil pressure below threshold",
            "E002": "Water temperature critical",
            "E003": "Gearbox temperature warning",
            "E004": "Brake bias out of range",
            "E005": "DRS actuator failure",
            "T001": "Front-left tyre pressure low",
            "T002": "Front-right tyre pressure low",
            "T003": "Rear-left tyre pressure low",
            "T004": "Rear-right tyre pressure low",
        }
        return [
            {"code": code, "description": fault_db.get(code, "Unknown fault code")}
            for code in codes
        ]

    def prioritise_faults(self, faults: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort and prioritise faults by severity for engineer attention."""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return sorted(
            faults,
            key=lambda f: severity_order.get(f.get("severity", "info"), 99),
        )


class SetupSkills:
    """Car setup optimisation skills for injection into agents."""

    def suggest_setup_changes(self, lap_time_delta: float,
                               tyre_temps: dict[str, float],
                               conditions: str) -> dict[str, Any]:
        """
        Suggest setup changes based on lap time delta and tyre temperature data.

        Args:
            lap_time_delta: Positive = slower than target, negative = faster.
            tyre_temps: Dict with keys fl, fr, rl, rr in Celsius.
            conditions: Track conditions (dry, wet, damp).

        Returns:
            Dictionary of suggested setup adjustments.
        """
        suggestions = []

        if lap_time_delta > 0.3:
            suggestions.append("Consider increasing rear wing for more stability")

        avg_front = (tyre_temps.get("fl", 80) + tyre_temps.get("fr", 80)) / 2
        avg_rear = (tyre_temps.get("rl", 80) + tyre_temps.get("rr", 80)) / 2

        if avg_front > 100:
            suggestions.append("Front tyres overheating — reduce front wing angle or adjust tyre pressure")
        if avg_rear > 105:
            suggestions.append("Rear tyres overheating — increase rear ride height or adjust camber")
        if conditions == "wet":
            suggestions.append("Wet conditions: increase wing angles for maximum downforce and stability")

        return {
            "lap_time_delta_s": lap_time_delta,
            "front_tyre_avg_temp": avg_front,
            "rear_tyre_avg_temp": avg_rear,
            "suggestions": suggestions,
        }
