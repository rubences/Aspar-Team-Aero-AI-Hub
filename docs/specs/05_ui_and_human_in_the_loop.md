# Specification 05: UI and Human-in-the-Loop Validation

## Overview
This specification defines the frontend interface for the Aero-Hub, emphasizing high-fidelity visualization and mandatory human validation for AI-driven operational decisions.

## Frameworks
- **React (Vite)**: Component-based UI.
- **FastAPI**: Backend gateway.
- **D3.js / Recharts**: Real-time telemetry visualization.
- **WebSockets**: Live telemetry streaming.

## Human-in-the-Loop (HITL) Principle
AI recommendations with operational impact (e.g., changes to wing angles, suspension settings) MUST:
1.  Display a "Validation Pending" status.
2.  Provide a clear "Approve" or "Reject" toggle.
3.  Log the operator's decision in MongoDB before execution.
4.  Prevent automated commands from being sent without this explicit handshake.

## Layout
- **Left Panel**: Real-time telemetry sparklines.
- **Center Panel**: Conversational AI Assistant.
- **Right Panel**: HITL Approval Queue and predictive aero-map.
- **Bottom Bar**: System health and communication status.
