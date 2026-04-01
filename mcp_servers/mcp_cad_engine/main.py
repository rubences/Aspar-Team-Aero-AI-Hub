# MCP CAD Engine Server
# Exposes Onshape and geometric meshes for aerodynamic analysis.

from fastapi import FastAPI

app = FastAPI(title="MCP CAD Engine Server")

@app.get("/parts")
def list_parts():
    return {"parts": ["fairing_front", "tail_section", "swingarm"]}
