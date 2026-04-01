# Engram Persistence Memory

## Core Project Context
The Aspar-Team-Aero-AI-Hub is a high-performance telemetry and AI analytics platform for professional motorcycle racing. 

## Key Architectural Decisions
- **Babai Quantization**: Used for lattice-based telemetry compression to mitigate bandwidth bottlenecks.
- **GRU Inference**: Recurrent networks concatenated with historical context for dynamics prediction.
- **Microservices**: Decoupled ingestion, persistence, and AI layers.
- **HITL Integration**: Security-first approach where AI recommendations require manual validation.

## Master Architecture Specification
- **Contract**: [00_master_architecture.md](file:///c:/Users/rjuarcad/OneDrive%20-%20Universidad%20Alfonso%20X%20el%20Sabio/Escritorio/Quimera/Paper_Teleco/Aspar-Team-Aero-AI-Hub/docs/specs/00_master_architecture.md)
- **Constraint**: All code must strictly respect the domain-oriented folders and separation of responsibilities defined in the spec.

## Status: 2026-04-01
- Project structure initialized.
- Core Babai decoder and GRU models implemented.
- Edge-RAG retrieval engine prototype complete.
- Backend API and initial Vite/React interface scaffolded.
