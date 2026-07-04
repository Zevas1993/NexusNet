# Next Watch And Source Candidates

Status: research docket. The three P0 videos listed first were watched locally on 2026-05-06 and now have spec sheets in this packet; the remaining items are not yet watched with the local video watcher.

Purpose: identify the next videos to download/watch and the primary online sources to inspect for additional NexusNet assimilation targets. Keep all imported ideas refs-only until a later implementation pass validates them against the live NexusNet code and governance boundaries.

## Recommended Download Queue

| Priority | Candidate | Link | Why watch it | NexusNet assimilation target |
|---|---|---|---|---|
| P0 watched | World's First SELF IMPROVING CODING AI AGENT - Darwin Godel Machine | https://www.youtube.com/watch?v=1XXxG6PqzOY | Watched locally. See [Darwin Godel Machine Lineage](08-darwin-godel-machine-lineage-spec.md). | Add a DGM-style lineage archive and eval-gated offspring review path to Recursive Dreaming, Deep Replay, Teacher Council review, and KAC refs-only artifacts. |
| P0 watched | New maths discoveries! All announced at once! | https://www.youtube.com/watch?v=sGCmu7YKgPA | Watched locally. See [AlphaEvolve Verifier Search](09-alphaevolve-verifier-search-spec.md). | Extract evaluator-first design patterns: objective scorer, candidate database, mutation lineage, and proof/result handoff for NexusNet research modes. |
| P0 watched | TARS Agent: Powerful AI Operating System Can Automate ALL Computer Tasks! | https://www.youtube.com/watch?v=vF8FWmzRd5M | Watched locally. See [TARS Computer-Use Operator](10-tars-computer-use-operator-spec.md). | Improve VisualOps/browser-control planning with explicit action logs, permission gates, UI-grounding confidence, and rollback/stop controls. |
| P1 | 5 - Getting Started With Agentic RAG With Detailed Implementation Using LangGraph | https://www.youtube.com/watch?v=Chl-cRcwVpA | Implementation-oriented walkthrough of agentic RAG routing, grading, query rewriting, and LangGraph orchestration. | Turn the existing RAG evolution spec into concrete planner/retriever/critic/synthesizer control-panel states. |
| P1 | Google's Secret AI Weapon? AlphaEvolve Just Changed Everything | https://www.youtube.com/watch?v=_jj583bFMfc | Secondary but timely AlphaEvolve explainer; useful for spotting popular framing and claims that need primary-source verification. | Strengthen the synthetic-truth guard: claims from videos should become untrusted candidates until matched to DeepMind paper/blog facts. |
| P1 | Google's AlphaEvolve: The AI That Will Change Everything in the Next 24 Months | https://www.youtube.com/watch?v=hlswHfvQfeA | Another AlphaEvolve explainer with transcript availability through public summary mirrors. | Useful only as a framing contrast against primary AlphaEvolve sources; do not assimilate unique claims without verification. |
| P1 | Agent2Agent official intro video | https://a2a-protocol.org/dev/ | Official A2A docs page includes a short intro video plus links to spec, samples, and SDKs. | Define NexusNet's future agent-to-agent boundary: agent cards, task state, opaque peer agents, and no shared private memory by default. |
| P2 | A2A Protocol Explained: How AI Agents Collaborate | https://www.youtube.com/results?search_query=A2A+Protocol+Agent2Agent+Explained+Martin+Keen+IBM+Technology | Search anchor for the IBM Technology/Martin Keen explainer found in secondary references. | Add an operator-friendly protocol comparison layer: MCP for tools/context, A2A for peer delegation, ACP for application UI control. |
| P2 | Browser-Use tutorial/demo | https://youtu.be/97S8IWlDzMY | Search result anchor for a Browser-Use automation tutorial; useful for browser-action ergonomics and failure modes. | Compare Browser Use style DOM/action automation against NexusNet VisualOps and local browser permission gates. |
| P2 | Building Agentic RAG with LangGraph and OpenSearch | https://bigdataboutique.com/blog/building-agentic-rag-with-langgraph-opensearch | Live-build series focused on production RAG failures, mapping errors, query rewriting, hybrid search, and observability. | Convert RAG improvements into operator-visible failure states, retry loops, and retrieval-quality telemetry. |
| P2 | Flow Engineering and Agentic RAG with LangGraph | https://lilys.ai/notes/168013 | LangChain/LangGraph-oriented session about cyclic agents and flow engineering. | Improve workflow graph explainability for NexusNet brain routes and agentic retrieval flows. |
| P3 | Deep dive into open-endedness and Darwin Godel Machine discussion | https://www.youtube.com/watch?v=T08wc4xD3KA | Hacker News discussion references this as an open-endedness primer connected to DGM. | Use as background only: extract concepts, then verify against DGM technical report and code before adding to canon. |

## Primary Source Queue

| Priority | Source | What to extract | NexusNet use |
|---|---|---|---|
| P0 | Google DeepMind AlphaEvolve blog and white paper: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/ | Evolutionary program database, automated evaluator contract, deployment criteria, and objective metrics. | Create a clean-room "evaluator-first improvement loop" spec for research artifacts, not direct self-mutation. |
| P0 | Sakana AI Darwin Godel Machine: https://sakana.ai/dgm/ and https://arxiv.org/abs/2505.22954 | Self-modifying coding-agent archive, offspring scoring, transferability, and safety section. | Design a shadow-only NexusNet self-improvement lane with lineage, benchmark gates, and no production authority. |
| P0 | UI-TARS Desktop / Agent TARS: https://github.com/bytedance/ui-tars-desktop and UI-TARS paper link from that repo | Local/remote computer operators, browser operator, GUI action surface, Event Stream Viewer, sandbox notes. | Improve VisualOps action telemetry, UI-control consent, remote/local operator separation, and replayable action traces. |
| P0 | OSWorld: https://arxiv.org/abs/2404.07972 and project page https://os-world.github.io/ | Real desktop benchmark tasks, execution-based evaluation, GUI-grounding failures, and reproducibility setup. | Build a NexusNet computer-use eval checklist before trusting browser/desktop action agents. |
| P0 | MCP latest specification: https://modelcontextprotocol.io/specification/2025-11-25 | Host/client/server split, resources/prompts/tools, roots, elicitation, sampling controls, trust and consent. | Harden NexusNet's tool-context boundary and keep private/local data behind explicit authorization gates. |
| P0 | A2A official docs/spec: https://a2a-protocol.org/dev/ and https://github.com/a2aproject/A2A | Agent cards, peer task state, streaming, opaque collaboration, and MCP complementarity. | Define future multi-agent interoperability without exposing internal Hive Mind memory or tools by default. |
| P1 | ACP: https://acp-protocol.org/ | Protocol for agents operating existing application UIs. | Map ACP to a controlled application UI lane, separate from A2A peer delegation and MCP tool access. |
| P1 | OpenTelemetry GenAI semantic conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/ | Agent/model spans, events, metrics, exceptions, and MCP semantic conventions. | Standardize NexusNet brain traces, tool-call spans, model-call spans, and retrieval/agent event telemetry. |
| P1 | Mem0: https://github.com/mem0ai/mem0 and https://arxiv.org/abs/2504.19413 | Multi-level long-term memory, memory benchmarks, graph memory claims, and open-source architecture. | Compare against NexusNet graph-backed memory and decide what belongs as refs-only evidence versus implementable storage policy. |
| P1 | Zep/Graphiti: https://arxiv.org/abs/2501.13956 and https://github.com/getzep/graphiti | Temporal knowledge graph, evolving facts, conversational/business data synthesis, and historical relationships. | Improve NexusNet memory with temporal conflict handling, current-fact resolution, and provenance scoring. |
| P1 | LightRAG: https://arxiv.org/abs/2410.05779 and https://github.com/HKUDS/LightRAG | Graph-plus-vector retrieval, dual-level retrieval, incremental update algorithm. | Upgrade the agentic RAG planner with low-level/high-level retrieval choices and incremental corpus refresh states. |
| P1 | HippoRAG: https://arxiv.org/abs/2405.14831 and https://github.com/OSU-NLP-Group/HippoRAG | Hippocampal-inspired indexing, cheap single-step retrieval, and long-term memory integration. | Evaluate as a candidate retrieval/memory mode for KAC and long-context recall, without replacing current graph memory prematurely. |
| P1 | OpenHands: https://github.com/OpenHands/OpenHands | Sandboxed AI-driven development agent, SDK shape, trajectories, and developer workflow UI. | Compare against NexusNet native expert execution and code-change governance. |
| P1 | SWE-bench/SWE-agent ecosystem: https://github.com/swe-bench and https://arxiv.org/abs/2405.15793 | SWE-agent computer interface, sandboxing, benchmarks, mini agents, and training/eval data. | Improve NexusNet native behavior validation with issue-style tasks, test feedback loops, and agent-computer-interface design. |
| P1 | OpenEvolve: https://github.com/algorithmicsuperintelligence/openevolve | Open implementation of AlphaEvolve-style evolutionary coding loops. | Use as a code-level reference for a sandboxed evaluator loop, not as production self-editing authority. |
| P2 | Liquid AI LFM2.5-350M: https://www.liquid.ai/blog/lfm2-5-350m-no-size-left-behind and https://huggingface.co/LiquidAI/LFM2.5-350M | Small-model training, edge/runtime suitability, RL/post-training details, WebGPU demo. | Extend the open-first teacher/runtime roster for local lightweight specialist lanes. |
| P2 | Google Gemma 4: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ | Current open-model lineup, license, local/agentic positioning, size/performance tiers. | Refresh the open-first model roster and local runtime planning assumptions. |
| P2 | Qwen3-Coder and Qwen3-Coder-Next: https://qwenlm.github.io/blog/qwen3-coder/ and https://arxiv.org/abs/2603.00729 | Open-weight coding-agent models, long context, agentic coding tool, sparse active-parameter design. | Candidate expert model lane for native code execution and repo-oriented teacher council reviews. |
| P2 | Tandem Browser: https://tandembrowser.org/ | MCP-native browser, local-first agent connection, structured browser endpoints, threat scanning. | Watchlist source for local browser-control architecture and browser-as-operating-surface ideas. |
| P3 | OS-Harm: https://arxiv.org/abs/2506.14866 | Safety benchmark for computer-use agents across misuse, prompt injection, and unsafe actions. | Add negative evals before any high-authority VisualOps or computer-use lane is enabled. |

## Assimilation Rules For This Queue

- Video claims are candidate evidence, not canon. Promote only claims that match a primary source, repo, paper, benchmark, or reproducible local test.
- Self-improvement concepts stay shadow-only: lineage, scoring, replay, and recommendations are allowed; automatic production mutation is not.
- Browser and computer-use ideas require explicit user consent, visible action traces, permission scoping, and a stop/rollback path.
- Protocol ideas must keep MCP, A2A, and ACP separate: MCP connects agents to tools/context, A2A connects peer agents, and ACP targets existing application UIs.
- Memory and RAG ideas must preserve provenance, temporal conflict handling, and refs-only import boundaries for knowledge artifacts.
- Open-first model candidates need license, runtime, quantization, local hardware, and benchmark checks before they become a recommended NexusNet lane.

## Suggested Watcher Prompts

Use these prompts when each file is downloaded and passed through the video watcher:

1. "Watch this as a NexusNet assimilation target. Extract concrete mechanisms, primary-source claims to verify, failure modes, and a spec sheet for how NexusNet could adopt the useful parts without granting mutation authority."
2. "Separate demo polish from implementable architecture. Mark anything that depends on hosted services, private APIs, unclear licensing, or unverifiable benchmark claims."
3. "For every implementation idea, map it to one of: KAC refs-only artifact, Control Panel surface, Brain routing, VisualOps/computer-use lane, RAG/memory lane, telemetry lane, or model/runtime candidate."
