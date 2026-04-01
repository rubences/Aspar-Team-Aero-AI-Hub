import requests
from langchain.tools import tool

# Internal service URLs
MCP_TELEMETRY_URL = "http://localhost:8001"
MCP_ML_CORE_URL = "http://localhost:8002"

@tool
def get_live_telemetry_summary(bike_id: str, sensor_name: str):
    """
    Retrieves the most recent telemetry data points for a specific bike and sensor.
    Use this to get real-time context before making any engineering recommendations.
    """
    try:
        response = requests.get(f"{MCP_TELEMETRY_URL}/telemetry/query", params={"bike_id": bike_id, "sensor": sensor_name})
        if response.status_code == 200:
            return response.json()
        return f"Error: Telemetry service returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to Telemetry service: {e}"

@tool
def request_ml_inference(bike_id: str, sensor_data: list, model_type: str = "pinn"):
    """
    Triggers a physics-informed or GRU-based prediction.
    Use this when you need to project future performance or identify anomalies in complex aerodynamics.
    """
    try:
        payload = {"bike_id": bike_id, "sensor_stream": sensor_data, "model_name": model_type}
        response = requests.post(f"{MCP_ML_CORE_URL}/ml/predict", json=payload)
        if response.status_code == 200:
            return response.json()
        return f"Error: ML Core service returned {response.status_code}"
    except Exception as e:
        return f"Error connecting to ML Core service: {e}"

# Tool list for Export
AERO_TOOLS = [get_live_telemetry_summary, request_ml_inference]
RACE_TOOLS = [get_live_telemetry_summary]
