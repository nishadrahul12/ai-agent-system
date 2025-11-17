import json
import os
from .typing import Dict, List, Tuple, Any, Optional
import math

class SimpleVectorStore:
    """
    Simple vector store for semantic similarity search.
    Uses cosine similarity with pre-computed embeddings.
    Note: For production, use ChromaDB or Milvus instead.
    """
    
    def __init__(self, storage_path: str = "./memory/vector_store/"):
        """
        Initialize vector store.
        
        Args:
            storage_path: Directory for storing embeddings
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.vectors_file = os.path.join(storage_path, "vectors.json")
        self._ensure_vectors_file()
    
    def _ensure_vectors_file(self):
        """Create vectors file if it doesn't exist."""
        if not os.path.exists(self.vectors_file):
            with open(self.vectors_file, 'w') as f:
                json.dump({"vectors": []}, f)
    
    def add_vector(self, 
                   memory_id: str, 
                   text: str, 
                   embedding: List[float], 
                   metadata: Dict[str, Any] = None) -> str:
        """
        Add a vector to the store.
        
        Args:
            memory_id: Reference to long-term memory ID
            text: Original text/description
            embedding: Vector embedding (list of floats)
            metadata: Optional metadata
            
        Returns:
            vector_id: Unique ID for this vector
        """
        vector_id = f"vec_{memory_id}"
        
        vector_record = {
            "vector_id": vector_id,
            "memory_id": memory_id,
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        
        # Load existing vectors
        with open(self.vectors_file, 'r') as f:
            data = json.load(f)
        
        # Add new vector
        data["vectors"].append(vector_record)
        
        # Save
        with open(self.vectors_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return vector_id
    
    def similarity_search(self, 
                         query_embedding: List[float], 
                         top_k: int = 5, 
                         threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find similar vectors using cosine similarity.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            threshold: Minimum similarity score
            
        Returns:
            List of similar records with similarity scores
        """
        results = []
        
        # Load vectors
        with open(self.vectors_file, 'r') as f:
            data = json.load(f)
        
        # Compute similarity for each vector
        similarities = []
        for vector_record in data["vectors"]:
            similarity = self._cosine_similarity(query_embedding, vector_record["embedding"])
            if similarity >= threshold:
                similarities.append((vector_record, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return [
            {
                "vector_id": rec["vector_id"],
                "memory_id": rec["memory_id"],
                "text": rec["text"],
                "similarity": sim,
                "metadata": rec["metadata"]
            }
            for rec, sim in similarities[:top_k]
        ]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if len(vec1) != len(vec2):
            return 0.0
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific vector by ID.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            Vector record or None
        """
        with open(self.vectors_file, 'r') as f:
            data = json.load(f)
        
        for vector_record in data["vectors"]:
            if vector_record["vector_id"] == vector_id:
                return vector_record
        
        return None
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        with open(self.vectors_file, 'r') as f:
            data = json.load(f)
        
        original_count = len(data["vectors"])
        data["vectors"] = [v for v in data["vectors"] if v["vector_id"] != vector_id]
        
        if len(data["vectors"]) < original_count:
            with open(self.vectors_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about vectors."""
        with open(self.vectors_file, 'r') as f:
            data = json.load(f)
        
        return {
            "total_vectors": len(data["vectors"]),
            "vectors_file_size_kb": os.path.getsize(self.vectors_file) / 1024
        }


# Example usage
if __name__ == "__main__":
    # Initialize vector store
    vs = SimpleVectorStore()
    
    # Add sample vectors (in reality, these come from an embedding model)
    sample_embedding1 = [0.1, 0.2, 0.3, 0.4, 0.5]
    sample_embedding2 = [0.1, 0.2, 0.3, 0.4, 0.5]  # Highly similar
    sample_embedding3 = [0.9, 0.8, 0.7, 0.6, 0.5]  # Different
    
    vs.add_vector("mem_001", "Analyze telecom KPIs", sample_embedding1)
    vs.add_vector("mem_002", "Analyze network metrics", sample_embedding2)
    vs.add_vector("mem_003", "Generate report", sample_embedding3)
    
    # Search for similar vectors
    query = [0.1, 0.2, 0.3, 0.4, 0.5]
    results = vs.similarity_search(query, top_k=2, threshold=0.5)
    print(f"Similar vectors: {results}")
    
    # Statistics
    stats = vs.get_statistics()
    print(f"Vector store stats: {stats}")
