# Domain-Specialist Teacher Models - Online Research (June 2026)

Status: web research to find real, current models usable as Ivy-League TEACHERS for each expert
capsule's area of expertise (canon: per-domain Mixture-of-Teachers, C38M0258). These replace the
generic deep-reasoning pool for fields where a genuine domain specialist exists. Wired into
`nexusnet/hive/curriculum.py` (`DOMAIN_SPECIALIST_PROFILES` + `DOMAIN_SPECIALIST_TEACHERS`).

## Findings by field

| Capsule | Researched teacher model(s) | Why |
| --- | --- | --- |
| mathematician | **DeepSeek-Math V2**, Qwen-Math, QwQ-32B, DeepSeek-R1 | DeepSeek-Math V2 hit IMO-2025 gold (5/6); QwQ-32B strong open math reasoning |
| chemist | **ChemDFM v1.5-8B**, **ChemLLM** (7B/20B), SciGLM | ChemDFM: LLaMA-3-8B + 34B-token chem corpus, >= GPT-4 on chem tasks; ChemLLM chem-specialized |
| biologist | **BioMistral-7B**, **ESMC** (protein), SciGLM | BioMistral = Mistral + PubMed Central; ESMC = SOTA protein LM (2.8B sequences, beats AF3 on Ab-Ag) |
| neuroscientist | BioMistral-7B, SciGLM, DeepSeek-V4/R1 | biomedical + scientific reasoning (no dedicated neuro LM found) |
| medical | **MedGemma 27B**, **OpenBioLLM-70B**, **Med42-v2**, **Meditron3** | MedGemma 1.5 (Jan 2026) ~91% MedQA, current SOTA open medical |
| legal | **SaulLM-141B**, **SaulLM-54B** | Mixtral-based legal models, SOTA on LegalBench-Instruct (400B-token legal corpus) |
| financial / economist | **FinGPT** (AI4Finance), DeepSeek-V4 | open financial LLM framework (data-centric, LoRA fine-tuning) |
| physicist | **SciGLM**, **P1-VL-235B**, DeepSeek-Math V2, QwQ-32B | SciGLM = physics/chem/math/proofs reasoning; P1-VL = physics-olympiad VLM (HiPhO golds) |
| cosmologist | SciGLM, DeepSeek-Math V2, QwQ-32B | astrophysics is math/physics-reasoning heavy |
| scientist (general) | **SciGLM**, DeepSeek-V4, QwQ-32B | SciGLM trained on SciInstruct (physics/chem/math/proofs) |
| materials_scientist | **MatterGen**, SciGLM, DeepSeek-V4 | MatterGen = generative inorganic materials design (Microsoft) |
| logician | DeepSeek-Math V2, SciGLM, QwQ-32B | formal proofs / proof-theory = math-proof reasoning |
| quantum_information | SciGLM, DeepSeek-Math V2, QwQ-32B | quantum algorithms = math/physics reasoning |
| cryptographer | DeepSeek-Math V2, DeepSeek-R1, QwQ-32B, SciGLM | security proofs / number theory = math reasoning |
| coder (existing) | Qwen3-Coder-Next, Devstral-2 | already domain-correct in the registry |
| vision (existing) | Qwen3-VL | already domain-correct |
| auditory (existing) | Voxtral Small | already domain-correct |

Fields with NO dedicated specialist model found (philosopher, historian, strategist, etc.) keep strong
general reasoning models (DeepSeek-R1/V4, QwQ-32B, Qwen3-30B) - documented as such, not faked.

## Notes
- These are EXTERNAL teacher models the matching capsule is distilled from during bootstrap, then
  replaced once the student surpasses them (canon TRP). Many (ChemDFM, BioMistral, SaulLM, FinGPT,
  Meditron, OpenBioLLM, ESMC, SciGLM, MatterGen) are open-weight and locally runnable; some are
  research artifacts (P1-VL, ESMC) better used as remote/reference teachers.
- License/locality should be verified per model before live use (same gate as the existing registry).

## Sources
- Chemistry: https://github.com/OpenDFM/ChemDFM , https://arxiv.org/pdf/2402.06852 (ChemLLM)
- Biology/protein: https://huggingface.co/BioMistral/BioMistral-7B , https://biohub.org/news/world-model-of-protein-biology/ (ESMC)
- Math: https://tech-now.io/en/blogs/deepseek-math-v2-the-open-source-ai-model-redefining-mathematical-reasoning , https://huggingface.co/Qwen/QwQ-32B
- Medical: https://awesomeagents.ai/leaderboards/medical-llm-leaderboard/ , https://nirmitee.io/blog/healthcare-llm-landscape-2026-medgemma-meditron-clinical-model-guide/ , https://arxiv.org/pdf/2408.06142 (Med42-v2)
- Legal: https://arxiv.org/pdf/2407.19584 (SaulLM-54B/141B) , https://arxiv.org/pdf/2403.03883 (SaulLM-7B)
- Finance: https://arxiv.org/html/2306.06031v2 (FinGPT)
- Science/physics: https://github.com/THUDM/SciGLM , https://arxiv.org/pdf/2602.09443 (P1-VL)
- Materials: https://arxiv.org/abs/2312.03687 (MatterGen) , https://advanced.onlinelibrary.wiley.com/doi/10.1002/adfm.202525897

## Double-check pass (validation, June 2026)

Re-verified all teacher/student pairings online; results:
- **Code** (Qwen3-Coder-Next 58.7% SWE-Verified, Devstral-2/Small-2 72.2%/68%) - confirmed correct;
  flagship alternatives Kimi K2.6, DeepSeek-V4-Pro, MiniMax M3 (59.0% SWE-Bench Pro, Jun 2026).
- **Vision** (Qwen3-VL latest; InternVL3-78B strongest MIT; Molmo fully-open) - Qwen3-VL confirmed.
- **Audio** - REFRESHED to current models: **Voxtral Transcribe 2** (Apache-2.0, 5.9% WER FLEURS,
  streaming), **Canary-Qwen 2.5B** (NVIDIA, tops Open ASR @5.63% WER), **Qwen3-ASR** (52 langs),
  **Whisper large-v3** (99+ langs). (Previously voxtral-small.)
- **Climate science** - found real specialist **ClimateGPT** (Llama-2 + IPCC corpus, 7B/13B/70B) ->
  assigned to climate_scientist + oceanographer.
- **Geoscience** - found **JiuZhou** (Mistral-7B geoscience continued-pretrain) -> assigned to geologist.
- **Psychology/mental-health** - found **PsycoLLM** -> assigned to psychologist.
- **Flagship general pool** validated: Kimi K2.6 (highest open-weight Intelligence Index 54),
  DeepSeek-V4-Pro (52), DeepSeek-V4-Flash, GLM-5.1, MiniMax M3, Qwen3-30B-A3B, Mistral Small 4 -
  these back the fields with NO dedicated specialist (philosopher, historian, sociologist, etc.).
- **No dedicated specialist found** (kept strong general/reasoning models, documented not faked):
  philosopher, historian, music (musicologist), education (educator), most humanities/business roles,
  most engineering subfields (use SciGLM + reasoning), cryptography/quantum (use math-reasoning).

### Additional sources (validation)
- Coding 2026: https://kilo.ai/open-source-models , https://huggingface.co/blog/daya-shankar/open-source-llms
- Vision 2026: https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models
- Audio 2026: https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks , https://mistral.ai/news/voxtral/
- ClimateGPT: https://github.com/mbzuai-oryx/ClimateGPT , https://arxiv.org/html/2401.09646v1
- JiuZhou (geoscience): https://arxiv.org/pdf/2506.13796
- PsycoLLM: https://arxiv.org/pdf/2407.05721
- Flagship leaderboards: https://artificialanalysis.ai/leaderboards/models , https://llm-stats.com/leaderboards/open-llm-leaderboard
