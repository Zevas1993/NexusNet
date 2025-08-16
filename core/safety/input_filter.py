import re
from typing import List, Dict, Any

class InputFilter:
    def __init__(self):
        self.blocked_patterns = [
            r'(?i)\b(hack|exploit|malware|virus)\b',
            r'(?i)\b(password|secret|key)\s*[:=]\s*\w+',
            r'(?i)\b(ssn|social.*security)\b.*\d{3}-?\d{2}-?\d{4}',
        ]
        self.compiled_patterns = [re.compile(p) for p in self.blocked_patterns]
    
    def is_safe(self, text: str) -> Dict[str, Any]:
        """Check if input text is safe"""
        violations = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(text):
                violations.append({
                    'rule': i,
                    'description': 'Potentially unsafe content detected'
                })
        
        return {
            'safe': len(violations) == 0,
            'violations': violations,
            'filtered_text': self._filter_text(text) if violations else text
        }
    
    def _filter_text(self, text: str) -> str:
        """Filter out unsafe content"""
        filtered = text
        for pattern in self.compiled_patterns:
            filtered = pattern.sub('[FILTERED]', filtered)
        return filtered