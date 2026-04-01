from typing import TypedDict, List, Annotated, Union
import operator
import os
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
llm = ChatOpenAI(model="gpt-4o", temperature=0) if os.getenv("OPENAI_API_KEY") else None

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
    Uses Aero tools + CAD Metadata + PINN Validation to provide a grounded recommendation.
    """
    # 1. Simulate CAD Tool Call: get_component_metadata("front_wing_l")
    component_context = "Component: Front Wing Left (W01-L), Surface Area: 0.12m2"
    
    # 2. Simulate PIIN Tool Call: validate_recommendation({"angle": +1.2})
    pinn_validation = "Physicality Score: 0.94 (Navier-Stokes Consistent)"
    
    recommendation = f"AeroEngineer: Based on {component_context} and {pinn_validation}, increase rake by 1.2mm for Curve 3."
    
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
