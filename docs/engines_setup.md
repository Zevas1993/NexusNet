
# Engines Setup

- **Transformers (local):** set `HF_MODEL_ID`, optional `HF_DEVICE=cpu|cuda`.
- **Ollama:** run `ollama serve`, set `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
- **vLLM:** run compatible server at `VLLM_BASE_URL` (OpenAI-style `/v1/completions`).
- **TGI:** run server at `TGI_BASE_URL` exposing `/generate`.
