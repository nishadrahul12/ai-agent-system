from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(Enum):
    """Task status in workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class WorkflowStatus(Enum):
    """Workflow status."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowTask:
    """Represents a task in a workflow."""
    
    def __init__(self, 
                 step: int, 
                 agent_id: str, 
                 description: str, 
                 dependencies: List[int] = None):
        """
        Initialize workflow task.
        
        Args:
            step: Step number
            agent_id: Agent to execute this task
            description: Task description
            dependencies: List of step numbers this depends on
        """
        self.step = step
        self.agent_id = agent_id
        self.description = description
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING.value
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step": self.step,
            "agent_id": self.agent_id,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat()
        }

class Workflow:
    """Multi-step workflow coordination."""
    
    def __init__(self, name: str):
        """
        Initialize workflow.
        
        Args:
            name: Workflow name
        """
        self.workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.tasks: Dict[int, WorkflowTask] = {}
        self.status = WorkflowStatus.CREATED.value
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def add_task(self, 
                 step: int, 
                 agent_id: str, 
                 description: str, 
                 dependencies: List[int] = None) -> WorkflowTask:
        """
        Add a task to the workflow.
        
        Args:
            step: Step number
            agent_id: Agent to execute
            description: Task description
            dependencies: Dependent steps
            
        Returns:
            WorkflowTask
        """
        task = WorkflowTask(step, agent_id, description, dependencies)
        self.tasks[step] = task
        return task
    
    def get_next_executable_task(self) -> Optional[WorkflowTask]:
        """
        Get next task that can be executed (dependencies satisfied).
        
        Returns:
            Task or None if none available
        """
        for step in sorted(self.tasks.keys()):
            task = self.tasks[step]
            
            # Check if task is pending
            if task.status != TaskStatus.PENDING.value:
                continue
            
            # Check if all dependencies are completed
            all_deps_completed = all(
                self.tasks[dep].status == TaskStatus.COMPLETED.value
                for dep in task.dependencies
                if dep in self.tasks
            )
            
            if all_deps_completed:
                return task
        
        return None
    
    def start_task(self, step: int) -> bool:
        """
        Mark task as in-progress.
        
        Args:
            step: Step number
            
        Returns:
            True if successful
        """
        if step not in self.tasks:
            return False
        
        task = self.tasks[step]
        task.status = TaskStatus.IN_PROGRESS.value
        task.started_at = datetime.now()
        
        if self.status == WorkflowStatus.CREATED.value:
            self.status = WorkflowStatus.IN_PROGRESS.value
            self.started_at = datetime.now()
        
        return True
    
    def complete_task(self, step: int, result: Any) -> bool:
        """
        Mark task as completed with result.
        
        Args:
            step: Step number
            result: Task result
            
        Returns:
            True if successful
        """
        if step not in self.tasks:
            return False
        
        task = self.tasks[step]
        task.status = TaskStatus.COMPLETED.value
        task.result = result
        task.completed_at = datetime.now()
        
        return True
    
    def fail_task(self, step: int, error: str) -> bool:
        """
        Mark task as failed.
        
        Args:
            step: Step number
            error: Error message
            
        Returns:
            True if successful
        """
        if step not in self.tasks:
            return False
        
        task = self.tasks[step]
        task.status = TaskStatus.FAILED.value
        task.error = error
        task.completed_at = datetime.now()
        
        # Fail dependent tasks
        for other_step, other_task in self.tasks.items():
            if step in other_task.dependencies and other_task.status == TaskStatus.PENDING.value:
                other_task.status = TaskStatus.BLOCKED.value
        
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """Get workflow progress."""
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED.value)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED.value)
        in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS.value)
        total = len(self.tasks)
        
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total - completed - in_progress - failed,
            "completion_percent": round((completed / total * 100) if total > 0 else 0, 1)
        }
    
    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        if not self.tasks:
            return False
        
        return all(
            t.status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]
            for t in self.tasks.values()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "tasks": {step: task.to_dict() for step, task in self.tasks.items()},
            "progress": self.get_progress()
        }


class WorkflowCoordinator:
    """Manages multiple workflows."""
    
    def __init__(self):
        """Initialize workflow coordinator."""
        self.workflows: Dict[str, Workflow] = {}
    
    def create_workflow(self, name: str) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(name)
        self.workflows[workflow.workflow_id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        """Get all workflows."""
        return list(self.workflows.values())


# Example usage
if __name__ == "__main__":
    # Create workflow
    coordinator = WorkflowCoordinator()
    workflow = coordinator.create_workflow("Multi-Step KPI Analysis")
    
    # Add tasks
    workflow.add_task(1, "worker_telecom", "Extract KPI data")
    workflow.add_task(2, "worker_generic", "Analyze trends", dependencies=[1])
    workflow.add_task(3, "evaluator", "Quality check", dependencies=[2])
    
    # Execute workflow
    print(f"Workflow created: {workflow.workflow_id}")
    
    # Get next executable task
    next_task = workflow.get_next_executable_task()
    print(f"Next task: Step {next_task.step} - {next_task.description}")
    
    # Start and complete task
    workflow.start_task(1)
    workflow.complete_task(1, {"data": [1, 2, 3]})
    
    # Get progress
    progress = workflow.get_progress()
    print(f"Progress: {progress}")
    
    # Get next task (now it's task 2)
    next_task = workflow.get_next_executable_task()
    print(f"Next task: Step {next_task.step} - {next_task.description}")
