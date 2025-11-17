import re
from .typing import Dict, List, Any, Tuple
from .datetime import datetime

class PrivacyChecker:
    """
    Detects personally identifiable information (PII) in text.
    Masks sensitive data to prevent leaks.
    """
    
    def __init__(self):
        """Initialize privacy checker with PII patterns."""
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            "api_key": r'\b(sk_live|sk_test|pk_live|pk_test)_[A-Za-z0-9]{20,}\b',
            "password": r'(password|passwd|pwd)\s*[:=]\s*[^\s]+',
            "token": r'\b(token|auth|bearer)\s+[A-Za-z0-9\._\-]{20,}\b'
        }
        
        self.sensitive_keywords = {
            "confidential": 10,
            "internal": 8,
            "secret": 12,
            "classified": 15,
            "private": 7,
            "restricted": 9
        }
    
    def scan_text(self, text: str) -> Dict[str, Any]:
        """
        Scan text for PII.
        
        Args:
            text: Text to scan
            
        Returns:
            Privacy scan report
        """
        findings = []
        risk_score = 0
        
        # Check for PII patterns
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                finding = {
                    "pii_type": pii_type,
                    "value": match.group(),
                    "position": match.start(),
                    "severity": "high"
                }
                findings.append(finding)
                risk_score += 15  # Each PII finding adds 15 points
        
        # Check for sensitive keywords
        for keyword, weight in self.sensitive_keywords.items():
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                findings.append({
                    "pii_type": "sensitive_keyword",
                    "value": keyword,
                    "severity": "medium"
                })
                risk_score += weight
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        return {
            "scan_timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "findings_count": len(findings),
            "findings": findings,
            "risk_score": risk_score,
            "contains_pii": len(findings) > 0,
            "is_safe": risk_score < 30
        }
    
    def mask_pii(self, text: str) -> str:
        """
        Mask PII in text.
        
        Args:
            text: Text to mask
            
        Returns:
            Masked text
        """
        masked_text = text
        
        # Mask emails
        masked_text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            lambda m: m.group(0)[0] + '***@' + m.group(0).split('@')[1],
            masked_text,
            flags=re.IGNORECASE
        )
        
        # Mask phone numbers
        masked_text = re.sub(
            r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            '+1-***-***-****',
            masked_text
        )
        
        # Mask SSN
        masked_text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '***-**-****',
            masked_text
        )
        
        # Mask credit cards
        masked_text = re.sub(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            '****-****-****-****',
            masked_text
        )
        
        # Mask API keys
        masked_text = re.sub(
            r'\b(sk_live|sk_test|pk_live|pk_test)_[A-Za-z0-9]{20,}\b',
            r'\1_***',
            masked_text
        )
        
        return masked_text
    
    def get_privacy_report(self, text: str) -> Dict[str, Any]:
        """Get comprehensive privacy report."""
        scan = self.scan_text(text)
        masked = self.mask_pii(text)
        
        return {
            "scan": scan,
            "masked_text": masked,
            "privacy_action": "BLOCK" if not scan["is_safe"] else "ALLOW"
        }


# Example usage
if __name__ == "__main__":
    checker = PrivacyChecker()
    
    # Test text with PII
    test_text = "Send report to john.doe@example.com at +1-555-123-4567. SSN: 123-45-6789"
    
    report = checker.get_privacy_report(test_text)
    print(f"Privacy report: {report}")
