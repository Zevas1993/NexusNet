# Model Eval Harness Federation Spec

Status: P1 online assimilation target. Research-only until mapped to NexusNet's open-first model roster and local runtime stack.

## Source Evidence

- OpenAI Evals repository: https://github.com/openai/evals
- EleutherAI lm-evaluation-harness repository: https://github.com/EleutherAI/lm-evaluation-harness
- Hugging Face LightEval docs: https://huggingface.co/docs/lighteval/index
- Stanford HELM repository: https://github.com/stanford-crfm/helm
- Source status: official public evaluation repositories and docs.

## Finding

Model evaluation frameworks differ in task format, metrics, provider adapters, local model support, and reporting. NexusNet should not lock itself into one harness when its model roster spans local GGUF, edge runtimes, server backends, open-weight models, and possible frontier fallbacks.

## NexusNet Assimilation Target

Build an eval federation layer that normalizes results from multiple harnesses into a single NexusNet model passport. Each model route should have task scores, hardware profile, latency, memory, tool-call ability, RAG behavior, license, and cost assumptions.

## Proposed NexusNet Components

- `ModelEvalPassport`: model, runtime, quantization, hardware, prompt template, eval suite, score, cost, and limitations.
- `HarnessAdapter`: OpenAI Evals, lm-eval-harness, LightEval, HELM, Inspect, and custom NexusNet task adapters.
- `ScoreNormalizationLedger`: metric definition, task version, sample count, and comparability warning.
- `OpenModelRegressionGate`: recurring tests for promoted local/open models.
- `ModelRouteDecisionSurface`: Control Panel view comparing quality, speed, memory, tool use, and safety.

## Promotion Gates

- Do not compare scores across harnesses without task and metric metadata.
- Separate benchmark quality from runtime fit and license fit.
- Run NexusNet-specific tasks before changing default model routes.
- Keep eval artifacts reproducible and versioned.

## Risks

- Harness adapters can hide prompt-format or tokenizer differences.
- Leaderboards drift faster than local certification.
- Generic benchmarks may not predict NexusNet tool, memory, and Control Panel behavior.
