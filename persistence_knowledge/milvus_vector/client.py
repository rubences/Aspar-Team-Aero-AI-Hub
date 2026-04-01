from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import numpy as np

class MilvusClient:
    """
    Client for Milvus Vector Database.
    Handles semantic search for historical telemetry and manual embeddings.
    """
    def __init__(self, host: str = "localhost", port: str = "19530"):
        connections.connect("default", host=host, port=port)
        self.collection_name = "telemetry_embeddings"
        
    def create_collection(self, dim: int):
        """
        Initializes collection schema for telemetry vectors.
        """
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="timestamp", dtype=DataType.INT64),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, "Aspar Team Telemetry Vector Store")
        self.collection = Collection(self.collection_name, schema)
        
        # Create IVF_FLAT index for fast search
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        self.collection.create_index("embedding", index_params)

    def insert(self, embeddings: list, timestamps: list, metadata_list: list):
        """
        Inserts batch of embeddings and metadata.
        """
        col = Collection(self.collection_name)
        data = [embeddings, timestamps, metadata_list]
        col.insert(data)
        col.flush()

    def search(self, query_vec: np.ndarray, limit: int = 5):
        """
        Performs semantic similarity search.
        """
        col = Collection(self.collection_name)
        col.load()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = col.search(
            data=[query_vec.tolist()], 
            anns_field="embedding", 
            param=search_params, 
            limit=limit, 
            output_fields=["timestamp", "metadata"]
        )
        return results

if __name__ == "__main__":
    # client = MilvusClient()
    # client.create_collection(128)
    print("Milvus Client initialized (Skeleton)")
