# Orchestrator System Schema

## Overview
The orchestrator coordinates multiple AI agents, routes tasks, and manages their lifecycle.

## Agent Types
{
"agent_id": "agent_123",
"agent_type": "supervisor",
"name": "Main Supervisor",
"capability": ["task_decomposition", "delegation", "monitoring"],
"status": "active",
"created_at": "2025-11-17T15:00:00Z"
}


## Task Structure
{
"task_id": "task_20251117_001",
"user_request": "Analyze Q3 telecom KPIs",
"priority": "high",
"assigned_agent": "supervisor_01",
"subtasks": [
{
"subtask_id": "subtask_001",
"description": "Extract KPI data",
"assigned_to": "worker_telecom",
"status": "pending"
}
],
"created_at": "2025-11-17T15:00:00Z",
"deadline": "2025-11-17T16:00:00Z"
}


## Agent Capabilities Mapping
supervisor → task_decomposition, delegation, monitoring
worker_generic → general_task_execution, tool_usage
worker_telecom → telecom_analysis, kpi_extraction, optimization
evaluator → quality_scoring, validation, feedback
safety_filter → risk_detection, privacy_check, security_scan
memory_retriever → context_search, memory_query, summarization
tool_executor → api_calls, file_io, code_execution


## Task Routing Rules
1. **Priority-based**: Critical tasks → Supervisor immediately
2. **Capability-based**: Match task keywords to agent capabilities
3. **Load-based**: Route to least busy agent
4. **Fallback**: If no match, use worker_generic

## Agent Lifecycle States
Initializing → Active → Processing → Idle → Completed/Failed


## Communication Protocol
- Agent → Agent: Message passing via orchestrator
- Agent → Memory: Direct access to memory system
- Agent → Tools: Via tool_executor agent
- Agent → Supervisor: Status updates every 5 seconds
