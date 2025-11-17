import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class LongTermMemory:
    """
    Manages persistent long-term memory stored as JSON files.
    Handles creation, retrieval, update, and deletion of memory records.
    """
    
    def __init__(self, storage_path: str = "./memory/long_term/"):
        """
        Initialize long-term memory system.
        
        Args:
            storage_path: Directory where JSON memory files are stored
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.memory_index_file = os.path.join(storage_path, "memory_index.json")
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create memory index file if it doesn't exist."""
        if not os.path.exists(self.memory_index_file):
            with open(self.memory_index_file, 'w') as f:
                json.dump({"memories": []}, f, indent=2)
    
    def store_memory(self, memory_type: str, content: Dict[str, Any]) -> str:
        """
        Store a new memory record.
        
        Args:
            memory_type: Type of memory (task_history, entity_knowledge, error_log, best_practices)
            content: Dictionary containing memory content
            
        Returns:
            memory_id: Unique identifier for the stored memory
        """
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        memory_record = {
            "memory_id": memory_id,
            "memory_type": memory_type,
            "timestamp": datetime.now().isoformat(),
            "content": content
        }
        
        # Save to individual JSON file
        memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
        with open(memory_file, 'w') as f:
            json.dump(memory_record, f, indent=2)
        
        # Update index
        self._update_index(memory_id, memory_type, "created")
        
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: Unique identifier of the memory
            
        Returns:
            Memory record or None if not found
        """
        memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
        
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                return json.load(f)
        return None
    
    def retrieve_by_type(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve all memories of a specific type.
        
        Args:
            memory_type: Type of memory to retrieve
            limit: Maximum number of results to return
            
        Returns:
            List of memory records
        """
        memories = []
        
        # Load index
        with open(self.memory_index_file, 'r') as f:
            index = json.load(f)
        
        # Find all memories of this type
        for mem_entry in index["memories"]:
            if mem_entry["memory_type"] == memory_type:
                memory_record = self.retrieve_memory(mem_entry["memory_id"])
                if memory_record:
                    memories.append(memory_record)
                    if len(memories) >= limit:
                        break
        
        return memories
    
    def retrieve_recent(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories from the last N days.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of recent memory records
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        memories = []
        
        # Load index
        with open(self.memory_index_file, 'r') as f:
            index = json.load(f)
        
        for mem_entry in index["memories"]:
            mem_timestamp = datetime.fromisoformat(mem_entry["timestamp"])
            if mem_timestamp > cutoff_date:
                memory_record = self.retrieve_memory(mem_entry["memory_id"])
                if memory_record:
                    memories.append(memory_record)
                    if len(memories) >= limit:
                        break
        
        return memories
    
    def update_memory(self, memory_id: str, updated_content: Dict[str, Any]) -> bool:
        """
        Update an existing memory record.
        
        Args:
            memory_id: ID of memory to update
            updated_content: New content
            
        Returns:
            True if successful, False if memory not found
        """
        memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
        
        if not os.path.exists(memory_file):
            return False
        
        # Load existing record
        with open(memory_file, 'r') as f:
            memory_record = json.load(f)
        
        # Update content and timestamp
        memory_record["content"] = updated_content
        memory_record["updated_at"] = datetime.now().isoformat()
        
        # Save updated record
        with open(memory_file, 'w') as f:
            json.dump(memory_record, f, indent=2)
        
        return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory record.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if successful, False if memory not found
        """
        memory_file = os.path.join(self.storage_path, f"{memory_id}.json")
        
        if os.path.exists(memory_file):
            os.remove(memory_file)
            self._update_index(memory_id, "", "deleted")
            return True
        return False
    
    def _update_index(self, memory_id: str, memory_type: str, action: str):
        """
        Update the memory index file.
        
        Args:
            memory_id: Memory ID
            memory_type: Type of memory
            action: 'created', 'updated', or 'deleted'
        """
        with open(self.memory_index_file, 'r') as f:
            index = json.load(f)
        
        if action == "created":
            index["memories"].append({
                "memory_id": memory_id,
                "memory_type": memory_type,
                "timestamp": datetime.now().isoformat()
            })
        elif action == "deleted":
            index["memories"] = [m for m in index["memories"] if m["memory_id"] != memory_id]
        
        with open(self.memory_index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        with open(self.memory_index_file, 'r') as f:
            index = json.load(f)
        
        memory_types = {}
        for mem in index["memories"]:
            mem_type = mem["memory_type"]
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
        
        return {
            "total_memories": len(index["memories"]),
            "by_type": memory_types,
            "index_file": self.memory_index_file
        }


# Example usage
if __name__ == "__main__":
    # Initialize memory system
    memory = LongTermMemory()
    
    # Store a task history memory
    task_content = {
        "task_name": "Analyze Q3 KPIs",
        "agent": "worker_telecom",
        "result": "Analysis complete",
        "cells_analyzed": ["CELL_A_01", "CELL_A_02"]
    }
    task_id = memory.store_memory("task_history", task_content)
    print(f"Stored task memory: {task_id}")
    
    # Retrieve it
    retrieved = memory.retrieve_memory(task_id)
    print(f"Retrieved: {retrieved}")
    
    # Get statistics
    stats = memory.get_statistics()
    print(f"Statistics: {stats}")
