from .typing import Dict, Any, Optional, List
from .datetime import datetime
from .enum import Enum

class RepairStrategy(Enum):
    """Available repair strategies."""
    PROMPT_ADJUSTMENT = "prompt_adjustment"
    AGENT_SWAP = "agent_swap"
    TASK_DELEGATION = "task_delegation"
    ESCALATION = "escalation"

class SupervisorRepairBrain:
    """
    Detects agent failures and auto-repairs systems.
    Implements self-healing mechanisms.
    """
    
    def __init__(self):
        """Initialize supervisor repair brain."""
        self.failure_history: List[Dict[str, Any]] = []
        self.repair_attempts: List[Dict[str, Any]] = []
        self.max_retry_attempts = 3
        self.repair_strategies = [
            RepairStrategy.PROMPT_ADJUSTMENT,
            RepairStrategy.AGENT_SWAP,
            RepairStrategy.TASK_DELEGATION,
            RepairStrategy.ESCALATION
        ]
    
    def detect_failure(self, 
                      agent_id: str, 
                      task_id: str,
                      failure_reason: str,
                      metrics: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Detect agent failure.
        
        Args:
            agent_id: ID of failing agent
            task_id: ID of failing task
            failure_reason: Description of failure
            metrics: Performance metrics
            
        Returns:
            Failure detection report
        """
        failure = {
            "failure_id": f"fail_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_id": agent_id,
            "task_id": task_id,
            "reason": failure_reason,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat(),
            "severity": self._assess_severity(failure_reason, metrics),
            "repair_required": True
        }
        
        self.failure_history.append(failure)
        
        return failure
    
    def _assess_severity(self, reason: str, metrics: Dict[str, float] = None) -> str:
        """Assess failure severity."""
        if "critical" in reason.lower() or "crash" in reason.lower():
            return "critical"
        elif "timeout" in reason.lower() or "slow" in reason.lower():
            return "high"
        else:
            return "medium"
    
    def initiate_repair(self, 
                       failure_id: str, 
                       agent_id: str,
                       task_id: str) -> Dict[str, Any]:
        """
        Initiate repair for a failed agent.
        
        Args:
            failure_id: ID of failure
            agent_id: ID of agent to repair
            task_id: ID of task to retry
            
        Returns:
            Repair plan
        """
        repair_plan = {
            "repair_id": f"repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "failure_id": failure_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "strategies": [],
            "current_strategy_index": 0,
            "retry_count": 0,
            "max_retries": self.max_retry_attempts,
            "status": "initiated"
        }
        
        # Build repair strategy sequence
        repair_plan["strategies"] = [
            {
                "order": 1,
                "strategy": RepairStrategy.PROMPT_ADJUSTMENT.value,
                "description": "Adjust agent system prompt for clarity",
                "parameters": {"clarity_level": 0.9}
            },
            {
                "order": 2,
                "strategy": RepairStrategy.AGENT_SWAP.value,
                "description": "Switch to backup agent",
                "parameters": {"backup_agent": f"{agent_id}_backup"}
            },
            {
                "order": 3,
                "strategy": RepairStrategy.TASK_DELEGATION.value,
                "description": "Break task into subtasks",
                "parameters": {"subtask_count": 3}
            },
            {
                "order": 4,
                "strategy": RepairStrategy.ESCALATION.value,
                "description": "Escalate to human supervisor",
                "parameters": {"alert_level": "critical"}
            }
        ]
        
        self.repair_attempts.append(repair_plan)
        
        return repair_plan
    
    def execute_repair_step(self, repair_id: str, strategy_index: int) -> Dict[str, Any]:
        """
        Execute a repair step.
        
        Args:
            repair_id: ID of repair plan
            strategy_index: Index of strategy to execute
            
        Returns:
            Repair step result
        """
        # Find repair plan
        repair_plan = None
        for plan in self.repair_attempts:
            if plan["repair_id"] == repair_id:
                repair_plan = plan
                break
        
        if not repair_plan:
            return {"error": "Repair plan not found"}
        
        if strategy_index >= len(repair_plan["strategies"]):
            return {"error": "Strategy index out of range"}
        
        strategy = repair_plan["strategies"][strategy_index]
        
        result = {
            "repair_id": repair_id,
            "strategy": strategy["strategy"],
            "status": "executed",
            "timestamp": datetime.now().isoformat(),
            "outcome": self._simulate_repair_outcome(strategy["strategy"]),
            "next_action": self._determine_next_action(strategy_index, len(repair_plan["strategies"]))
        }
        
        return result
    
    def _simulate_repair_outcome(self, strategy: str) -> str:
        """Simulate repair outcome."""
        outcomes = {
            "prompt_adjustment": "success_70_percent",
            "agent_swap": "success_85_percent",
            "task_delegation": "success_80_percent",
            "escalation": "pending_human_review"
        }
        return outcomes.get(strategy, "unknown")
    
    def _determine_next_action(self, current_index: int, total_strategies: int) -> str:
        """Determine next action after repair step."""
        if current_index + 1 < total_strategies:
            return f"Execute strategy {current_index + 2}"
        else:
            return "Escalate to human supervisor"
    
    def get_repair_history(self) -> Dict[str, Any]:
        """Get repair history and statistics."""
        successful_repairs = sum(
            1 for r in self.repair_attempts 
            if "success" in r.get("status", "").lower()
        )
        
        return {
            "total_failures": len(self.failure_history),
            "repair_attempts": len(self.repair_attempts),
            "successful_repairs": successful_repairs,
            "failure_types": list(set(f["reason"] for f in self.failure_history)),
            "recent_failures": self.failure_history[-5:] if self.failure_history else []
        }


# Example usage
if __name__ == "__main__":
    supervisor = SupervisorRepairBrain()
    
    # Detect failure
    failure = supervisor.detect_failure(
        agent_id="agent_001",
        task_id="task_123",
        failure_reason="Agent returned inconsistent results",
        metrics={"quality_score": 0.45, "expected": 0.90}
    )
    print(f"Failure detected: {failure}")
    
    # Initiate repair
    repair_plan = supervisor.initiate_repair(
        failure_id=failure["failure_id"],
        agent_id="agent_001",
        task_id="task_123"
    )
    print(f"Repair plan: {repair_plan}")
    
    # Execute repair step
    result = supervisor.execute_repair_step(repair_plan["repair_id"], 0)
    print(f"Repair result: {result}")
    
    # Get history
    history = supervisor.get_repair_history()
    print(f"History: {history}")
