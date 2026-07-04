# WASM Component Tool Sandbox Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet tool manifests, runtime adapters, and sandbox policy gates.

## Source Evidence

- WebAssembly Component Model docs: https://component-model.bytecodealliance.org/design/component-model-concepts.html
- Wasmtime introduction: https://docs.wasmtime.dev/
- Component Model running components docs: https://component-model.bytecodealliance.org/running-components.html
- WASI reference site: https://wasi.dev/
- Source status: official docs from Bytecode Alliance, Wasmtime, and WASI.

## Finding

The WebAssembly Component Model and WASI create a practical pattern for portable, interface-described tools with explicit host imports. Wasmtime already frames WebAssembly, WASI, and the Component Model as one runtime surface. This is a strong fit for NexusNet tools that should not receive ambient file, network, clock, or process authority.

## NexusNet Assimilation Target

Create a WASM-backed tool capsule lane for third-party or high-risk tools. A NexusNet tool should be able to run as a component with a typed interface, explicit WASI capability grant, bounded compute, and traceable host calls.

## Proposed NexusNet Components

- `WasmToolCapsule`: signed component artifact, WIT interface, hash, source status, and license.
- `WasiCapabilityManifest`: allowed filesystem roots, network hosts, clocks, randomness, environment variables, and stdout/stderr policy.
- `ComponentAbiContract`: typed import/export schema checked before registration.
- `ToolSandboxRunner`: executes the component with fuel, timeout, memory, and output limits.
- `HostCallTrace`: records every host import call and links it to the run trace.

## Promotion Gates

- Deny all host imports unless listed in the capability manifest.
- Require artifact signature, hash, and source lineage before installing a component.
- Enforce fuel, memory, wall-clock timeout, and output byte limits.
- Reject components whose declared imports exceed the requested tool purpose.
- Test sandbox escape attempts before allowing any marketplace-style tool onboarding.

## Risks

- WASI and Component Model tooling still evolves, so ABI stability needs version pinning.
- GPU and native library access do not naturally fit the WASM sandbox.
- Host functions can reintroduce risk if they are too broad or poorly audited.
