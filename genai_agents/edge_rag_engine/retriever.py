from persistence_knowledge.milvus_vector.client import MilvusVectorClient
from langchain_openai import OpenAIEmbeddings
import os

class EdgeRetriever:
    """
    Sub-millisecond semantic retriever for Technical Regulations and Racing History.
    Uses Milvus for vector storage and OpenAI for embeddings.
    """
    def __init__(self, collection_name: str = "aero_knowledge"):
        self.client = MilvusVectorClient(collection_name=collection_name)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def retrieve_context(self, query: str, limit: int = 3):
        """
        Retrieves the most relevant regulation fragments for a query.
        """
        query_vector = self.embeddings.embed_query(query)
        results = self.client.search_vectors(query_vector, limit=limit)
        
        context_fragments = []
        for res in results[0]:
            # Each res has metadata with the actual text and source
            metadata = res.entity.get('metadata')
            context_fragments.append({
                "text": metadata.get("text", ""),
                "source": metadata.get("source", "Technical Regs 2024"),
                "distance": res.distance
            })
            
        return context_fragments

    def format_for_llm(self, context_fragments: list) -> str:
        """
        Helper to convert fragments into a single string for the prompt.
        """
        formatted = "--- RELEVANT REGULATIONS ---\n"
        for i, frag in enumerate(context_fragments):
            formatted += f"[{i+1}] Source: {frag['source']}\nContent: {frag['text']}\n"
        return formatted

if __name__ == "__main__":
    # retriever = EdgeRetriever()
    print("Edge RAG Retriever initialized (Skeleton)")
