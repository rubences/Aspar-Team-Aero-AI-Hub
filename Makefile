# --- Aspar Team Aero-AI-Hub Lifecycle Management ---

.PHONY: help up down restart logs health smoke metrics replay run-poc sim-normal sim-stress ui-install ui-dev shell-api

# Default help
help:
	@echo "Aspar Aero Hub - Master Operations"
	@echo "---------------------------------"
	@echo "make up          : Start infrastructure (Databases, Kafka, MinIO)"
	@echo "make down        : Stop all services and containers"
	@echo "make health      : Run system diagnostic check (13+ services)"
	@echo "make smoke       : Run end-to-end API/MCP smoke validation"
	@echo "make metrics     : Open Prometheus/Grafana metrics endpoint"
	@echo "make replay      : Start Session Replay at 5x speed"
	@echo "make run-poc     : EXECUTE FULL MISSION PoC (Start All)"
	@echo "make sim-normal  : Start 100Hz Telemetry Simulation"
	@echo "make sim-stress  : Start 1000Hz Stress Test + Anomaly injection"
	@echo "make ui-dev      : Start React Operator Interface"
	@echo "make logs        : Follow backend gateway logs"

# Orchestration
up:
	docker-compose up -d --build

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker logs -f aspar-api-gateway

metrics:
	curl http://localhost:8000/metrics

replay:
	python scripts/replay_session.py --speed 5.0

run-poc:
	python scripts/run_poc_mission.py

# Diagnostics
health:
	python scripts/system_health.py

smoke:
	python scripts/smoke_test_stack.py

# Simulation & Stress Tests
sim-normal:
	python scripts/sim_bike_telemetry.py --freq 100

sim-stress:
	python scripts/stress_test_e2e.py

# Frontend
ui-install:
	cd unified_operator_interface && npm install

ui-dev:
	cd unified_operator_interface && npm run dev

# Debugging
shell-api:
	docker exec -it aspar-api-gateway /bin/bash
