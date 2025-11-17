from .typing import Dict, List, Optional, Any
from .collections import deque
from .datetime import datetime
import uuid

class Task:
    """Represents a single task."""
    
    def __init__(self, 
                 description: str, 
                 priority: str = "medium",
                 deadline: Optional[str] = None):
        """
        Initialize a task.
        
        Args:
            description: Task description
            priority: Priority level (low, medium, high, critical)
            deadline: Optional deadline
        """
        self.task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.status = "pending"
        self.created_at = datetime.now()
        self.assigned_agent = None
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat()
        }


class TaskQueue:
    """
    Manages task queue with priority levels.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize task queue.
        
        Args:
            max_size: Maximum queue size
        """
        self.max_size = max_size
        self.priority_queues = {
            "critical": deque(),
            "high": deque(),
            "medium": deque(),
            "low": deque()
        }
        self.task_history: Dict[str, Task] = {}
    
    def enqueue(self, task: Task) -> bool:
        """
        Add task to queue.
        
        Args:
            task: Task to add
            
        Returns:
            True if successful
        """
        if self.get_queue_size() >= self.max_size:
            return False
        
        priority = task.priority
        if priority not in self.priority_queues:
            priority = "medium"
        
        self.priority_queues[priority].append(task)
        self.task_history[task.task_id] = task
        
        return True
    
    def dequeue(self) -> Optional[Task]:
        """
        Get next task from queue (highest priority first).
        
        Returns:
            Next task or None if queue empty
        """
        # Check priority queues in order
        for priority in ["critical", "high", "medium", "low"]:
            if self.priority_queues[priority]:
                task = self.priority_queues[priority].popleft()
                task.status = "assigned"
                return task
        
        return None
    
    def get_queue_size(self) -> int:
        """Get total number of pending tasks."""
        total = 0
        for queue in self.priority_queues.values():
            total += len(queue)
        return total
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get status of all queues."""
        return {
            priority: len(queue)
            for priority, queue in self.priority_queues.items()
        }
    
    def complete_task(self, task_id: str, result: Any) -> bool:
        """
        Mark task as completed.
        
        Args:
            task_id: Task ID
            result: Task result
            
        Returns:
            True if successful
        """
        if task_id not in self.task_history:
            return False
        
        task = self.task_history[task_id]
        task.status = "completed"
        task.result = result
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """
        Mark task as failed.
        
        Args:
            task_id: Task ID
            error: Error description
            
        Returns:
            True if successful
        """
        if task_id not in self.task_history:
            return False
        
        task = self.task_history[task_id]
        task.status = "failed"
        task.result = error
        
        return True


# Example usage
if __name__ == "__main__":
    # Create queue
    queue = TaskQueue(max_size=10)
    
    # Add tasks
    task1 = Task("Analyze KPIs", priority="high")
    task2 = Task("Generate report", priority="medium")
    task3 = Task("System alert", priority="critical")
    
    queue.enqueue(task1)
    queue.enqueue(task2)
    queue.enqueue(task3)
    
    print(f"Queue status: {queue.get_queue_status()}")
    
    # Dequeue (critical should come first)
    next_task = queue.dequeue()
    print(f"Next task: {next_task.description} (priority: {next_task.priority})")
    
    # Complete task
    queue.complete_task(next_task.task_id, {"result": "done"})
    print(f"Task completed: {next_task.status}")
