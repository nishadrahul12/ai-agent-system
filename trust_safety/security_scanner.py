import re
from .typing import Dict, List, Any, Tuple
from .datetime import datetime
from .enum import Enum

class ThreatLevel(Enum):
    """Threat severity levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityScanner:
    """
    Detects security threats in requests and data.
    Prevents injection attacks, code execution exploits, etc.
    """
    
    def __init__(self):
        """Initialize security scanner with threat patterns."""
        self.threat_patterns = {
            "sql_injection": [
                r"('\s*(or|and)\s*'|;\s*drop|insert\s+into|update\s+set|delete\s+from)",
                r"union.*select|exec\s*\(",
            ],
            "code_injection": [
                r"import\s+os|__import__|exec\s*\(|eval\s*\(",
                r"subprocess\.|system\(|popen\(",
            ],
            "xss": [
                r"<script[^>]*>|javascript:",
                r"onerror\s*=|onclick\s*=",
            ],
            "path_traversal": [
                r"\.\./|\.\.\\",
                r"/etc/passwd|/windows/system",
            ],
            "command_injection": [
                r";\s*rm\s+|;\s*del\s+",
                r"\|\s*nc\s+|\|\s*bash",
            ]
        }
        
        self.dangerous_operations = [
            "delete_database",
            "drop_table",
            "modify_system",
            "access_credentials",
            "extract_all_data",
            "send_to_external"
        ]
    
    def scan_text(self, text: str) -> Dict[str, Any]:
        """
        Scan text for security threats.
        
        Args:
            text: Text to scan
            
        Returns:
            Security scan report
        """
        findings = []
        threat_level = ThreatLevel.SAFE
        risk_score = 0
        
        # Check for threat patterns
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    finding = {
                        "threat_type": threat_type,
                        "pattern": match.group(),
                        "position": match.start(),
                        "severity": "high"
                    }
                    findings.append(finding)
                    risk_score += 25
                    
                    if threat_level == ThreatLevel.SAFE or threat_level.value < ThreatLevel.CRITICAL.value:
                        threat_level = ThreatLevel.CRITICAL
        
        # Cap risk score
        risk_score = min(risk_score, 100)
        
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "findings_count": len(findings),
            "findings": findings,
            "threat_level": threat_level.value,
            "risk_score": risk_score,
            "is_safe": risk_score < 30
        }
    
    def scan_operation(self, operation: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Scan an operation for security issues.
        
        Args:
            operation: Operation name (e.g., "delete_database")
            params: Operation parameters
            
        Returns:
            Security assessment
        """
        threat_level = ThreatLevel.SAFE
        risk_score = 0
        issues = []
        
        # Check if operation is dangerous
        if operation in self.dangerous_operations:
            threat_level = ThreatLevel.CRITICAL
            risk_score = 90
            issues.append(f"Operation '{operation}' is flagged as dangerous")
        
        # Scan parameters for threats
        if params:
            params_text = str(params)
            param_scan = self.scan_text(params_text)
            
            if not param_scan["is_safe"]:
                risk_score = max(risk_score, param_scan["risk_score"])
                threat_level = ThreatLevel.CRITICAL if param_scan["risk_score"] > 70 else ThreatLevel.HIGH
                issues.extend([f["threat_type"] for f in param_scan["findings"]])
        
        return {
            "operation": operation,
            "threat_level": threat_level.value,
            "risk_score": risk_score,
            "issues": issues,
            "is_safe": risk_score < 30,
            "action": "BLOCK" if risk_score >= 85 else "ALLOW" if risk_score < 30 else "REVIEW"
        }
    
    def get_security_report(self, 
                           text: str = None, 
                           operation: str = None,
                           params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive security report."""
        reports = {}
        overall_risk = 0
        
        if text:
            reports["text_scan"] = self.scan_text(text)
            overall_risk = max(overall_risk, reports["text_scan"]["risk_score"])
        
        if operation:
            reports["operation_scan"] = self.scan_operation(operation, params)
            overall_risk = max(overall_risk, reports["operation_scan"]["risk_score"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "scans": reports,
            "overall_risk_score": overall_risk,
            "action": "BLOCK" if overall_risk >= 85 else "ALLOW" if overall_risk < 30 else "REVIEW"
        }


# Example usage
if __name__ == "__main__":
    scanner = SecurityScanner()
    
    # Test SQL injection
    malicious_text = "'; DROP TABLE users; --"
    report = scanner.get_security_report(text=malicious_text)
    print(f"Security report: {report}")
    
    # Test dangerous operation
    op_report = scanner.get_security_report(operation="delete_database", params={"db": "prod"})
    print(f"Operation report: {op_report}")
