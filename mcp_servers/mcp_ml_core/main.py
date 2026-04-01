# MCP ML Core Server
# Exposes PINN/GRU models for prediction under demand.

from fastapi import FastAPI

app = FastAPI(title="MCP ML Core Server")

@app.get("/models")
def list_models():
    return {"models": ["aero_pinn_v1", "dynamics_gru_v2", "rl_optim_wing"]}
