# Liquid Efficiency Assimilation

## Canon Status
- Existing multimodal and teacher system: `LOCKED CANON`
- Edge vision lane: `EXPLORATORY / PROTOTYPE`

## Explicit LFM2.5-VL-450M Lane
- Candidate provider: `LiquidAI/LFM2.5-VL-450M`
- Candidate teacher lane: `lfm2.5-vl-450m::vision-edge`
- Intended modes: `low-power`, `safe-mode`, `edge-lane`

## Design Lessons Captured
- Compact edge-first design
- More pretraining instead of only scaling size
- Preference optimization plus reinforcement learning for reliability
- Structured outputs
- Grounding and bounding boxes
- Multilingual support
- Function calling
- Device-aware latency and quality budgets

## Sources
- https://huggingface.co/LiquidAI/LFM2.5-VL-450M
- https://huggingface.co/LiquidAI/LFM2.5-VL-450M-GGUF
