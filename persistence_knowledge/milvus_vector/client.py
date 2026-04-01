from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import os

class MilvusVectorClient:
    """
    Client for Milvus Vector Database.
    Handles semantic storage for technical documents and historical telemetry patterns.
    """
    def __init__(self, host: str = "localhost", port: str = "19530", collection_name: str = "aero_knowledge"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._connect()

    def _connect(self):
        connections.connect("default", host=self.host, port=self.port)

    def create_collection(self, dim: int = 768):
        """
        Creates a collection for vector storage.
        """
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, "Knowledge collection for Aero hub")
        self.collection = Collection(self.collection_name, schema)
        return self.collection

    def insert_vectors(self, vectors: list, metadata_list: list):
        """
        Inserts vectors and their associated metadata.
        """
        if not utility.has_collection(self.collection_name):
            self.create_collection(len(vectors[0]))
        
        collection = Collection(self.collection_name)
        data = [
            vectors,
            metadata_list
        ]
        return collection.insert(data)

    def search_vectors(self, query_vector: list, limit: int = 5):
        """
        Searches for similar vectors in the collection.
        """
        collection = Collection(self.collection_name)
        collection.load()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        return collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=limit,
            output_fields=["metadata"]
        )

if __name__ == "__main__":
    # client = MilvusVectorClient()
    print("Milvus Vector Client initialized (Skeleton)")
