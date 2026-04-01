from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI(title="Aspar Aero Hub Gateway")

# Internal service URLs (would be environment variables in production)
MCP_TELEMETRY_URL = "http://localhost:8001"
MCP_ML_CORE_URL = "http://localhost:8002"

class SessionMetadata(BaseModel):
    bike_id: str
    track: str
    driver: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aspar Team Aero-AI-Hub Backend API"}

@app.post("/sessions/create")
def create_session(metadata: SessionMetadata):
    """
    Registers a new racing session in the MongoDB store.
    """
    # Simple placeholder for recording a session
    return {"status": "SUCCESS", "session_id": "session-2024-001"}

@app.get("/telemetry/active")
def get_live_metrics(bike_id: str):
    """
    Proxies calls to the Telemetry MCP Server.
    """
    try:
        response = requests.get(f"{MCP_TELEMETRY_URL}/telemetry/query", params={"bike_id": bike_id, "sensor": "speed"})
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to Telemetry service: {e}")

# In-memory storage for pending validation (for development)
hitl_queue = []

class ValidationResponse(BaseModel):
    recommendation_id: int
    status: str # "APPROVED" or "REJECTED"

@app.get("/hitl/queue")
def list_pending_validations():
    """
    Returns the list of recommendations awaiting human sign-off.
    """
    return hitl_queue

@app.post("/hitl/validate")
def validate_recommendation(validation: ValidationResponse):
    """
    Receives the sign-off or rejection from the operator interface.
    Updates the HITL state and allows the orchestrator to proceed.
    """
    for rec in hitl_queue:
        if rec["id"] == validation.recommendation_id:
            rec["status"] = validation.status
            return {"status": "UPDATED", "recommendation_id": validation.recommendation_id}
    
    raise HTTPException(status_code=404, detail="Recommendation ID not found in queue")

@app.get("/health")
def system_health():
    """
    Standard health check endpoint for the entire gateway.
    """
    return {"status": "HEALTHY", "v": "1.0.0", "queue_size": len(hitl_queue)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
