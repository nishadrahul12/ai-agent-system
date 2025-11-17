from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os

from .agent import SupervisorAgent, WorkerAgent, EvaluatorAgent
from .agent_registry import AgentRegistry
from .router import Router
from .task_queue import TaskQueue, Task
from .config import config


class Orchestrator:
    """
    Main Orchestrator: Coordinates all agents, routes tasks, manages lifecycle.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.orchestrator_id = f"orch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.registry = AgentRegistry()
        self.router = Router(self.registry)
        self.task_queue = TaskQueue(
            max_size=config.get("task_queue.max_queue_size", 100)
        )
        self.status = "initializing"
        self.created_at = datetime.now()
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize default agents."""
        # Create supervisor
        supervisor = SupervisorAgent(name="Main Supervisor")
        self.registry.register_agent(supervisor)
        
        # Create workers
        worker_generic = WorkerAgent(
            worker_type="generic",
            name="Generic Worker"
        )
        self.registry.register_agent(worker_generic)
        
        worker_telecom = WorkerAgent(
            worker_type="telecom",
            name="Telecom Worker"
        )
        self.registry.register_agent(worker_telecom)
        
        # Create evaluator
        evaluator = EvaluatorAgent(name="Quality Evaluator")
        self.registry.register_agent(evaluator)
        
        self.status = "ready"
    
    def add_task(self, 
                 description: str, 
                 priority: str = "medium",
                 deadline: Optional[str] = None) -> Optional[str]:
        """
        Add a new task to the queue.
        
        Args:
            description: Task description
            priority: Priority level
            deadline: Optional deadline
            
        Returns:
            task_id or None if queue full
        """
        task = Task(description, priority, deadline)
        
        if self.task_queue.enqueue(task):
            return task.task_id
        else:
            return None
    
    def process_tasks(self, max_tasks: int = 10) -> List[Dict[str, Any]]:
        """
        Process tasks from the queue.
        
        Args:
            max_tasks: Maximum tasks to process
            
        Returns:
            List of processed task results
        """
        results = []
        processed = 0
        
        while processed < max_tasks:
            # Get next task
            task = self.task_queue.dequeue()
            if not task:
                break
            
            # Route to appropriate agent
            agent, confidence = self.router.route_task(task.description)
            
            if not agent:
                self.task_queue.fail_task(task.task_id, "No suitable agent found")
                continue
            
            # Execute task
            result = agent.execute_task(task.to_dict())
            
            # Complete task
            self.task_queue.complete_task(task.task_id, result)
            
            results.append(result)
            processed += 1
        
        return results
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """Get task queue status."""
        return {
            "queue_size": self.task_queue.get_queue_size(),
            "by_priority": self.task_queue.get_queue_status()
        }
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get agent registry status."""
        return self.registry.get_registry_status()
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get overall orchestrator status."""
        return {
            "orchestrator_id": self.orchestrator_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "total_agents": self.registry.get_agent_count(),
            "queue_status": self.get_task_queue_status(),
            "agents": self.get_registry_status()
        }
    
    def shutdown(self):
        """Shutdown the orchestrator."""
        self.status = "shutdown"


# Example usage
if __name__ == "__main__":
    # Initialize orchestrator
    orch = Orchestrator()
    print(f"Orchestrator initialized: {orch.orchestrator_id}")
    
    # Add tasks
    task1_id = orch.add_task("Analyze Q3 telecom KPIs", priority="high")
    task2_id = orch.add_task("Generate performance report", priority="medium")
    task3_id = orch.add_task("Run system diagnostic", priority="low")
    
    print(f"Added tasks: {task1_id}, {task2_id}, {task3_id}")
    
    # Check queue
    print(f"Queue status: {orch.get_task_queue_status()}")
    
    # Process tasks
    results = orch.process_tasks(max_tasks=3)
    print(f"Processed {len(results)} tasks")
    
    # Get status
    status = orch.get_orchestrator_status()
    print(f"Orchestrator status: {json.dumps(status, indent=2)}")
    
    # Shutdown
    orch.shutdown()
