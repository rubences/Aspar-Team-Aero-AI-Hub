from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from backend_api.routes import genai, telemetry, auth
from backend_api.routes import race_engineering

app = FastAPI(
    title="Aspar Aero-AI-Hub Gateway",
    description="Enterprise Mission Control for Aerodynamic Race Engineering",
    version="1.0.0"
)

# 1. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to racing domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Add Monitoring (Prometheus)
Instrumentator().instrument(app).expose(app)

# 3. Include Specialized Routers
app.include_router(auth.router)
app.include_router(genai.router)
app.include_router(telemetry.router)
app.include_router(race_engineering.router)

@app.get("/")
def read_root():
    """
    Gateway Landing Page.
    """
    return {
        "agency": "Aspar Team",
        "system": "Aero-AI-Hub",
        "status": "OPERATIONAL",
        "nodes": ["GenAI", "Telemetry", "Auth", "Metrics"]
    }

@app.get("/health")
def system_health():
    """
    Health check endpoint for Kubernetes/Docker orchestration.
    """
    return {"status": "HEALTHY", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
