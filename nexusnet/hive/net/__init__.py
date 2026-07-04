"""The actual trainable NexusNet neural network (PyTorch). Requires torch.

Real learnable parameters + backprop + optimizer. This is the substrate that trains itself (via the
Ivy-League teachers, dreaming, and federated learning) and grows into the birthed MoE model.
"""
from __future__ import annotations

from .model import NexusNetModel, MoECapsuleLayer, SwiGLUExpert, MiniNexusNetExpert, squash
from .governed_routing import GovernedSparseRouter, fabric_expert_governance
from .layers import (
    RMSNorm,
    GQAttention,
    EBTRefinement,
    RecurrentDepth,
    MultiPlaneMemory,
    CortexPool,
    build_rope,
    apply_rope,
)
from .transformer import NexusNetTransformer, TransformerBlock
from .advanced_layers import (
    SelectiveSSM,
    MLAttention,
    HybridSSMAttentionBlock,
    build_rope_yarn,
)
from .train import make_nonlinear_dataset, make_sequence_dataset, train_model, train_demo
from .tokenizer import ByteTokenizer, VOCAB_SIZE
from .lm import NexusNetLM, CausalLMBlock
from .encoders import (
    TextEncoder, CodeEncoder, VisionEncoder, AudioEncoder, VideoEncoder, TableEncoder,
    MultimodalFusion, MODALITIES,
)
from .bpe_tokenizer import BPETokenizer
from .quantize_export import (
    FakeQuantize, quantization_error, quantize_dynamic_int8, export_birthed_model,
)
from .retrieval import (
    MemoryStore, RetrievalAugmentedMemory, KnowledgeGraph, GraphGroundedMemory,
)
from .inference_runtime import (
    speculative_decode, PrefixCache, ContinuousBatcher, kv_cache_report,
)
from .hardware_safe_mode import (
    HardwareProfile, RuntimePlan, AdaptiveRuntimePolicy, SafeModeGuard, SafeModeDecision, safe_forward,
)
from .neurosymbolic import Rule, SymbolicRuleEngine, NeuroSymbolicReasoner
from .born_serving import BornModelRunner
from .dreaming_jepa import JEPAWorldModel, sigreg, dream_step, train_world_model
from .hopfield import (
    hopfield_retrieve, ModernHopfield, HopfieldAssociativeStore, HopfieldLayer,
)
from .federated import (
    fedavg, divergence_guard, secure_aggregate, federated_train_round,
)
from .governed_federation import (
    sanitized_update_packet, verify_packet, governed_federated_round,
)
from .recursive_dream_training import recursive_dream_train, recursive_dream_cycles
from .integration import MultimodalNexusNet, birth_expert
from .birth_orchestrator import birth_expert_node, birth_hive
from .full_birth import full_birth
from .real_birth import build_real_corpus, make_token_windows, run_real_birth
from .absorption import (
    native_features, absorb_wrapper, BornNexus,
    NATIVE_WRAPPER_FEATURES, CAPABILITY_WRAPPER_FEATURES,
)
from .efficiency_autopilot import (
    layer_quant_sensitivity, optimize_bit_allocation, EfficiencyAutopilot,
)
from .base_model_attach import inspect_base_model, LoRAAdapter, attach_base_model_adapters
from .expert_assimilation import assimilate_expert, make_swiglu_expert, fuse_moe_layers
from .meta_evolution import (
    ModelGenome, random_genome, mutate, crossover, genome_fitness, evolve_architecture,
)
from .kv_cache import LayerKVCache, cached_generate
from .quantize_advanced import nf4_quantize, gptq_quantize, awq_quantize, NF4_CODEBOOK
from .regulation_hooks import (
    NeuralImmuneGate, consequence_weighted_loss, SelectiveDecayRegularizer,
)
from .observability import Span, GenAISpanRecorder
from .distill import kd_loss_torch, FrozenTeacher, train_with_distillation
from .rl import correctness_reward, grpo_step, train_grpo, r_zero_self_play
from .corpora import (
    build_domain_corpus, build_rich_domain_corpus, domain_corpus_for_capsule, all_domain_corpora,
)
from .eval_gates import measure_language_model, evaluate_gate, evaluate_capsule_gates
from .train_infra import save_training_state, load_training_state, fit_lm
from .birth import (
    make_corpus_windows,
    make_structured_corpus,
    split_windows,
    train_language_model,
    independence_milestones,
    evaluate_node_promotions,
    save_checkpoint,
    load_checkpoint,
    birth_model,
)

__all__ = [
    "NexusNetModel",
    "MoECapsuleLayer",
    "SwiGLUExpert",
    "MiniNexusNetExpert",
    "squash",
    "GovernedSparseRouter",
    "fabric_expert_governance",
    "RMSNorm",
    "GQAttention",
    "EBTRefinement",
    "RecurrentDepth",
    "MultiPlaneMemory",
    "CortexPool",
    "build_rope",
    "apply_rope",
    "NexusNetTransformer",
    "TransformerBlock",
    "SelectiveSSM",
    "MLAttention",
    "HybridSSMAttentionBlock",
    "build_rope_yarn",
    "make_nonlinear_dataset",
    "make_sequence_dataset",
    "train_model",
    "train_demo",
    "ByteTokenizer",
    "VOCAB_SIZE",
    "NexusNetLM",
    "CausalLMBlock",
    "make_corpus_windows",
    "make_structured_corpus",
    "split_windows",
    "train_language_model",
    "independence_milestones",
    "evaluate_node_promotions",
    "save_checkpoint",
    "load_checkpoint",
    "birth_model",
    "kd_loss_torch",
    "FrozenTeacher",
    "train_with_distillation",
    "correctness_reward",
    "grpo_step",
    "train_grpo",
    "r_zero_self_play",
    "build_domain_corpus",
    "build_rich_domain_corpus",
    "domain_corpus_for_capsule",
    "all_domain_corpora",
    "birth_expert_node",
    "birth_hive",
    "full_birth",
    "build_real_corpus",
    "make_token_windows",
    "run_real_birth",
    "native_features",
    "absorb_wrapper",
    "BornNexus",
    "layer_quant_sensitivity",
    "optimize_bit_allocation",
    "EfficiencyAutopilot",
    "sanitized_update_packet",
    "verify_packet",
    "governed_federated_round",
    "recursive_dream_train",
    "recursive_dream_cycles",
    "inspect_base_model",
    "LoRAAdapter",
    "attach_base_model_adapters",
    "assimilate_expert",
    "make_swiglu_expert",
    "fuse_moe_layers",
    "ModelGenome",
    "random_genome",
    "mutate",
    "crossover",
    "genome_fitness",
    "evolve_architecture",
    "measure_language_model",
    "evaluate_gate",
    "evaluate_capsule_gates",
    "save_training_state",
    "load_training_state",
    "fit_lm",
    "TextEncoder",
    "CodeEncoder",
    "VisionEncoder",
    "AudioEncoder",
    "VideoEncoder",
    "TableEncoder",
    "MultimodalFusion",
    "MODALITIES",
    "BPETokenizer",
    "FakeQuantize",
    "quantization_error",
    "quantize_dynamic_int8",
    "export_birthed_model",
    "MemoryStore",
    "RetrievalAugmentedMemory",
    "KnowledgeGraph",
    "GraphGroundedMemory",
    "speculative_decode",
    "PrefixCache",
    "ContinuousBatcher",
    "kv_cache_report",
    "HardwareProfile",
    "RuntimePlan",
    "AdaptiveRuntimePolicy",
    "SafeModeGuard",
    "SafeModeDecision",
    "safe_forward",
    "Rule",
    "SymbolicRuleEngine",
    "NeuroSymbolicReasoner",
    "BornModelRunner",
    "JEPAWorldModel",
    "sigreg",
    "dream_step",
    "train_world_model",
    "hopfield_retrieve",
    "ModernHopfield",
    "HopfieldAssociativeStore",
    "HopfieldLayer",
    "fedavg",
    "divergence_guard",
    "secure_aggregate",
    "federated_train_round",
    "MultimodalNexusNet",
    "birth_expert",
    "LayerKVCache",
    "cached_generate",
    "nf4_quantize",
    "gptq_quantize",
    "awq_quantize",
    "NF4_CODEBOOK",
    "NeuralImmuneGate",
    "consequence_weighted_loss",
    "SelectiveDecayRegularizer",
    "Span",
    "GenAISpanRecorder",
]
