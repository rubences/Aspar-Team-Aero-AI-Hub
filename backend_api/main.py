"""
Backend API — Central application orchestrator.
FastAPI server exposing REST endpoints for telemetry, agents, and chat.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend_api.auth.provider import get_current_user, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("Starting Aspar SmartOps Aero Hub API...")
    yield
    logger.info("Shutting down Aspar SmartOps Aero Hub API...")


# ─── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Aspar SmartOps Aero Hub API",
    description="Central orchestrator for AI-powered aerodynamic and race operations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    vehicle_id: str = "ASPAR_44"
    session_id: str = "default"
    context: dict[str, Any] = {}


class ChatResponse(BaseModel):
    response: str
    agent: str
    intent: str
    session_id: str


class TelemetryResponse(BaseModel):
    vehicle_id: str
    speed_kmh: float | None = None
    rpm: float | None = None
    throttle_pct: float | None = None
    brake_pct: float | None = None
    gear: int | None = None
    oil_temp_c: float | None = None
    water_temp_c: float | None = None
    downforce_n: float | None = None
    drag_n: float | None = None


class FaultsResponse(BaseModel):
    vehicle_id: str
    faults: list[dict[str, Any]]


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Service health check endpoint."""
    return {"status": "ok", "service": "aspar-smartops-aero-hub"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Process a natural language query through the multi-agent system.
    Routes to the appropriate specialist agent via the supervisor.
    """
    from genai_agents.supervisor_agent import SupervisorAgent
    from genai_agents.aero_engineer_agent import AeroEngineerAgent
    from genai_agents.race_engineer_agent import RaceEngineerAgent
    from langchain_core.messages import HumanMessage

    supervisor = SupervisorAgent()
    intent, route = supervisor.classify_and_route(request.message)

    state = {
        "messages": [HumanMessage(content=request.message)],
        "context": request.context,
        "vehicle_id": request.vehicle_id,
        "session_id": request.session_id,
    }

    if route == "aero":
        result = AeroEngineerAgent().handle(state)
    else:
        result = RaceEngineerAgent().handle(state)

    return ChatResponse(
        response=result.get("response", "No response generated."),
        agent=result.get("agent", "UnknownAgent"),
        intent=intent,
        session_id=request.session_id,
    )


@app.get("/api/telemetry/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(
    vehicle_id: str = "ASPAR_44",
    current_user: User = Depends(get_current_user),
) -> TelemetryResponse:
    """Get the latest telemetry snapshot for a vehicle."""
    # In production, this queries the InfluxDB store
    # Returning a mock response for demonstration
    import random
    return TelemetryResponse(
        vehicle_id=vehicle_id,
        speed_kmh=round(random.uniform(100, 280), 1),
        rpm=round(random.uniform(8000, 13000)),
        throttle_pct=round(random.uniform(0, 100), 1),
        brake_pct=round(random.uniform(0, 100), 1),
        gear=random.randint(1, 6),
        oil_temp_c=round(random.uniform(90, 125), 1),
        water_temp_c=round(random.uniform(85, 102), 1),
        downforce_n=round(random.uniform(800, 1800), 0),
        drag_n=round(random.uniform(150, 350), 0),
    )


@app.get("/api/faults/active", response_model=FaultsResponse)
async def get_active_faults(
    vehicle_id: str = "ASPAR_44",
    current_user: User = Depends(get_current_user),
) -> FaultsResponse:
    """Get active fault reports for a vehicle."""
    return FaultsResponse(vehicle_id=vehicle_id, faults=[])


@app.get("/api/mesh/{document_id}")
async def get_mesh(
    document_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Retrieve a CAD mesh for 3D visualisation."""
    from mcp_servers.mcp_cad_engine.server import MCPCADEngineServer
    server = MCPCADEngineServer(
        onshape_access_key=os.getenv("ONSHAPE_ACCESS_KEY", ""),
        onshape_secret_key=os.getenv("ONSHAPE_SECRET_KEY", ""),
    )
    return server.get_mesh(document_id, "default")


if __name__ == "__main__":
    uvicorn.run(
        "backend_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
