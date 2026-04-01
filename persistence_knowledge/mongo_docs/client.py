from pymongo import MongoClient
import datetime

class MongoEventClient:
    """
    Client for MongoDB to store enriched events, configurations, and session metadata.
    """
    def __init__(self, uri: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client["aspar_aero_hub"]
        self.events = self.db["events"]
        self.setups = self.db["bike_setups"]

    def log_event(self, event_type: str, source: str, data: dict, severity: str = "INFO"):
        """
        Persists a high-level event for documentation and audit.
        """
        event = {
            "type": event_type,
            "source": source,
            "data": data,
            "severity": severity,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        return self.events.insert_one(event).inserted_id

    def save_setup(self, bike_id: str, setup_data: dict, author: str):
        """
        Saves a bike configuration snapshot.
        """
        setup = {
            "bike_id": bike_id,
            "config": setup_data,
            "author": author,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        return self.setups.insert_one(setup).inserted_id

    def get_latest_setup(self, bike_id: str):
        """
        Retrieves the most recent setup for a bike.
        """
        return self.setups.find_one({"bike_id": bike_id}, sort=[("timestamp", -1)])

if __name__ == "__main__":
    # client = MongoEventClient()
    print("MongoDB Client initialized (Skeleton)")
