"""
Test orchestrator functionality.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.orchestrator import Orchestrator
from orchestrator.task_queue import Task, TaskQueue


def test_orchestrator_initialization():
    """Test that orchestrator can be initialized."""
    orch = Orchestrator()
    assert orch is not None
    assert orch.status == "ready"


def test_add_task():
    """Test adding a task to orchestrator."""
    orch = Orchestrator()
    task_id = orch.add_task("Test task", priority="high")
    assert task_id is not None
    assert isinstance(task_id, str)


def test_task_queue():
    """Test task queue operations."""
    queue = TaskQueue(max_size=10)
    
    # Add task
    task = Task("Test task", priority="high")
    success = queue.enqueue(task)
    assert success == True
    
    # Get queue size
    size = queue.get_queue_size()
    assert size == 1
    
    # Dequeue task
    next_task = queue.dequeue()
    assert next_task is not None
    assert next_task.description == "Test task"


def test_orchestrator_status():
    """Test orchestrator status retrieval."""
    orch = Orchestrator()
    status = orch.get_orchestrator_status()
    
    assert "orchestrator_id" in status
    assert "status" in status
    assert "total_agents" in status
    assert status["total_agents"] >= 4  # Should have at least 4 agents
