# Specification 04: Multi-Agent Conversational Core

## Overview
This specification details the GenAI agent architecture for the Aspar Team Aero-Hub, utilizing LangGraph for distributed orchestration and state management.

## Frameworks
- **LangChain/LangGraph**: Multi-agent state machine.
- **Milvus**: RAG backend for regulation context.
- **Short-term memory**: In-memory Redis or LangGraph state.
- **Long-term memory**: MongoDB `agent_memory` collection.

## Agents

### 1. `supervisor_agent.py`
- **Role**: Traffic controller and orchestrator.
- **Inputs**: User prompts in the operator interface.
- **Logic**: Routes to specialized agents based on classification (e.g., Aero Engineer, Strategy, System Health).

### 2. `aero_engineer_agent.py`
- **Role**: Aerodynamic analysis expert.
- **Knowledge**: Accesses `mcp_knowledge` (Milvus) and `mcp_telemetry` (InfluxDB).
- **Function**: Provide reasoning for aero changes (e.g., "Increase spoiler angle by 2.5 deg due to high temperature on rear tires").

## Memory Strategy
- **Contextual RAG**: All agents query Milvus before answering to prevent hallucinations.
- **Physical Validation**: Recommendations must pass through the ML Core (PINN) when applicable.
