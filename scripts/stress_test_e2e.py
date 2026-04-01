import time
import requests
import json
import numpy as np
from scripts.sim_bike_telemetry import BikeTelemetrySimulator
import threading

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_DURATION = 15 # seconds
STRESS_FREQUENCY = 1000 # 1000Hz

def check_hitl_queue():
    """
    Checks if a recommendation has been triggered in the HITL queue.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/hitl/queue")
        if response.status_code == 200:
            queue = response.json()
            return queue
        return []
    except Exception:
        return []

def run_stress_test():
    """
    Orchestrates the 1000Hz stress test and anomaly detection validation.
    """
    print(f"--- STARTING E2E STRESS TEST ({STRESS_FREQUENCY}Hz) ---")
    
    sim = BikeTelemetrySimulator()
    sim.frequency = STRESS_FREQUENCY
    
    # 1. Start Simulation in Thread
    sim_thread = threading.Thread(target=sim.generate_telemetry, daemon=True)
    sim_thread.start()
    
    print("Capturing 5 seconds of normal data...")
    time.sleep(5)
    
    # 2. Inject Anomaly
    print("\n[STRESS TEST] Injecting Aerodynamic Anomaly (Rake drop)...")
    sim.toggle_anomaly()
    
    # 3. Wait for GenAI to react and Operator Interface to receive
    print("Waiting for GenAI detection and HITL recommendation...")
    found_recommendation = False
    
    for _ in range(10): # Try for 10 seconds
        queue = check_hitl_queue()
        if len(queue) > 0:
            for rec in queue:
                if "Rake" in rec.get("recommendation", "") or "Aerodinámica" in rec.get("recommendation", ""):
                    print(f"\n[SUCCESS] Recommendation Found: {rec['recommendation']}")
                    found_recommendation = True
                    break
        if found_recommendation: break
        time.sleep(1)
        print(".", end="", flush=True)

    # 4. Cleanup
    sim.stop()
    sim_thread.join(timeout=2)
    
    if found_recommendation:
        print("\n--- TEST PASSED: End-to-End Pipeline Validated ---")
    else:
        print("\n--- TEST FAILED: No recommendation triggered within timeout ---")

if __name__ == "__main__":
    run_stress_test()
