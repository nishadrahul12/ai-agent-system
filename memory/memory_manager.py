from .long_term_memory import LongTermMemory
from .vector_store import SimpleVectorStore
from .memory_retriever import MemoryRetriever
from .memory_summarizer import MemorySummarizer
from .typing import Dict, List, Any, Optional
import json

class MemoryManager:
    """
    Unified manager for all memory operations.
    Coordinates long-term storage, vector search, retrieval, and summarization.
    """
    
    def __init__(self):
        """Initialize all memory subsystems."""
        self.long_term = LongTermMemory()
        self.vector_store = SimpleVectorStore()
        self.retriever = MemoryRetriever()
        self.summarizer = MemorySummarizer()
    
    def store_task_result(self, 
                         task_name: str, 
                         agent: str, 
                         result: str, 
                         metadata: Dict[str, Any] = None,
                         embedding: List[float] = None) -> str:
        """
        Store a task completion result.
        
        Args:
            task_name: Name of the task
            agent: Name of agent that completed it
            result: Result/output
            metadata: Additional metadata
            embedding: Optional vector embedding
            
        Returns:
            memory_id for future reference
        """
        task_content = {
            "task_name": task_name,
            "agent": agent,
            "result": result,
            "metadata": metadata or {},
            "outcome": "success"
        }
        
        memory_id = self.long_term.store_memory("task_history", task_content)
        
        # Optionally store vector for semantic search
        if embedding:
            text = f"{task_name} - {result[:100]}"
            self.vector_store.add_vector(memory_id, text, embedding, {"agent": agent})
        
        return memory_id
    
    def store_entity_knowledge(self, 
                              entity_id: str, 
                              entity_type: str, 
                              attributes: Dict[str, Any]) -> str:
        """
        Store knowledge about an entity (e.g., cell).
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            attributes: Entity attributes
            
        Returns:
            memory_id
        """
        entity_content = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "attributes": attributes
        }
        
        return self.long_term.store_memory("entity_knowledge", entity_content)
    
    def store_error(self, 
                   agent: str, 
                   error_type: str, 
                   error_message: str, 
                   task_id: str = None, 
                   resolution: str = None) -> str:
        """
        Store an error for learning.
        
        Args:
            agent: Agent name
            error_type: Type of error
            error_message: Error message
            task_id: Related task ID
            resolution: How it was resolved
            
        Returns:
            memory_id
        """
        error_content = {
            "agent": agent,
            "error_type": error_type,
            "error_message": error_message,
            "task_id": task_id,
            "resolution": resolution
        }
        
        return self.long_term.store_memory("error_log", error_content)
    
    def store_best_practice(self, 
                           title: str, 
                           description: str, 
                           steps: List[str], 
                           use_cases: List[str]) -> str:
        """
        Store a best practice/learned pattern.
        
        Args:
            title: Practice title
            description: What it is
            steps: Step-by-step guide
            use_cases: When to use it
            
        Returns:
            memory_id
        """
        practice_content = {
            "title": title,
            "description": description,
            "steps": steps,
            "use_cases": use_cases,
            "success_rate": 1.0
        }
        
        return self.long_term.store_memory("best_practices", practice_content)
    
    def query_similar_tasks(self, 
                           query_embedding: List[float], 
                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar tasks using vector search.
        
        Args:
            query_embedding: Query vector
            limit: Number of results
            
        Returns:
            List of similar task memories
        """
        return self.retriever.retrieve_similar(query_embedding, limit=limit)
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get system-wide memory statistics."""
        lt_stats = self.long_term.get_statistics()
        vs_stats = self.vector_store.get_statistics()
        
        return {
            "long_term": lt_stats,
            "vector_store": vs_stats
        }


# Example usage
if __name__ == "__main__":
    mm = MemoryManager()
    
    # Store a task result
    task_id = mm.store_task_result(
        task_name="Analyze Q3 KPIs",
        agent="worker_telecom",
        result="KPI analysis complete with trends",
        metadata={"cells": ["CELL_A_01", "CELL_A_02"]}
    )
    print(f"Stored task: {task_id}")
    
    # Store entity knowledge
    entity_id = mm.store_entity_knowledge(
        entity_id="CELL_A_01",
        entity_type="cell",
        attributes={"location": "Downtown", "tech": "5G"}
    )
    print(f"Stored entity: {entity_id}")
    
    # Store error
    error_id = mm.store_error(
        agent="worker_generic",
        error_type="API_TIMEOUT",
        error_message="Request took > 30s",
        resolution="Retry with backoff"
    )
    print(f"Stored error: {error_id}")
    
    # Get statistics
    stats = mm.get_memory_statistics()
    print(f"Memory stats: {stats}")
