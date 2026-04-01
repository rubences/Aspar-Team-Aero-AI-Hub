import time
import subprocess
import os
import requests
import json

# --- CONFIGURATION ---
GATEWAY_URL = "http://localhost:8000"
SIM_SCRIPT = "scripts/sim_bike_telemetry.py"
INGESTOR_SCRIPT = "ingestion_correlation/kafka_consumers/telemetry_consumer.py"
SEED_SCRIPT = "scripts/seed_knowledge.py"

def run_step(name, command):
    print(f"\n[ STEP ] {name}...")
    try:
        # Using Popen for background processes
        process = subprocess.Popen(command, shell=True)
        return process
    except Exception as e:
        print(f"[ ERROR ] Failed to start {name}: {e}")
        return None

def check_gateway():
    print("[ CHECK ] Initializing Service Mesh Diagnostic...")
    for _ in range(10):
        try:
            res = requests.get(f"{GATEWAY_URL}/health", timeout=2)
            if res.ok:
                print("[ PASS ] Gateway API Online.")
                return True
        except:
            pass
        time.sleep(2)
    return False

def main():
    print("====================================================")
    print("   ASPAR TEAM AERO-AI-HUB | MISSION POC LAUNCHER    ")
    print("====================================================")
    
    # 1. Check Infrastructure
    if not check_gateway():
        print("[ FAIL ] Infrastructure not ready. Run 'make up' first.")
        return

    # 2. Seed Knowledge (Milvus)
    print("\n[ SEED ] Populating Regulation RAG Engine...")
    subprocess.run(f"python {SEED_SCRIPT}", shell=True)

    # 3. Start Smart Ingestor (Background)
    ingestor = run_step("Smart Ingestor (GRU Predictive)", f"python {INGESTOR_SCRIPT}")

    # 4. Start Mission Simulator (Background)
    # We start with anomaly=False but high frequency for the PoC
    simulator = run_step("1000Hz Telemetry Simulator", f"python {SIM_SCRIPT}")

    print("\n" + "="*52)
    print(" [ MISSION ACTIVE ]")
    print(f" URL: http://localhost:5173 (Frontend)")
    print(f" API: {GATEWAY_URL}/docs")
    print("="*52)
    print("\nPresiona CTRL+C para abortar la mision y apagar servicios.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[ ABORT ] Apagando telemetra e ingestores...")
        ingestor.terminate()
        simulator.terminate()
        print("[ DONE ] Mision finalizada.")

if __name__ == "__main__":
    main()
