"""
Test memory system functionality.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.long_term_memory import LongTermMemory
from memory.vector_store import SimpleVectorStore


def test_long_term_memory_initialization():
    """Test memory system can be initialized."""
    memory = LongTermMemory(storage_path="./memory/long_term/test/")
    assert memory is not None


def test_store_memory():
    """Test storing a memory."""
    memory = LongTermMemory(storage_path="./memory/long_term/test/")
    
    content = {
        "task_name": "Test task",
        "result": "Success"
    }
    
    memory_id = memory.store_memory("task_history", content)
    assert memory_id is not None
    assert isinstance(memory_id, str)


def test_retrieve_memory():
    """Test retrieving a stored memory."""
    memory = LongTermMemory(storage_path="./memory/long_term/test/")
    
    # Store
    content = {"task": "Test"}
    memory_id = memory.store_memory("task_history", content)
    
    # Retrieve
    retrieved = memory.retrieve_memory(memory_id)
    assert retrieved is not None
    assert retrieved["memory_id"] == memory_id


def test_vector_store_initialization():
    """Test vector store can be initialized."""
    vs = SimpleVectorStore(storage_path="./memory/vector_store/test/")
    assert vs is not None


def test_add_vector():
    """Test adding a vector to store."""
    vs = SimpleVectorStore(storage_path="./memory/vector_store/test/")
    
    embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    vector_id = vs.add_vector(
        memory_id="test_mem_001",
        text="Test vector",
        embedding=embedding
    )
    
    assert vector_id is not None
    assert isinstance(vector_id, str)
