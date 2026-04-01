from confluent_kafka import Consumer, KafkaError
import json
import logging
import signal

class KafkaBaseConsumer:
    """
    Standardizes Kafka stream consumption across all services.
    Handles configuration, subscription, and graceful shutdown.
    """
    def __init__(self, topics: list, bootstrap_servers: str = "localhost:9092", group_id: str = "aspar_default_group"):
        self.config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.topics = topics
        self.consumer = Consumer(self.config)
        self.running = True
        
        # Configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        # Setup exit handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum=None, frame=None):
        """
        Stops the consumption loop and closes connection safely.
        """
        self.logger.info("Interrupt received, shutting down consumer...")
        self.running = False

    def start_polling(self, callback_func):
        """
        Continuous polling loop that invokes callback for each message.
        """
        self.consumer.subscribe(self.topics)
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        self.logger.error(f"Kafka error: {msg.error()}")
                        break

                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                    callback_func(payload)
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
        finally:
            self.consumer.close()
            self.logger.info("Kafka consumer closed.")

if __name__ == "__main__":
    # consumer = KafkaBaseConsumer(["telemetry.raw"])
    print("Kafka Base Consumer initialized (Skeleton)")
