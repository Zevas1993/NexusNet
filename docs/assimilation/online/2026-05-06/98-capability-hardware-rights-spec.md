# Capability Hardware Rights Spec

Status: P2 online assimilation target. Research-only until NexusNet has native helper or embedded runtime surfaces that justify hardware-capability planning.

## Source Evidence

- CHERI project page: https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- CHERI C/C++ capabilities guide: https://ctsrd-cheri.github.io/cheri-c-programming/background/cheri-capabilities.html
- CHERI capability permissions guide: https://ctsrd-cheri.github.io/cheri-c-programming/apis/capability-permissions.html
- FreeBSD Capsicum manual: https://man.freebsd.org/cgi/man.cgi?query=capsicum
- Source status: official university/project documentation and OS manual page.

## Finding

CHERI extends processor architectures with hardware-enforced capabilities for fine-grained memory protection and compartmentalization. Capsicum shows the same authority idea at the OS API level: explicit handles confer limited rights. For NexusNet, this is a north-star primitive for native helper safety.

## NexusNet Assimilation Target

Plan native helpers, local runtimes, and embedded modules around handle-scoped rights rather than ambient process authority. Even without CHERI hardware, the same model can shape APIs: a component receives only the memory, file, model, socket, or tool handle it needs.

## Proposed NexusNet Components

- `NativeCapabilityHandle`: typed authority token for memory buffers, files, model contexts, sockets, and tools.
- `HandleRightsMask`: read, write, execute, seek, resize, network, export, and delegate flags.
- `CompartmentBoundaryProbe`: test helper that attempts out-of-bounds memory or unauthorized handle use.
- `CapabilityDowngradePath`: reduces rights before passing a handle to lower-trust code.
- `NativeHelperRightsAudit`: reports ambient authority still present in native helpers.

## Promotion Gates

- Avoid broad process globals in native helper APIs.
- Prefer passing explicit handles with minimal rights.
- Record which native component received which handle and for what run.
- Test downgrade, revocation, and confused-deputy scenarios.
- Treat CHERI and Capsicum as design references unless the deployment platform actually supports them.

## Risks

- Hardware capabilities are not widely available on commodity user machines.
- Capability APIs can be awkward if retrofitted after broad global access exists.
- Handle rights do not solve prompt injection or policy mistakes by themselves.
