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
                "c/tier.h": "1971c5325fc4ffe5dce17e50d7781dc64ef31d14ebf354cb2452ca6c13a3d495",
                "c/resource_plan.py": "07a9549fed35fe080468b12eae38fe5e576a851efcd157cb3fd47353019f9980",
            },
            "destination_sha256": {
                "nexusnet/runtime/moe_residency/heat.py": "7b0eec65dba422090e86588ee70ddd6d00e8de3edffb7934a697b835e98e7bfb",
                "nexusnet/runtime/moe_residency/planner.py": "d8d88511a82e6c6b0225900b61ea5024bd2b817e4bbab240de8d38b034bd6ea2",
            },
            "license_file": "docs/third-party/licenses/Apache-2.0-Colibri.txt",
            "integration_boundary": "native-nexusnet-runtime-no-colibri-provider-server-cli-or-process",
        }
