from typing import Dict, Any, Optional
from datetime import datetime
from privacy_checker import PrivacyChecker
from security_scanner import SecurityScanner
import json

class RiskEngine:
    """
    Comprehensive risk assessment combining privacy and security risks.
    Assigns risk scores and recommends actions.
    """
    
    def __init__(self):
        """Initialize risk engine."""
        self.privacy_checker = PrivacyChecker()
        self.security_scanner = SecurityScanner()
        self.risk_threshold_warning = 30
        self.risk_threshold_critical = 70
        self.risk_threshold_block = 85
        self.risk_history = []
    
    def assess_request(self, 
                      request_id: str,
                      content: str,
                      operation: str = None,
                      params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive risk assessment for a request.
        
        Args:
            request_id: Unique request identifier
            content: Request content to analyze
            operation: Operation being requested
            params: Operation parameters
            
        Returns:
            Risk assessment report
        """
        # Privacy check
        privacy_scan = self.privacy_checker.scan_text(content)
        privacy_risk = privacy_scan["risk_score"]
        
        # Security check
        security_report = self.security_scanner.get_security_report(
            text=content,
            operation=operation,
            params=params
        )
        security_risk = security_report["overall_risk_score"]
        
        # Calculate combined risk
        combined_risk = (privacy_risk * 0.4) + (security_risk * 0.6)
        combined_risk = min(combined_risk, 100)
        
        # Determine action
        if combined_risk >= self.risk_threshold_block:
            action = "BLOCK"
            reason = "Risk score exceeds critical threshold"
        elif combined_risk >= self.risk_threshold_critical:
            action = "ESCALATE"
            reason = "High risk - requires supervisor review"
        elif combined_risk >= self.risk_threshold_warning:
            action = "ALLOW_WITH_LOGGING"
            reason = "Elevated risk - monitor and log"
        else:
            action = "ALLOW"
            reason = "Risk within acceptable limits"
        
        assessment = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "risk_score": round(combined_risk, 1),
            "risk_components": {
                "privacy_risk": privacy_risk,
                "security_risk": security_risk
            },
            "privacy_findings": privacy_scan["findings"],
            "security_findings": security_report["scans"].get("text_scan", {}).get("findings", []),
            "action": action,
            "reason": reason,
            "approved": action != "BLOCK"
        }
        
        # Store in history
        self.risk_history.append(assessment)
        
        # Keep only last 1000 assessments
        if len(self.risk_history) > 1000:
            self.risk_history = self.risk_history[-1000:]
        
        return assessment
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get statistics on risk assessments."""
        if not self.risk_history:
            return {"message": "No risk assessments yet"}
        
        total = len(self.risk_history)
        blocked = sum(1 for r in self.risk_history if r["action"] == "BLOCK")
        escalated = sum(1 for r in self.risk_history if r["action"] == "ESCALATE")
        allowed = sum(1 for r in self.risk_history if r["action"] == "ALLOW")
        
        avg_risk = sum(r["risk_score"] for r in self.risk_history) / total
        
        return {
            "total_assessments": total,
            "blocked": blocked,
            "escalated": escalated,
            "allowed": allowed,
            "average_risk_score": round(avg_risk, 1),
            "block_rate": round((blocked / total) * 100, 1)
        }


# Example usage
if __name__ == "__main__":
    engine = RiskEngine()
    
    # Test safe request
    safe_assessment = engine.assess_request(
        request_id="req_001",
        content="Analyze Q3 sales data",
        operation="analyze"
    )
    print(f"Safe request: {safe_assessment}")
    
    # Test risky request
    risky_assessment = engine.assess_request(
        request_id="req_002",
        content="Delete all customer records from john.doe@example.com",
        operation="delete_database",
        params={"table": "customers"}
    )
    print(f"Risky request: {risky_assessment}")
    
    # Statistics
    stats = engine.get_risk_statistics()
    print(f"Risk statistics: {stats}")
