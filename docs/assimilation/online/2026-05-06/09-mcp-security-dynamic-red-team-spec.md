# MCP Security And Dynamic Red Team Spec

Status: P0 online assimilation target. Research-only until mapped to NexusNet protocol/security modules.

## Source Evidence

- MCP latest specification: https://modelcontextprotocol.io/specification/2025-11-25
- CSA MCP STDIO design flaw note: https://labs.cloudsecurityalliance.org/research/csa-research-note-mcp-rce-design-vulnerability-20260423-csa/
- OX Security MCP supply-chain report page: https://www.ox.security/resource-category/whitepapers-and-reports/mother-of-all-ai-supply-chains/
- MCP tool-poisoning threat modeling paper: https://arxiv.org/abs/2603.22489
- Breaking the Protocol / MCPBench paper: https://arxiv.org/abs/2601.17549
- AgentDyn dynamic prompt-injection benchmark: https://arxiv.org/abs/2602.03117
- Source status: official spec plus security advisories and primary paper pages.

## Finding

MCP is now a central tool/context protocol, but current research and advisories show recurring risks around STDIO command execution, tool poisoning through metadata, capability claims without strong attestation, sampling/origin confusion, dynamic prompt injection, and multi-server trust propagation.

## NexusNet Assimilation Target

Create a zero-trust MCP and tool-protocol gate. NexusNet should treat MCP servers as untrusted dependencies until identity, command source, transport, permissions, tool descriptions, and runtime behavior are validated.

## Proposed NexusNet Components

- `ProtocolServerPassport`: transport, command path, package identity, source registry, version, signature, and privilege scope.
- `STDIOExecutionGate`: blocks dynamic command strings, repo-supplied MCP config, shell metacharacter expansion, and unknown binary paths.
- `ToolDescriptionScanner`: compares tool metadata against trusted baselines and detects hidden instructions or unexpected behavior changes.
- `CapabilityAttestationRecord`: separates claimed capabilities from verified capabilities.
- `DynamicInjectionSuite`: runs AgentDyn-style shopping, GitHub, and daily-life prompt-injection cases against NexusNet tool flows.

## Promotion Gates

- Disable or sandbox STDIO by default unless explicitly required.
- Require operator consent for every new server, changed tool description, or expanded scope.
- Never let MCP server-supplied descriptions become privileged instructions.
- Persist deny/allow decisions with provenance and expiration.

## Risks

- Protocol security information is moving quickly; re-check advisories before implementation.
- Some public advisories are vendor-disputed; use them as threat models, not final legal claims.
- Strong gating may reduce plug-and-play ergonomics, but the alternative is unacceptable authority leakage.
