from __future__ import annotations

import time

from pydantic import BaseModel, ConfigDict, Field

from .schemas import CalibrationMetric


class CalibrationLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    memory_bytes: int = Field(default=4 * 1024 * 1024, gt=0, le=16 * 1024 * 1024)
    memory_rounds: int = Field(default=3, gt=0, le=8)
    compute_iterations: int = Field(default=20_000, gt=0, le=100_000)


class BoundedHostCalibrator:
    def __init__(self, *, limits: CalibrationLimits | None = None) -> None:
        self.limits = limits or CalibrationLimits()

    def calibrate(self) -> list[CalibrationMetric]:
        return [self._memory_copy_metric(), self._cpu_compute_metric()]

    def _memory_copy_metric(self) -> CalibrationMetric:
        source = bytearray((index % 251 for index in range(self.limits.memory_bytes)))
        target = bytearray(self.limits.memory_bytes)
        started = time.perf_counter()
        for _ in range(self.limits.memory_rounds):
            target[:] = source
        duration = max(time.perf_counter() - started, 1e-9)
        transferred = self.limits.memory_bytes * self.limits.memory_rounds
        return CalibrationMetric(
            metric_id="memory-copy-gib-s",
            value=max(transferred / duration / 1024**3, 1e-12),
            unit="GiB/s",
            sample_count=self.limits.memory_rounds,
            duration_ms=max(duration * 1000, 1e-9),
            target_node_ids=["ram:0"],
        )

    def _cpu_compute_metric(self) -> CalibrationMetric:
        accumulator = 0x9E3779B1
        started = time.perf_counter()
        for index in range(self.limits.compute_iterations):
            accumulator = ((accumulator ^ index) * 1_664_525 + 1_013_904_223) & 0xFFFFFFFF
        duration = max(time.perf_counter() - started, 1e-9)
        if accumulator < 0:
            raise AssertionError("unreachable unsigned calibration state")
        return CalibrationMetric(
            metric_id="cpu-scalar-mops",
            value=max(self.limits.compute_iterations / duration / 1_000_000, 1e-12),
            unit="Mop/s",
            sample_count=self.limits.compute_iterations,
            duration_ms=max(duration * 1000, 1e-9),
            target_node_ids=["cpu:0"],
        )
