from typing import Dict, List, Any
from .long_term_memory import LongTermMemory
import json

class MemorySummarizer:
    """
    Summarizes long interactions and stores compressed versions.
    Helps manage memory size and improve retrieval efficiency.
    """
    
    def __init__(self, storage_path: str = "./memory/summaries/"):
        """Initialize summarizer."""
        self.long_term = LongTermMemory()
        self.storage_path = storage_path
        import os
        os.makedirs(storage_path, exist_ok=True)
    
    def summarize_task_history(self, 
                               memory_id: str, 
                               compression_ratio: float = 0.3) -> Dict[str, Any]:
        """
        Summarize a task history memory.
        
        Args:
            memory_id: Task memory ID to summarize
            compression_ratio: Target size ratio (0.3 = 30% of original)
            
        Returns:
            Summarized memory
        """
        memory = self.long_term.retrieve_memory(memory_id)
        if not memory:
            return {}
        
        content = memory.get("content", {})
        
        # Extract key information
        summary = {
            "task_name": content.get("task_name"),
            "agent": content.get("agent"),
            "status": content.get("outcome"),
            "key_result": self._extract_key_result(content.get("result", "")),
            "duration_ms": content.get("duration_ms"),
            "confidence": content.get("confidence"),
            "metadata": content.get("metadata", {})
        }
        
        return summary
    
    def summarize_interaction_sequence(self, 
                                      memory_ids: List[str], 
                                      max_lines: int = 20) -> Dict[str, Any]:
        """
        Summarize a sequence of interactions.
        
        Args:
            memory_ids: List of memory IDs
            max_lines: Maximum lines in summary
            
        Returns:
            Summarized interaction sequence
        """
        memories = []
        for mem_id in memory_ids:
            mem = self.long_term.retrieve_memory(mem_id)
            if mem:
                memories.append(mem)
        
        # Build summary timeline
        timeline = []
        for mem in memories:
            timestamp = mem.get("timestamp", "")
            mem_type = mem.get("memory_type", "")
            content = mem.get("content", {})
            
            entry = f"[{timestamp}] {mem_type}: {content.get('task_name', 'unknown')}"
            timeline.append(entry)
        
        summary = {
            "total_interactions": len(memories),
            "timeline": timeline[:max_lines],
            "truncated": len(timeline) > max_lines
        }
        
        return summary
    
    def summarize_entity_performance(self, entity_id: str) -> Dict[str, Any]:
        """
        Summarize performance history for an entity.
        
        Args:
            entity_id: Entity ID (e.g., cell ID)
            
        Returns:
            Performance summary
        """
        # Retrieve all entity memories
        entity_memories = self.long_term.retrieve_by_type("entity_knowledge", limit=100)
        entity_memory = None
        
        for mem in entity_memories:
            if mem.get("content", {}).get("entity_id") == entity_id:
                entity_memory = mem
                break
        
        if not entity_memory:
            return {}
        
        content = entity_memory.get("content", {})
        performance_history = content.get("performance_history", [])
        
        # Calculate statistics
        if performance_history:
            sinr_values = [p.get("sinr_avg", 0) for p in performance_history]
            throughput_values = [p.get("throughput_mbps", 0) for p in performance_history]
            
            summary = {
                "entity_id": entity_id,
                "entity_type": content.get("entity_type"),
                "latest_performance": performance_history[-1] if performance_history else {},
                "sinr_trend": {
                    "min": min(sinr_values) if sinr_values else 0,
                    "max": max(sinr_values) if sinr_values else 0,
                    "avg": sum(sinr_values) / len(sinr_values) if sinr_values else 0
                },
                "throughput_trend": {
                    "min": min(throughput_values) if throughput_values else 0,
                    "max": max(throughput_values) if throughput_values else 0,
                    "avg": sum(throughput_values) / len(throughput_values) if throughput_values else 0
                },
                "history_count": len(performance_history)
            }
        else:
            summary = {
                "entity_id": entity_id,
                "message": "No performance history"
            }
        
        return summary
    
    def _extract_key_result(self, result_text: str, max_length: int = 100) -> str:
        """Extract key result from long text."""
        if len(result_text) <= max_length:
            return result_text
        
        # Try to find first sentence
        sentences = result_text.split('.')
        if sentences:
            return sentences[0][:max_length] + "..."
        
        return result_text[:max_length] + "..."
    
    def create_memory_report(self) -> Dict[str, Any]:
        """
        Create a comprehensive memory system report.
        
        Returns:
            Memory system report
        """
        lt_stats = self.long_term.get_statistics()
        
        return {
            "total_memories": lt_stats["total_memories"],
            "by_type": lt_stats["by_type"],
            "report_generated": str(__import__('datetime').datetime.now())
        }


# Example usage
if __name__ == "__main__":
    summarizer = MemorySummarizer()
    
    # Create report
    report = summarizer.create_memory_report()
    print(f"Memory report: {report}")
