# Computer Fabric v1 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the ten approved Computer Fabric hardening upgrades sequentially: provider registry, snapshot/rewind, approval queue, secrets broker, prompt-injection firewall, artifact trust bridge, skill compiler, persistent governor, eval gauntlet, and replay cockpit.

**Architecture:** Keep the work inside the isolated `nexusnet/computer_fabric` package. Add small focused modules for each concern and wire their summaries into `ComputerFabricService.start_session()` and `ComputerFabricService.scorecard()`. Do not wire API/UI routes in this pass because the isolated branch still has a pre-existing full-suite failure in the API import path.

**Tech Stack:** Python 3.11, dataclasses, pathlib/json/hashlib, pytest.

---

## Sequential Tasks

1. Provider registry: create provider records and capability probes for `venv`, `docker`, `podman`, `wsl`, `devcontainer`, `remote-vm`, `browser-operator`, and `local-cli-bridge`.
2. Snapshot/rewind: write checkpoint metadata, artifact hash set, env manifest, dependency lock placeholder, and cleanup/rewind proof.
3. Approval queue: create approval request records for approval-required actions without treating them as hard policy failure.
4. Secrets broker: create scoped secret references with TTL, mount mode, redaction policy, audit refs, and no secret values.
5. Prompt firewall: classify operator instruction, system policy, webpage/document/repo/OCR/tool evidence, and block external evidence from authority.
6. Artifact trust bridge: write final bundle first, then trust bridge summary after artifact index generation.
7. Skill compiler: convert successful sessions into governed skill candidates with inputs, tools, checks, failure modes, artifacts, evals, and rollback.
8. Persistent governor: emit uptime, disk, network, public URL, port, cost, backup, and kill-switch policy for persistent computers.
9. Eval gauntlet: add benchmark cases and scoring for reliability, cost, latency, cleanup, trust, and policy compliance.
10. Replay cockpit: expand scorecard with timeline, commands, file diff, approvals, provider state, cleanup proof, and promotion blockers.

## Verification

Run after each task:

```powershell
python -m pytest tests/test_computer_fabric.py -q
```

Run before final commit:

```powershell
@'
from pathlib import Path
from nexusnet.computer_fabric import ComputerFabricService, ComputerSessionRequest
service = ComputerFabricService(artifacts_dir=Path("runtime/test-computer-fabric-artifacts"))
summary = service.start_session(ComputerSessionRequest(goal="verify v1", task_type="repo patch + tests", requested_tools=["shell.test"], privacy_class="project-internal"))
print(summary.status)
print(service.scorecard()["control_panel_label"])
print(service.scorecard()["replay_cockpit"]["timeline_count"])
'@ | python -
```
