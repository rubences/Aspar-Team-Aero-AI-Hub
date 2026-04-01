from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import numpy as np
import sys
import os

# Adjust path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion_correlation.babai_quantization.decoder import BabaiDecoder
from ai_applications.ai_aero_predict.gru_inference.model import GRUInferenceEngine
from genai_agents.edge_rag_engine.engine import EdgeRAGEngine

app = FastAPI(title="Aspar-Team-Aero-AI-Hub Backend")

# Initialize global engines (using mock basis for Babai)
BABAI_BASIS = np.eye(16) # Example 16D space
babai_decoder = BabaiDecoder(BABAI_BASIS)

# GRU: input=16 (reconstructed tele), context=64, hidden=128, output=5
gru_engine = GRUInferenceEngine(16, 64, 128, 5)

# Edge-RAG: 64D embeddings
rag_engine = EdgeRAGEngine(64)

class TelemetryPayload(BaseModel):
    device_id: str
    quantized_vector: list # List of integers

@app.get("/")
def read_root():
    return {"status": "Aspar-Team-Aero-AI-Hub is Operational"}

@app.post("/ingest/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Ingest compressed telemetry, decode using Babai, and run AI prediction.
    """
    try:
        # 1. Decode Babai-quantized vector
        z = np.array(payload.quantized_vector, dtype=int)
        reconstructed = babai_decoder.decode(z)
        
        # 2. Retrieve historical context (Mocking embedding generation)
        # In a real scenario, we'd use an encoder network here
        mock_query_emb = np.random.randn(64)
        history = rag_engine.retrieve(mock_query_emb, k=1)
        
        context_vector = history[0][1]["vector"] if history else np.zeros(64)
        
        # 3. Predict Dynamics and Anomalies
        # Reshape for sequence of 1
        prediction = gru_engine.predict_dynamics(
            reconstructed.reshape(1, -1), 
            context_vector.reshape(1, -1)
        )
        
        return {
            "status": "processed",
            "received": payload.device_id,
            "prediction": prediction.tolist(),
            "anomaly_score": float(np.max(np.abs(prediction))) # Simple heuristic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/query")
async def agent_query(query: str = Body(...)):
    """
    Main entry point for Multi-Agent orchestrator interaction.
    """
    # This would route to LangGraph supervisor
    return {"response": f"Acknowledged: {query}. Routing to specialized agents..."}

if __name__ == "__main__":
    import uvicorn
    # Mocking some data in RAG engine for the demo
    for i in range(10):
        rag_engine.upsert(np.random.randn(64), {"id": i, "vector": np.random.randn(64)})
        
    uvicorn.run(app, host="0.0.0.0", port=8000)
