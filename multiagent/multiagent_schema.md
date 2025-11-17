# Multi-Agent System Schema

## Message Protocol

### Message Structure
{
"message_id": "msg_20251117_001_a1b2c3d4",
"sender_id": "agent_123",
"receiver_id": "agent_456",
"message_type": "request",
"timestamp": "2025-11-17T16:00:00Z",
"priority": "high",
"payload": {
"action": "analyze_kpi",
"data": {...}
},
"context": {
"task_id": "task_001",
"parent_message_id": "msg_20251117_000"
},
"status": "sent"
}


### Message Types
- `request` — Agent A asks Agent B to do something
- `response` — Agent B responds to Agent A
- `broadcast` — Agent sends to all agents
- `health_check` — System checks if agent is alive
- `error` — Agent reports an error

### Message Status Flow
Created → Queued → Sent → Delivered → Processed/Failed


## Drift Detection

### What is Drift?
When an agent's behavior changes unexpectedly:
- Output quality decreases
- Response time increases
- Error rate goes up
- Decisions become inconsistent

### Drift Metrics
{
"agent_id": "agent_123",
"timestamp": "2025-11-17T16:00:00Z",
"metrics": {
"output_quality": {
"baseline": 0.92,
"current": 0.85,
"drift_score": 0.07
},
"response_time": {
"baseline_ms": 1200,
"current_ms": 2500,
"drift_score": 1.08
},
"error_rate": {
"baseline": 0.02,
"current": 0.08,
"drift_score": 0.06
}
},
"overall_drift_score": 0.27,
"drifted": true,
"alert_level": "warning"
}


## Reliability Monitoring

### Health Check
{
"agent_id": "agent_123",
"timestamp": "2025-11-17T16:00:00Z",
"status": "healthy",
"metrics": {
"uptime_percent": 99.8,
"task_success_rate": 0.94,
"avg_response_time_ms": 1234,
"memory_usage_mb": 245,
"error_count_last_hour": 2
},
"alerts": []
}


### Health Status Levels
- `healthy` — All metrics normal
- `degraded` — Some metrics below threshold
- `critical` — Multiple failures detected
- `offline` — Agent not responding

## Workflow Coordination

### Workflow Structure
{
"workflow_id": "wf_20251117_001",
"name": "Multi-Step KPI Analysis",
"tasks": [
{
"step": 1,
"assigned_agent": "worker_telecom",
"task": "Extract KPI data",
"dependencies": [],
"status": "completed"
},
{
"step": 2,
"assigned_agent": "worker_generic",
"task": "Analyze trends",
"dependencies":,​
"status": "in_progress"
},
{
"step": 3,
"assigned_agent": "evaluator",
"task": "Quality check",
"dependencies":,​
"status": "pending"
}
],
"created_at": "2025-11-17T15:00:00Z",
"status": "in_progress"
}


### Task Dependencies
- Step 1 must complete before Step 2 starts
- Step 2 must complete before Step 3 starts
- Enables complex multi-step workflows
