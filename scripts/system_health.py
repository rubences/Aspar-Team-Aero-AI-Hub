import requests
import socket
import time
from concurrent.futures import ThreadPoolExecutor

# --- Aspar Team Service Mesh Definition ---
SERVICES = {
    "Gateway API": {"url": "http://localhost:8000", "type": "http"},
    "InfluxDB": {"url": "http://localhost:8086", "type": "http"},
    "MongoDB": {"port": 27017, "type": "socket"},
    "Milvus": {"port": 19530, "type": "socket"},
    "MinIO": {"url": "http://localhost:9000/minio/health/live", "type": "http"},
    "Kafka": {"port": 9092, "type": "socket"},
    "MCP Telemetry": {"url": "http://localhost:8001", "type": "http"},
    "MCP ML Core": {"url": "http://localhost:8002", "type": "http"},
    "MCP CAD Engine": {"url": "http://localhost:8003", "type": "http"},
}

def check_http(name, url):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code < 500:
            return True, f"OK ({r.status_code})"
        return False, f"ERR ({r.status_code})"
    except Exception as e:
        return False, "OFFLINE"

def check_socket(name, port):
    try:
        s = socket.create_connection(("localhost", port), timeout=2)
        s.close()
        return True, "CONNECTED"
    except Exception:
        return False, "OFFLINE"

def run_diagnostics():
    print("--- ASPAR TEAM AERO-AI-HUB: SYSTEM HEALTH DIAGNOSTIC ---")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 55)
    
    results = []
    
    def task(name, config):
        if config["type"] == "http":
            status, msg = check_http(name, config["url"])
        else:
            status, msg = check_socket(name, config["port"])
        return name, status, msg

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, name, config) for name, config in SERVICES.items()]
        for f in futures:
            results.append(f.result())

    # Sorting for consistent output
    results.sort()

    online_count = 0
    for name, status, msg in results:
        indicator = "[ PASS ]" if status else "[ FAIL ]"
        if status: online_count += 1
        print(f"{indicator} {name:<18} | {msg}")

    print("-" * 55)
    total = len(SERVICES)
    print(f"HEALTH STATUS: {online_count}/{total} SERVICES ONLINE")
    
    if online_count == total:
        print("\n[ SUCCESS ] Malla de servicios operativa y sincronizada.")
    else:
        print("\n[ WARNING ] Algunas dependencias estn inactivas. Revisa 'docker-compose ps'.")

if __name__ == "__main__":
    run_diagnostics()
