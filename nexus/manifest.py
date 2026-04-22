from __future__ import annotations


def build_workspace_manifest(services) -> str:
    lines = [
        "# Nexus Workspace Manifest",
        "",
        f"- Version: {services.version}",
        f"- Database: `{services.paths.database_path}`",
        f"- UI: `{services.paths.ui_dir}`",
        "",
        "## Runtime Surface",
    ]
    for profile in services.runtime_registry.list_profiles():
        mode = profile.health.get("mode", "unknown")
        lines.append(f"- `{profile.runtime_name}`: available={profile.available}, mode={mode}")
    lines.append("")
    lines.append("## Models")
    for model in services.model_registry.list_models()[:20]:
        lines.append(f"- `{model.model_id}` -> `{model.runtime_name}` available={model.available}")
    lines.append("")
    lines.append("## AOs")
    if hasattr(services, "brain_aos"):
        for descriptor in services.brain_aos.snapshot().active_aos:
            lines.append(f"- `{descriptor['name']}`: {descriptor['description']}")
    else:
        for descriptor in services.ao_registry.list():
            lines.append(f"- `{descriptor.name}`: {descriptor.description}")
    lines.append("")
    lines.append("## Agents")
    for descriptor in services.agent_registry.list():
        lines.append(f"- `{descriptor.name}`: {descriptor.description}")
    lines.append("")
    lines.append("## Tools")
    for manifest in services.tool_registry.list():
        lines.append(f"- `{manifest.tool_name}` ({manifest.permission_class})")
    return "\n".join(lines)
