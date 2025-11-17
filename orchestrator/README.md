# Orchestrator System

## Overview
The orchestrator is the central coordinator for all AI agents.

## Components

### 1. Agent (`agent.py`)
- Base Agent class
- Supervisor, Worker, Evaluator agent types
- Capability matching
- Task execution

### 2. Agent Registry (`agent_registry.py`)
- Tracks all agents
- Capability-based agent lookup
- Agent lifecycle management

### 3. Router (`router.py`)
- Routes tasks to best-matching agents
- Tracks routing decisions
- Load balancing

### 4. Task Queue (`task_queue.py`)
- Priority-based task queue
- Task lifecycle (pending → assigned → completed/failed)
- Handles 4 priority levels

### 5. Orchestrator (`orchestrator.py`)
- Main coordinator
- Initializes agents
- Processes task queue
- Manages system lifecycle

### 6. Config (`config.py`)
- Configuration management
- Loads from JSON files

## Usage
from orchestrator import Orchestrator

Initialize
orch = Orchestrator()

Add tasks
task_id = orch.add_task("Analyze KPIs", priority="high")

Process
results = orch.process_tasks()

Status
status = orch.get_orchestrator_status()


## Architecture
User Request
↓
Task Queue (priority-based)
↓
Router (capability matching)
↓
Agent Registry (find best agent)
↓
Agent Execution
↓
Result

undefined

