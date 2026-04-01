# Specification 01: Persistence and Ingestion Layer

## Overview
This specification defines the persistence infrastructure for the Aspar Team Aero-AI-Hub. It focuses on multi-modal data storage to support real-time telemetry, metadata management, and vector-based knowledge retrieval.

## Components

### 1. InfluxDB (Time-Series)
- **Role**: High-fidelity storage for telemetry data (RPM, temperature, pressure, etc.).
- **Organization**: `aspar-team`
- **Bucket**: `telemetry`
- **Retention**: 30 days (standard) / Long-term for historical race analysis.

### 2. MongoDB (Metadata & General Persistence)
- **Role**: Storage for motorcycle configurations, session metadata, unit conversions, and user profiles.
- **Database**: `aero_hub_db`
- **Key Collections**: `bikes`, `sessions`, `sensor_mappings`.

### 3. Milvus & MinIO (Vector Database & Storage)
- **Role**: Semantic storage for the technical regulations (RAG) and historical context for the predictive GRU.
- **Milvus Standalone**: Vector processing.
- **MinIO**: Object storage for Milvus segments and raw log archives.
- **etcd**: Metadata management for Milvus.

### 4. Apache Kafka (Messaging Backbone)
- **Role**: Sub-millisecond telemetry ingestion and event-driven architecture.
- **Default Topics**: `telemetry.raw`, `alerts.realtime`, `model.outputs`.
- **Distribution**: Bitnami (standalone mode for development).

## Network Architecture
A dedicated Docker internal network (`aero-ai-network`) will be used to encapsulate traffic, ensuring that only necessary ports are exposed to the host machine.

## Service Ports Table

| Service  | Host Port | Internal Port | Access  |
|----------|-----------|---------------|---------|
| InfluxDB | 8086      | 8086          | External|
| MongoDB  | 27017     | 27017         | Internal|
| Milvus   | 19530     | 19530         | Internal|
| MinIO    | 9000      | 9000          | Internal|
| Kafka    | 9092      | 9092          | External|
