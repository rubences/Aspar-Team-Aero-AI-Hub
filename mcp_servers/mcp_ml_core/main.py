from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="MCP ML Core Server")

class InferenceRequest(BaseModel):
    bike_id: str
    sensor_stream: List[float]
    model_name: str = "pinn_aero_01"

@app.post("/ml/predict")
def run_inference(request: InferenceRequest):
    """
    Triggers a physics-informed or GRU prediction on the given stream.
    """
    return {
        "prediction": [12.4, 12.5, 12.7],
        "confidence": 0.98,
        "delta_to_target": -0.05
    }

@app.get("/ml/models/active")
def list_active_models():
    """
    Lists deployed models and their current metrics.
    """
    return ["pinn_aero_01", "gru_lap_timer", "anomaly_detector_shocks"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
