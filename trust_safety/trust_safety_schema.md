# Trust & Safety System Schema

## Risk Scoring

### Risk Score Levels
- **0-20**: Safe - Proceed normally
- **21-50**: Low Risk - Monitor and log
- **51-75**: Medium Risk - Require review
- **76-85**: High Risk - Escalate to supervisor
- **86-100**: Critical Risk - Block and alert

### Risk Score Breakdown
{
"request_id": "req_20251117_001",
"timestamp": "2025-11-17T16:00:00Z",
"risk_score": 45,
"risk_level": "low_risk",
"components": {
"privacy_risk": {
"score": 20,
"issues": ["Contains email address"]
},
"security_risk": {
"score": 15,
"issues": ["Potential SQL injection pattern"]
},
"content_risk": {
"score": 10,
"issues": ["Mentions confidential data"]
}
},
"recommendation": "LOG_AND_PROCEED",
"action": "ALLOW"
}


## Privacy Violations

### PII Detection
{
"pii_type": "email",
"pattern": "john.doe@example.com",
"context": "Send report to john.doe@example.com",
"severity": "high",
"action": "MASK"
}


### Masking Examples
- Email: `john.doe@example.com` → `j***@example.com`
- Phone: `+1-555-123-4567` → `+1-555-***-****`
- SSN: `123-45-6789` → `***-**-6789`
- API Key: `sk_live_51ABC...` → `sk_***`

## Security Threats

### Injection Attack Patterns
- SQL Injection: `'; DROP TABLE users; --`
- Code Injection: `import os; os.system('rm -rf /')`
- Command Injection: `| rm -rf /tmp`

### Detection Action
{
"threat_type": "sql_injection",
"severity": "critical",
"pattern_matched": "'; DROP TABLE",
"action": "BLOCK",
"reason": "SQL injection detected in query"
}


## Supervisor Self-Repair

### Failure Detection
{
"agent_id": "worker_001",
"task_id": "task_123",
"failure_reason": "Agent returned inconsistent results",
"drift_detected": true,
"repair_initiated": true,
"repair_strategy": "prompt_adjustment",
"steps": [
"Adjust system prompt for clarity",
"Retry with modified instructions",
"Validate output against baseline",
"If still failing, escalate to supervisor"
]
}


### Repair Strategies
1. **Prompt Adjustment**: Modify agent instructions
2. **Agent Swap**: Switch to different agent
3. **Task Delegation**: Break task into smaller parts
4. **Escalation**: Ask supervisor for help

## Safety Guardrails

### Action Categories
- **Safe**: Proceed normally (analysis, reporting, retrieval)
- **Review**: Require approval (deletion, modification, external calls)
- **Block**: Prevent execution (dangerous code, data extraction, system access)

### Examples
{
"action": "Delete customer records",
"category": "dangerous",
"guardrail": "BLOCK",
"reason": "Destructive operation requires explicit approval",
"required_approval": true
}

undefined