from typing import List, Dict, Any, Optional
from long_term_memory import LongTermMemory
from vector_store import SimpleVectorStore
import json

class MemoryRetriever:
    """
    Unified interface for retrieving memories by keyword or semantic similarity.
    Combines long-term memory and vector store searches.
    """
    
    def __init__(self):
        """Initialize retriever with memory systems."""
        self.long_term = LongTermMemory()
        self.vector_store = SimpleVectorStore()
    
    def retrieve_by_keyword(self, 
                           keyword: str, 
                           memory_type: str = None, 
                           limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories by keyword search.
        
        Args:
            keyword: Search keyword
            memory_type: Optional filter by memory type
            limit: Max results
            
        Returns:
            List of matching memories
        """
        results = []
        
        if memory_type:
            candidates = self.long_term.retrieve_by_type(memory_type, limit=100)
        else:
            candidates = self.long_term.retrieve_recent(limit=100)
        
        # Simple keyword matching
        keyword_lower = keyword.lower()
        for memory in candidates:
            content = json.dumps(memory.get("content", {})).lower()
            if keyword_lower in content:
                results.append(memory)
                if len(results) >= limit:
                    break
        
        return results
    
    def retrieve_similar(self, 
                        query_embedding: List[float], 
                        limit: int = 5, 
                        threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Retrieve memories by semantic similarity.
        
        Args:
            query_embedding: Query vector embedding
            limit: Max results
            threshold: Minimum similarity score
            
        Returns:
            List of similar memories with scores
        """
        vector_results = self.vector_store.similarity_search(
            query_embedding, 
            top_k=limit, 
            threshold=threshold
        )
        
        # Enrich results with full memory content
        enriched_results = []
        for vec_result in vector_results:
            memory = self.long_term.retrieve_memory(vec_result["memory_id"])
            if memory:
                memory["similarity_score"] = vec_result["similarity"]
                enriched_results.append(memory)
        
        return enriched_results
    
    def retrieve_task_history(self, agent_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve task history memories.
        
        Args:
            agent_name: Optional filter by agent name
            limit: Max results
            
        Returns:
            List of task history memories
        """
        tasks = self.long_term.retrieve_by_type("task_history", limit=limit)
        
        if agent_name:
            tasks = [t for t in tasks if t.get("content", {}).get("agent") == agent_name]
        
        return tasks
    
    def retrieve_entity_knowledge(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve knowledge about a specific entity.
        
        Args:
            entity_id: Entity identifier (e.g., cell ID)
            
        Returns:
            Entity knowledge memory or None
        """
        entities = self.long_term.retrieve_by_type("entity_knowledge", limit=100)
        
        for entity in entities:
            if entity.get("content", {}).get("entity_id") == entity_id:
                return entity
        
        return None
    
    def retrieve_error_logs(self, 
                           agent_name: str = None, 
                           error_type: str = None, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve error logs for analysis.
        
        Args:
            agent_name: Optional filter by agent
            error_type: Optional filter by error type
            limit: Max results
            
        Returns:
            List of error logs
        """
        errors = self.long_term.retrieve_by_type("error_log", limit=limit)
        
        if agent_name:
            errors = [e for e in errors if e.get("content", {}).get("agent") == agent_name]
        
        if error_type:
            errors = [e for e in errors if e.get("content", {}).get("error_type") == error_type]
        
        return errors
    
    def retrieve_best_practices(self, use_case: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve best practices for a use case.
        
        Args:
            use_case: Optional filter by use case
            
        Returns:
            List of best practice memories
        """
        practices = self.long_term.retrieve_by_type("best_practices", limit=100)
        
        if use_case:
            practices = [p for p in practices if use_case in p.get("content", {}).get("use_cases", [])]
        
        return practices
    
    def get_context_summary(self, memory_id: str) -> Dict[str, Any]:
        """
        Get a summary of context around a memory.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Context summary
        """
        memory = self.long_term.retrieve_memory(memory_id)
        if not memory:
            return {}
        
        memory_type = memory.get("memory_type")
        
        # Get related memories by type
        related = self.long_term.retrieve_by_type(memory_type, limit=3)
        
        return {
            "target_memory": memory,
            "related_memories": related,
            "memory_type": memory_type
        }


# Example usage
if __name__ == "__main__":
    retriever = MemoryRetriever()
    
    # Retrieve task history
    tasks = retriever.retrieve_task_history(limit=5)
    print(f"Task history: {tasks}")
    
    # Retrieve by keyword
    kpi_tasks = retriever.retrieve_by_keyword("KPI")
    print(f"KPI-related tasks: {kpi_tasks}")
    
    # Retrieve error logs
    errors = retriever.retrieve_error_logs(limit=5)
    print(f"Error logs: {errors}")
