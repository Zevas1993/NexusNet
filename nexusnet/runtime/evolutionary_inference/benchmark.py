from __future__ import annotations

import hashlib
import json
from statistics import mean, median, pstdev

from .schemas import ExecutionPlan, PlanEvidence, TransferRequest, WorkloadProfile
from .transfer import TransferExecutor


class PlanBenchmark:
    def __init__(self, transfer_executor: TransferExecutor) -> None:
        self.transfer_executor = transfer_executor

    def run(self, plan: ExecutionPlan, workload: WorkloadProfile, repeat_count: int = 3, cancel_check=None) -> PlanEvidence:
        transfer_kind = "pageable"
        backend = "portable"
        direction = "host-to-host"
        if "transfer.double-buffered" in plan.primitive_ids:
            transfer_kind = "double-buffered"
        elif "transfer.accelerator-resident" in plan.primitive_ids:
            transfer_kind = "accelerator"
            backend = "cuda"
            direction = "host-to-device"
        elif "transfer.unified-memory" in plan.primitive_ids:
            transfer_kind = "accelerator"
            backend = "metal"
            direction = "host-to-device"
        benchmark_bytes = min(max(64 * 1024, workload.batch_size * (workload.prompt_tokens + workload.max_new_tokens) * 512), 4 * 1024 * 1024)
        request = TransferRequest(
            kind=transfer_kind,
            bytes=benchmark_bytes,
            chunk_bytes=min(int(plan.parameters.get("chunk_bytes", 256 * 1024)), benchmark_bytes),
            repeat_count=repeat_count,
            compute_iterations=int(plan.parameters.get("compute_iterations", 128)),
            backend=backend,
            direction=direction,
        )
        transfer = self.transfer_executor.execute(request, cancel_check=cancel_check)
        measurements = transfer.duration_ms
        warm = median(measurements[1:] or measurements) if measurements else None
        uncertainty = pstdev(measurements) / mean(measurements) if len(measurements) > 1 and mean(measurements) else 1.0
        status = transfer.status
        checksum = hashlib.sha256(
            json.dumps(
                {
                    "workload": workload.model_dump(mode="json"),
                    "quality": plan.quality_semantics,
                    "equivalent": transfer.checksum_equivalent,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        return PlanEvidence(
            evidence_id=f"plan-evidence::{hashlib.sha256((plan.plan_id + checksum + str(measurements)).encode()).hexdigest()[:24]}",
            plan=plan,
            status=status,
            repeat_count=len(measurements),
            cold_latency_ms=measurements[0] if measurements else None,
            warm_latency_ms=warm,
            throughput_tokens_s=(workload.max_new_tokens * 1000 / warm) if warm else 0,
            peak_ram_bytes=benchmark_bytes * max(1, int(plan.parameters.get("buffer_depth", 1))),
            peak_vram_bytes=plan.estimated_peak_vram_bytes,
            bytes_moved=transfer.bytes_moved,
            quality_equivalent=transfer.checksum_equivalent and plan.quality_semantics == "bit-equivalent",
            stable=status == "completed" and uncertainty <= 0.75,
            uncertainty=max(uncertainty, 0.0),
            measurements_ms=measurements,
            checksum=checksum,
            reason_codes=transfer.reason_codes,
        )
