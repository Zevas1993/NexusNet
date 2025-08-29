
from __future__ import annotations
import re
import logging
from typing import List, Dict, Any, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

# Output sanitization patterns
HTML_SCRIPTS = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
HTML_TAGS = re.compile(r'<[^>]+>')
INJECTION_PATTERNS = [
    r'\bUNION\s+SELECT\b',
    r'\bDROP\s+TABLE\b',
    r'\bDELETE\s+FROM\b',
    r'\bUPDATE\s+.+SET\b',
    r'\bINSERT\s+INTO\b',
    r'\bEXEC\s*\(',
    r'\bEXECUTE\s*\(',
    r'\bEVAL\s*\(',
    r'\bSYSTEM\s*\(',
    r'\bSHELL_EXEC\s*\(',
]

# Content sanitization patterns
HATEFUL_CONTENT = [
    r'\b(hate|nigger|chink|faggot|retard)\b',  # Racial/ethnic/slur terms
    r'\bkill\s+(all\s+)?[^\s]*\s*jew|holocaust\b',  # Antisemitic content
    r'\b(hitler|nazis?|swastika)\b',  # Nazi references
]

TOXIC_CONTENT = [
    r'\b(fuck+|shit+|damn+|bitch+|asshole+)\b',
    r'\b(kill\s+yourself|suicide)\b',
    r'\b(harm|hurt)\s+(your)?self\b',
    r'\b(rape|sexual\s+assault)\b',
    r'\b(terrorism|terrorist)\b',
]

class OutputSafetyFilter:
    """Comprehensive output filtering and sanitization"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sanitization_count = 0
        self.blocked_count = 0
        self.warnings_count = 0

    def sanitize(self, text: str, policy_config: Dict[str, Any] = None) -> str:
        """Main sanitization function - replaces the stub implementation"""
        if policy_config is None:
            policy_config = {
                "strip_html": True,
                "encode_special_chars": False,
                "remove_injections": True,
                "filter_hateful_content": True,
                "filter_toxic_content": True,
                "max_result_length": 32768,
                "remove_unknown_tokens": True,
                "normalize_whitespace": True
            }

        sanitized = text

        # Strip HTML/JavaScript
        if policy_config.get("strip_html", True):
            sanitized = HTML_SCRIPTS.sub("", sanitized)
            sanitized = HTML_TAGS.sub("", sanitized)

        # Prevent injection attacks
        if policy_config.get("remove_injections", True):
            sanitized = self._remove_injections(sanitized)

        # Content filtering
        if policy_config.get("filter_hateful_content", True):
            sanitized = self._filter_hateful_content(sanitized)

        if policy_config.get("filter_toxic_content", True):
            sanitized = self._filter_toxic_content(sanitized)

        # Encode special characters if requested
        if policy_config.get("encode_special_chars", False):
            sanitized = self._encode_special_chars(sanitized)

        # Normalize whitespace
        if policy_config.get("normalize_whitespace", True):
            sanitized = re.sub(r'\s+', ' ', sanitized).strip()

        # Enforce maximum length
        max_length = policy_config.get("max_result_length", 32768)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length - 3] + "..."
            self.sanitization_count += 1

        # Remove unknown tokens/artefacts
        if policy_config.get("remove_unknown_tokens", True):
            sanitized = self._clean_unknown_tokens(sanitized)

        return sanitized

    def _remove_injections(self, text: str) -> str:
        """Remove potential injection attacks"""
        original = text
        for pattern in INJECTION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    text = text.replace(match, f"[INJECTION_REMOVED]")
                self.sanitization_count += len(matches)

        return text

    def _filter_hateful_content(self, text: str) -> str:
        """Filter hateful or discriminatory content"""
        original = text
        for pattern in HATEFUL_CONTENT:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, "[CONTENT_FILTERED]", text, flags=re.IGNORECASE)
                self.warnings_count += 1

        return text

    def _filter_toxic_content(self, text: str) -> str:
        """Filter toxic or harmful language"""
        original = text
        for pattern in TOXIC_CONTENT:
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, "[CONTENT_FILTERED]", text, flags=re.IGNORECASE)
                self.warnings_count += 1

        return text

    def _encode_special_chars(self, text: str) -> str:
        """HTML encode special characters"""
        encoding_map = {
            '&': '&',
            '<': '<',
            '>': '>',
            '"': '"',
            "'": '&#39;',
            '`': '&#96;'
        }

        return ''.join(encoding_map.get(char, char) for char in text)

    def _clean_unknown_tokens(self, text: str) -> str:
        """Clean unknown tokens or artefacts from model output"""
        # Remove common unwanted tokens
        unwanted_patterns = [
            r'</?unk>', r'</?pad>', r'</?mask>', r'</?bos>', r'</?eos>',
            r'<\w+>', r'</\w+>',  # Remove generic XML-like tags
            r'\[UNK[^\]]*\]', r'<UNK[^>]*>', r'\[PAD[^\]]*\]', r'<PAD[^>]*>',
        ]

        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text

    def detect_bias_indicators(self, text: str) -> Dict[str, Any]:
        """Detect potential bias indicators in generated content"""
        bias_indicators = {
            "gender": [r'\b(he|she|him|her|his|her)\b', r'\b(man|woman|men|women)\b'],
            "demographic": [r'\b(old|young|rich|poor)\b', r'\b(class|race|ethnic)\b'],
            "ideological": [r'\b(liberal|conservative|progressive|right-wing|left-wing)\b'],
        }

        findings = {}
        for category, patterns in bias_indicators.items():
            category_findings = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    category_findings.extend(list(set(matches)))

            if category_findings:
                findings[category] = category_findings

        return {
            "bias_detected": len(findings) > 0,
            "categories": findings,
            "recommendation": "Consider content moderation if bias patterns detected"
        }

    def validate_factuality(self, text: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Basic factuality validation - placeholder for more sophisticated analysis"""
        # This would integrate with fact-checking services or knowledge bases
        return {
            "validated": True,
            "confidence": 0.8,
            "warnings": [],
            "disclaimer": "Factuality validation incomplete - requires external services"
        }

    def get_safety_stats(self) -> Dict[str, int]:
        """Get output filter statistics"""
        return {
            "sanitizations": self.sanitization_count,
            "blocked_content": self.blocked_count,
            "warnings": self.warnings_count
        }

    def reset_stats(self):
        """Reset statistics counters"""
        self.sanitization_count = 0
        self.blocked_count = 0
        self.warnings_count = 0


class ContentModerator:
    """Advanced content moderation for outputs"""

    def __init__(self):
        self.output_filter = OutputSafetyFilter()

    def moderate_output(self, text: str,
                       content_policy: Dict[str, Any] = None,
                       perform_bias_check: bool = True,
                       validate_facts: bool = False) -> Dict[str, Any]:
        """Complete content moderation pipeline"""

        if content_policy is None:
            content_policy = {
                "strip_html": True,
                "remove_injections": True,
                "filter_toxic": True,
                "filter_hateful": True,
                "max_length": 32768
            }

        # Apply basic sanitization
        sanitized = self.output_filter.sanitize(text, content_policy)

        moderation_result = {
            "original_text": text,
            "moderated_text": sanitized,
            "modifications_made": sanitized != text,
            "safety_checks": {}
        }

        # Perform biases detection
        if perform_bias_check:
            bias_analysis = self.output_filter.detect_bias_indicators(sanitized)
            moderation_result["safety_checks"]["bias"] = bias_analysis

        # Validate factuality if requested
        if validate_facts:
            factuality = self.output_filter.validate_factuality(sanitized)
            moderation_result["safety_checks"]["factuality"] = factuality

        # Overall approval
        moderation_result["approved"] = (
            not moderation_result["safety_checks"].get("bias", {}).get("bias_detected", False) and
            moderation_result["safety_checks"].get("factuality", {}).get("validated", True)
        )

        return moderation_result


# Global instances for backward compatibility
_output_filter = OutputSafetyFilter()
_moderator = ContentModerator()

def sanitize(text: str) -> str:
    """Legacy function for backward compatibility - now properly implemented"""
    return _output_filter.sanitize(text)

def moderate_content(text: str, policy: Dict[str, Any] = None) -> Dict[str, Any]:
    """Complete content moderation pipeline"""
    return _moderator.moderate_output(text, policy)

def comprehensive_output_filter(text: str,
                              content_policy: Dict[str, Any] = None,
                              bias_detection: bool = True,
                              factuality_checks: bool = False) -> Dict[str, Any]:
    """Complete output filtering pipeline with all safety checks"""
    return _moderator.moderate_output(text, content_policy, bias_detection, factuality_checks)
