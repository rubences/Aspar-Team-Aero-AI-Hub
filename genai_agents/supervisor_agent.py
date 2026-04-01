from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, END

# Define Agent State
class AgentState(TypedDict):
    messages: Annotated[List[str], operator.add]
    next_agent: str

def supervisor_node(state: AgentState):
    """
    Decides whether to route to AeroEngineer, RaceEngineer, or Finish.
    """
    last_msg = state['messages'][-1].lower()
    if "aero" in last_msg or "wing" in last_msg or "drag" in last_msg:
        return {"next_agent": "AeroEngineer"}
    elif "procedimiento" in last_msg or "fuel" in last_msg or "estrategia" in last_msg:
        return {"next_agent": "RaceEngineer"}
    else:
        return {"next_agent": "FINISH"}

def aero_engineer_node(state: AgentState):
    return {"messages": ["AeroEngineer: Based on PINN analysis, I recommend increasing rake by 1.5mm."], "next_agent": "FINISH"}

def race_engineer_node(state: AgentState):
    return {"messages": ["RaceEngineer: Consumo de combustible crítico. Cambiar a Mapa Motor 2 inmediatamente."], "next_agent": "FINISH"}

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("Supervisor", supervisor_node)
builder.add_node("AeroEngineer", aero_engineer_node)
builder.add_node("RaceEngineer", race_engineer_node)

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
builder.add_edge("AeroEngineer", END)
builder.add_edge("RaceEngineer", END)

# Compile Graph
orchestrator = builder.compile()

if __name__ == "__main__":
    initial_state = {"messages": ["Cual es la recomendación aerodinámica para la curva 3?"], "next_agent": ""}
    for output in orchestrator.stream(initial_state):
        print(output)
