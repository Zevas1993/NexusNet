from __future__ import annotations

from pathlib import Path

from nexusnet.tools.extensions.catalog import ExtensionCatalogService


def test_extension_catalog_reuses_bundle_records_across_snapshot_summary_calls(tmp_path: Path):
    service = ExtensionCatalogService(
        runtime_configs={
            "goose_lane": {
                "extensions": {
                    "catalog": [
                        {
                            "extension_id": "alpha",
                            "label": "Alpha",
                            "extension_kind": "mcp",
                            "enabled": True,
                            "workspace_scopes": ["default"],
                            "roots": [],
                        },
                        {
                            "extension_id": "beta",
                            "label": "Beta",
                            "extension_kind": "mcp",
                            "enabled": True,
                            "workspace_scopes": ["default"],
                            "roots": [],
                        },
                    ]
                }
            }
        },
        project_root=str(tmp_path),
    )
    service.policy.policy_set_summary = lambda: {
        "items": [],
        "status_counts": {},
        "history_count": 0,
        "rollouts": {"family_count": 0, "status_counts": {}, "latest_bundle_family": None},
    }

    calls: list[str] = []

    def counted_bundle_record(*, item: dict, workspace_id: str) -> dict:
        calls.append(str(item["extension_id"]))
        return {
            **item,
            "created_at": item["extension_id"],
            "enabled_state": "enabled",
            "approval_path": {"decision": "allow"},
            "high_risk_tools": [],
            "policy_set_id": f"{item['extension_id']}-policy",
            "bundle_family": "test",
            "certification_status": "certified",
        }

    service._bundle_record = counted_bundle_record  # type: ignore[method-assign]

    first = service.summary(workspace_id="default")
    second = service.summary(workspace_id="default")
    policy_sets = service.policy_set_summary(workspace_id="default")

    assert first["extension_count"] == 2
    assert second["extension_count"] == 2
    assert policy_sets["workspace_id"] == "default"
    assert calls == ["alpha", "beta"]
