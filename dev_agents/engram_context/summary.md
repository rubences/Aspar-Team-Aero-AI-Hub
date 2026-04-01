# Engram Persistence Memory

## Core Project Context
The Aspar-Team-Aero-AI-Hub is a high-performance telemetry and AI analytics platform for professional motorcycle racing. 

## Key Architectural Decisions
- **Babai Quantization**: Used for lattice-based telemetry compression to mitigate bandwidth bottlenecks.
- **GRU Inference**: Recurrent networks concatenated with historical context for dynamics prediction.
- **Microservices**: Decoupled ingestion, persistence, and AI layers.
- **HITL Integration**: Security-first approach where AI recommendations require manual validation.

## Status: 2026-04-01
- Project structure initialized.
- Core Babai decoder and GRU models implemented.
- Edge-RAG retrieval engine prototype complete.
- Backend API and initial Vite/React interface scaffolded.
