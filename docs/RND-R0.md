
# RND‑R0: Integrating Recursive Neural Dreaming with R‑Zero

This module adds a disciplined self‑curriculum loop to NexusNet. It pairs a **Challenger** and **Solver**
(two instances of the same base model) and iteratively:
1) Generates challenging‑but‑solvable questions (uncertainty‑driven).
2) Pseudo‑labels via majority vote across multiple Solver attempts.
3) Trains the Solver on the curated band; penalizes repetition and bad format.
4) Retrains the Challenger against the improved Solver and repeats.

## Quick start
```bash
python -m apps.admin.rzero --model your-base-model --seeds "algebra,word problems" --experiment pilot
```

Curated data lands in `data/rzero/curated-<experiment>-<ts>.jsonl` and can be ingested into Assimilation/DPO via:
```bash
python -m training.assimilation.ingest_rzero --path data/rzero/curated-*.jsonl
```

## Files
- `training/rzero/engine.py` – loop coordinator
- `training/rzero/rewards.py` – uncertainty/repetition/format rewards
- `training/rzero/labeling.py` – majority vote + informative band filtering
- `training/rzero/dataset.py` – JSONL writer
- `training/rzero/policies.py` – model stubs (replace with your serving & GRPO code)
- `runtime/config/rzero.yaml` – default hyperparameters
- `apps/admin/rzero.py` – CLI entrypoint
- `training/assimilation/ingest_rzero.py` – feeder into Assimilation/DPO
- `core/experts/rzero_math.yaml` – example expert profile
```

## Implementation notes
- Replace stubs in `policies.py` with your model APIs and GRPO trainer.
- The repetition penalty currently uses token Jaccard; swap for BLEU/semantic similarity if available.
- Start with verifiable domains (math/code) before open‑ended tasks.

## Admin API

If your admin service uses FastAPI, the following route is added:

- `POST /rzero/run` with JSON body:
  ```json
  {
    "model": "local:path-or-hf-id",
    "seeds": "algebra,number theory",
    "experiment": "pilot",
    "device": "cuda"
  }
  ```
  Returns a JSON report for one full Challenger→Solver iteration.

If your admin app is not FastAPI-based, use the CLI:
```bash
python -m apps.admin.rzero --model local:your-model --seeds "algebra,probability" --experiment pilot
```
