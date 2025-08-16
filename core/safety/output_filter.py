import re
from typing import Dict, Any

class OutputFilter:
    def __init__(self):
        self.sensitive_patterns = [
            r'(?i)\b\d{3}-?\d{2}-?\d{4}\b',  # SSN
            r'(?i)\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'(?i)\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        ]
        self.compiled_patterns = [re.compile(p) for p in self.sensitive_patterns]
    
    def sanitize(self, text: str) -> Dict[str, Any]:
        """Sanitize output text"""
        sanitized = text
        redactions = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                redactions.extend(matches)
                sanitized = pattern.sub('[REDACTED]', sanitized)
        
        return {
            'sanitized_text': sanitized,
            'redactions_count': len(redactions),
            'original_length': len(text),
            'sanitized_length': len(sanitized)
        }