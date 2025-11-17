# Memory System Schema

## Overview
The memory system stores and retrieves contextual information for agents.

## Memory Structure

### 1. Task History Memory
{
"memory_type": "task_history",
"memory_id": "task_20251117_001",
"task_name": "Analyze Q3 KPIs",
"timestamp": "2025-11-17T14:30:00Z",
"agent": "worker_telecom",
"input": "Analyze cell performance metrics",
"output": "KPI analysis with trends",
"outcome": "success",
"duration_ms": 1234,
"confidence": 0.95,
"metadata": {
"cells_analyzed": ["CELL_A_01", "CELL_A_02"],
"dataset_version": "v1.0"
}
}


### 2. Entity Knowledge Memory
{
"memory_type": "entity_knowledge",
"memory_id": "entity_20251117_cell_a_01",
"entity_type": "cell",
"entity_id": "CELL_A_01",
"attributes": {
"location": "Downtown Tower A, Sector 1",
"technology": "5G SA",
"power_class": "Macro",
"last_optimization": "2025-10-20"
},
"performance_history": [
{
"date": "2025-11-15",
"sinr_avg": 15.2,
"throughput_mbps": 450.5
}
],
"timestamp": "2025-11-17T14:30:00Z"
}


### 3. Error Log Memory
{
"memory_type": "error_log",
"memory_id": "error_20251117_001",
"timestamp": "2025-11-17T10:15:00Z",
"agent": "worker_generic",
"error_type": "API_TIMEOUT",
"error_message": "API call exceeded 30 second timeout",
"task_id": "task_20251117_002",
"attempted_solution": "Retried with backoff",
"resolution": "success",
"lesson_learned": "Reduce batch size for API calls"
}


### 4. Best Practices Memory
{
"memory_type": "best_practices",
"memory_id": "practice_20251117_001",
"title": "Optimal Cell Analysis Workflow",
"description": "Proven approach for analyzing telecom cells",
"steps": [
"Query memory for recent cell metrics (< 7 days)",
"If data stale, trigger new data fetch",
"Normalize metrics to standard scale",
"Perform anomaly detection",
"Generate 3 ranked recommendations"
],
"success_rate": 0.92,
"use_cases": ["kpi_analysis", "optimization"],
"created_date": "2025-10-01",
"last_used": "2025-11-16"
}


## Vector Store Schema
{
"vector_id": "vec_20251117_001",
"memory_id": "task_20251117_001",
"embedding": [0.234, -0.156, 0.891, ...],
"text": "Analyzed Q3 telecom KPIs for 5G cells",
"metadata": {
"memory_type": "task_history",
"timestamp": "2025-11-17T14:30:00Z"
}
}


## Retention Policy
- Task History: 90 days active, archive after 1 year
- Entity Knowledge: Permanent (update as needed)
- Error Logs: 30 days, archive after 90 days
- Best Practices: Permanent
