from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import numpy as np
import sys
import os

# Adjust path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Domain Layer Imports
from ingestion_correlation.babai_quantization.decoder import BabaiDecoder
from ingestion_correlation.normalizers.standard_schema import TelemetryNormalizer
from ai_applications.ai_aero_predict.gru_inference.model import GRUInferenceEngine
from ai_applications.ai_fault_diagnosis.diagnostics import FaultDiagnosisAgent
from genai_agents.edge_rag_engine.engine import EdgeRAGEngine
from genai_agents.supervisor_agent import orchestrator

app = FastAPI(title="Aspar-Team-Aero-AI-Hub Central API")

# Initialize Domain Engines
feature_map = {"speed": 0, "rpm": 1, "lean_angle": 2, "throttle": 3}
normalizer = TelemetryNormalizer(feature_map)
babai_decoder = BabaiDecoder(np.eye(len(feature_map)))
gru_engine = GRUInferenceEngine(len(feature_map), 64, 128, 5)
rag_engine = EdgeRAGEngine(64)
diagnostician = FaultDiagnosisAgent()

class TelemetryPayload(BaseModel):
    bike_id: str
    quantized_vector: list # Int indices

@app.post("/api/v1/telemetry/ingest")
async def ingest(payload: TelemetryPayload):
    """
    Unified Ingestion Endpoint: Decodes, Diagnoses, and Predicts in one flow.
    """
    try:
        # 1. Decode Lattice
        z = np.array(payload.quantized_vector, dtype=int)
        raw_vec = babai_decoder.decode(z)
        
        # 2. Denormalize for Diagnostics
        readable_data = normalizer.denormalize(raw_vec)
        alerts = diagnostician.diagnose(readable_data)
        
        # 3. Retrieve Context & Predict Dynamics
        mock_query = np.random.randn(64)
        history = rag_engine.retrieve(mock_query, k=1)
        ctx = history[0][1]["vector"] if history else np.zeros(64)
        
        prediction = gru_engine.predict_dynamics(raw_vec.reshape(1, -1), ctx.reshape(1, -1))
        
        return {
            "bike_id": payload.bike_id,
            "status": "success",
            "telemetry": readable_data,
            "alerts": alerts,
            "prediction": prediction.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agent/chat")
async def chat(query: str = Body(..., embed=True)):
    """
    Routes natural language queries to the LangGraph supervisor.
    """
    try:
        initial_state = {"messages": [query], "next_agent": ""}
        results = []
        for output in orchestrator.stream(initial_state):
            results.append(output)
        
        # Extract last meaningful message
        final_response = "No se pudo obtener respuesta del agente."
        for res in results:
            if "messages" in res:
                final_response = res["messages"][-1]
                
        return {"response": final_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
