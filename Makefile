# --- Aspar Team Aero-AI-Hub Lifecycle Management ---

.PHONY: help up down restart logs health sim-normal sim-stress ui-install ui-dev shell-api

# Default help
help:
	@echo "Aspar Aero Hub - Master Operations"
	@echo "---------------------------------"
	@echo "make up          : Start infrastructure (Databases, Kafka, MinIO)"
	@echo "make down        : Stop all services and containers"
	@echo "make health      : Run system diagnostic check (13+ services)"
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

# Diagnostics
health:
	python scripts/system_health.py

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
