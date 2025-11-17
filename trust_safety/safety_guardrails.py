from .typing import Dict, List, Any, Optional
from .datetime import datetime
from .enum import Enum

class ActionCategory(Enum):
    """Action safety categories."""
    SAFE = "safe"
    REVIEW = "review"
    BLOCK = "block"

class SafetyGuardrails:
    """
    Implements safety guardrails to prevent dangerous operations.
    Maintains audit logs of all actions.
    """
    
    def __init__(self):
        """Initialize safety guardrails."""
        self.safe_actions = [
            "read_data", "analyze_data", "generate_report",
            "query_database", "retrieve_information", "search"
        ]
        
        self.review_actions = [
            "modify_data", "update_record", "export_data",
            "send_notification", "create_alert", "schedule_task"
        ]
        
        self.dangerous_actions = [
            "delete_data", "drop_table", "modify_system_settings",
            "access_credentials", "execute_code", "modify_permissions",
            "delete_backup", "disable_monitoring", "export_all_data"
        ]
        
        self.audit_log: List[Dict[str, Any]] = []
        self.blocked_actions: List[Dict[str, Any]] = []
    
    def classify_action(self, action: str) -> ActionCategory:
        """
        Classify an action by safety level.
        
        Args:
            action: Action to classify
            
        Returns:
            ActionCategory
        """
        action_lower = action.lower()
        
        if action_lower in self.dangerous_actions:
            return ActionCategory.BLOCK
        elif action_lower in self.review_actions:
            return ActionCategory.REVIEW
        elif action_lower in self.safe_actions:
            return ActionCategory.SAFE
        else:
            # Unknown action - err on side of caution
            return ActionCategory.REVIEW
    
    def evaluate_action(self, 
                       agent_id: str,
                       action: str,
                       params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate if action should be allowed.
        
        Args:
            agent_id: Agent requesting action
            action: Action to evaluate
            params: Action parameters
            
        Returns:
            Evaluation result
        """
        category = self.classify_action(action)
        
        evaluation = {
            "action_id": f"act_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_id": agent_id,
            "action": action,
            "category": category.value,
            "timestamp": datetime.now().isoformat(),
            "allowed": category != ActionCategory.BLOCK,
            "requires_approval": category == ActionCategory.REVIEW or category == ActionCategory.BLOCK,
            "reason": self._get_action_reason(category),
            "parameters": params or {}
        }
        
        # Log action
        self.audit_log.append(evaluation)
        
        # Track blocked actions
        if not evaluation["allowed"]:
            self.blocked_actions.append(evaluation)
        
        return evaluation
    
    def _get_action_reason(self, category: ActionCategory) -> str:
        """Get reason for action classification."""
        reasons = {
            ActionCategory.SAFE: "Action is safe and can proceed",
            ActionCategory.REVIEW: "Action requires review before approval",
            ActionCategory.BLOCK: "Action is dangerous and blocked"
        }
        return reasons.get(category, "Unknown category")
    
    def request_approval(self, 
                        action_id: str,
                        approver_id: str,
                        approved: bool,
                        notes: str = "") -> Dict[str, Any]:
        """
        Request approval for a blocked/review action.
        
        Args:
            action_id: ID of action to approve
            approver_id: ID of approver
            approved: Whether action is approved
            notes: Optional approval notes
            
        Returns:
            Approval result
        """
        # Find action in audit log
        action = None
        for log_entry in self.audit_log:
            if log_entry["action_id"] == action_id:
                action = log_entry
                break
        
        if not action:
            return {"error": "Action not found"}
        
        approval = {
            "action_id": action_id,
            "approver_id": approver_id,
            "approved": approved,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "action_allowed": approved
        }
        
        # Log approval
        self.audit_log.append(approval)
        
        return approval
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:] if self.audit_log else []
    
    def get_blocked_actions(self) -> List[Dict[str, Any]]:
        """Get all blocked actions."""
        return self.blocked_actions
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """Get safety statistics."""
        total_actions = len(self.audit_log)
        blocked = len(self.blocked_actions)
        safe_actions = sum(
            1 for log in self.audit_log 
            if log.get("category") == "safe"
        )
        review_actions = sum(
            1 for log in self.audit_log 
            if log.get("category") == "review"
        )
        
        return {
            "total_actions_evaluated": total_actions,
            "safe": safe_actions,
            "review": review_actions,
            "blocked": blocked,
            "block_rate": round((blocked / total_actions * 100) if total_actions > 0 else 0, 1)
        }


# Example usage
if __name__ == "__main__":
    guardrails = SafetyGuardrails()
    
    # Test safe action
    safe_eval = guardrails.evaluate_action(
        agent_id="agent_001",
        action="read_data",
        params={"table": "users"}
    )
    print(f"Safe action: {safe_eval}")
    
    # Test dangerous action
    dangerous_eval = guardrails.evaluate_action(
        agent_id="agent_002",
        action="delete_data",
        params={"table": "users", "where": "1=1"}
    )
    print(f"Dangerous action: {dangerous_eval}")
    
    # Get statistics
    stats = guardrails.get_safety_statistics()
    print(f"Safety stats: {stats}")
