from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .config import NexusPaths, ensure_paths


def _json_dump(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, default=str)


def _json_load(payload: str | None, default: Any) -> Any:
    if not payload:
        return default
    return json.loads(payload)


class NexusStore:
    def __init__(self, paths: NexusPaths):
        self.paths = ensure_paths(paths)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.paths.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        schema = """
        create table if not exists models (
            model_id text primary key,
            runtime_name text not null,
            registration_json text not null,
            created_at text not null,
            updated_at text not null
        );
        create table if not exists runtime_profiles (
            runtime_name text primary key,
            profile_json text not null,
            updated_at text not null
        );
        create table if not exists execution_traces (
            trace_id text primary key,
            session_id text not null,
            status text not null,
            trace_json text not null,
            created_at text not null
        );
        create table if not exists critiques (
            critique_id text primary key,
            trace_id text not null,
            critique_json text not null,
            created_at text not null
        );
        create table if not exists memory_records (
            memory_id text primary key,
            session_id text not null,
            plane text not null,
            role text,
            content_json text not null,
            tags_json text not null,
            score_json text not null,
            created_at text not null,
            updated_at text not null
        );
        create table if not exists memory_analytics (
            session_id text primary key,
            analytics_json text not null,
            updated_at text not null
        );
        create table if not exists retrieval_documents (
            doc_id text primary key,
            source text not null,
            title text,
            content text not null,
            metadata_json text not null,
            created_at text not null
        );
        create table if not exists retrieval_chunks (
            chunk_id text primary key,
            doc_id text not null,
            chunk_index integer not null,
            source text not null,
            content text not null,
            metadata_json text not null,
            created_at text not null
        );
        create table if not exists experiments (
            experiment_id text primary key,
            kind text not null,
            name text not null,
            status text not null,
            record_json text not null,
            created_at text not null
        );
        create table if not exists promotion_candidates (
            candidate_id text primary key,
            candidate_kind text not null,
            subject_id text not null,
            review_status text not null,
            candidate_json text not null,
            created_at text not null
        );
        create table if not exists promotion_evaluations (
            evaluation_id text primary key,
            candidate_id text not null,
            decision text not null,
            evaluation_json text not null,
            created_at text not null
        );
        create table if not exists promotion_decisions (
            decision_id text primary key,
            candidate_id text not null,
            subject_id text not null,
            decision text not null,
            decision_json text not null,
            created_at text not null
        );
        create table if not exists approvals (
            decision_id text primary key,
            subject text not null,
            decision text not null,
            approver text not null,
            detail_json text not null,
            created_at text not null
        );
        create table if not exists rollbacks (
            rollback_id text primary key,
            subject text not null,
            status text not null,
            record_json text not null,
            created_at text not null
        );
        create table if not exists audit_events (
            event_id text primary key,
            action text not null,
            detail_json text not null,
            created_at text not null
        );
        create table if not exists curriculum_transcript (
            record_id text primary key,
            subject text not null,
            course text not null,
            status text not null,
            score real,
            detail_json text not null,
            created_at text not null
        );
        create table if not exists teacher_scorecards (
            scorecard_id text primary key,
            subject text not null,
            benchmark_family_id text not null,
            scorecard_json text not null,
            created_at text not null
        );
        create table if not exists teacher_disagreement_artifacts (
            artifact_id text primary key,
            subject text not null,
            registry_layer text not null,
            artifact_json text not null,
            created_at text not null
        );
        create table if not exists teacher_evidence_bundles (
            bundle_id text primary key,
            subject text not null,
            registry_layer text not null,
            bundle_json text not null,
            created_at text not null
        );
        create table if not exists takeover_scorecards (
            scorecard_id text primary key,
            subject text not null,
            bundle_id text,
            scorecard_json text not null,
            created_at text not null
        );
        create table if not exists retirement_shadow_log (
            record_id text primary key,
            teacher_id text not null,
            decision text not null,
            record_json text not null,
            created_at text not null
        );
        create table if not exists teacher_trend_scorecards (
            trend_id text primary key,
            subject text not null,
            benchmark_family_id text not null,
            trend_json text not null,
            created_at text not null
        );
        create table if not exists takeover_trend_reports (
            trend_id text primary key,
            subject text not null,
            trend_json text not null,
            created_at text not null
        );
        create table if not exists teacher_benchmark_fleet_summaries (
            summary_id text primary key,
            fleet_id text not null,
            subject text,
            summary_json text not null,
            created_at text not null
        );
        create table if not exists teacher_cohort_scorecards (
            cohort_id text primary key,
            fleet_id text not null,
            subject text,
            cohort_json text not null,
            created_at text not null
        );
        create table if not exists replacement_readiness_reports (
            report_id text primary key,
            subject text not null,
            teacher_id text not null,
            report_json text not null,
            created_at text not null
        );
        """
        with self._connect() as conn:
            conn.executescript(schema)

    def write_artifact(self, relative_path: str, content: str) -> str:
        destination = self.paths.artifacts_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return str(destination)

    def upsert_model(self, model_id: str, runtime_name: str, payload: dict[str, Any], created_at: str, updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into models(model_id, runtime_name, registration_json, created_at, updated_at)
                values (?, ?, ?, ?, ?)
                on conflict(model_id) do update set
                    runtime_name=excluded.runtime_name,
                    registration_json=excluded.registration_json,
                    updated_at=excluded.updated_at
                """,
                (model_id, runtime_name, _json_dump(payload), created_at, updated_at),
            )

    def list_models(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select registration_json from models order by model_id").fetchall()
        return [_json_load(row["registration_json"], {}) for row in rows]

    def upsert_runtime_profile(self, runtime_name: str, payload: dict[str, Any], updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into runtime_profiles(runtime_name, profile_json, updated_at)
                values (?, ?, ?)
                on conflict(runtime_name) do update set
                    profile_json=excluded.profile_json,
                    updated_at=excluded.updated_at
                """,
                (runtime_name, _json_dump(payload), updated_at),
            )

    def list_runtime_profiles(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select profile_json from runtime_profiles order by runtime_name").fetchall()
        return [_json_load(row["profile_json"], {}) for row in rows]

    def save_trace(self, trace_id: str, session_id: str, status: str, payload: dict[str, Any], created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into execution_traces(trace_id, session_id, status, trace_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(trace_id) do update set
                    status=excluded.status,
                    trace_json=excluded.trace_json
                """,
                (trace_id, session_id, status, _json_dump(payload), created_at),
            )

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("select trace_json from execution_traces where trace_id = ?", (trace_id,)).fetchone()
        if not row:
            return None
        return _json_load(row["trace_json"], {})

    def list_traces(self, limit: int = 100, status: str | None = None) -> list[dict[str, Any]]:
        sql = "select trace_json from execution_traces"
        params: list[Any] = []
        if status:
            sql += " where status = ?"
            params.append(status)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["trace_json"], {}) for row in rows]

    def save_critique(self, critique_id: str, trace_id: str, payload: dict[str, Any], created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into critiques(critique_id, trace_id, critique_json, created_at)
                values (?, ?, ?, ?)
                on conflict(critique_id) do update set
                    critique_json=excluded.critique_json
                """,
                (critique_id, trace_id, _json_dump(payload), created_at),
            )

    def list_critiques(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select critique_json from critiques order by created_at desc limit ?", (limit,)).fetchall()
        return [_json_load(row["critique_json"], {}) for row in rows]

    def add_memory_record(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into memory_records(memory_id, session_id, plane, role, content_json, tags_json, score_json, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(memory_id) do update set
                    role=excluded.role,
                    content_json=excluded.content_json,
                    tags_json=excluded.tags_json,
                    score_json=excluded.score_json,
                    updated_at=excluded.updated_at
                """,
                (
                    payload["memory_id"],
                    payload["session_id"],
                    payload["plane"],
                    payload.get("role"),
                    _json_dump(payload.get("content", {})),
                    _json_dump(payload.get("tags", [])),
                    _json_dump(payload.get("score", {})),
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )

    def list_memory_records(self, session_id: str, plane: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = """
            select memory_id, session_id, plane, role, content_json, tags_json, score_json, created_at, updated_at
            from memory_records where session_id = ?
        """
        params: list[Any] = [session_id]
        if plane:
            sql += " and plane = ?"
            params.append(plane)
        sql += " order by created_at asc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        output = []
        for row in rows:
            output.append(
                {
                    "memory_id": row["memory_id"],
                    "session_id": row["session_id"],
                    "plane": row["plane"],
                    "role": row["role"],
                    "content": _json_load(row["content_json"], {}),
                    "tags": _json_load(row["tags_json"], []),
                    "score": _json_load(row["score_json"], {}),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        return output

    def save_memory_analytics(self, session_id: str, payload: dict[str, Any], updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into memory_analytics(session_id, analytics_json, updated_at)
                values (?, ?, ?)
                on conflict(session_id) do update set
                    analytics_json=excluded.analytics_json,
                    updated_at=excluded.updated_at
                """,
                (session_id, _json_dump(payload), updated_at),
            )

    def get_memory_analytics(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("select analytics_json from memory_analytics where session_id = ?", (session_id,)).fetchone()
        if not row:
            return None
        return _json_load(row["analytics_json"], {})

    def save_retrieval_document(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into retrieval_documents(doc_id, source, title, content, metadata_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(doc_id) do update set
                    source=excluded.source,
                    title=excluded.title,
                    content=excluded.content,
                    metadata_json=excluded.metadata_json
                """,
                (
                    payload["doc_id"],
                    payload["source"],
                    payload.get("title"),
                    payload["content"],
                    _json_dump(payload.get("metadata", {})),
                    payload["created_at"],
                ),
            )

    def replace_retrieval_chunks(self, doc_id: str, chunks: list[dict[str, Any]]) -> None:
        with self._connect() as conn:
            conn.execute("delete from retrieval_chunks where doc_id = ?", (doc_id,))
            conn.executemany(
                """
                insert into retrieval_chunks(chunk_id, doc_id, chunk_index, source, content, metadata_json, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk["chunk_id"],
                        chunk["doc_id"],
                        chunk["chunk_index"],
                        chunk["source"],
                        chunk["content"],
                        _json_dump(chunk.get("metadata", {})),
                        chunk["created_at"],
                    )
                    for chunk in chunks
                ],
            )

    def list_retrieval_chunks(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select chunk_id, doc_id, chunk_index, source, content, metadata_json, created_at from retrieval_chunks order by created_at asc"
            ).fetchall()
        return [
            {
                "chunk_id": row["chunk_id"],
                "doc_id": row["doc_id"],
                "chunk_index": row["chunk_index"],
                "source": row["source"],
                "content": row["content"],
                "metadata": _json_load(row["metadata_json"], {}),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_experiment(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into experiments(experiment_id, kind, name, status, record_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(experiment_id) do update set
                    status=excluded.status,
                    record_json=excluded.record_json
                """,
                (
                    payload["experiment_id"],
                    payload["kind"],
                    payload["name"],
                    payload["status"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_experiments(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("select record_json from experiments order by created_at desc").fetchall()
        return [_json_load(row["record_json"], {}) for row in rows]

    def save_promotion_candidate(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into promotion_candidates(candidate_id, candidate_kind, subject_id, review_status, candidate_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(candidate_id) do update set
                    review_status=excluded.review_status,
                    candidate_json=excluded.candidate_json
                """,
                (
                    payload["candidate_id"],
                    payload["candidate_kind"],
                    payload["subject_id"],
                    payload["review_status"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def get_promotion_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select candidate_json from promotion_candidates where candidate_id = ?",
                (candidate_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["candidate_json"], {})

    def list_promotion_candidates(self, *, candidate_kind: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select candidate_json from promotion_candidates"
        params: list[Any] = []
        if candidate_kind:
            sql += " where candidate_kind = ?"
            params.append(candidate_kind)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["candidate_json"], {}) for row in rows]

    def save_promotion_evaluation(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into promotion_evaluations(evaluation_id, candidate_id, decision, evaluation_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(evaluation_id) do update set
                    decision=excluded.decision,
                    evaluation_json=excluded.evaluation_json
                """,
                (
                    payload["evaluation_id"],
                    payload["candidate_id"],
                    payload["decision"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_promotion_evaluations(self, *, candidate_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select evaluation_json from promotion_evaluations"
        params: list[Any] = []
        if candidate_id:
            sql += " where candidate_id = ?"
            params.append(candidate_id)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["evaluation_json"], {}) for row in rows]

    def latest_promotion_evaluation(self, candidate_id: str) -> dict[str, Any] | None:
        evaluations = self.list_promotion_evaluations(candidate_id=candidate_id, limit=1)
        return evaluations[0] if evaluations else None

    def save_promotion_decision(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into promotion_decisions(decision_id, candidate_id, subject_id, decision, decision_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(decision_id) do update set
                    decision=excluded.decision,
                    decision_json=excluded.decision_json
                """,
                (
                    payload["decision_id"],
                    payload["candidate_id"],
                    payload["subject_id"],
                    payload["decision"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_promotion_decisions(self, *, candidate_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select decision_json from promotion_decisions"
        params: list[Any] = []
        if candidate_id:
            sql += " where candidate_id = ?"
            params.append(candidate_id)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["decision_json"], {}) for row in rows]

    def latest_promotion_decision(self, candidate_id: str) -> dict[str, Any] | None:
        decisions = self.list_promotion_decisions(candidate_id=candidate_id, limit=1)
        return decisions[0] if decisions else None

    def save_approval(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into approvals(decision_id, subject, decision, approver, detail_json, created_at)
                values (?, ?, ?, ?, ?, ?)
                on conflict(decision_id) do update set
                    decision=excluded.decision,
                    approver=excluded.approver,
                    detail_json=excluded.detail_json
                """,
                (
                    payload["decision_id"],
                    payload["subject"],
                    payload["decision"],
                    payload["approver"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_approvals(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select detail_json from approvals order by created_at desc limit ?",
                (limit,),
            ).fetchall()
        return [_json_load(row["detail_json"], {}) for row in rows]

    def save_rollback(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into rollbacks(rollback_id, subject, status, record_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(rollback_id) do update set
                    status=excluded.status,
                    record_json=excluded.record_json
                """,
                (
                    payload["rollback_id"],
                    payload["subject"],
                    payload["status"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def save_audit_event(self, event_id: str, action: str, detail: dict[str, Any], created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into audit_events(event_id, action, detail_json, created_at)
                values (?, ?, ?, ?)
                on conflict(event_id) do update set
                    action=excluded.action,
                    detail_json=excluded.detail_json
                """,
                (event_id, action, _json_dump(detail), created_at),
            )

    def list_audit_events(self, limit: int = 200) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select event_id, action, detail_json, created_at from audit_events order by created_at desc limit ?",
                (limit,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "action": row["action"],
                "detail": _json_load(row["detail_json"], {}),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_curriculum_record(
        self,
        record_id: str,
        subject: str,
        course: str,
        status: str,
        score: float | None,
        detail: dict[str, Any],
        created_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into curriculum_transcript(record_id, subject, course, status, score, detail_json, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                on conflict(record_id) do update set
                    status=excluded.status,
                    score=excluded.score,
                    detail_json=excluded.detail_json
                """,
                (record_id, subject, course, status, score, _json_dump(detail), created_at),
            )

    def list_curriculum_records(self, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = """
            select record_id, subject, course, status, score, detail_json, created_at
            from curriculum_transcript
        """
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            {
                "record_id": row["record_id"],
                "subject": row["subject"],
                "course": row["course"],
                "status": row["status"],
                "score": row["score"],
                "detail": _json_load(row["detail_json"], {}),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_teacher_scorecard(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_scorecards(scorecard_id, subject, benchmark_family_id, scorecard_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(scorecard_id) do update set
                    scorecard_json=excluded.scorecard_json
                """,
                (
                    payload["scorecard_id"],
                    payload["subject"],
                    payload["benchmark_family_id"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_teacher_scorecards(self, *, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select scorecard_json from teacher_scorecards"
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["scorecard_json"], {}) for row in rows]

    def get_teacher_scorecard(self, scorecard_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select scorecard_json from teacher_scorecards where scorecard_id = ?",
                (scorecard_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["scorecard_json"], {})

    def save_teacher_disagreement_artifact(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_disagreement_artifacts(artifact_id, subject, registry_layer, artifact_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(artifact_id) do update set
                    artifact_json=excluded.artifact_json
                """,
                (
                    payload["artifact_id"],
                    payload["subject"],
                    payload["registry_layer"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_teacher_disagreement_artifacts(self, *, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select artifact_json from teacher_disagreement_artifacts"
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["artifact_json"], {}) for row in rows]

    def save_teacher_evidence_bundle(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_evidence_bundles(bundle_id, subject, registry_layer, bundle_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(bundle_id) do update set
                    bundle_json=excluded.bundle_json
                """,
                (
                    payload["bundle_id"],
                    payload["subject"],
                    payload["registry_layer"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def get_teacher_evidence_bundle(self, bundle_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select bundle_json from teacher_evidence_bundles where bundle_id = ?",
                (bundle_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["bundle_json"], {})

    def list_teacher_evidence_bundles(self, *, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select bundle_json from teacher_evidence_bundles"
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["bundle_json"], {}) for row in rows]

    def save_takeover_scorecard(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into takeover_scorecards(scorecard_id, subject, bundle_id, scorecard_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(scorecard_id) do update set
                    scorecard_json=excluded.scorecard_json
                """,
                (
                    payload["scorecard_id"],
                    payload["subject"],
                    payload.get("teacher_evidence_bundle_id"),
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def get_takeover_scorecard(self, scorecard_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select scorecard_json from takeover_scorecards where scorecard_id = ?",
                (scorecard_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["scorecard_json"], {})

    def list_takeover_scorecards(self, *, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select scorecard_json from takeover_scorecards"
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["scorecard_json"], {}) for row in rows]

    def save_retirement_shadow_record(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into retirement_shadow_log(record_id, teacher_id, decision, record_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(record_id) do update set
                    decision=excluded.decision,
                    record_json=excluded.record_json
                """,
                (
                    payload["record_id"],
                    payload["teacher_id"],
                    payload["decision"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_retirement_shadow_records(self, *, teacher_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select record_json from retirement_shadow_log"
        params: list[Any] = []
        if teacher_id:
            sql += " where teacher_id = ?"
            params.append(teacher_id)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["record_json"], {}) for row in rows]

    def save_teacher_trend_scorecard(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_trend_scorecards(trend_id, subject, benchmark_family_id, trend_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(trend_id) do update set
                    trend_json=excluded.trend_json
                """,
                (
                    payload["trend_id"],
                    payload["subject"],
                    payload["benchmark_family_id"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def get_teacher_trend_scorecard(self, trend_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select trend_json from teacher_trend_scorecards where trend_id = ?",
                (trend_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["trend_json"], {})

    def list_teacher_trend_scorecards(
        self,
        *,
        subject: str | None = None,
        benchmark_family_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        sql = "select trend_json from teacher_trend_scorecards"
        params: list[Any] = []
        clauses: list[str] = []
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if benchmark_family_id:
            clauses.append("benchmark_family_id = ?")
            params.append(benchmark_family_id)
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["trend_json"], {}) for row in rows]

    def save_takeover_trend_report(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into takeover_trend_reports(trend_id, subject, trend_json, created_at)
                values (?, ?, ?, ?)
                on conflict(trend_id) do update set
                    trend_json=excluded.trend_json
                """,
                (
                    payload["trend_id"],
                    payload["subject"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def get_takeover_trend_report(self, trend_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "select trend_json from takeover_trend_reports where trend_id = ?",
                (trend_id,),
            ).fetchone()
        if not row:
            return None
        return _json_load(row["trend_json"], {})

    def list_takeover_trend_reports(self, *, subject: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        sql = "select trend_json from takeover_trend_reports"
        params: list[Any] = []
        if subject:
            sql += " where subject = ?"
            params.append(subject)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["trend_json"], {}) for row in rows]

    def save_teacher_benchmark_fleet_summary(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_benchmark_fleet_summaries(summary_id, fleet_id, subject, summary_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(summary_id) do update set
                    summary_json=excluded.summary_json
                """,
                (
                    payload["summary_id"],
                    payload["fleet_id"],
                    payload.get("subject"),
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_teacher_benchmark_fleet_summaries(
        self,
        *,
        fleet_id: str | None = None,
        subject: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        sql = "select summary_json from teacher_benchmark_fleet_summaries"
        params: list[Any] = []
        clauses: list[str] = []
        if fleet_id:
            clauses.append("fleet_id = ?")
            params.append(fleet_id)
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["summary_json"], {}) for row in rows]

    def save_teacher_cohort_scorecard(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into teacher_cohort_scorecards(cohort_id, fleet_id, subject, cohort_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(cohort_id) do update set
                    cohort_json=excluded.cohort_json
                """,
                (
                    payload["cohort_id"],
                    payload["fleet_id"],
                    payload.get("subject"),
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_teacher_cohort_scorecards(
        self,
        *,
        fleet_id: str | None = None,
        subject: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        sql = "select cohort_json from teacher_cohort_scorecards"
        params: list[Any] = []
        clauses: list[str] = []
        if fleet_id:
            clauses.append("fleet_id = ?")
            params.append(fleet_id)
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["cohort_json"], {}) for row in rows]

    def save_replacement_readiness_report(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into replacement_readiness_reports(report_id, subject, teacher_id, report_json, created_at)
                values (?, ?, ?, ?, ?)
                on conflict(report_id) do update set
                    report_json=excluded.report_json
                """,
                (
                    payload["report_id"],
                    payload["subject"],
                    payload["teacher_id"],
                    _json_dump(payload),
                    payload["created_at"],
                ),
            )

    def list_replacement_readiness_reports(
        self,
        *,
        subject: str | None = None,
        teacher_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        sql = "select report_json from replacement_readiness_reports"
        params: list[Any] = []
        clauses: list[str] = []
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if teacher_id:
            clauses.append("teacher_id = ?")
            params.append(teacher_id)
        if clauses:
            sql += " where " + " and ".join(clauses)
        sql += " order by created_at desc limit ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_json_load(row["report_json"], {}) for row in rows]
