from __future__ import annotations

from nexus.memory import MemoryService
from nexus.schemas import MemoryRecord, MemoryScore, Message
from nexus.storage import NexusStore

from ..schemas import BenchmarkRun, CompressionTrace, InferenceTrace, SessionContext


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


class NeuralMemoryCortex:
    def __init__(self, memory: MemoryService, store: NexusStore):
        self.memory = memory
        self.store = store

    def recent_messages(self, session_id: str, limit: int = 6) -> list[Message]:
        return self.memory.recent_messages(session_id, limit=limit)

    def compress_prompt(self, prompt: str, target_tokens: int = 512) -> tuple[str, CompressionTrace | None]:
        if not prompt.strip():
            return prompt, None
        before = _estimate_tokens(prompt)
        if before <= target_tokens:
            return prompt, None
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        if len(lines) <= 8:
            keep = lines[:]
        else:
            head = lines[:4]
            tail = lines[-3:]
            middle = [line for line in lines[4:-3] if line.lower().startswith("user request:") or line.lower().startswith("retrieved context:")]
            keep = head + middle[:2] + tail
        summary = "\n".join(keep)
        after = _estimate_tokens(summary)
        loss_estimate = round(min(0.95, max(0.0, 1.0 - (after / max(before, 1)))), 3)
        trace = CompressionTrace(
            strategy="dual-track-summary",
            original_chars=len(prompt),
            compressed_chars=len(summary),
            estimated_tokens_before=before,
            estimated_tokens_after=after,
            loss_estimate=loss_estimate,
            summary=summary,
        )
        return summary, trace

    def record_inference(
        self,
        *,
        session_context: SessionContext,
        prompt: str,
        output: str,
        trace: InferenceTrace,
        retrieval_hits: int,
    ) -> int:
        written = 0
        self.memory.append_messages(session_context.session_id, [Message(role="user", content=prompt)])
        written += 1
        self.memory.append_messages(session_context.session_id, [Message(role="assistant", content=output)])
        written += 1
        self.memory.record_episode(session_context.session_id, trace.trace_id, prompt[:240], output[:240])
        written += 1
        self._record_extra(
            session_id=session_context.session_id,
            plane="optimization",
            content={
                "trace_id": trace.trace_id,
                "runtime_name": trace.runtime_name,
                "model_id": trace.model_id,
                "latency_ms": trace.latency_ms,
                "retrieval_hit_count": retrieval_hits,
                "compression": trace.compression.model_dump(mode="json") if trace.compression else None,
            },
            tags=["nexusnet", "inference", "optimization"],
            score=MemoryScore(relevance=0.6, freshness=0.9, importance=0.8),
        )
        written += 1
        return written

    def record_benchmark_run(self, run: BenchmarkRun) -> MemoryRecord:
        return self._record_extra(
            session_id=f"benchmark::{run.suite_name}",
            plane="benchmark",
            content=run.model_dump(mode="json"),
            tags=["nexusnet", "benchmark"],
            score=MemoryScore(relevance=0.8, freshness=0.8, importance=0.9, success_history=run.pass_rate),
        )

    def record_curriculum_state(self, subject: str, detail: dict) -> MemoryRecord:
        return self._record_extra(
            session_id=subject,
            plane="curriculum",
            content=detail,
            tags=["nexusnet", "curriculum"],
            score=MemoryScore(relevance=0.7, freshness=0.7, importance=0.9),
        )

    def record_dream_episode(self, subject: str, detail: dict) -> MemoryRecord:
        return self._record_extra(
            session_id=subject,
            plane="dream",
            content=detail,
            tags=["nexusnet", "dream"],
            score=MemoryScore(relevance=0.7, freshness=0.8, importance=0.8),
        )

    def record_architecture_change(self, subject: str, detail: dict) -> MemoryRecord:
        return self._record_extra(
            session_id=subject,
            plane="architecture",
            content=detail,
            tags=["nexusnet", "architecture"],
            score=MemoryScore(relevance=0.8, freshness=0.7, importance=1.0),
        )

    def _record_extra(self, *, session_id: str, plane: str, content: dict, tags: list[str], score: MemoryScore) -> MemoryRecord:
        record = MemoryRecord(session_id=session_id, plane=plane, content=content, tags=tags, score=score)
        self.store.add_memory_record(record.model_dump(mode="json"))
        return record
