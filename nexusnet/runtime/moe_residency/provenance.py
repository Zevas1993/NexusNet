from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ColibriAssimilationProvenance:
    repository: str = "https://github.com/JustVugg/colibri"
    commit: str = "748787c3afa8ab336bb51bf616f212a04f209bba"
    license: str = "Apache-2.0"
    eligible_attributed_sources: tuple[str, ...] = (
        "c/tier.h",
        "c/resource_plan.py",
    )
    conceptual_sources: tuple[str, ...] = (
        "c/st.h",
        "c/glm.c",
        "docs/grammar-draft.md",
        "docs/experiments/glm52-6x5090-2026-07-12.md",
    )
    excluded_sources: tuple[str, ...] = ("c/openai_server.py",)

    def as_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "commit": self.commit,
            "license": self.license,
            "eligible_attributed_sources": list(self.eligible_attributed_sources),
            "conceptual_sources": list(self.conceptual_sources),
            "excluded_sources": list(self.excluded_sources),
            "assimilation_classification": "independent-behavioral-assimilation",
            "source_sha256": {
                "c/tier.h": "93c2a90ebb233f30a9cf1a5adb6228583ab4ad9ca9caad1bd5bfdcf336364625",
                "c/resource_plan.py": "dfd18afc3e419c6a8afba97d3d893ec69ca4db4b41560abc910fd94e052f797c",
            },
            "destination_sha256": {
                "nexusnet/runtime/moe_residency/heat.py": "7b0eec65dba422090e86588ee70ddd6d00e8de3edffb7934a697b835e98e7bfb",
                "nexusnet/runtime/moe_residency/planner.py": "edbf4dd163e059b3bdc66743e4c01da7920540393e2e9779a5cc9ac69799b96f",
            },
            "license_file": "docs/third-party/licenses/Apache-2.0-Colibri.txt",
            "integration_boundary": "native-nexusnet-runtime-no-colibri-provider-server-cli-or-process",
        }
