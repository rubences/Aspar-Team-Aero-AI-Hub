import numpy as np
import time
from typing import List, Tuple, Optional

class EdgeRAGEngine:
    """
    Sub-millisecond Vector Retrieval Engine for Aspar Team.
    Uses an in-memory vector cache to provide instantaneous historical context.
    """
    def __init__(self, embedding_dim: int, cache_size: int = 1000):
        self.embedding_dim = embedding_dim
        # Using simple numpy array for high-performance in-memory search
        self.vector_cache = np.zeros((cache_size, embedding_dim))
        self.metadata_cache = [None] * cache_size
        self.current_idx = 0
        self.is_filled = False

    def upsert(self, embedding: np.ndarray, metadata: dict):
        """
        Adds a new embedding and metadata to the circular buffer.
        """
        self.vector_cache[self.current_idx] = embedding
        self.metadata_cache[self.current_idx] = metadata
        
        self.current_idx += 1
        if self.current_idx >= len(self.vector_cache):
            self.current_idx = 0
            self.is_filled = True

    def retrieve(self, query_embedding: np.ndarray, k: int = 1) -> List[Tuple[float, dict]]:
        """
        Retrieves top-k similar vectors using cosine similarity.
        Target latency: < 500 microseconds.
        """
        start_time = time.perf_counter()
        
        # Determine valid search range
        limit = len(self.vector_cache) if self.is_filled else self.current_idx
        if limit == 0:
            return []
            
        search_space = self.vector_cache[:limit]
        
        # Compute Cosine Similarity: (A . B) / (||A|| * ||B||)
        # Normalize search space and query
        search_norm = np.linalg.norm(search_space, axis=1, keepdims=True)
        query_norm = np.linalg.norm(query_embedding)
        
        # Avoid division by zero
        search_norm[search_norm == 0] = 1e-9
        if query_norm == 0: query_norm = 1e-9
        
        similarities = np.dot(search_space, query_embedding) / (search_norm.flatten() * query_norm)
        
        # Get top-k indices
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        results = [
            (float(similarities[idx]), self.metadata_cache[idx])
            for idx in top_k_indices
        ]
        
        end_time = time.perf_counter()
        # print(f"Retrieval latency: {(end_time - start_time) * 1000000:.2f} microseconds")
        
        return results

if __name__ == "__main__":
    # Benchmark retrieval
    engine = EdgeRAGEngine(embedding_dim=128, cache_size=5000)
    
    # Fill cache with mock data
    for i in range(5000):
        engine.upsert(np.random.randn(128), {"id": i, "tag": "telemetry_snapshot"})
        
    # Query
    q = np.random.randn(128)
    results = engine.retrieve(q, k=3)
    
    # Measure latency over 1000 trials
    start = time.perf_counter()
    for _ in range(1000):
        _ = engine.retrieve(q, k=1)
    end = time.perf_counter()
    
    print(f"Average latency over 1000 trials: {(end - start) / 1000 * 1000000:.2f} microseconds")
    print(f"Top result: {results[0]}")
