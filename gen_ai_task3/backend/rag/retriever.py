import time
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from backend.config import QDRANT_PATH, TOP_K
from backend.rag.embeddings import Embedder
from backend.logging_config import logger

class Retriever:
    def __init__(self, collection_name: str = "university_handbook"):
        self.collection_name = collection_name
        self.client = QdrantClient(path=QDRANT_PATH)
        self.embedder = Embedder()

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        start_time = time.time()
        
        # Embed the query
        query_vector = self.embedder.embed_query(query)
        
        # Query Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=TOP_K
        )
        
        retrieved_data = []
        retrieved_sections = []
        scores = []
        
        for res in results:
            payload = res.payload
            retrieved_data.append({
                "score": res.score,
                "section": payload.get("section", "Unknown"),
                "text": payload.get("text", ""),
                "source": payload.get("source", "Unknown")
            })
            retrieved_sections.append(payload.get("section", "Unknown"))
            scores.append(f"{res.score:.4f}")
            
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Log LLMOps metrics
        logger.info(
            f"rag_retrieval | query='{query[:50]}' | latency_ms={latency_ms} | "
            f"sections={retrieved_sections} | scores={scores}"
        )
        
        return retrieved_data
