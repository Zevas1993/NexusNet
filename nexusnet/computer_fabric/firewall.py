from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nexus.schemas import utcnow


class PromptInjectionFirewall:
    EXTERNAL_EVIDENCE_KEYS = ("webpage_text", "document_text", "repo_file_text", "ocr_text", "tool_output")

    def scan(self, *, session_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
        evidence_classes: list[dict[str, Any]] = []
        findings: list[str] = []
        operator_instruction = metadata.get("operator_instruction")
        if operator_instruction:
            evidence_classes.append({"class": "operator_instruction", "authority": "can-authorize", "present": True})
        evidence_classes.append({"class": "system_policy", "authority": "can-authorize", "present": True})
        for key in self.EXTERNAL_EVIDENCE_KEYS:
            value = str(metadata.get(key) or "")
            if not value:
                continue
            lowered = value.lower()
            evidence_classes.append({"class": key, "authority": "evidence-only", "present": True})
            if "ignore previous instructions" in lowered or "export all credentials" in lowered or "reveal secrets" in lowered:
                findings.append("external-evidence-instruction-blocked")
        report = {
            "created_at": utcnow().isoformat(),
            "evidence_classes": evidence_classes,
            "findings": findings,
            "authority_rule": "external evidence never authorizes tool calls",
        }
        (session_dir / "prompt-firewall.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return report
