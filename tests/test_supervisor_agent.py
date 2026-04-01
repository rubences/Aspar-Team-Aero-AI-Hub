"""
Tests for the Supervisor Agent intent classification and routing.
"""

import pytest

from genai_agents.supervisor_agent import SupervisorAgent


class TestSupervisorAgent:
    """Test suite for the SupervisorAgent."""

    def setup_method(self):
        self.agent = SupervisorAgent()

    def test_classify_aero_intent(self):
        """Messages with aerodynamic keywords should route to aero."""
        intent, route = self.agent.classify_and_route(
            "What is the current downforce balance on the front wing?"
        )
        assert route == "aero"
        assert intent == "aero"

    def test_classify_race_intent(self):
        """Messages with fault/race keywords should route to race."""
        intent, route = self.agent.classify_and_route(
            "There is a critical engine temperature fault, what should we do?"
        )
        assert route == "race"
        assert intent == "race"

    def test_classify_tyre_intent_to_race(self):
        """Tyre-related queries should route to the race engineer."""
        intent, route = self.agent.classify_and_route(
            "Front tyre temperatures are too high, suggest a setup change."
        )
        assert route == "race"

    def test_classify_cfd_to_aero(self):
        """CFD-related queries should route to the aero engineer."""
        intent, route = self.agent.classify_and_route(
            "Show me the drag coefficient from the latest CFD analysis."
        )
        assert route == "aero"

    def test_empty_message_defaults_to_race(self):
        """Empty or unclear messages should default to race engineer."""
        intent, route = self.agent.classify_and_route("")
        assert route in ("race", "end")

    def test_handle_state_with_messages(self):
        """handle() should populate intent and route in state."""
        from langchain_core.messages import HumanMessage
        state = {
            "messages": [HumanMessage(content="Check the rear wing drag coefficient")],
        }
        result = self.agent.handle(state)
        assert "intent" in result
        assert "route" in result
        assert result["route"] == "aero"

    def test_handle_empty_messages(self):
        """handle() with no messages should return a valid default state."""
        result = self.agent.handle({"messages": []})
        assert result["intent"] == "general"
        assert result["route"] == "end"
