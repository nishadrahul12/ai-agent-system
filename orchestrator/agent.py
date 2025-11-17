from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid
import json

class Agent:
    """
    Base Agent class. All agents inherit from this.
    Defines common behavior and interface for all agents.
    """
    
    def __init__(self, 
                 agent_type: str, 
                 name: str, 
                 capabilities: List[str],
                 prompt: str = ""):
        """
        Initialize an agent.
        
        Args:
            agent_type: Type of agent (supervisor, worker_generic, etc.)
            name: Human-readable name
            capabilities: List of capabilities this agent has
            prompt: System prompt for LLM
        """
        self.agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities
        self.prompt = prompt
        self.status = "initializing"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.task_count = 0
        self.error_count = 0
        self.metadata = {}
    
    def can_handle_task(self, task_description: str) -> float:
        """
        Check if agent can handle a task and return confidence score.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Confidence score (0-1)
        """
        # Simple keyword matching for now
        task_lower = task_description.lower()
        matched_capabilities = sum(
            1 for cap in self.capabilities 
            if cap.lower() in task_lower
        )
        
        if matched_capabilities > 0:
            return min(matched_capabilities / len(self.capabilities), 1.0)
        
        return 0.0
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task dictionary with requirements
            
        Returns:
            Task result
        """
        self.status = "processing"
        self.last_activity = datetime.now()
        self.task_count += 1
        
        try:
            # Placeholder: Override in subclasses
            result = {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "status": "completed",
                "result": "Task executed",
                "timestamp": datetime.now().isoformat()
            }
            
            self.status = "idle"
            return result
        
        except Exception as e:
            self.error_count += 1
            self.status = "error"
            
            return {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "task_count": self.task_count,
            "error_count": self.error_count,
            "last_activity": self.last_activity.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class SupervisorAgent(Agent):
    """
    Supervisor Agent: Decomposes tasks and delegates to workers.
    """
    
    def __init__(self, name: str = "Supervisor", prompt: str = ""):
        super().__init__(
            agent_type="supervisor",
            name=name,
            capabilities=["task_decomposition", "delegation", "monitoring", "quality_control"],
            prompt=prompt
        )
        self.delegated_tasks = []
    
    def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a task into subtasks.
        
        Args:
            task: Original task
            
        Returns:
            List of subtasks
        """
        # Placeholder: Should use LLM to intelligently decompose
        subtasks = [
            {
                "subtask_id": f"subtask_{i}",
                "description": f"Step {i}: {task.get('description', 'unknown')}",
                "priority": "high" if i == 0 else "medium"
            }
            for i in range(1, 3)
        ]
        
        return subtasks


class WorkerAgent(Agent):
    """
    Worker Agent: Executes tasks using prompts and tools.
    """
    
    def __init__(self, 
                 worker_type: str = "generic", 
                 name: str = "Worker",
                 prompt: str = ""):
        capabilities = [
            "task_execution",
            "tool_usage",
            "data_analysis",
            "result_formatting"
        ]
        
        super().__init__(
            agent_type=f"worker_{worker_type}",
            name=name,
            capabilities=capabilities,
            prompt=prompt
        )
        self.worker_type = worker_type


class EvaluatorAgent(Agent):
    """
    Evaluator Agent: Quality checks and scores work.
    """
    
    def __init__(self, name: str = "Evaluator", prompt: str = ""):
        super().__init__(
            agent_type="evaluator",
            name=name,
            capabilities=["quality_scoring", "validation", "feedback_generation"],
            prompt=prompt
        )
    
    def evaluate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a work result.
        
        Args:
            result: Result to evaluate
            
        Returns:
            Evaluation score and feedback
        """
        evaluation = {
            "result_id": result.get("task_id"),
            "quality_score": 85,  # Placeholder
            "feedback": "Good work",
            "recommendation": "APPROVE"
        }
        
        return evaluation


# Example usage
if __name__ == "__main__":
    # Create agents
    supervisor = SupervisorAgent(name="Main Supervisor")
    worker = WorkerAgent(worker_type="generic", name="Worker 1")
    evaluator = EvaluatorAgent(name="Evaluator 1")
    
    # Check status
    print(f"Supervisor: {supervisor.get_status()}")
    print(f"Worker: {worker.get_status()}")
    
    # Test task execution
    test_task = {
        "task_id": "test_001",
        "description": "Test task"
    }
    
    result = worker.execute_task(test_task)
    print(f"Execution result: {result}")
