import sys
import requests

BASE_API = "http://localhost:8000"
MCP_ENDPOINTS = [
    ("MCP Telemetry", "http://localhost:8001/telemetry/stream/status"),
    ("MCP ML Core", "http://localhost:8002/ml/models/active"),
    ("MCP CAD Engine", "http://localhost:8003/cad/aerodynamic/map"),
]


def check(name, condition, detail):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}: {detail}")
    return condition


def main():
    ok = True

    # Gateway health
    try:
        r = requests.get(f"{BASE_API}/health", timeout=10)
        ok &= check("Gateway Health", r.status_code == 200, f"status={r.status_code}")
    except Exception as exc:
        ok &= check("Gateway Health", False, f"error={exc}")

    # Auth flow
    token = None
    try:
        r = requests.post(
            f"{BASE_API}/auth/token",
            data={"username": "aspar_engineer", "password": "aspar_pass_2024"},
            timeout=10,
        )
        ok &= check("Auth Token", r.status_code == 200, f"status={r.status_code}")
        if r.status_code == 200:
            token = r.json().get("access_token")
            ok &= check("Auth Token Payload", bool(token), "token present" if token else "token missing")
    except Exception as exc:
        ok &= check("Auth Token", False, f"error={exc}")

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # Protected endpoint
    try:
        r = requests.get(f"{BASE_API}/auth/me", headers=headers, timeout=10)
        ok &= check("Auth Me", r.status_code == 200, f"status={r.status_code}")
    except Exception as exc:
        ok &= check("Auth Me", False, f"error={exc}")

    # GenAI + HITL queue
    try:
        r = requests.post(
            f"{BASE_API}/genai/chat",
            headers=headers,
            json={"message": "aero rake recommendation", "bike_id": "ASPAR-AERO-01"},
            timeout=15,
        )
        ok &= check("GenAI Chat", r.status_code == 200, f"status={r.status_code}")
    except Exception as exc:
        ok &= check("GenAI Chat", False, f"error={exc}")

    try:
        r = requests.get(f"{BASE_API}/genai/hitl/queue", headers=headers, timeout=10)
        ok &= check("HITL Queue", r.status_code == 200, f"status={r.status_code}")
    except Exception as exc:
        ok &= check("HITL Queue", False, f"error={exc}")

    # MCP services
    for name, url in MCP_ENDPOINTS:
        try:
            r = requests.get(url, timeout=10)
            ok &= check(name, r.status_code == 200, f"status={r.status_code}")
        except Exception as exc:
            ok &= check(name, False, f"error={exc}")

    print("\nRESULT:", "SUCCESS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
