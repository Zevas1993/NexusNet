# BrowserGym Web Agent Harness Spec

Status: P1 online assimilation target. Research-only until benchmark licenses, container setup, and browser-control safety boundaries are inspected locally.

## Source Evidence

- BrowserGym repository: https://github.com/ServiceNow/BrowserGym
- WorkArena paper: https://arxiv.org/abs/2403.07718
- BrowserGym ecosystem source status: public repository with bundled benchmark adapters for MiniWoB, WebArena, WebArenaVerified, VisualWebArena, WorkArena, AssistantBench, WebLINX, OpenApps, and TimeWarp.

## Finding

BrowserGym is a Gym-style environment layer for browser agents. Its strongest assimilation value is not a single leaderboard score; it is the shared task abstraction for web observations, browser actions, benchmark adapters, traces, and repeatable agent loops across multiple browser-task families.

## NexusNet Assimilation Target

Create a BrowserOps certification harness before NexusNet gives any agent broad web-control authority. Browser tasks should run through explicit task passports, browser traces, allowlisted environments, and deterministic result checks where possible.

## Proposed NexusNet Components

- `BrowserTaskPassport`: start URL, allowed domains, credential policy, action set, timeout, evaluator, and privacy class.
- `BrowserActionTrace`: screenshot digest, DOM snapshot digest, action, coordinates or selector, model rationale reference, and result.
- `BrowserHarnessAdapter`: maps NexusNet VisualOps/browser control into a BrowserGym-like environment loop.
- `WebBenchmarkRegistry`: keeps WebArena, WorkArena, AssistantBench, OpenApps, and custom tasks separate from live user browsing.
- `Control Panel`: replay browser traces, show failed actions, highlight blocked domains, and compare agent runs.

## Promotion Gates

- Run benchmarks in isolated browser profiles with no user cookies or personal credentials.
- Prefer local or benchmark-hosted sites before live public websites.
- Require domain allowlists, step limits, network logs, and screenshot redaction.
- Separate benchmark success from production authority.

## Risks

- Browser benchmarks can drift when sites, dependencies, or hosted environments change.
- Web-control agents can leak private information if profiles or screenshots are not isolated.
- A benchmark abstraction can hide whether success came from robust perception, brittle selectors, or task-specific shortcuts.
