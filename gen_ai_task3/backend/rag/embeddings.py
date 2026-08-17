from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL

class Embedder:
    def __init__(self):
        # Local model loading using sentence-transformers
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_query(self, text: str) -> list:
        # Normalize embeddings to allow simple cosine similarity
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: list) -> list:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
