import json
import logging
from confluent_kafka import Consumer, KafkaError
import numpy as np
import requests
import torch
import os
from persistence_knowledge.influx_timeseries.client import InfluxTelemetryClient
from ingestion_correlation.babai_quantization.solver import BabaiLatticeSolver
from ai_applications.ai_aero_predict.gru_inference.model import GRUInferenceEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryConsumer")

# Internal Service URL for Backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "aspar_engineer")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "aspar_pass_2024")

class TelemetryConsumer:
    """
    Production-ready Kafka Consumer for Aspar Team.
    Integrates real-time de-quantization (Babai), Persistence (InfluxDB), 
    and AI-Driven Predictive Anomaly Forecasting (GRU).
    """
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'allow.auto.create.topics': True
        }
        self.consumer = Consumer(self.conf)
        self.consumer.subscribe(topics)
        
        # Clients
        self.influx_client = InfluxTelemetryClient()
        self.solver = BabaiLatticeSolver(np.eye(3) * 0.1)
        
        # ML Inference (GRU)
        # Dimensions: 3 (rpm, temp, rake) + 0 context (simplified for e2e)
        self.gru_engine = GRUInferenceEngine(input_dim=3, context_dim=0, hidden_dim=64, output_dim=3)
        self.window_buffer = []
        self.window_size = 10 # 10ms sliding window at 1000Hz
        self._access_token = None

    def _get_access_token(self):
        """
        Requests and caches an access token for protected backend endpoints.
        """
        if self._access_token:
            return self._access_token

        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/token",
                data={"username": AUTH_USERNAME, "password": AUTH_PASSWORD},
                timeout=5
            )
            if response.ok:
                self._access_token = response.json().get("access_token")
                return self._access_token
            logger.error(f"Auth failed for telemetry consumer: {response.status_code} {response.text}")
        except Exception as e:
            logger.error(f"Failed to authenticate telemetry consumer: {e}")
        return None

    def _trigger_genai_alert(self, bike_id: str, alert_msg: str, is_predictive: bool = False):
        """
        Sends an automated alert to the API Gateway.
        """
        prefix = "PREDICTIVE ALERT" if is_predictive else "CRITICAL ALERT"
        try:
            token = self._get_access_token()
            if not token:
                return

            requests.post(
                f"{BACKEND_URL}/genai/chat",
                json={
                    "message": f"{prefix}: {alert_msg}. ¿Qué recomiendas?",
                    "bike_id": bike_id
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to trigger GenAI alert: {e}")

    def start_polling(self):
        """
        Main loop to poll for telemetry events.
        """
        logger.info("Smart Telemetry Consumer with AI Forecasting started.")
        
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None: continue
                if msg.error():
                    err_code = msg.error().code()
                    if err_code in (KafkaError._PARTITION_EOF, KafkaError.UNKNOWN_TOPIC_OR_PART):
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    break
                
                # 1. Parse & De-quantize
                payload = json.loads(msg.value().decode('utf-8'))
                sensors = payload.get("sensors", {})
                bike_id = payload.get("bike_id")
                
                raw_vector = np.array([sensors.get("rpm", 0), sensors.get("temp", 0), sensors.get("rake", 0)])
                clean_vector = self.solver.solve(raw_vector)
                
                # 2. Persistence
                for i, name in enumerate(["rpm", "temp", "rake"]):
                    self.influx_client.write_sensor_data(name, float(clean_vector[i]), bike_id)
                
                # 3. AI SLIDING WINDOW INFERENCE (Every 10ms)
                self.window_buffer.append(clean_vector)
                if len(self.window_buffer) >= self.window_size:
                    # Run GRU Inference
                    input_seq = np.array(self.window_buffer).reshape(1, self.window_size, 3)
                    # For this E2E, we pass zeros as context
                    mock_context = np.zeros((1, self.window_size, 0))
                    
                    prediction = self.gru_engine.predict_dynamics(input_seq, mock_context)
                    
                    # Check for predictive anomalies (e.g. predicted rake drop)
                    predicted_rake = prediction[2]
                    if predicted_rake < 0.7:
                        self._trigger_genai_alert(bike_id, f"IA predice caída de Rake a {predicted_rake:.2f}mm en los próximos 50ms", is_predictive=True)
                    
                    # Slide the window
                    self.window_buffer.pop(0)

                # 4. Reactive Thresholds (Real-time)
                if clean_vector[2] < 0.6:
                    self._trigger_genai_alert(bike_id, f"Caída crítica de Rake (REAL): {clean_vector[2]}mm")

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()
            self.influx_client.close()

if __name__ == "__main__":
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    group_id = os.getenv("KAFKA_GROUP_ID", "aspar_telemetry_group")
    topics = os.getenv("KAFKA_TOPICS", "telemetry.raw").split(",")

    consumer = TelemetryConsumer(bootstrap_servers=bootstrap, group_id=group_id, topics=topics)
    consumer.start_polling()
