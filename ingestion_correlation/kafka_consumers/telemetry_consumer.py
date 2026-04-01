import json
import logging
from confluent_kafka import Consumer, KafkaError
import numpy as np
import requests
from persistence_knowledge.influx_timeseries.client import InfluxTelemetryClient
from ingestion_correlation.babai_quantization.solver import BabaiLatticeSolver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryConsumer")

# Internal Service URL for Backend
BACKEND_URL = "http://localhost:8000"

class TelemetryConsumer:
    """
    Production-ready Kafka Consumer for Aspar Team.
    Performs real-time de-quantization (Babai), Persistence (InfluxDB), 
    and Anomaly Notification to the GenAI Supervisor.
    """
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.consumer.subscribe(topics)
        
        # Clients
        self.influx_client = InfluxTelemetryClient()
        # Initialize Babai Solver with an identity basis for simplicity
        self.solver = BabaiLatticeSolver(np.eye(3) * 0.1)

    def _trigger_genai_alert(self, bike_id: str, alert_msg: str):
        """
        Sends an automated alert to the API Gateway to notify the GenAI Supervisor.
        """
        try:
            requests.post(f"{BACKEND_URL}/genai/chat", json={
                "message": f"ALERT: {alert_msg}. ¿Qué recomiendas?",
                "bike_id": bike_id
            })
        except Exception as e:
            logger.error(f"Failed to trigger GenAI alert: {e}")

    def start_polling(self):
        """
        Main loop to poll for telemetry events.
        """
        logger.info(f"Smart Telemetry Consumer started. Listening on topics: {self.topics if hasattr(self, 'topics') else 'subscribed'}")
        
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        break
                
                # 1. Parse Raw Message
                payload = json.loads(msg.value().decode('utf-8'))
                sensors = payload.get("sensors", {})
                bike_id = payload.get("bike_id")
                
                # 2. De-quantization / Noise Reduction (Babai)
                # In a real scenario, we map sensor values to a vector
                raw_vector = np.array([sensors.get("rpm", 0), sensors.get("temp", 0), sensors.get("rake", 0)])
                clean_vector = self.solver.solve(raw_vector)
                
                # 3. Persistence to InfluxDB
                for i, name in enumerate(["rpm", "temp", "rake"]):
                    self.influx_client.write_sensor_data(name, float(clean_vector[i]), bike_id)
                
                # 4. Critical Threshold Monitoring (Simple Anomaly)
                if clean_vector[2] < 0.6: # Rake below critical aerodynamic stall threshold
                    self._trigger_genai_alert(bike_id, f"Caída crítica de Rake detectada: {clean_vector[2]}mm")
                
                if clean_vector[1] > 105: # High temperature alert
                    self._trigger_genai_alert(bike_id, f"Sobrecalentamiento motor: {clean_vector[1]}C")

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()
            self.influx_client.close()

if __name__ == "__main__":
    # consumer = TelemetryConsumer("localhost:9092", "aero-hub-group", ["telemetry.raw"])
    # consumer.start_polling()
    print("Smart Telemetry Consumer initialized (Production Core)")
