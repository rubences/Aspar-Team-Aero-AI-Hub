from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="MCP CAD Engine Server")

class ComponentMetadata(BaseModel):
    id: str
    name: str
    coords: Dict[str, float] # {x, y, z}
    surface_area: float # m2

@app.get("/cad/component/{part_id}")
def get_component_metadata(part_id: str):
    """
    Returns localized 3D points and surface area for a specific bike segment.
    """
    # Simulated metadata mapping for Aspar 2024 speculative CAD
    catalog = {
        "front_wing_l": {"id": "W01-L", "name": "Front Wing Left", "coords": {"x": 0.5, "y": 0.2, "z": 0.1}, "surface_area": 0.12},
        "front_wing_r": {"id": "W01-R", "name": "Front Wing Right", "coords": {"x": -0.5, "y": 0.2, "z": 0.1}, "surface_area": 0.12},
        "sidepod_l": {"id": "S22-L", "name": "Sidepod Intake Left", "coords": {"x": 0.4, "y": 0.8, "z": 0.4}, "surface_area": 0.35},
        "diffuser": {"id": "D99", "name": "Rear Bottom Diffuser", "coords": {"x": 0.0, "y": 1.5, "z": 0.05}, "surface_area": 0.45}
    }
    
    return catalog.get(part_id, {"error": "Component not found in current spec"})

@app.get("/cad/aerodynamic/map")
def get_aerodynamic_map():
    """
    Returns a physics-informed map of expected pressure per geometric region.
    """
    return {
        "pressure_regions": [
            {"region": "Nose Cone", "expected_cp": 1.0, "critical": True},
            {"region": "Undertray", "expected_cp": -2.5, "critical": True},
            {"region": "Rear Wing", "expected_cp": -1.2, "critical": False}
        ],
        "mesh_resolution": "High (5M cells CFD equivalent)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
