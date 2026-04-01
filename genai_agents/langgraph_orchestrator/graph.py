"""
LangGraph Orchestrator — Distributed multi-agent workflow orchestration.
Defines the agent graph, state management, and routing logic using LangGraph.
"""

import logging
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Shared state passed between agents in the LangGraph workflow."""
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    context: dict[str, Any]
    vehicle_id: str
    session_id: str
    route: str
    result: dict[str, Any] | None
    error: str | None


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """Supervisor node: classify intent and determine routing."""
    from genai_agents.supervisor_agent import SupervisorAgent
    agent = SupervisorAgent()
    intent, route = agent.classify_and_route(state["messages"][-1].content)
    return {"intent": intent, "route": route}


def aero_engineer_node(state: AgentState) -> dict[str, Any]:
    """Aero engineer agent node: handle aerodynamic analysis requests."""
    from genai_agents.aero_engineer_agent import AeroEngineerAgent
    agent = AeroEngineerAgent()
    result = agent.handle(state)
    return {"result": result}


def race_engineer_node(state: AgentState) -> dict[str, Any]:
    """Race engineer agent node: handle operational and incident requests."""
    from genai_agents.race_engineer_agent import RaceEngineerAgent
    agent = RaceEngineerAgent()
    result = agent.handle(state)
    return {"result": result}


def route_decision(state: AgentState) -> Literal["aero_engineer", "race_engineer", "end"]:
    """Routing function: decide which agent node to call next."""
    route = state.get("route", "end")
    if route == "aero":
        return "aero_engineer"
    elif route == "race":
        return "race_engineer"
    return "end"


def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph multi-agent workflow."""
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("aero_engineer", aero_engineer_node)
    graph.add_node("race_engineer", race_engineer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "aero_engineer": "aero_engineer",
            "race_engineer": "race_engineer",
            "end": END,
        },
    )
    graph.add_edge("aero_engineer", END)
    graph.add_edge("race_engineer", END)

    return graph.compile()


# Module-level compiled graph instance
agent_graph = build_agent_graph()
