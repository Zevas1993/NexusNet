from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
import ipaddress
import json
from pathlib import Path
import re
import socket
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from nexus.schemas import utcnow
from nexusnet.research.forward_radar import ForwardRadarCandidateRequest, ForwardRadarRegistry


class ResearchMonitor:
    MAX_RESPONSE_BYTES = 1_048_576

    def __init__(
        self,
        *,
        artifacts_dir: Path,
        radar: ForwardRadarRegistry,
        allow_private_network: bool = False,
    ) -> None:
        self.root = Path(artifacts_dir) / "research" / "monitors"
        self.sources_dir = self.root / "sources"
        self.events_dir = self.root / "events"
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.radar = radar
        self.allow_private_network = allow_private_network

    def add_source(
        self,
        *,
        source_id: str,
        url: str,
        interval_seconds: int = 3600,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        source_id = _safe_id(source_id)
        self._validate_url(url)
        if interval_seconds < 15:
            raise ValueError("interval_seconds must be at least 15")
        existing = self._load_source(source_id) or {}
        source = {
            **existing,
            "source_id": source_id,
            "url": url,
            "interval_seconds": interval_seconds,
            "etag": existing.get("etag"),
            "last_modified": existing.get("last_modified"),
            "last_content_digest": existing.get("last_content_digest"),
            "last_polled_at": existing.get("last_polled_at"),
            "topics": sorted({_safe_id(topic) for topic in (topics or existing.get("topics") or [])}),
        }
        self._write_json(self.sources_dir / f"{source_id}.json", source)
        return source

    def poll(self, source_id: str) -> dict[str, Any]:
        source = self._load_source(_safe_id(source_id))
        if source is None:
            raise KeyError(f"unknown research monitor source: {source_id}")
        headers = {"User-Agent": "NexusNet-ResearchMonitor/1.0", "Accept": "text/html,application/json,text/plain"}
        if source.get("etag"):
            headers["If-None-Match"] = str(source["etag"])
        if source.get("last_modified"):
            headers["If-Modified-Since"] = str(source["last_modified"])
        request = Request(source["url"], headers=headers, method="GET")
        try:
            response = urlopen(request, timeout=20)
        except HTTPError as exc:
            if exc.code == 304:
                return self._record_not_modified(source)
            raise RuntimeError(f"research source returned HTTP {exc.code}") from exc
        with response:
            self._validate_url(response.geturl())
            body = response.read(self.MAX_RESPONSE_BYTES + 1)
            if len(body) > self.MAX_RESPONSE_BYTES:
                raise ValueError("research source exceeds bounded response size")
            content_type = str(response.headers.get("Content-Type") or "")
            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
        digest = hashlib.sha256(body).hexdigest()
        if digest == source.get("last_content_digest"):
            return self._record_not_modified(source, state="duplicate_content")
        title, summary = _summarize(body, content_type=content_type)
        now = utcnow().isoformat()
        source.update(
            {
                "etag": etag,
                "last_modified": last_modified,
                "last_content_digest": digest,
                "last_polled_at": now,
            }
        )
        self._write_json(self.sources_dir / f"{source['source_id']}.json", source)
        candidate_id = f"monitor::{source['source_id']}::{digest[:12]}"
        candidate = self.radar.review(
            candidate_id,
            ForwardRadarCandidateRequest(
                radar_id=candidate_id,
                title=title or f"Changed source: {source['source_id']}",
                lane="research-monitor",
                summary=summary,
                source_refs=[source["url"]],
                source_quality="primary",
                license_status="needs_review",
                security_review="needs_review",
                rollback_plan="remove-shadow-candidate-and-monitor-event",
                metadata={
                    "source_id": source["source_id"],
                    "content_digest": digest,
                    "trend_topics": source.get("topics") or [],
                    "raw_content_persisted": False,
                },
            ),
        )
        event = {
            "event_id": f"monitor_event_{digest[:16]}",
            "source_id": source["source_id"],
            "state": "changed",
            "content_digest": digest,
            "candidate_id": candidate["radar_id"],
            "topics": source.get("topics") or [],
            "polled_at": now,
            "raw_content_persisted": False,
        }
        self._write_json(self.events_dir / f"{event['event_id']}.json", event)
        return event

    def poll_due(self) -> dict[str, Any]:
        due_source_ids: list[str] = []
        skipped = 0
        now = utcnow()
        for path in sorted(self.sources_dir.glob("*.json")):
            source = json.loads(path.read_text(encoding="utf-8"))
            last_polled = source.get("last_polled_at")
            if not last_polled:
                due_source_ids.append(path.stem)
                continue
            last_polled_at = datetime.fromisoformat(str(last_polled))
            if last_polled_at.tzinfo is None:
                last_polled_at = last_polled_at.replace(tzinfo=timezone.utc)
            if last_polled_at + timedelta(seconds=int(source["interval_seconds"])) <= now:
                due_source_ids.append(path.stem)
            else:
                skipped += 1
        results = [self.poll(source_id) for source_id in due_source_ids]
        return {
            "polled_count": len(results),
            "skipped_not_due_count": skipped,
            "results": results,
        }

    def summary(self) -> dict[str, Any]:
        events = [json.loads(path.read_text(encoding="utf-8")) for path in self.events_dir.glob("*.json")]
        topic_sources: dict[str, set[str]] = {}
        for event in events:
            if event.get("state") != "changed":
                continue
            for topic in event.get("topics") or []:
                topic_sources.setdefault(str(topic), set()).add(str(event.get("source_id") or ""))
        strong_trends = [
            {"topic": topic, "source_count": len(source_ids), "source_ids": sorted(source_ids)}
            for topic, source_ids in sorted(topic_sources.items())
            if len(source_ids) >= 2
        ]
        return {
            "surface_id": "research-monitor-runtime",
            "source_count": len(list(self.sources_dir.glob("*.json"))),
            "poll_count": len(events),
            "changed_count": sum(1 for event in events if event.get("state") == "changed"),
            "strong_trends": strong_trends,
            "events": sorted(events, key=lambda item: item.get("polled_at") or "", reverse=True),
        }

    def _record_not_modified(self, source: dict[str, Any], *, state: str = "not_modified") -> dict[str, Any]:
        source["last_polled_at"] = utcnow().isoformat()
        self._write_json(self.sources_dir / f"{source['source_id']}.json", source)
        return {
            "source_id": source["source_id"],
            "state": state,
            "content_digest": source.get("last_content_digest"),
            "polled_at": source["last_polled_at"],
        }

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("research monitor sources must use http or https")
        if self.allow_private_network:
            return
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port or 443)}
        except socket.gaierror as exc:
            raise ValueError(f"research source host could not be resolved: {parsed.hostname}") from exc
        if any(_private_address(address) for address in addresses):
            raise ValueError("research monitor source resolves to a private network")

    def _load_source(self, source_id: str) -> dict[str, Any] | None:
        path = self.sources_dir / f"{source_id}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(path)


def _safe_id(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-").lower()
    if not normalized:
        raise ValueError("source_id is required")
    return normalized


def _private_address(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return bool(address.is_private or address.is_loopback or address.is_link_local or address.is_reserved)


def _summarize(body: bytes, *, content_type: str) -> tuple[str, str]:
    text = body.decode("utf-8", errors="replace")
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip()[:200] if title_match else ""
    if "html" in content_type.lower() or "<html" in text[:500].lower():
        text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
    summary = re.sub(r"\s+", " ", text).strip()[:1000]
    return title, summary
