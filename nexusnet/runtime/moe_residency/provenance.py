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
            "integration_boundary": "native-nexusnet-runtime-no-colibri-provider-server-cli-or-process",
        }
