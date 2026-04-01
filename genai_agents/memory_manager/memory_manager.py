from persistence_knowledge.mongo_docs.client import MongoEventClient
import datetime

class AgentMemoryManager:
    """
    Maintains persistent memory of conversations and mechanical setups.
    Interface between GenAI agents and the MongoDB persistence layer.
    """
    def __init__(self, db_uri: str = "mongodb://localhost:27017/"):
        self.db = MongoEventClient(db_uri)

    def store_conversation(self, bike_id: str, messages: list, session_id: str):
        """
        Stores serialized conversation history for later retrieval.
        """
        data = {
            "session_id": session_id,
            "bike_id": bike_id,
            "messages": [msg.dict() if hasattr(msg, 'dict') else str(msg) for msg in messages]
        }
        return self.db.log_event("genai_conversation", "supervisor_agent", data)

    def store_mechanical_recommendation(self, bike_id: str, recommendation: str, status: str = "PENDING"):
        """
        Records a specific engineering recommendation for human-in-the-loop validation.
        """
        data = {
            "recommendation": recommendation,
            "status": status,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        return self.db.log_event("mechanical_recommendation", "aero_engineer", data)

    def get_last_approved_setup(self, bike_id: str):
        """
        Retrieves the most recent setup configuration that was signed off by the operator.
        """
        return self.db.get_latest_setup(bike_id)

if __name__ == "__main__":
    # memory = AgentMemoryManager()
    print("Agent Memory Manager initialized (Skeleton)")
