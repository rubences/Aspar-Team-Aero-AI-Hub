import json
import time
import argparse
from confluent_kafka import Producer
from persistence_knowledge.minio_storage.client import MinioStorageClient

# Default Config
KAFKA_SERVER = "localhost:9092"
MINIO_ENDPOINT = "localhost:9000"
KAFKA_TOPIC = "telemetry.raw"

class SessionReplayEngine:
    """
    The Time Machine: Replays historical telemetry sessions from MinIO 
    into the Kafka pipeline for back-testing and analysis.
    """
    def __init__(self, session_id: str, speed_multiplier: float = 1.0):
        self.session_id = session_id
        self.speed = speed_multiplier
        self.producer = Producer({'bootstrap.servers': KAFKA_SERVER})
        self.minio = MinioStorageClient(MINIO_ENDPOINT, "minioadmin", "minioadmin")

    def run_replay(self, local_data_path: str = None):
        """
        Starts the playback process.
        """
        print(f"--- ASPAR TELEMETRY REPLAY: {self.session_id} ---")
        print(f"Speed: {self.speed}x | Target: {KAFKA_TOPIC}")
        
        # 1. Download session log from MinIO (Mock logic)
        # In a real scenario, this would be a large JSON array of telemetry
        # For now, we simulate a small sequence of 50 samples
        mock_history = []
        for i in range(50):
            mock_history.append({
                "bike_id": "ASPAR-AERO-REPLAY",
                "timestamp": i * 0.001, # ms precision
                "sensors": {"rpm": 13000 + i*10, "temp": 95 + i*0.1, "rake": 1.2 - i*0.01},
                "meta": {"replay": True}
            })
            
        print(f"Loaded {len(mock_history)} samples. Starting stream...")
        
        # 2. Iterate and Stream to Kafka
        for msg in mock_history:
            self.producer.produce(KAFKA_TOPIC, json.dumps(msg).encode('utf-8'))
            
            # 3. Simulate Original Frequency (1000Hz) adjusted by Speed
            delay = 0.001 / self.speed
            time.sleep(delay)
            
            if i % 10 == 0:
                self.producer.flush()

        print("[ REPLAY COMPLETE ] All packets injected into the pipeline.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aspar Telemetry Replay Engine")
    parser.add_argument("--session", type=str, default="session-2024-01", help="ID of the session to replay")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier (e.g. 5.0 for 5x)")
    
    args = parser.parse_args()
    engine = SessionReplayEngine(args.session, args.speed)
    engine.run_replay()
