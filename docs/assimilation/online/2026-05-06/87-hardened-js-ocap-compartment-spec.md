# Hardened JS Ocap Compartment Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet UI extensions and JavaScript tool execution.

## Source Evidence

- Endo SES module docs: https://docs.endojs.org/modules/ses.html
- Endo and HardenedJS reference: https://docs.endojs.org/documents/reference.html
- LavaMoat docs: https://lavamoat.github.io/
- Source status: official Endo/SES and LavaMoat documentation.

## Finding

SES/HardenedJS applies object-capability programming to JavaScript compartments: code receives no ambient authority by default and can only use capabilities explicitly endowed by the host. This is a useful model for plugin UI, browser-adjacent helpers, and JavaScript tools where a full VM may be too heavy.

## NexusNet Assimilation Target

Add a JavaScript compartment lane for NexusNet extensions. Third-party UI plugins and lightweight tools should run in compartments with frozen intrinsics, explicit endowments, import maps, and effect traces.

## Proposed NexusNet Components

- `JsCompartmentManifest`: module graph, endowments, import map, resource limits, and source digest.
- `HardenedPluginRunner`: locks down intrinsics and evaluates plugin modules in compartments.
- `EndowmentPolicy`: maps declared plugin purpose to allowed host APIs.
- `CompartmentImportAudit`: reports unexpected imports, dynamic evaluation, and blocked globals.
- `PluginSupplyChainPolicy`: combines compartment restrictions with package provenance.

## Promotion Gates

- No default `fetch`, filesystem, process, clock, or connector access.
- Freeze shared intrinsics before loading untrusted plugins.
- Require explicit endowments for every host capability.
- Trace host calls and module imports.
- Fuzz plugins for access to blocked globals and prototype pollution attempts.

## Risks

- JavaScript sandboxing depends on correct host hardening.
- CPU and memory exhaustion still need separate limits.
- Supply-chain attacks can occur before code reaches the compartment if dependencies are not governed.
