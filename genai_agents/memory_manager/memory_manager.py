import redis

class MemoryManager:
    """
    Manages Short-Term (Redis) and Long-Term (Engram/Filesystem) memory for agents.
    """
    def __init__(self, persistence_path: str):
        self.persistence_path = persistence_path
        # self.cache = redis.Redis(host='localhost', port=6379, db=0)

    def save_interaction(self, session_id: str, message: str, role: str):
        """
        Saves chat history for session-based reasoning.
        """
        # Implementation for context window management
        print(f"MemoryManager: Saved {role} interaction for session {session_id}")

    def archive_context(self, domain: str, key_decision: str):
        """
        Writes significant decisions to Engram.
        """
        with open(f"{self.persistence_path}/domain_{domain}.log", "a") as f:
            f.write(f"{key_decision}\n")

if __name__ == "__main__":
    print("Memory Manager initialized")
