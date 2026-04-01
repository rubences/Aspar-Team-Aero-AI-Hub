from typing import TypedDict, List, Annotated, Union
import operator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from genai_agents.skills_library.mcp_bridge import AERO_TOOLS, RACE_TOOLS

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str
    requires_validation: bool
    validation_status: str # "PENDING", "APPROVED", "REJECTED"

# LLM Setup (GPT-4o or similar)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def supervisor_node(state: AgentState):
    """
    Decides the routing logic based on the conversation history.
    """
    last_msg = state['messages'][-1].content.lower()
    if any(k in last_msg for k in ["aero", "wing", "drag", "rake"]):
        return {"next_agent": "AeroEngineer"}
    elif any(k in last_msg for k in ["procedimiento", "fuel", "mapa", "estrategia"]):
        return {"next_agent": "RaceEngineer"}
    else:
        return {"next_agent": "FINISH"}

def aero_engineer_node(state: AgentState):
    """
    Uses Aero tools to provide a technical recommendation.
    """
    # In a real scenario, we would use llm.bind_tools(AERO_TOOLS)
    # For now, we simulate the logic with tool-awareness
    recommendation = "AeroEngineer: Based on live telemetry, increase rake by 1.2mm for Curve 3."
    return {
        "messages": [AIMessage(content=recommendation)], 
        "next_agent": "ValidationNode",
        "requires_validation": True
    }

def race_engineer_node(state: AgentState):
    """
    Uses Race tools for strategy advice.
    """
    recommendation = "RaceEngineer: Fuel consumption high. Switch to Engine Map 2."
    return {
        "messages": [AIMessage(content=recommendation)], 
        "next_agent": "ValidationNode",
        "requires_validation": True
    }

def validation_node(state: AgentState):
    """
    HITL node: Pauses the graph or checks for validation status.
    In a real LangGraph setup with persistence, this would 'interrupt' the flow.
    """
    if state.get("validation_status") == "APPROVED":
        return {"messages": [AIMessage(content="VALIDATION: APPROVED BY OPERATOR. Action applied.")], "next_agent": "FINISH"}
    elif state.get("validation_status") == "REJECTED":
        return {"messages": [AIMessage(content="VALIDATION: REJECTED BY OPERATOR. Recommendation discarded.")], "next_agent": "FINISH"}
    else:
        # This state triggers the 'pause' behavior in the backend/UI bridge
        return {"next_agent": "WAIT_FOR_OPERATOR"}

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("Supervisor", supervisor_node)
builder.add_node("AeroEngineer", aero_engineer_node)
builder.add_node("RaceEngineer", race_engineer_node)
builder.add_node("ValidationNode", validation_node)

builder.set_entry_point("Supervisor")

# Define Edges
builder.add_conditional_edges(
    "Supervisor",
    lambda x: x["next_agent"],
    {
        "AeroEngineer": "AeroEngineer",
        "RaceEngineer": "RaceEngineer",
        "FINISH": END
    }
)

builder.add_edge("AeroEngineer", "ValidationNode")
builder.add_edge("RaceEngineer", "ValidationNode")

builder.add_conditional_edges(
    "ValidationNode",
    lambda x: x["next_agent"],
    {
        "FINISH": END,
        "WAIT_FOR_OPERATOR": END # The backend will handle the external loop
    }
)

orchestrator = builder.compile()

if __name__ == "__main__":
    test_msg = HumanMessage(content="Cual es el rake recomendado?")
    initial_state = {"messages": [test_msg], "next_agent": "", "requires_validation": False, "validation_status": "PENDING"}
    for output in orchestrator.stream(initial_state):
        print(output)
