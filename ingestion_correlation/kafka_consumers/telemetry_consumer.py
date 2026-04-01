import json
import logging
from confluent_kafka import Consumer, KafkaError
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryConsumer")

class TelemetryConsumer:
    """
    Asynchronous Kafka Consumer for Aspar Team Telemetry.
    Connects to the telemetry stream and prepares data for decoding and normalization.
    """
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.consumer.subscribe(topics)

    def start_polling(self, callback):
        """
        Main loop to poll for telemetry events.
        """
        logger.info(f"Starting telemetry consumer on topics: {self.consumer.list_topics()}")
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
                
                # Process message
                payload = json.loads(msg.value().decode('utf-8'))
                callback(payload)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

if __name__ == "__main__":
    # Mock callback for testing
    def process_telemetry(data):
        print(f"Received Telemetry: {data}")

    # For development, we skip actual Kafka connection if not running
    # consumer = TelemetryConsumer("localhost:9092", "aero-hub-group", ["live_telemetry"])
    # consumer.start_polling(process_telemetry)
    print("Telemetry Consumer initialized (Skeleton)")
