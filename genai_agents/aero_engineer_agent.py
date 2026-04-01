"""
Aero Engineer Agent — Specialist aerodynamic analysis and optimisation agent.
Handles CFD result interpretation, PINN predictions, wing configuration advice,
and aerodynamic performance queries.
"""

import logging
from typing import Any

from genai_agents.edge_rag_engine.engine import EdgeRAGEngine
from genai_agents.memory_manager.manager import MemoryManager
from genai_agents.skills_library.skills import AeroSkills

logger = logging.getLogger(__name__)


class AeroEngineerAgent:
    """
    AI specialist agent for aerodynamic engineering decisions.

    Uses the Edge RAG engine for fast regulation and technical document retrieval,
    the PINN/GRU models for predictions, and the skills library for domain logic.
    """

    def __init__(self) -> None:
        self.skills = AeroSkills()
        self.memory = MemoryManager()
        self.rag = EdgeRAGEngine()
        self._name = "AeroEngineerAgent"

    def handle(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an aerodynamic engineering request.

        Args:
            state: Agent workflow state containing messages, context, etc.

        Returns:
            Result dictionary with analysis, recommendations, and reasoning.
        """
        messages = state.get("messages", [])
        context = state.get("context", {})
        telemetry = context.get("telemetry", {})
        vehicle_id = state.get("vehicle_id", "unknown")

        last_message = messages[-1] if messages else None
        query = (
            last_message.content
            if last_message and hasattr(last_message, "content")
            else "No query provided"
        )

        self.memory.add_short_term(f"Query: {query}", importance=0.6,
                                   tags=["aero", "query"])

        analysis: dict[str, Any] = {"agent": self._name, "query": query}

        # Wing balance analysis if telemetry available
        if telemetry:
            balance = self.skills.analyse_wing_balance(telemetry)
            analysis["wing_balance"] = balance
            self.memory.add_short_term(
                f"Wing balance: {balance['recommendation']}",
                importance=0.7, tags=["aero", "balance"]
            )

            downforce = telemetry.get("downforce_n", 0.0)
            drag = telemetry.get("drag_n", 1.0)
            efficiency = self.skills.compute_aero_efficiency(downforce, drag)
            analysis["aero_efficiency"] = efficiency

        context_str = self.memory.get_short_term_context()
        analysis["context_summary"] = context_str

        analysis["response"] = self._generate_response(query, analysis)

        logger.info("%s handled query for vehicle %s", self._name, vehicle_id)
        return analysis

    def _generate_response(self, query: str, analysis: dict[str, Any]) -> str:
        """Generate a natural language response based on the analysis."""
        parts = [f"Aerodynamic analysis for query: '{query}'"]

        if "wing_balance" in analysis:
            wb = analysis["wing_balance"]
            parts.append(
                f"Wing balance: {wb['front_balance_pct']}% front / "
                f"{wb['rear_balance_pct']}% rear. {wb['recommendation']}."
            )

        if "aero_efficiency" in analysis:
            ae = analysis["aero_efficiency"]
            parts.append(
                f"Aerodynamic efficiency (Cl/Cd ratio): {ae['efficiency_ratio']} — "
                f"{ae['interpretation']}."
            )

        return " ".join(parts)
