# Aspar SmartOps Aero AI Hub

AI-powered aerodynamic and race operations platform for the **Aspar Team** MotoGP programme.
Combines Physics-Informed Neural Networks (PINN), GRU anomaly detection, multi-agent AI,
and real-time telemetry processing in a fully containerised architecture.

---

## Architecture Overview

```
aspar-smartops-aero-hub/
├── .github/workflows/          # CI/CD — tests, security scans, Docker builds
├── .gga/                       # Gentleman Guardian Angel — code & security audit config
├── mcp_servers/                # Universal MCP connectors (Model Context Protocol)
│   ├── mcp_telemetry/          # InfluxDB + Kafka → any agent
│   ├── mcp_cad_engine/         # Onshape CAD + geometric meshes → any agent
│   ├── mcp_knowledge/          # Milvus (regulations) + MongoDB (setups) → any agent
│   └── mcp_ml_core/            # PINN/GRU models for on-demand prediction → any agent
├── dev_agents/                 # AI-assisted development environment
│   ├── gentle_ai_config.yaml   # Spec-driven development configuration
│   └── engram_context/         # Persistent memory for project decisions and context
├── ingestion_correlation/      # Event ingestion and correlation layer
│   ├── kafka_consumers/        # Async Kafka/RabbitMQ integration
│   ├── babai_quantization/     # [NEW] Babai nearest plane algorithm decoder for sensor denoising
│   └── normalizers/            # Per-source event normalisation to common schema
├── persistence_knowledge/      # Structured and document storage
│   ├── milvus_vector/          # Vector DB for semantic search and RAG
│   ├── influx_timeseries/      # Time-series DB for telemetry
│   ├── mongo_docs/             # Document DB for enriched events and configurations
│   └── minio_storage/          # Object storage for models, artifacts, and evidence
├── ai_applications/            # Analytical and predictive modules
│   ├── ai_aero_predict/
│   │   ├── pinn/               # Physics-Informed Neural Networks for aerodynamic modelling
│   │   ├── gru_inference/      # [NEW] GRU network for telemetry anomaly detection
│   │   └── rl_env/             # Gymnasium environment for aero design optimisation
│   ├── ai_fault_diagnosis/     # Multi-signal fault diagnosis engine
│   └── ai_maintenance/         # Predictive maintenance and degradation alerting
├── genai_agents/               # Advanced multi-agent architecture
│   ├── langgraph_orchestrator/ # LangGraph-based distributed workflow orchestration
│   ├── memory_manager/         # Short-term vs long-term memory management
│   ├── edge_rag_engine/        # [NEW] In-memory vector retrieval in microseconds
│   ├── skills_library/         # Injectable domain skills for agents
│   ├── supervisor_agent.py     # Intent classification and agent routing
│   ├── aero_engineer_agent.py  # Aerodynamic specialist agent
│   └── race_engineer_agent.py  # Race operations and incident resolution agent
├── unified_operator_interface/ # "Digital Pit Wall" presentation layer
│   └── src/
│       ├── components/         # TelemetryDashboard with human-in-the-loop validation
│       ├── chat_interface/     # Natural language conversational console
│       └── Viewport3D.jsx      # 3D aerodynamic flow visualiser (Three.js)
├── backend_api/                # Central application orchestrator
│   ├── main.py                 # FastAPI REST server
│   └── auth/                   # OAuth2/OpenID Connect via Keycloak
├── observability/              # Full-stack observability
│   └── monitoring_stack/       # Prometheus, Grafana, Loki, OpenTelemetry
├── docker-compose.yml          # Reproducible multi-service deployment
└── requirements.txt            # Python dependencies
```

---

## Key New Modules

### `ingestion_correlation/babai_quantization/`
Implements **Babai's nearest plane algorithm** (CVP approximation) for lattice-based
quantisation of high-dimensional sensor readings. Reduces measurement noise before
correlation and storage.

### `ai_applications/ai_aero_predict/gru_inference/`
**Gated Recurrent Unit (GRU)** network for real-time telemetry anomaly detection.
Processes multi-variate time sequences to detect point anomalies, contextual anomalies,
and collective deviations from normal operating patterns.

### `genai_agents/edge_rag_engine/`
**In-memory RAG engine** using L2-normalised vector similarity search (matrix
multiplication over NumPy arrays). Achieves sub-millisecond retrieval latency for
real-time race decisions without dependence on external vector databases.

---

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env   # Edit with your credentials

# 2. Start all services
docker compose up -d

# 3. Backend API: http://localhost:8000
# 4. Frontend:    http://localhost:3000
# 5. Grafana:     http://localhost:3001
# 6. InfluxDB:    http://localhost:8086
# 7. MinIO:       http://localhost:9001
```

## Development

```bash
pip install -r requirements.txt
uvicorn backend_api.main:app --reload
```

## Testing

```bash
pytest --cov=. --cov-report=term-missing
```

---

## Services

| Service | Port | Description |
|---|---|---|
| Backend API | 8000 | FastAPI REST server |
| Frontend | 3000 | React operator interface |
| Grafana | 3001 | Metrics dashboards |
| Prometheus | 9090 | Metrics collection |
| InfluxDB | 8086 | Time-series telemetry |
| MongoDB | 27017 | Document store |
| Milvus | 19530 | Vector database |
| MinIO | 9000/9001 | Object storage |
| Kafka | 9092 | Event streaming |
| Keycloak | 8080 | Identity provider |
| Loki | 3100 | Log aggregation |