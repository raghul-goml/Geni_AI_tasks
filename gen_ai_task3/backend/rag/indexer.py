from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from backend.config import QDRANT_PATH
from backend.rag.embeddings import Embedder
import os

class Indexer:
    def __init__(self, collection_name: str = "university_handbook"):
        self.collection_name = collection_name
        # Local Qdrant Storage
        os.makedirs(QDRANT_PATH, exist_ok=True)
        self.client = QdrantClient(path=QDRANT_PATH)
        self.embedder = Embedder()

    def create_collection(self):
        dimension = self.embedder.get_dimension()
        
        # Check if collection already exists, if so recreate it
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if exists:
            self.client.delete_collection(self.collection_name)
            
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    def index_chunks(self, chunks: list):
        self.create_collection()
        
        points = []
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed_documents(texts)
        
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=idx,
                    vector=vector,
                    payload={
                        "section": chunk["section"],
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "chunk_id": chunk["chunk_id"]
                    }
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Indexed {len(points)} chunks into collection '{self.collection_name}'")
