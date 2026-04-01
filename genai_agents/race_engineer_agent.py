"""
Race Engineer Agent — Operational incident resolution and procedure agent.
Handles fault diagnosis, strategic decisions, tyre management,
maintenance alerts, and operational race procedures.
"""

import logging
from typing import Any

from genai_agents.edge_rag_engine.engine import EdgeRAGEngine
from genai_agents.memory_manager.manager import MemoryManager
from genai_agents.skills_library.skills import DiagnosticSkills, SetupSkills

logger = logging.getLogger(__name__)


class RaceEngineerAgent:
    """
    AI specialist agent for race operations and incident resolution.

    Integrates fault diagnosis, setup recommendations, and operational procedures
    to support race engineers with real-time decision-making during sessions.
    """

    def __init__(self) -> None:
        self.diagnostic_skills = DiagnosticSkills()
        self.setup_skills = SetupSkills()
        self.memory = MemoryManager()
        self.rag = EdgeRAGEngine()
        self._name = "RaceEngineerAgent"

    def handle(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Handle a race operations request.

        Args:
            state: Agent workflow state containing messages, context, etc.

        Returns:
            Result dictionary with diagnosis, recommendations, and actions.
        """
        messages = state.get("messages", [])
        context = state.get("context", {})
        vehicle_id = state.get("vehicle_id", "unknown")
        session_id = state.get("session_id", "unknown")

        last_message = messages[-1] if messages else None
        query = (
            last_message.content
            if last_message and hasattr(last_message, "content")
            else "No query provided"
        )

        self.memory.add_short_term(f"Race query: {query}", importance=0.6,
                                   tags=["race", "query"])

        result: dict[str, Any] = {
            "agent": self._name,
            "query": query,
            "vehicle_id": vehicle_id,
            "session_id": session_id,
        }

        # Fault code interpretation
        fault_codes = context.get("fault_codes", [])
        if fault_codes:
            interpreted = self.diagnostic_skills.interpret_fault_codes(fault_codes)
            result["fault_interpretations"] = interpreted
            self.memory.add_short_term(
                f"Faults detected: {[f['description'] for f in interpreted]}",
                importance=0.9, tags=["race", "fault"]
            )

        # Setup suggestions if lap data available
        lap_data = context.get("lap_data", {})
        if lap_data:
            suggestions = self.setup_skills.suggest_setup_changes(
                lap_time_delta=lap_data.get("delta_s", 0.0),
                tyre_temps=lap_data.get("tyre_temps", {}),
                conditions=lap_data.get("conditions", "dry"),
            )
            result["setup_suggestions"] = suggestions

        result["response"] = self._generate_response(query, result)

        logger.info("%s handled query for vehicle %s", self._name, vehicle_id)
        return result

    def _generate_response(self, query: str, result: dict[str, Any]) -> str:
        """Generate a natural language response for the race engineer."""
        parts = [f"Race operations analysis for: '{query}'"]

        faults = result.get("fault_interpretations", [])
        if faults:
            fault_list = "; ".join(f["description"] for f in faults[:3])
            parts.append(f"Active faults: {fault_list}.")

        suggestions = result.get("setup_suggestions", {})
        if suggestions and suggestions.get("suggestions"):
            parts.append("Setup recommendations: " +
                         " | ".join(suggestions["suggestions"][:2]) + ".")

        if not faults and not suggestions:
            parts.append("No active faults detected. Vehicle systems nominal.")

        return " ".join(parts)
