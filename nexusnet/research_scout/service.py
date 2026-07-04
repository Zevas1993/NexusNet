from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from nexus.schemas import new_id, utcnow


class ResearchScoutService:
    SUPPORTED_SOURCE_TYPES = {
        "github",
        "hugging_face",
        "arxiv",
        "npm",
        "vendor_doc",
        "runtime_release_notes",
        "model_card",
        "benchmark",
        "security_advisory",
    }

    LIVE_SOURCE_TYPES = {"github", "hugging_face", "arxiv", "npm"}

    def __init__(self, *, artifacts_dir: Path | str, assimilation: Any | None = None, events: Any | None = None):
        self.artifacts_dir = Path(artifacts_dir)
        self.output_dir = self.artifacts_dir / "research-scout"
        self.run_dir = self.output_dir / "runs"
        self.assimilation = assimilation
        self.events = events
        self.metadata_fetcher = self._default_fetch

    def summary(self, *, limit: int = 100) -> dict[str, Any]:
        items = self._records(limit=limit)
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "supported_source_types": sorted(self.SUPPORTED_SOURCE_TYPES),
            "candidate_count": len(items),
            "source_type_counts": self._counts([item.get("source", {}) for item in items], "source_type"),
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_candidate": items[0] if items else None,
            "latest_runs": self._runs(limit=10),
            "items": items,
        }

    def compact_summary(self, *, limit: int = 50) -> dict[str, Any]:
        payload = self.summary(limit=limit)
        return {
            "status_label": payload["status_label"],
            "candidate_count": payload["candidate_count"],
            "source_type_counts": payload["source_type_counts"],
            "execution_allowed": False,
            "mutation_allowed": False,
            "latest_candidate": payload["latest_candidate"],
        }

    def ingest(
        self,
        *,
        source_type: str,
        source_name: str,
        source_url: str,
        claimed_capability: str = "",
        capability_family: str = "research",
        hardware_tier_fit: list[str] | None = None,
        license_posture: str = "requires_review",
        risk_flags: list[str] | None = None,
        dependency_posture: str = "candidate_only",
        confidence: float = 0.5,
        required_eval_suite: str = "regression_behavior",
    ) -> dict[str, Any]:
        if source_type not in self.SUPPORTED_SOURCE_TYPES:
            raise ValueError(f"unsupported research source_type: {source_type}")
        record = self._candidate(
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            claimed_capability=claimed_capability,
            capability_family=capability_family,
            hardware_tier_fit=hardware_tier_fit or ["tier_2_mainstream_local"],
            license_posture=license_posture,
            risk_flags=risk_flags or [],
            dependency_posture=dependency_posture,
            confidence=confidence,
            required_eval_suite=required_eval_suite,
        )
        assimilation_record = self._ingest_assimilation_shadow(record)
        if assimilation_record:
            record["assimilation_candidate_id"] = assimilation_record.get("candidate", {}).get("candidate_id")
        self._write(record)
        self._event("research_scout.candidate_ingested", record)
        return {"status_label": "STRONG ACCEPTED DIRECTION", "candidate": record}

    def run(
        self,
        *,
        query: str = "capability updates",
        source_types: list[str] | None = None,
        live_fetch: bool = False,
        max_candidates_per_source: int = 3,
    ) -> dict[str, Any]:
        selected_sources = source_types or ["github", "hugging_face", "arxiv", "vendor_doc"]
        unsupported = [source for source in selected_sources if source not in self.SUPPORTED_SOURCE_TYPES]
        if unsupported:
            raise ValueError(f"unsupported research source_type: {unsupported[0]}")
        run_id = new_id("researchscout")
        candidate_limit = max(0, min(int(max_candidates_per_source or 0), 10))
        source_checks: list[dict[str, Any]] = []
        candidates: list[dict[str, Any]] = []
        if self.events:
            self.events.record(
                event_type="research_scout.started",
                subject=f"research-scout:{run_id}",
                payload={
                    "query": query,
                    "source_types": selected_sources,
                    "live_fetch": bool(live_fetch),
                    "network_execution_allowed": bool(live_fetch),
                    "execution_allowed": False,
                },
            )
        for source_type in selected_sources:
            source_check = self._check_source(
                run_id=run_id,
                query=query,
                source_type=source_type,
                live_fetch=live_fetch,
                limit=candidate_limit,
            )
            source_checks.append(source_check)
            candidates.extend(source_check.get("candidates", []))
        return {
            "status_label": "STRONG ACCEPTED DIRECTION",
            "run_id": run_id,
            "status": "completed_metadata_only",
            "query": query,
            "source_types": selected_sources,
            "source_checks": [{key: value for key, value in item.items() if key != "candidates"} for item in source_checks],
            "candidate_count": len(candidates),
            "candidate_ingestion_count": len(candidates),
            "network_execution_allowed": bool(live_fetch),
            "execution_allowed": False,
            "mutation_allowed": False,
            "candidate_ingestion_required_for_promotion": True,
            "artifact_path": self._write_run(
                {
                    "run_id": run_id,
                    "query": query,
                    "source_types": selected_sources,
                    "live_fetch": bool(live_fetch),
                    "source_checks": [{key: value for key, value in item.items() if key != "candidates"} for item in source_checks],
                    "candidate_record_ids": [candidate["record_id"] for candidate in candidates],
                    "created_at": utcnow().isoformat(),
                    "execution_allowed": False,
                    "mutation_allowed": False,
                }
            ),
        }

    def _candidate(
        self,
        *,
        source_type: str,
        source_name: str,
        source_url: str,
        claimed_capability: str,
        capability_family: str,
        hardware_tier_fit: list[str],
        license_posture: str,
        risk_flags: list[str],
        dependency_posture: str,
        confidence: float,
        required_eval_suite: str,
        source_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record_id = new_id("researchcandidate")
        tier = hardware_tier_fit[0] if hardware_tier_fit else "tier_2_mainstream_local"
        path = self.output_dir / f"{record_id}.json"
        source_payload = {
            "source_type": source_type,
            "source_name": source_name,
            "source_url": source_url,
            "claimed_capability": claimed_capability,
            "observed_at": utcnow().isoformat(),
        }
        source_payload.update(source_metadata or {})
        return {
            "record_id": record_id,
            "status": "candidate",
            "tier": tier,
            "capability_family": capability_family,
            "source": source_payload,
            "target_subsystem": self._target_subsystem(capability_family),
            "hardware_profile": {"hardware_tier_fit": hardware_tier_fit},
            "runtime_candidates": [],
            "provider_candidates": [],
            "model_artifact_formats": [],
            "quantization_posture": {"state": "candidate_dependent"},
            "offline_posture": "unknown_until_validation",
            "privacy_posture": "requires_review",
            "cost_posture": {"state": "not_estimated"},
            "policy_path": [{"stage": "research-scout", "decision": "hold", "reason": "candidate-metadata-only"}],
            "approval_path": {"decision": "not_requested", "human_approval_is_not_execution_authority": True},
            "product_sweep_gate_ids": ["research-provenance-gate", "license-review", "security-review"],
            "eval_suite_ids": [required_eval_suite],
            "telemetry_trace_ids": [f"trace_{record_id}"],
            "provenance": {"metadata_only": True, "scout": "nexusnet-research-scout", "created_at": utcnow().isoformat()},
            "artifacts": [str(path).replace("\\", "/")],
            "execution_allowed": False,
            "mutation_allowed": False,
            "license_posture": license_posture,
            "risk_flags": risk_flags,
            "dependency_posture": dependency_posture,
            "confidence": confidence,
            "required_eval_suite": required_eval_suite,
            "hardware_tier_fit": hardware_tier_fit,
        }

    def _ingest_assimilation_shadow(self, record: dict[str, Any]) -> dict[str, Any] | None:
        if self.assimilation is None:
            return None
        try:
            return self.assimilation.ingest(
                category="runtime" if record["capability_family"] in {"inference", "provider_fallback"} else "research",
                source_name=record["source"]["source_name"],
                source_url=record["source"]["source_url"],
                license_posture=record["license_posture"],
                target_subsystem=record["target_subsystem"],
                governance_status="gated",
                provenance={"source": "research-scout", "metadata_only": True, "record_id": record["record_id"]},
                scorecard={"confidence": record["confidence"], "hardware_tier_fit": record["hardware_tier_fit"]},
            )
        except ValueError:
            return None

    def _target_subsystem(self, capability_family: str) -> str:
        return {
            "provider_fallback": "runtime",
            "inference": "runtime",
            "code_agent": "parallel_runs",
            "parallel_agent": "parallel_runs",
            "protocol_tooling": "protocols",
        }.get(capability_family, capability_family)

    def _check_source(
        self,
        *,
        run_id: str,
        query: str,
        source_type: str,
        live_fetch: bool,
        limit: int,
    ) -> dict[str, Any]:
        query_plan = self._query_plan(source_type=source_type, query=query, limit=limit)
        source_check: dict[str, Any] = {
            "source_type": source_type,
            "status": "planned_only",
            "query_plan": query_plan,
            "network_execution_allowed": False,
            "candidate_count": 0,
            "candidates": [],
        }
        if not live_fetch or source_type not in self.LIVE_SOURCE_TYPES or limit <= 0:
            self._source_event(run_id, query, source_check)
            return source_check
        source_check["network_execution_allowed"] = True
        try:
            status_code, body = self.metadata_fetcher(
                query_plan["url"],
                {
                    "Accept": query_plan["accept"],
                    "User-Agent": "NexusNet-ResearchScout/1.0 metadata-only",
                },
                10.0,
            )
            source_check["http_status"] = status_code
            source_check["status"] = "fetched_metadata" if 200 <= int(status_code) < 300 else "fetch_failed"
            if source_check["status"] == "fetched_metadata":
                parsed = self._parse_source_results(
                    source_type=source_type,
                    query=query,
                    url=query_plan["url"],
                    body=body,
                    limit=limit,
                )
                for candidate in parsed:
                    self._store_candidate(candidate)
                source_check["candidates"] = parsed
                source_check["candidate_count"] = len(parsed)
        except Exception as exc:
            source_check["status"] = "fetch_failed"
            source_check["error"] = str(exc)
        self._source_event(run_id, query, source_check)
        return source_check

    def _query_plan(self, *, source_type: str, query: str, limit: int) -> dict[str, Any]:
        bounded_limit = max(1, min(limit or 1, 10))
        if source_type == "github":
            params = {"q": query, "sort": "updated", "order": "desc", "per_page": bounded_limit}
            return {
                "url": f"https://api.github.com/search/repositories?{urlencode(params)}",
                "accept": "application/vnd.github+json",
                "method": "GET",
            }
        if source_type == "hugging_face":
            params = {"search": query, "sort": "lastModified", "direction": "-1", "limit": bounded_limit}
            return {
                "url": f"https://huggingface.co/api/models?{urlencode(params)}",
                "accept": "application/json",
                "method": "GET",
            }
        if source_type == "npm":
            params = {"text": query, "size": bounded_limit}
            return {
                "url": f"https://registry.npmjs.org/-/v1/search?{urlencode(params)}",
                "accept": "application/json",
                "method": "GET",
            }
        if source_type == "arxiv":
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": bounded_limit,
                "sortBy": "lastUpdatedDate",
                "sortOrder": "descending",
            }
            return {
                "url": f"https://export.arxiv.org/api/query?{urlencode(params)}",
                "accept": "application/atom+xml",
                "method": "GET",
            }
        return {
            "url": f"metadata-template://{source_type}/{query}",
            "accept": "metadata/template",
            "method": "PLAN_ONLY",
        }

    def _parse_source_results(self, *, source_type: str, query: str, url: str, body: str, limit: int) -> list[dict[str, Any]]:
        if source_type == "github":
            return self._parse_github(body=body, query=query, url=url, limit=limit)
        if source_type == "hugging_face":
            return self._parse_hugging_face(body=body, query=query, url=url, limit=limit)
        if source_type == "npm":
            return self._parse_npm(body=body, query=query, url=url, limit=limit)
        if source_type == "arxiv":
            return self._parse_arxiv(body=body, query=query, url=url, limit=limit)
        return []

    def _parse_github(self, *, body: str, query: str, url: str, limit: int) -> list[dict[str, Any]]:
        payload = json.loads(body or "{}")
        candidates = []
        for item in (payload.get("items") or [])[:limit]:
            text = " ".join(
                [
                    str(item.get("full_name") or ""),
                    str(item.get("description") or ""),
                    " ".join(str(topic) for topic in (item.get("topics") or [])),
                    str(item.get("language") or ""),
                ]
            )
            license_id = (((item.get("license") or {}).get("spdx_id")) or "").strip()
            candidates.append(
                self._candidate(
                    source_type="github",
                    source_name=str(item.get("full_name") or item.get("name") or "github-repository"),
                    source_url=str(item.get("html_url") or item.get("url") or url),
                    claimed_capability=str(item.get("description") or f"GitHub metadata match for {query}"),
                    capability_family=self._infer_capability_family(text),
                    hardware_tier_fit=self._infer_hardware_tiers(text),
                    license_posture=self._license_posture(license_id),
                    risk_flags=self._risk_flags(text=text, source_type="github"),
                    dependency_posture="source_metadata_only",
                    confidence=self._bounded_confidence(0.58, item.get("stargazers_count")),
                    required_eval_suite=self._required_eval_suite(text),
                    source_metadata={
                        "fetched_url": url,
                        "fetch_state": "fetched_metadata",
                        "api_source": "github_search_repositories",
                        "language": item.get("language"),
                        "topics": item.get("topics") or [],
                        "stars": item.get("stargazers_count"),
                    },
                )
            )
        return candidates

    def _parse_hugging_face(self, *, body: str, query: str, url: str, limit: int) -> list[dict[str, Any]]:
        payload = json.loads(body or "[]")
        if isinstance(payload, dict):
            payload = payload.get("models") or payload.get("items") or []
        candidates = []
        for item in payload[:limit]:
            tags = [str(tag) for tag in (item.get("tags") or [])]
            model_id = str(item.get("modelId") or item.get("id") or "huggingface-model")
            text = " ".join([model_id, str(item.get("pipeline_tag") or ""), " ".join(tags)])
            candidates.append(
                self._candidate(
                    source_type="hugging_face",
                    source_name=model_id,
                    source_url=f"https://huggingface.co/{model_id}",
                    claimed_capability=str(item.get("pipeline_tag") or f"Hugging Face model metadata match for {query}"),
                    capability_family=self._infer_capability_family(text),
                    hardware_tier_fit=self._infer_hardware_tiers(text),
                    license_posture=self._license_posture(self._license_from_tags(tags)),
                    risk_flags=self._risk_flags(text=text, source_type="hugging_face"),
                    dependency_posture="model_metadata_only",
                    confidence=self._bounded_confidence(0.54, item.get("downloads")),
                    required_eval_suite=self._required_eval_suite(text),
                    source_metadata={
                        "fetched_url": url,
                        "fetch_state": "fetched_metadata",
                        "api_source": "huggingface_models",
                        "tags": tags,
                        "downloads": item.get("downloads"),
                        "pipeline_tag": item.get("pipeline_tag"),
                    },
                )
            )
        return candidates

    def _parse_npm(self, *, body: str, query: str, url: str, limit: int) -> list[dict[str, Any]]:
        payload = json.loads(body or "{}")
        candidates = []
        for item in (payload.get("objects") or [])[:limit]:
            package = item.get("package") or {}
            keywords = [str(keyword) for keyword in (package.get("keywords") or [])]
            name = str(package.get("name") or "npm-package")
            text = " ".join([name, str(package.get("description") or ""), " ".join(keywords)])
            candidates.append(
                self._candidate(
                    source_type="npm",
                    source_name=name,
                    source_url=str(((package.get("links") or {}).get("npm")) or f"https://www.npmjs.com/package/{name}"),
                    claimed_capability=str(package.get("description") or f"npm package metadata match for {query}"),
                    capability_family=self._infer_capability_family(text),
                    hardware_tier_fit=self._infer_hardware_tiers(text),
                    license_posture=self._license_posture(package.get("license")),
                    risk_flags=self._risk_flags(text=text, source_type="npm"),
                    dependency_posture="package_metadata_only_no_install",
                    confidence=self._bounded_confidence(0.52, (((item.get("score") or {}).get("final")) or 0) * 1000),
                    required_eval_suite=self._required_eval_suite(text),
                    source_metadata={
                        "fetched_url": url,
                        "fetch_state": "fetched_metadata",
                        "api_source": "npm_registry_search",
                        "version": package.get("version"),
                        "keywords": keywords,
                        "score": item.get("score") or {},
                    },
                )
            )
        return candidates

    def _parse_arxiv(self, *, body: str, query: str, url: str, limit: int) -> list[dict[str, Any]]:
        root = ET.fromstring(body)
        atom = "{http://www.w3.org/2005/Atom}"
        candidates = []
        for entry in root.findall(f"{atom}entry")[:limit]:
            title = self._xml_text(entry, f"{atom}title") or "arXiv paper"
            summary = self._xml_text(entry, f"{atom}summary") or f"arXiv metadata match for {query}"
            source_url = self._xml_text(entry, f"{atom}id") or url
            categories = [item.attrib.get("term") for item in entry.findall(f"{atom}category") if item.attrib.get("term")]
            authors = [self._xml_text(author, f"{atom}name") for author in entry.findall(f"{atom}author")]
            text = " ".join([title, summary, " ".join(categories)])
            candidates.append(
                self._candidate(
                    source_type="arxiv",
                    source_name=" ".join(title.split()),
                    source_url=source_url,
                    claimed_capability=" ".join(summary.split())[:500],
                    capability_family=self._infer_capability_family(text),
                    hardware_tier_fit=self._infer_hardware_tiers(text),
                    license_posture="requires_review",
                    risk_flags=["research_claim_requires_validation"],
                    dependency_posture="paper_metadata_only",
                    confidence=0.62,
                    required_eval_suite=self._required_eval_suite(text),
                    source_metadata={
                        "fetched_url": url,
                        "fetch_state": "fetched_metadata",
                        "api_source": "arxiv_query",
                        "published": self._xml_text(entry, f"{atom}published"),
                        "updated": self._xml_text(entry, f"{atom}updated"),
                        "authors": [author for author in authors if author],
                        "categories": categories,
                    },
                )
            )
        return candidates

    def _store_candidate(self, record: dict[str, Any]) -> None:
        assimilation_record = self._ingest_assimilation_shadow(record)
        if assimilation_record:
            record["assimilation_candidate_id"] = assimilation_record.get("candidate", {}).get("candidate_id")
        self._write(record)
        self._event("research_scout.candidate_ingested", record)

    def _default_fetch(self, url: str, headers: dict[str, str], timeout: float) -> tuple[int, str]:
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return int(getattr(response, "status", 200)), body

    def _source_event(self, run_id: str, query: str, source_check: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type="research_scout.source_checked",
            subject=f"research-scout:{run_id}:{source_check['source_type']}",
            payload={
                "query": query,
                "source_type": source_check["source_type"],
                "status": source_check["status"],
                "candidate_count": source_check["candidate_count"],
                "network_execution_allowed": source_check["network_execution_allowed"],
                "execution_allowed": False,
            },
        )

    def _write_run(self, record: dict[str, Any]) -> str:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        path = self.run_dir / f"{record['run_id']}.json"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return str(path).replace("\\", "/")

    def _runs(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.run_dir.exists():
            return []
        items = []
        for path in sorted(self.run_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _infer_capability_family(self, text: str) -> str:
        normalized = text.lower()
        if any(term in normalized for term in ("retrieval", "rag", "vector", "search")):
            return "retrieval"
        if any(term in normalized for term in ("agent", "workflow", "tool", "mcp", "plugin", "extension")):
            return "code_agent"
        if any(term in normalized for term in ("eval", "benchmark", "red team", "safety")):
            return "eval"
        if any(term in normalized for term in ("memory", "compaction")):
            return "memory"
        return "inference"

    def _infer_hardware_tiers(self, text: str) -> list[str]:
        normalized = text.lower()
        tiers = []
        if any(term in normalized for term in ("tiny", "mobile", "edge", "npu", "qnn", "tflite", "int8")):
            tiers.extend(["tier_1_constrained_edge", "tier_2_mainstream_local"])
        if any(term in normalized for term in ("gguf", "onnx", "local", "webgpu", "directml")):
            tiers.append("tier_2_mainstream_local")
        if any(term in normalized for term in ("gpu", "server", "vllm", "sglang", "tensorrt")):
            tiers.extend(["tier_3_premium_local", "tier_4_local_server"])
        if any(term in normalized for term in ("cloud", "hosted", "api")):
            tiers.append("tier_5_governed_cloud")
        return list(dict.fromkeys(tiers or ["tier_2_mainstream_local"]))

    def _risk_flags(self, *, text: str, source_type: str) -> list[str]:
        normalized = text.lower()
        flags = [f"{source_type}_metadata_only"]
        if any(term in normalized for term in ("native", "runtime", "kernel", "cuda", "driver")):
            flags.append("native_runtime_requires_sandbox_review")
        if any(term in normalized for term in ("cloud", "hosted", "api")):
            flags.append("data_egress_review_required")
        if source_type in {"npm", "github"}:
            flags.append("package_or_source_not_executed")
        return flags

    def _required_eval_suite(self, text: str) -> str:
        family = self._infer_capability_family(text)
        return {
            "retrieval": "rag_quality",
            "code_agent": "code_agent_issue_to_patch",
            "eval": "regression_behavior",
            "memory": "regression_behavior",
            "inference": "runtime_quality",
        }.get(family, "regression_behavior")

    def _license_from_tags(self, tags: list[str]) -> str:
        for tag in tags:
            if tag.startswith("license:"):
                return tag.split(":", 1)[1]
        return ""

    def _license_posture(self, license_id: Any) -> str:
        normalized = str(license_id or "").strip()
        if not normalized or normalized.upper() == "NOASSERTION":
            return "requires_review"
        return f"declared:{normalized}"

    def _bounded_confidence(self, base: float, popularity: Any) -> float:
        try:
            score = float(popularity or 0)
        except (TypeError, ValueError):
            score = 0.0
        return round(min(0.95, base + min(score, 100000.0) / 1000000.0), 3)

    def _xml_text(self, element: ET.Element, path: str) -> str:
        value = element.findtext(path)
        return " ".join(str(value or "").split())

    def _records(self, *, limit: int) -> list[dict[str, Any]]:
        if not self.output_dir.exists():
            return []
        items = []
        for path in sorted(self.output_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
            if len(items) >= limit:
                break
        return items

    def _write(self, record: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{record['record_id']}.json"
        record["artifacts"] = [str(path).replace("\\", "/")]
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _event(self, event_type: str, record: dict[str, Any]) -> None:
        if not self.events:
            return
        self.events.record(
            event_type=event_type,
            subject=f"research-scout:{record['record_id']}",
            trace_ids=record.get("telemetry_trace_ids", []),
            payload={
                "record_id": record["record_id"],
                "source_type": record["source"]["source_type"],
                "capability_family": record["capability_family"],
                "execution_allowed": False,
                "mutation_allowed": False,
            },
        )

    def _counts(self, items: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = str(item.get(key) or "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
