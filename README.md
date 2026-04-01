# 🏁 Aspar Team Aero-AI-Hub 🛸

> **Mission-Critical Aerodynamic Intelligence & Telemetry Digital Twin for MotoGP/Moto2.**

The Aspar Team Aero-AI-Hub is an advanced, distributed ecosystem designed to optimize motorcycle aerodynamics through real-time telemetry de-quantization, predictive AI forecasting, and physics-informed geometric validation. It bridges the gap between raw track data and actionable engineering decisions.

---

## 💎 Core Pillars

- **Babai Lattice Decoder**: 1000Hz de-quantization of compressed telemetry for ultra-low noise analysis.
- **GRU Predictive Brain**: 10ms sliding window inference to forecast aerodynamic stalls and anomalies *before* they occur.
- **Physics-Informed (PINN)**: Recommendations grounded in Navier-Stokes fluid dynamics to ensure physical consistency.
- **LangGraph Orchestrator**: Multi-agent collaboration (Aero, Race, and CAD engineers) to solve complex track problems.
- **Human-in-the-Loop (HITL)**: Secure validation queue ensuring all AI actions have manual engineering sign-off.

---

## 🧬 Technological DNA

### 1. Ingestion & Correlation (`ingestion_correlation/`)
- **Babai Solver**: Uses the Closest Plane Algorithm to map quantized sensor input back to Euclidean space.
- **Smart Consumer**: A high-speed Kafka consumer that filters noise and persists data to **InfluxDB** (Telemetry) and **MinIO** (Artifacts).

### 2. Cognitive Layer (`genai_agents/`)
- **Aero/Race Engineer Agents**: Specialized LLM-based agents with memory and tool access (CAD Metadata, Regs RAG).
- **Edge-RAG Engine**: Sub-millisecond retrieval of FIM/MotoGP technical regulations stored in **Milvus**.

### 3. Visual Mission Control (`unified_operator_interface/`)
- **3D Digital Twin**: Real-time **Three.js** viewport with dynamic particle states visualizing aerodynamic flow separation.
- **Predictive Dashboard**: Live sparklines (RPM, Temp, Rake) with purple AI Forecast alerts for pre-emptive warnings.

### 4. Enterprise Infrastructure (`docker-compose.yml`)
- **Persistence**: Hybrid mesh using InfluxDB, Milvus, MongoDB, and MinIO.
- **Security**: JWT-protected API Gateway with RBAC-ready logic.
- **Observability**: **Prometheus** metrics endpoint for real-time performance tracking.

---

## 🚀 Quick Start (Mission Execution)

The entire platform is orchestrated through a unified developer interface.

### 1. Initialize Infrastructure
```bash
make up        # Starts all 13+ Docker services (Kafka, DBs, MinIO)
make health    # Verifies the service mesh connectivity
```

### 2. Execute Full Mission PoC
This command seeds the knowledge base, starts the smart ingestors, and launches the 1000Hz simulator.
```bash
make run-poc
```

### 3. The Time Machine (Playback)
Re-run historical race data through the AI pipeline at variable speeds (e.g., 5x) for deep post-track analysis.
```bash
make replay
```

---

## 🛠 Project Structure (Screaming Architecture)

```
├── ai_applications/        # Neural Core (GRU, PINN, Training)
├── backend_api/            # Secure Gateway (JWT, Routes, Metrics)
├── genai_agents/           # Cognitive Orchestration (LangGraph)
├── ingestion_correlation/   # Babai Decoders & Kafka Consumers
├── persistence_knowledge/  # DB Clients (Milvus, Influx, MinIO)
├── unified_operator_interface/ # React/Three.js Frontend
├── scripts/                # Tools (Simulator, Health, Seeding)
└── Makefile                # Unified Command Center
```

---

## 🧪 Simulation Scenarios
- **Normal (100Hz)**: Standard telemetry flow for monitoring.
- **Stress (1000Hz)**: High-frequency data injection to validate de-quantization logic.
- **Anomaly**: Triggers an "Aerodynamic Stall" sequence to observe the GRU detector and Agent alerts.

---
**© 2024 Aspar Team - Advanced Agentic Coding PoC**