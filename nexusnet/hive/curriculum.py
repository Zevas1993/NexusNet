"""Per-expert curriculum, DESIGNED AROUND each expert node's area of expertise (canon C12M0027,
C38M0258, C38M0030).

The curriculum is NOT a fixed universal pipeline. Each of the canonical expert capsules declares its
own AREA OF EXPERTISE, and its curriculum (task families, difficulty ladder, eval gates) plus its
Mixture-of-Teachers (Coach/Critic/Socratic/Referee) are DERIVED FROM that domain. The Coder expert
learns a coding curriculum from coding teachers; the Vision expert learns a vision curriculum from
vision teachers; and so on. A Challenger (R-Zero) escalates difficulty within the expert's own domain.

Shadow-only data/spec: this declares the curricula; it does not run distillation here.
"""
from __future__ import annotations

from typing import Any

# Teacher roles per capsule (best-ensemble-per-role).
ROLES = ("coach", "critic", "socratic", "referee")

# The 19 canonical expert capsules: area of expertise -> domain spec.
# `teachers` are real external teacher-model ids chosen FOR that domain (domain Mixture-of-Teachers).
EXPERT_CAPSULES: dict[str, dict[str, Any]] = {
    "vision": {
        "area_of_expertise": "visual perception: classification, detection, segmentation, captioning, OCR",
        "task_families": ["image_classification", "object_detection", "segmentation", "captioning", "ocr"],
        "teachers": ["qwen3-vl", "qwen3-vl", "qwen3-30b-a3b", "deepseek-v4-pro"],
        "eval_gates": ["imagenet_topk", "coco_map", "ocr_cer"],
    },
    "auditory": {
        "area_of_expertise": "speech & audio: ASR, speaker ID, audio understanding",
        "task_families": ["asr", "speaker_id", "audio_classification"],
        "teachers": ["voxtral-small", "voxtral-small", "qwen3-30b-a3b", "deepseek-v4-pro"],
        "eval_gates": ["wer", "audio_acc"],
    },
    "linguist": {
        "area_of_expertise": "language: translation, grammar, multilingual understanding",
        "task_families": ["translation", "grammar", "nli", "summarization"],
        "teachers": ["qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b", "deepseek-v4-pro"],
        "eval_gates": ["bleu", "xnli"],
    },
    "librarian": {
        "area_of_expertise": "retrieval & open-domain QA over documents",
        "task_families": ["retrieval", "open_domain_qa", "reranking", "citation"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["nq_em", "retrieval_recall"],
    },
    "mathematician": {
        "area_of_expertise": "mathematics: proofs, symbolic, numeric reasoning",
        "task_families": ["arithmetic", "algebra", "proof", "word_problems"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["gsm8k", "math"],
    },
    "coder": {
        "area_of_expertise": "software: code generation, debugging, refactoring, tests",
        "task_families": ["code_generation", "debugging", "refactoring", "test_writing"],
        "teachers": ["qwen3-coder-next", "devstral-2", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b"],
        "eval_gates": ["humaneval", "swe_bench"],
    },
    "scientist": {
        "area_of_expertise": "scientific reasoning, hypothesis, experiment design",
        "task_families": ["hypothesis", "experiment_design", "literature_synthesis"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["sciqa", "arc_challenge"],
    },
    "engineer": {
        "area_of_expertise": "engineering design, systems, optimization",
        "task_families": ["systems_design", "optimization", "tradeoff_analysis"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["design_rubric"],
    },
    "medical": {
        "area_of_expertise": "clinical reasoning (decision-support, non-diagnostic)",
        "task_families": ["clinical_qa", "triage_support", "literature_evidence"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["medqa", "safety_rubric"],
    },
    "legal": {
        "area_of_expertise": "legal analysis, statutes, precedent (non-advice)",
        "task_families": ["statute_analysis", "case_summary", "contract_review"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["legalbench"],
    },
    "financial": {
        "area_of_expertise": "financial modeling, valuation, risk (no certain-return claims)",
        "task_families": ["valuation", "risk_analysis", "budgeting"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b", "mistral-small-4"],
        "eval_gates": ["finqa"],
    },
    "strategist": {
        "area_of_expertise": "planning, long-horizon strategy, game theory",
        "task_families": ["planning", "strategy", "negotiation"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["planning_rubric"],
    },
    "simulator": {
        "area_of_expertise": "world modeling, simulation, prediction (JEPA)",
        "task_families": ["world_modeling", "trajectory_prediction", "what_if"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b", "mistral-small-4"],
        "eval_gates": ["prediction_error"],
    },
    "robotics": {
        "area_of_expertise": "robotics & control, action planning",
        "task_families": ["control", "motion_planning", "manipulation"],
        "teachers": ["nvidia-nemotron-3-nano-omni", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["control_rubric"],
    },
    "creative_artist": {
        "area_of_expertise": "creative generation: writing, design, ideation",
        "task_families": ["creative_writing", "ideation", "design_concept"],
        "teachers": ["mistral-small-4", "qwen3-30b-a3b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["creativity_rubric"],
    },
    "psychologist": {
        "area_of_expertise": "psychology, theory of mind, social reasoning",
        "task_families": ["theory_of_mind", "social_reasoning", "sentiment"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["tom_eval"],
    },
    "verifier": {
        "area_of_expertise": "verification, fact-checking, proof-checking",
        "task_families": ["fact_check", "proof_check", "consistency"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["verification_acc"],
    },
    "ethicist": {
        "area_of_expertise": "ethics, value alignment, harm analysis",
        "task_families": ["ethical_analysis", "value_alignment", "harm_assessment"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["ethics_rubric"],
    },
    "guardian": {
        "area_of_expertise": "safety, security, policy enforcement",
        "task_families": ["safety_screen", "policy_enforcement", "red_team_defense"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["safety_rubric", "jailbreak_resistance"],
    },
    # --- Expandable frontier / edge-case experts (canon: expert set is extensible without redesign) ---
    "philosopher": {
        "area_of_expertise": "philosophy: logic, metaphysics, epistemology, ethical theory",
        "task_families": ["argument_analysis", "epistemology", "metaphysics", "thought_experiment"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["argument_validity", "philpapers_qa"],
    },
    "physicist": {
        "area_of_expertise": "physics: classical, quantum, relativity, computational physics",
        "task_families": ["mechanics", "quantum", "relativity", "computational_physics"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["physics_olympiad", "derivation_check"],
    },
    "chemist": {
        "area_of_expertise": "chemistry: molecular structure, reactions, materials chemistry",
        "task_families": ["reaction_prediction", "retrosynthesis", "molecular_properties"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["chem_qa", "reaction_accuracy"],
    },
    "biologist": {
        "area_of_expertise": "biology: genomics, molecular & systems biology",
        "task_families": ["genomics", "protein_function", "systems_biology"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["bio_qa"],
    },
    "neuroscientist": {
        "area_of_expertise": "neuroscience: neural systems, cognition, computational neuro",
        "task_families": ["neural_dynamics", "cognition", "connectomics"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["neuro_qa"],
    },
    "cosmologist": {
        "area_of_expertise": "astrophysics & cosmology: gravitation, large-scale structure",
        "task_families": ["astrophysics", "cosmology", "orbital_mechanics"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["astro_qa", "derivation_check"],
    },
    "logician": {
        "area_of_expertise": "formal logic, proof theory, type theory, formal verification",
        "task_families": ["formal_proof", "type_theory", "model_checking"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["proof_check", "lean_pass"],
    },
    "economist": {
        "area_of_expertise": "economics: micro/macro theory, econometrics, mechanism design",
        "task_families": ["micro_theory", "macro_modeling", "econometrics"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["econ_qa"],
    },
    "historian": {
        "area_of_expertise": "history: causal analysis, source criticism, synthesis",
        "task_families": ["source_criticism", "causal_history", "synthesis"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["history_qa"],
    },
    "cryptographer": {
        "area_of_expertise": "cryptography: protocols, security proofs, cryptanalysis",
        "task_families": ["protocol_design", "security_proof", "cryptanalysis"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["crypto_proof_check"],
    },
    "quantum_information": {
        "area_of_expertise": "quantum computing & information: algorithms, error correction",
        "task_families": ["quantum_algorithms", "error_correction", "circuit_synthesis"],
        "teachers": ["deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["quantum_qa", "circuit_correctness"],
    },
    "materials_scientist": {
        "area_of_expertise": "materials science: condensed matter, crystallography, properties",
        "task_families": ["crystal_structure", "property_prediction", "phase_diagrams"],
        "teachers": ["deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b", "mistral-small-4"],
        "eval_gates": ["materials_qa"],
    },
    # --- Wider coverage: humanities & social sciences ---
    "sociologist": {"area_of_expertise": "sociology: social structures, institutions, methods",
        "task_families": ["social_theory", "survey_methods", "stratification"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["social_science_qa"]},
    "anthropologist": {"area_of_expertise": "anthropology: culture, ethnography, human evolution",
        "task_families": ["ethnography", "cultural_analysis", "human_evolution"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["anthro_qa"]},
    "political_scientist": {"area_of_expertise": "political science: governance, international relations, policy",
        "task_families": ["governance", "international_relations", "policy_analysis"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["polisci_qa"]},
    "geographer": {"area_of_expertise": "geography: spatial analysis, GIS, human & physical geography",
        "task_families": ["spatial_analysis", "gis", "human_geography"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["geo_qa"]},
    "archaeologist": {"area_of_expertise": "archaeology: material culture, dating, excavation analysis",
        "task_families": ["material_culture", "dating_methods", "stratigraphy"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["archaeology_qa"]},
    "religion_scholar": {"area_of_expertise": "comparative religion, theology, textual scholarship",
        "task_families": ["comparative_religion", "textual_exegesis", "theology"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["religion_qa"]},
    "art_historian": {"area_of_expertise": "art history: movements, visual analysis, provenance",
        "task_families": ["art_movements", "visual_analysis", "provenance"],
        "teachers": ["qwen3-vl", "qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4"],
        "eval_gates": ["art_history_qa"]},
    "musicologist": {"area_of_expertise": "musicology: theory, history, analysis",
        "task_families": ["music_theory", "music_history", "score_analysis"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["music_qa"]},
    "educator": {"area_of_expertise": "education: pedagogy, curriculum design, assessment",
        "task_families": ["pedagogy", "curriculum_design", "assessment"],
        "teachers": ["qwen3-30b-a3b", "mistral-small-4", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["education_qa"]},
    "diplomat": {"area_of_expertise": "diplomacy: negotiation, international relations, conflict resolution",
        "task_families": ["negotiation", "conflict_resolution", "treaty_analysis"],
        "teachers": ["deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b", "mistral-small-4"],
        "eval_gates": ["diplomacy_rubric"]},
    # --- Wider coverage: life & health sciences ---
    "geneticist": {"area_of_expertise": "genetics: heredity, genomics, gene editing",
        "task_families": ["heredity", "variant_analysis", "gene_editing"],
        "teachers": ["biomistral-7b", "esmc", "sciglm-32b", "deepseek-v4-pro"],
        "eval_gates": ["genetics_qa"]},
    "ecologist": {"area_of_expertise": "ecology: ecosystems, biodiversity, conservation",
        "task_families": ["ecosystem_modeling", "biodiversity", "conservation"],
        "teachers": ["sciglm-32b", "biomistral-7b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["ecology_qa"]},
    "pharmacologist": {"area_of_expertise": "pharmacology: drug mechanisms, pharmacokinetics",
        "task_families": ["drug_mechanism", "pharmacokinetics", "toxicology"],
        "teachers": ["medgemma-27b", "biomistral-7b", "chemdfm-v1.5-8b", "deepseek-v4-pro"],
        "eval_gates": ["pharma_qa"]},
    "epidemiologist": {"area_of_expertise": "epidemiology: disease spread, public health, biostatistics",
        "task_families": ["disease_modeling", "biostatistics", "public_health"],
        "teachers": ["medgemma-27b", "biomistral-7b", "deepseek-math-v2", "deepseek-v4-pro"],
        "eval_gates": ["epi_qa"]},
    "immunologist": {"area_of_expertise": "immunology: immune system, vaccines, antibodies",
        "task_families": ["immune_response", "vaccine_design", "antibody_analysis"],
        "teachers": ["biomistral-7b", "esmc", "medgemma-27b", "deepseek-v4-pro"],
        "eval_gates": ["immuno_qa"]},
    "microbiologist": {"area_of_expertise": "microbiology: microbes, pathogens, microbiome",
        "task_families": ["microbial_genetics", "pathogen_analysis", "microbiome"],
        "teachers": ["biomistral-7b", "esmc", "sciglm-32b", "deepseek-v4-pro"],
        "eval_gates": ["micro_qa"]},
    "nutritionist": {"area_of_expertise": "nutrition science: diet, metabolism, dietetics",
        "task_families": ["nutrition_science", "metabolism", "diet_planning"],
        "teachers": ["medgemma-27b", "biomistral-7b", "qwen3-30b-a3b", "deepseek-v4-pro"],
        "eval_gates": ["nutrition_qa"]},
    "veterinarian": {"area_of_expertise": "veterinary medicine: animal health & disease",
        "task_families": ["animal_diagnosis", "veterinary_pharmacology", "zoonoses"],
        "teachers": ["medgemma-27b", "biomistral-7b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["vet_qa"]},
    "bioinformatician": {"area_of_expertise": "bioinformatics: sequence analysis, computational biology",
        "task_families": ["sequence_alignment", "structural_bioinformatics", "omics_pipelines"],
        "teachers": ["esmc", "biomistral-7b", "qwen3-coder-next", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["bioinfo_qa"]},
    # --- Wider coverage: earth & physical sciences ---
    "geologist": {"area_of_expertise": "geology: earth structure, minerals, plate tectonics",
        "task_families": ["mineralogy", "plate_tectonics", "stratigraphy_geo"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwq-32b"],
        "eval_gates": ["geology_qa"]},
    "climate_scientist": {"area_of_expertise": "climate science: atmospheric modeling, climate dynamics",
        "task_families": ["climate_modeling", "atmospheric_dynamics", "carbon_cycle"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwq-32b"],
        "eval_gates": ["climate_qa"]},
    "oceanographer": {"area_of_expertise": "oceanography: marine systems, currents, marine biology",
        "task_families": ["ocean_dynamics", "marine_ecosystems", "bathymetry"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "biomistral-7b", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["ocean_qa"]},
    "astronomer": {"area_of_expertise": "observational astronomy: instrumentation, stellar systems",
        "task_families": ["observational_astronomy", "spectroscopy", "stellar_evolution"],
        "teachers": ["sciglm-32b", "deepseek-math-v2", "deepseek-v4-pro", "qwq-32b"],
        "eval_gates": ["astronomy_qa"]},
    # --- Wider coverage: quantitative & computing ---
    "statistician": {"area_of_expertise": "statistics: inference, probability, experimental design",
        "task_families": ["statistical_inference", "probability", "experimental_design"],
        "teachers": ["deepseek-math-v2", "qwen3-math", "deepseek-r1-distill-qwen-32b", "qwq-32b"],
        "eval_gates": ["stats_qa"]},
    "data_scientist": {"area_of_expertise": "data science: ML pipelines, analysis, visualization",
        "task_families": ["data_analysis", "ml_pipelines", "feature_engineering"],
        "teachers": ["qwen3-coder-next", "deepseek-math-v2", "deepseek-r1-distill-qwen-32b", "qwen3-30b-a3b"],
        "eval_gates": ["ds_bench"]},
    "ai_researcher": {"area_of_expertise": "AI/ML research: architectures, training, evaluation",
        "task_families": ["model_architecture", "training_methods", "evaluation_design"],
        "teachers": ["qwen3-coder-next", "deepseek-r1-distill-qwen-32b", "deepseek-v4-pro", "qwen3-30b-a3b"],
        "eval_gates": ["ml_research_rubric"]},
    # --- Wider coverage: engineering subfields ---
    "electrical_engineer": {"area_of_expertise": "electrical engineering: circuits, signals, power systems",
        "task_families": ["circuit_design", "signal_processing", "power_systems"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "qwen3-coder-next", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["ee_qa"]},
    "mechanical_engineer": {"area_of_expertise": "mechanical engineering: mechanics, thermodynamics, design",
        "task_families": ["statics_dynamics", "thermodynamics", "mechanical_design"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "deepseek-math-v2", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["me_qa"]},
    "civil_engineer": {"area_of_expertise": "civil engineering: structures, materials, infrastructure",
        "task_families": ["structural_analysis", "geotechnical", "infrastructure"],
        "teachers": ["sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "mistral-small-4"],
        "eval_gates": ["ce_qa"]},
    "aerospace_engineer": {"area_of_expertise": "aerospace engineering: aerodynamics, propulsion, orbital",
        "task_families": ["aerodynamics", "propulsion", "orbital_design"],
        "teachers": ["sciglm-32b", "deepseek-math-v2", "deepseek-v4-pro", "qwq-32b"],
        "eval_gates": ["aero_qa"]},
    "chemical_engineer": {"area_of_expertise": "chemical engineering: process design, reaction scale-up",
        "task_families": ["process_design", "reactor_engineering", "separations"],
        "teachers": ["chemdfm-v1.5-8b", "sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["cheme_qa"]},
    # --- Wider coverage: business & creative professions ---
    "accountant": {"area_of_expertise": "accounting: bookkeeping, audit, tax",
        "task_families": ["bookkeeping", "audit", "taxation"],
        "teachers": ["fingpt", "deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["accounting_qa"]},
    "marketer": {"area_of_expertise": "marketing: strategy, consumer behavior, branding",
        "task_families": ["marketing_strategy", "consumer_behavior", "branding"],
        "teachers": ["qwen3-30b-a3b", "mistral-small-4", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["marketing_rubric"]},
    "product_manager": {"area_of_expertise": "product management: strategy, roadmapping, prioritization",
        "task_families": ["product_strategy", "roadmapping", "prioritization"],
        "teachers": ["qwen3-30b-a3b", "deepseek-v4-pro", "mistral-small-4", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["pm_rubric"]},
    "architect": {"area_of_expertise": "architecture: building design, structures, aesthetics",
        "task_families": ["architectural_design", "structural_aesthetics", "space_planning"],
        "teachers": ["qwen3-vl", "sciglm-32b", "qwen3-30b-a3b", "deepseek-v4-pro"],
        "eval_gates": ["architecture_rubric"]},
    "game_designer": {"area_of_expertise": "game design: mechanics, level design, systems",
        "task_families": ["game_mechanics", "level_design", "systems_balancing"],
        "teachers": ["mistral-small-4", "qwen3-30b-a3b", "deepseek-v4-pro", "qwen3-coder-next"],
        "eval_gates": ["game_design_rubric"]},
    "journalist": {"area_of_expertise": "journalism: reporting, investigation, narrative writing",
        "task_families": ["investigative_reporting", "fact_gathering", "narrative_writing"],
        "teachers": ["qwen3-30b-a3b", "mistral-small-4", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
        "eval_gates": ["journalism_rubric"]},
}

# --- Researched real domain-specialist teacher models (web research, June 2026) ---
# Profiles for the specialist teacher models found for each field (sources in
# docs/research/DOMAIN_TEACHER_MODELS_RESEARCH_2026-06-01.md). These are EXTERNAL models the matching
# expert capsule is distilled from. Ids are kept registry-style (lowercase-hyphen).
DOMAIN_SPECIALIST_PROFILES: dict[str, dict[str, str]] = {
    "deepseek-math-v2": {"name": "DeepSeek-Math V2", "domain": "mathematics",
                          "source": "https://huggingface.co/deepseek-ai", "notes": "IMO-2025 gold-level math reasoning"},
    "qwen3-math": {"name": "Qwen Math (Qwen2.5/3-Math)", "domain": "mathematics",
                   "source": "https://huggingface.co/Qwen", "notes": "math-specialized Qwen line"},
    "qwq-32b": {"name": "QwQ-32B", "domain": "reasoning/math",
                "source": "https://huggingface.co/Qwen/QwQ-32B", "notes": "open reasoning model"},
    "sciglm-32b": {"name": "SciGLM", "domain": "science (physics/chem/math/proofs)",
                   "source": "https://github.com/THUDM/SciGLM", "notes": "scientific reasoning, SciInstruct"},
    "p1-vl-235b": {"name": "P1-VL", "domain": "physics (vision-language)",
                   "source": "https://arxiv.org/abs/2602.09443", "notes": "physics-olympiad VLM, HiPhO golds"},
    "chemdfm-v1.5-8b": {"name": "ChemDFM v1.5 8B", "domain": "chemistry",
                        "source": "https://github.com/OpenDFM/ChemDFM", "notes": "LLaMA-3-8B + 34B-token chem corpus"},
    "chemllm-20b": {"name": "ChemLLM", "domain": "chemistry",
                    "source": "https://huggingface.co/AI4Chem", "notes": "chemical LLM (7B/20B)"},
    "biomistral-7b": {"name": "BioMistral-7B", "domain": "biomedical/biology",
                      "source": "https://huggingface.co/BioMistral/BioMistral-7B", "notes": "Mistral + PubMed Central"},
    "esmc": {"name": "ESMC (EvolutionaryScale)", "domain": "protein biology",
             "source": "https://biohub.org/news/world-model-of-protein-biology/", "notes": "protein LM, 2.8B sequences"},
    "medgemma-27b": {"name": "MedGemma 27B", "domain": "medical",
                     "source": "https://huggingface.co/google", "notes": "SOTA open medical (~91% MedQA, Jan 2026)"},
    "openbiollm-70b": {"name": "OpenBioLLM-70B", "domain": "medical",
                       "source": "https://huggingface.co/aaditya", "notes": "open biomedical LLM"},
    "med42-v2": {"name": "Med42-v2", "domain": "medical",
                 "source": "https://huggingface.co/m42-health", "notes": "clinical LLM suite"},
    "meditron3": {"name": "Meditron3", "domain": "medical",
                  "source": "https://huggingface.co/epfl-llm", "notes": "open medical LLM (EPFL)"},
    "saullm-141b": {"name": "SaulLM-141B", "domain": "legal",
                    "source": "https://arxiv.org/abs/2407.19584", "notes": "Mixtral-based, SOTA LegalBench"},
    "saullm-54b": {"name": "SaulLM-54B", "domain": "legal",
                   "source": "https://arxiv.org/abs/2407.19584", "notes": "legal domain-adapted"},
    "fingpt": {"name": "FinGPT", "domain": "finance",
               "source": "https://github.com/AI4Finance-Foundation/FinGPT", "notes": "open financial LLM framework"},
    "mattergen": {"name": "MatterGen", "domain": "materials",
                  "source": "https://arxiv.org/abs/2312.03687", "notes": "generative inorganic materials design"},
    # validated additions (double-check pass, June 2026)
    "climategpt-70b": {"name": "ClimateGPT-70B", "domain": "climate science",
                       "source": "https://github.com/mbzuai-oryx/ClimateGPT", "notes": "Llama-2 + IPCC/climate corpus"},
    "jiuzhou": {"name": "JiuZhou", "domain": "geoscience",
                "source": "https://arxiv.org/pdf/2506.13796", "notes": "Mistral-7B geoscience continued-pretrain"},
    "psycollm": {"name": "PsycoLLM", "domain": "psychology/mental-health",
                 "source": "https://arxiv.org/pdf/2407.05721", "notes": "psychological understanding & evaluation"},
    "voxtral-transcribe-2": {"name": "Voxtral Transcribe 2", "domain": "speech/ASR",
                             "source": "https://mistral.ai/news/voxtral/", "notes": "Apache-2.0, 5.9% WER FLEURS, streaming"},
    "canary-qwen-2.5b": {"name": "Canary-Qwen 2.5B (NVIDIA)", "domain": "speech/ASR",
                         "source": "https://huggingface.co/spaces/hf-audio/open_asr_leaderboard", "notes": "tops Open ASR (5.63% WER), SALM"},
    "qwen3-asr": {"name": "Qwen3-ASR", "domain": "speech/ASR",
                  "source": "https://huggingface.co/Qwen", "notes": "52 languages, LID + timestamps"},
    "whisper-large-v3": {"name": "Whisper large-v3", "domain": "speech/ASR",
                         "source": "https://huggingface.co/openai/whisper-large-v3", "notes": "99+ languages, broad ecosystem"},
    "kimi-k2-6": {"name": "Kimi K2.6", "domain": "flagship reasoning/agentic",
                  "source": "https://huggingface.co/moonshotai", "notes": "highest open-weight Intelligence Index (54)"},
    "glm-5-1": {"name": "GLM-5.1", "domain": "flagship reasoning",
                "source": "https://huggingface.co/THUDM", "notes": "top open-weight 2026"},
    "minimax-m3": {"name": "MiniMax M3", "domain": "flagship multimodal/coding",
                   "source": "https://huggingface.co/MiniMaxAI", "notes": "1M ctx, multimodal, SWE-Bench Pro 59.0 (Jun 2026)"},
}

# Per-capsule domain teacher MoT using the researched specialists (4-role: coach/critic/socratic/referee).
# Fields with a genuine specialist get specialist-led pools; reasoning-heavy fields with no dedicated
# specialist keep strong reasoning models (documented as such).
DOMAIN_SPECIALIST_TEACHERS: dict[str, list[str]] = {
    "mathematician": ["deepseek-math-v2", "qwen3-math", "qwq-32b", "deepseek-r1-distill-qwen-32b"],
    "chemist": ["chemdfm-v1.5-8b", "chemllm-20b", "sciglm-32b", "deepseek-v4-pro"],
    "biologist": ["biomistral-7b", "esmc", "sciglm-32b", "deepseek-v4-pro"],
    "neuroscientist": ["biomistral-7b", "sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
    "medical": ["medgemma-27b", "openbiollm-70b", "med42-v2", "meditron3"],
    "legal": ["saullm-141b", "saullm-54b", "deepseek-v4-pro", "qwen3-30b-a3b"],
    "financial": ["fingpt", "deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b"],
    "economist": ["fingpt", "deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b"],
    "physicist": ["sciglm-32b", "p1-vl-235b", "deepseek-math-v2", "qwq-32b"],
    "cosmologist": ["sciglm-32b", "deepseek-math-v2", "qwq-32b", "deepseek-v4-pro"],
    "scientist": ["sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b", "qwq-32b"],
    "materials_scientist": ["mattergen", "sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
    "logician": ["deepseek-math-v2", "sciglm-32b", "qwq-32b", "deepseek-r1-distill-qwen-32b"],
    "quantum_information": ["sciglm-32b", "deepseek-math-v2", "qwq-32b", "deepseek-r1-distill-qwen-32b"],
    "cryptographer": ["deepseek-math-v2", "deepseek-r1-distill-qwen-32b", "qwq-32b", "sciglm-32b"],
    # validated specialist swaps (double-check pass): real domain models found for these fields
    "auditory": ["voxtral-transcribe-2", "canary-qwen-2.5b", "qwen3-asr", "whisper-large-v3"],
    "psychologist": ["psycollm", "deepseek-v4-pro", "qwen3-30b-a3b", "deepseek-r1-distill-qwen-32b"],
    "climate_scientist": ["climategpt-70b", "sciglm-32b", "deepseek-v4-pro", "deepseek-r1-distill-qwen-32b"],
    "geologist": ["jiuzhou", "sciglm-32b", "deepseek-v4-pro", "qwq-32b"],
    "oceanographer": ["climategpt-70b", "sciglm-32b", "biomistral-7b", "deepseek-v4-pro"],
}
# Merge researched specialists into the capsule specs (single source of truth).
for _key, _teachers in DOMAIN_SPECIALIST_TEACHERS.items():
    EXPERT_CAPSULES[_key]["teachers"] = _teachers
    EXPERT_CAPSULES[_key]["teacher_source"] = "domain-specialist-researched-2026-06"

CAPSULE_KEYS = tuple(EXPERT_CAPSULES.keys())   # the canonical 19 + expandable frontier areas


def domain_mixture_of_teachers(capsule_key: str) -> list[dict[str, str]]:
    """The expert's domain Mixture-of-Teachers: one teacher per role, chosen FOR this domain."""
    spec = EXPERT_CAPSULES[capsule_key]
    teachers = spec["teachers"]
    return [{"teacher_id": teachers[i % len(teachers)], "role": role} for i, role in enumerate(ROLES)]


def build_curriculum(capsule_key: str, *, difficulty_levels: int = 5) -> dict[str, Any]:
    """The curriculum DESIGNED AROUND this expert's area of expertise.

    Task families come from the domain; the Challenger (R-Zero) escalates difficulty within the domain;
    teachers are the domain MoT; eval gates are domain-specific. This is what the Curriculum-Architect
    Capsule produces per expert - not a one-size-fits-all pipeline.
    """
    if capsule_key not in EXPERT_CAPSULES:
        raise ValueError(f"unknown capsule {capsule_key!r}; known {CAPSULE_KEYS}")
    spec = EXPERT_CAPSULES[capsule_key]
    families = spec["task_families"]
    # difficulty ladder: each domain task family escalated across levels (Challenger frontier).
    ladder = [
        {"level": lvl, "families": families, "challenger_difficulty": round((lvl + 1) / difficulty_levels, 4)}
        for lvl in range(difficulty_levels)
    ]
    return {
        "capsule": capsule_key,
        "area_of_expertise": spec["area_of_expertise"],
        "task_families": families,                      # DOMAIN-specific tasks
        "difficulty_ladder": ladder,                    # Challenger escalation within the domain
        "teacher_mixture": domain_mixture_of_teachers(capsule_key),   # DOMAIN MoT (per-domain weighting)
        "eval_gates": spec["eval_gates"],               # DOMAIN eval gates
        "curriculum_source": "curriculum-architect-capsule-from-area-of-expertise",
        "production_mutation_allowed": False,
        "claim_boundary": "domain-curriculum-spec-shadow-only-not-run",
    }


def all_curricula() -> dict[str, dict[str, Any]]:
    return {key: build_curriculum(key) for key in CAPSULE_KEYS}
