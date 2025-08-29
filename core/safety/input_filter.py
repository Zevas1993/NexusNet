
from __future__ import annotations
import re
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

# PII Detection Patterns
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
SSN_RE = re.compile(r"\d{3}-?\d{2}-?\d{4}")
CREDIT_CARD_RE = re.compile(r"\d{4}-?\d{4}-?\d{4}-?\d{4}")
IP_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
API_KEY_RE = re.compile(r"(?i)(api[_-]?key|apikey|token|secret)(\s*[=:]\s*)['\"]([^'\"]*)['\"]")
CREDENTIAL_RE = re.compile(r"(?i)(password|passwd|pwd|credential)\s*[=:]\s*['\"]([^'\"]*)['\"]")

# Content Safety Patterns
INJURIOUS_PATTERNS = [
    r"\b(harm|hurt|damage|kill|injure)\s+(my|your)?self\b",
    r"\bsuicide|attempting\s+suicide\b",
    r"\bsexual\s+(abuse|assault|harassment)\b",
    r"\bviolence|violent crime|criminal activity\b",
    r"\billegal activity|breaking law\b",
]

MALICIOUS_PATTERNS = [
    r"\b(hack|breach|exploit|malware|virus)\b",
    r"\b unauthorized access|identity theft\b",
    r"\b(steal|fraud|falsify|forgery)\b",
    r"\bspam|phishing|scam\b",
]

class InputSafetyFilter:
    """Advanced input filtering with comprehensive safety checks"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pii_detected = 0
        self.injurious_detected = 0
        self.malicious_detected = 0

    def enforce_length(self, text: str, max_chars: int) -> str:
        """Enforce maximum input length"""
        if len(text) > max_chars:
            logger.warning(f"Input truncated from {len(text)} to {max_chars} characters")
            return text[:max_chars]
        return text

    def redact_pii(self, text: str, enabled: bool = True) -> str:
        """Redact personally identifiable information"""
        if not enabled:
            return text

        original_text = text
        replacements = []

        # Email addresses
        for match in EMAIL_RE.finditer(text):
            redacted = "[EMAIL-REDACTED]"
            text = text.replace(match.group(), redacted)
            replacements.append(("email", match.group(), redacted))

        # Phone numbers
        for match in PHONE_RE.finditer(text):
            redacted = "[PHONE-REDACTED]"
            text = text.replace(match.group(), redacted)
            replacements.append(("phone", match.group(), redacted))

        # Social Security Numbers
        for match in SSN_RE.finditer(text):
            redacted = "[SSN-REDACTED]"
            text = text.replace(match.group(), redacted)
            replacements.append(("ssn", match.group(), redacted))

        # Credit card numbers
        for match in CREDIT_CARD_RE.finditer(text):
            redacted = "[CARD-REDACTED]"
            text = text.replace(match.group(), redacted)
            replacements.append(("credit_card", match.group(), redacted))

        # IP addresses
        for match in IP_RE.finditer(text):
            redacted = "[IP-REDACTED]"
            text = text.replace(match.group(), redacted)
            replacements.append(("ip", match.group(), redacted))

        # API keys and credentials
        for match in API_KEY_RE.finditer(text):
            redacted = "[API-KEY-REDACTED]"
            text = text.replace(match.group(3), redacted)

        for match in CREDENTIAL_RE.finditer(text):
            redacted = "[CREDENTIAL-REDACTED]"
            text = text.replace(match.group(2), redacted)

        if len(replacements) > 0:
            self.pii_detected += len(replacements)
            logger.info(f"Redacted {len(replacements)} PII elements")

        return text

    def detect_injurious_content(self, text: str) -> Dict[str, Any]:
        """Detect potentially harmful or injurious content"""
        findings = []

        for pattern in INJURIOUS_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings.extend([(pattern, match) for match in matches])

        if findings:
            self.injurious_detected += len(findings)
            logger.warning(f"Detected {len(findings)} potentially injurious content patterns")

        return {
            "injurious_detected": len(findings) > 0,
            "findings": findings,
            "severity": "HIGH" if len(findings) > 2 else "MEDIUM" if findings else "LOW"
        }

    def detect_malicious_intent(self, text: str) -> Dict[str, Any]:
        """Detect potential malicious or harmful intent"""
        findings = []

        for pattern in MALICIOUS_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings.extend([(pattern, match) for match in matches])

        if findings:
            self.malicious_detected += len(findings)
            logger.warning(f"Detected {len(findings)} potentially malicious content patterns")

        return {
            "malicious_detected": len(findings) > 0,
            "findings": findings,
            "severity": "CRITICAL" if len(findings) > 3 else "HIGH" if len(findings) > 1 else "MEDIUM" if findings else "LOW"
        }

    def validate_content_policy(self, text: str, policy_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive content validation against policies"""
        if policy_config is None:
            policy_config = {
                "block_injurious_content": True,
                "block_malicious_content": True,
                "max_consecutive_repeats": 50,
                "block_gibberish": True,
                "min_content_words": 3
            }

        results = {
            "approved": True,
            "violations": [],
            "warnings": [],
            "metadata": {}
        }

        # Check length
        word_count = len(text.split())
        if word_count < policy_config.get("min_content_words", 0):
            results["violations"].append("Content too short")
            results["approved"] = False

        # Check for repetitive content
        if len(text) > policy_config.get("max_consecutive_repeats", 50):
            # Simple repeat detection - could be enhanced
            char_counts = {}
            max_consecutive = 0
            current_char = ''
            current_count = 0
            for char in text:
                if char == current_char:
                    current_count += 1
                else:
                    max_consecutive = max(max_consecutive, current_count)
                    current_char = char
                    current_count = 1

            if max_consecutive > policy_config.get("max_consecutive_repeats", 50):
                results["violations"].append("Excessive repetitive content")
                results["approved"] = False

        # Check for gibberish (very basic heuristic)
        if policy_config.get("block_gibberish", True):
            # More sophisticated gibberish detection would use ML models
            alphanumeric_ratio = sum(1 for c in text if c.isalnum()) / len(text) if text else 0
            if alphanumeric_ratio < 0.3:
                results["violations"].append("High non-alphanumeric content (possible gibberish)")
                results["approved"] = False

        return results

    def get_safety_stats(self) -> Dict[str, int]:
        """Get safety filter statistics"""
        return {
            "pii_detected": self.pii_detected,
            "injurious_detected": self.injurious_detected,
            "malicious_detected": self.malicious_detected
        }

    def reset_stats(self):
        """Reset safety statistics"""
        self.pii_detected = 0
        self.injurious_detected = 0
        self.malicious_detected = 0


# Global instance for backward compatibility
_filter_instance = InputSafetyFilter()

def enforce_length(text: str, max_chars: int) -> str:
    """Legacy function for backward compatibility"""
    return _filter_instance.enforce_length(text, max_chars)

def redact_pii(text: str, enabled: bool = True) -> str:
    """Legacy function for backward compatibility"""
    return _filter_instance.redact_pii(text, enabled)

def comprehensive_input_filter(text: str,
                             max_chars: int = 8000,
                             pii_redaction: bool = True,
                             safety_checks: bool = True,
                             policy_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Comprehensive input filtering pipeline"""
    filtered_text = text

    # Length enforcement
    filtered_text = _filter_instance.enforce_length(filtered_text, max_chars)

    # PII redaction
    if pii_redaction:
        filtered_text = _filter_instance.redact_pii(filtered_text)

    # Safety analysis
    safety_results = {}
    if safety_checks:
        safety_results["injurious"] = _filter_instance.detect_injurious_content(filtered_text)
        safety_results["malicious"] = _filter_instance.detect_malicious_intent(filtered_text)
        safety_results["policy"] = _filter_instance.validate_content_policy(filtered_text, policy_config)

    return {
        "original_text": text,
        "filtered_text": filtered_text,
        "length_enforced": len(filtered_text) < len(text) if len(text) > max_chars else False,
        "pii_redacted": filtered_text != text if pii_redaction else False,
        "safety_analysis": safety_results,
        "approved": all(not result.get("injurious_detected", False) and not result.get("malicious_detected", False) and result.get("approved", True)
                       for result in safety_results.values())
    }
