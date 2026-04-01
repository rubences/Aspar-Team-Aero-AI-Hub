"""
Supervisor Agent — Intent classification and routing to the appropriate specialist agent.
Analyses incoming messages and determines which agent should handle the request.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

INTENT_KEYWORDS: dict[str, list[str]] = {
    "aero": [
        "aerodynamic", "aero", "downforce", "drag", "wing", "diffuser",
        "cfd", "flow", "pressure", "coefficient", "cd", "cl", "drs",
        "front wing", "rear wing", "balance", "pinn", "mesh",
    ],
    "race": [
        "fault", "error", "failure", "anomaly", "incident", "pit", "tyre",
        "brake", "engine", "temperature", "pressure", "lap time", "setup",
        "strategy", "fuel", "maintenance", "service", "alert", "warning",
    ],
}


class SupervisorAgent:
    """
    Classifies user intent and routes requests to the appropriate specialist agent.

    Intent categories:
    - "aero": Aerodynamic analysis, CFD, wing configuration
    - "race": Operational decisions, fault diagnosis, strategy
    - "general": General questions that either agent can handle
    """

    def classify_and_route(self, message: str) -> tuple[str, str]:
        """
        Classify the intent of a message and return the routing target.

        Args:
            message: The user's input message.

        Returns:
            Tuple of (intent, route) where route is "aero", "race", or "end".
        """
        message_lower = message.lower()
        scores: dict[str, int] = {intent: 0 for intent in INTENT_KEYWORDS}

        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in message_lower:
                    scores[intent] += 1

        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

        if best_score == 0:
            logger.info("Supervisor: no clear intent detected, defaulting to race engineer")
            return "general", "race"

        route = best_intent
        logger.info("Supervisor: classified intent='%s', route='%s' (score=%d)",
                    best_intent, route, best_score)
        return best_intent, route

    def handle(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process state and update with intent and routing decision."""
        messages = state.get("messages", [])
        if not messages:
            return {"intent": "general", "route": "end"}

        last_message = messages[-1]
        content = (
            last_message.content
            if hasattr(last_message, "content")
            else str(last_message)
        )
        intent, route = self.classify_and_route(content)
        return {"intent": intent, "route": route}
