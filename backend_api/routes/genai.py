from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from genai_agents.supervisor_agent import orchestrator
from langchain_core.messages import HumanMessage
from backend_api.auth.core import get_current_user

router = APIRouter(prefix="/genai", tags=["GenAI"])

# In-memory storage (mock)
hitl_queue = []

class ChatRequest(BaseModel):
    message: str
    bike_id: str

@router.post("/chat")
async def chat_with_agents(request: ChatRequest, current_user: str = Depends(get_current_user)):
    """
    Invokes the LangGraph orchestrator with JWT protection.
    """
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "next_agent": "",
            "requires_validation": False,
            "validation_status": "PENDING"
        }
        
        final_state = orchestrator.invoke(initial_state)
        last_message = final_state["messages"][-1].content
        
        if final_state.get("requires_validation"):
            rec_id = len(hitl_queue) + 1
            hitl_queue.append({
                "id": rec_id,
                "bike_id": request.bike_id,
                "recommendation": last_message,
                "status": "PENDING"
            })
            return {"response": last_message, "hitl_id": rec_id}
            
        return {"response": last_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator Error: {e}")

@router.get("/hitl/queue")
async def list_pending_validations(current_user: str = Depends(get_current_user)):
    return hitl_queue

from confluent_kafka import Producer
import json

# Setup Producer for Closed-Loop Control
control_producer = Producer({'bootstrap.servers': 'localhost:9092'})

@router.post("/hitl/validate")
async def validate_recommendation(validation: ValidationResponse, current_user: str = Depends(get_current_user)):
    for rec in hitl_queue:
        if rec["id"] == validation.recommendation_id:
            rec["status"] = validation.status
            
            # CLOSED-LOOP LOGIC: If approved, apply the recommendation to the simulator
            if validation.status == "APPROVED":
                # Parse numeric recommendation (e.g. "increase rake by 1.2mm")
                # This is simplified for the PoC; a real system would use a structured schema
                if "rake" in rec["recommendation"].lower():
                    try:
                        # Extract number (primitive extraction for PoC)
                        import re
                        match = re.search(r"(\d+\.?\d*)", rec["recommendation"])
                        if match:
                            val = float(match.group(1))
                            # Send control signal to simulator
                            control_msg = {"param": "rake_offset", "value": val}
                            control_producer.produce("telemetry.control", json.dumps(control_msg).encode('utf-8'))
                            control_producer.flush()
                    except Exception as e:
                        print(f"Error producing control signal: {e}")

            return {"status": "UPDATED", "rec_id": validation.recommendation_id}
    raise HTTPException(status_code=404, detail="Not found")
