"""
Test memory system functionality.
"""
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.long_term_memory import LongTermMemory
from memory.vector_store import SimpleVectorStore


class TestMemory:
    """Memory tests using temporary directories."""
    
    @classmethod
    def setup_class(cls):
        """Create temp directory for all tests."""
        cls.temp_dir = tempfile.mkdtemp()
    
    @classmethod
    def teardown_class(cls):
        """Clean up temp directory."""
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def test_long_term_memory_initialization(self):
        """Test memory system can be initialized."""
        storage_path = os.path.join(self.temp_dir, "long_term_test")
        memory = LongTermMemory(storage_path=storage_path)
        assert memory is not None
    
    def test_store_memory(self):
        """Test storing a memory."""
        storage_path = os.path.join(self.temp_dir, "long_term_store")
        memory = LongTermMemory(storage_path=storage_path)
        
        content = {
            "task_name": "Test task",
            "result": "Success"
        }
        
        memory_id = memory.store_memory("task_history", content)
        assert memory_id is not None
        assert isinstance(memory_id, str)
    
    def test_retrieve_memory(self):
        """Test retrieving a stored memory."""
        storage_path = os.path.join(self.temp_dir, "long_term_retrieve")
        memory = LongTermMemory(storage_path=storage_path)
        
        # Store
        content = {"task": "Test"}
        memory_id = memory.store_memory("task_history", content)
        
        # Retrieve
        retrieved = memory.retrieve_memory(memory_id)
        assert retrieved is not None
        assert retrieved["memory_id"] == memory_id
    
    def test_vector_store_initialization(self):
        """Test vector store can be initialized."""
        storage_path = os.path.join(self.temp_dir, "vector_store_test")
        vs = SimpleVectorStore(storage_path=storage_path)
        assert vs is not None
    
    def test_add_vector(self):
        """Test adding a vector to store."""
        storage_path = os.path.join(self.temp_dir, "vector_store_add")
        vs = SimpleVectorStore(storage_path=storage_path)
        
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        vector_id = vs.add_vector(
            memory_id="test_mem_001",
            text="Test vector",
            embedding=embedding
        )
        
        assert vector_id is not None
        assert isinstance(vector_id, str)
