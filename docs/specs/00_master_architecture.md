# Master Architecture Specification: Aspar-Team-Aero-AI-Hub

This document defines the official directory structure and separation of responsibilities for the project. All development must strictly adhere to this contract.

## Directory Tree

```text
aspar-smartops-aero-hub/
├── .github/
│   └── workflows/              # CI/CD pipelines
├── .gga/                       # Gentleman-Guardian-Angel security/compliance
├── mcp_servers/                # Universal MCP Connectors
│   ├── mcp_telemetry/          # InfluxDB & Kafka gateway
│   ├── mcp_cad_engine/         # Onshape & Geometry gateway
│   ├── mcp_knowledge/          # Milvus & MongoDB gateway
│   └── mcp_ml_core/            # PINN/GRU model gateway
├── dev_agents/                 # AI development environment
│   ├── gentle_ai_config.yaml   # Agent configuration
│   └── engram_context/         # Persistent memory
├── ingestion_correlation/      # Data Ingestion & Lattice Decoding
│   ├── kafka_consumers/        # Asynchronous stream consumers
│   ├── babai_quantization/     # Babai Closest Plane decoding
│   └── normalizers/            # Schema standardization
├── persistence_knowledge/      # Persistent Storage
│   ├── milvus_vector/          # Vector/Semantic storage (RAG)
│   ├── influx_timeseries/      # Telemetry/Timeseries storage
│   ├── mongo_docs/             # Document/Event storage
│   └── minio_storage/          # Object/Blob storage
├── ai_applications/            # Analytics & Predictive Modeling
│   ├── ai_aero_predict/        # Physics & Dynamics prediction
│   ├── ai_fault_diagnosis/     # Anomaly & Fault detection
│   └── ai_maintenance/         # Predictive maintenance
├── genai_agents/               # Multi-Agent Architecture
│   ├── langgraph_orchestrator/ # Distributed orchestration
│   ├── memory_manager/         # S/L memory management
│   ├── edge_rag_engine/        # High-performance vector retrieval
│   └── skills_library/         # Agent tools & skills
├── unified_operator_interface/ # Dashboard & HITL Interface
├── backend_api/                # Central API Gateway
├── observability/              # Metrics & Logging
└── docker-compose.yml          # Infrastructure as Code
```

## Separation of Responsibilities
1. **Ingestion**: Raw data capture and mathematical reconstruction (Babai).
2. **Persistence**: Efficient storage based on data type (Vector, TS, Doc, Object).
3. **Analytics**: Heavy-duty physical and dynamic modeling (GRU, PINN).
4. **GenAI**: Cognitive layer and agent orchestration.
5. **Interface**: Presentation and required Human-in-the-Loop validation.
