from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from nexusnet.runtime.evolutionary_inference.schemas import (
    HardwareCapabilityGraph,
    HardwareProbeObservation,
)


@pytest.mark.parametrize(
    ("field_name", "raw_value"),
    [
        ("probe_id", "PCI\\\\VEN_10DE&DEV_2C05"),
        ("reason_code", "C:/Users/private"),
        ("probe_source", "COMPUTERNAME=HOST"),
        ("reason_code", "command output\\nwith multiple lines"),
    ],
)
def test_hardware_probe_observation_rejects_raw_or_sensitive_receipt_values(field_name, raw_value):
    observation = {
        "probe_id": "windows-cim-video-controller",
        "available": False,
        "reason_code": "cim-query-failed",
        "probe_source": "windows-cim",
    }
    observation[field_name] = raw_value

    with pytest.raises(ValidationError):
        HardwareProbeObservation(**observation)


def test_hardware_graph_preserves_failed_windows_cim_probe_as_strict_observation():
    graph = HardwareCapabilityGraph(
        host_fingerprint="a" * 32,
        collected_at=datetime(2026, 7, 18, tzinfo=timezone.utc),
        nodes=[],
        links=[],
        adapters=[],
        discovery_observations=[
            HardwareProbeObservation(
                probe_id="windows-cim-video-controller",
                available=False,
                reason_code="cim-query-failed",
                verification_state="unavailable",
                probe_source="windows-cim",
            )
        ],
    )

    assert graph.model_dump(mode="json")["discovery_observations"] == [
        {
            "probe_id": "windows-cim-video-controller",
            "available": False,
            "reason_code": "cim-query-failed",
            "device_count": 0,
            "verification_state": "unavailable",
            "probe_source": "windows-cim",
        }
    ]
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        HardwareProbeObservation(
            probe_id="windows-cim-video-controller",
            available=False,
            reason_code="cim-query-failed",
            probe_source="windows-cim",
            private_error="C:/Users/private",
        )
