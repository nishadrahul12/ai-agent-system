# Memory & Context Management System

## Overview
The memory system enables AI agents to store, retrieve, and learn from past interactions.

## Components

### 1. Long-Term Memory (`long_term_memory.py`)
- Persistent JSON-based storage
- Stores: tasks, entities, errors, best practices
- CRUD operations (Create, Read, Update, Delete)

### 2. Vector Store (`vector_store.py`)
- Semantic similarity search
- Cosine similarity algorithm
- Enables finding related memories by meaning

### 3. Memory Retriever (`memory_retriever.py`)
- Unified search interface
- Keyword search, semantic search, type filtering
- Returns relevant memories with context

### 4. Memory Summarizer (`memory_summarizer.py`)
- Compresses long interactions
- Calculates entity performance trends
- Generates memory reports

### 5. Memory Manager (`memory_manager.py`)
- Central coordinator for all operations
- Simple API for storing tasks, entities, errors, practices
- Statistics and monitoring

## File Structure
- `long_term/` - JSON storage files
- `vector_store/` - Embeddings and similarity data
- `summaries/` - Compressed summaries
- `memory_config.json` - Configuration
- `memory_schema.md` - Data structure documentation

## Usage Example
from memory_manager import MemoryManager

mm = MemoryManager()

Store task
task_id = mm.store_task_result(
task_name="Analyze KPIs",
agent="worker_telecom",
result="Analysis complete"
)

Store entity
mm.store_entity_knowledge(
entity_id="CELL_001",
entity_type="cell",
attributes={"location": "Downtown"}
)

Get statistics
stats = mm.get_memory_statistics()


## Next Steps
- Integrate with orchestrator
- Connect to LLM embeddings (OpenAI, HuggingFace)
- Add database backend (SQLite, PostgreSQL)
