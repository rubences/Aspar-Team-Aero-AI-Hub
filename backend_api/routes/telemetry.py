import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend_api.auth.core import get_current_user

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

MCP_TELEMETRY_URL = "http://localhost:8001"

class SessionMetadata(BaseModel):
    bike_id: str
    track: str
    driver: str

@router.get("/active")
async def get_live_metrics(bike_id: str, current_user: str = Depends(get_current_user)):
    """
    Proxies calls to the Telemetry MCP Server. Authorized only.
    """
    try:
        response = requests.get(f"{MCP_TELEMETRY_URL}/telemetry/query", params={"bike_id": bike_id, "sensor": "speed"})
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Telemetry error: {e}")

@router.post("/sessions/create")
async def create_session(metadata: SessionMetadata, current_user: str = Depends(get_current_user)):
    return {"status": "SUCCESS", "session_id": "session-2024-001", "created_by": current_user}
