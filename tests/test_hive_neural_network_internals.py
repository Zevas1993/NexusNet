from __future__ import annotations

from pathlib import Path

from nexusnet.hive import HiveForwardPassRequest, HiveNeuralSubstrate


def test_hive_forward_pass_materializes_embedding_attention_gate_and_backprop_ledgers(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-internals-session",
            task_id="neural-network-internals",
            intent="Route multimodal neural pathway internals through embeddings, attention, gates, and backpropagation.",
            requested_capabilities=["routing", "vision", "audio", "memory", "evaluation", "dreaming", "federation"],
            memory_refs=["memory::vision-context", "memory::audio-context"],
            requested_actions=[
                {"action_id": "inspect-internals", "action_type": "read", "target_ref": "hive-neural-internals"}
            ],
            max_loops=4,
        )
    )

    embedding = result["embedding_tensor_ledger"]
    attention = result["attention_routing_ledger"]
    gate = result["sparse_expert_gate_ledger"]
    backprop = result["loss_backpropagation_ledger"]

    assert embedding["surface_id"] == "hive-embedding-tensor-ledger-v0"
    assert embedding["activation_ref"] == result["activation"]["activation_id"]
    assert embedding["token_count"] >= 8
    assert embedding["embedding_shape"] == [embedding["token_count"], embedding["embedding_dimension"]]
    assert embedding["embedding_dimension"] == 13
    assert embedding["token_privacy"]["raw_tokens_stored"] is False
    assert embedding["token_privacy"]["raw_intent_stored"] is False
    assert all("token_hash" in token for token in embedding["token_records"])
    assert all("raw_token" not in token for token in embedding["token_records"])
    assert embedding["formula_basis"]["dimension_basis"] == "fibonacci_13"
    assert embedding["artifact_path"] and Path(embedding["artifact_path"]).exists()

    assert attention["surface_id"] == "hive-attention-routing-ledger-v0"
    assert attention["embedding_tensor_ref"] == embedding["embedding_ledger_id"]
    assert attention["attention_head_count"] >= 4
    assert attention["attention_integrity"]["softmax_normalized"] is True
    assert attention["attention_integrity"]["raw_private_content_read"] is False
    assert all(abs(sum(weight["attention_weight"] for weight in head["focus_weights"]) - 1.0) <= 0.01 for head in attention["attention_heads"])
    assert {"selected_nodes", "memory_refs", "policy_gate"}.issubset(
        {target["target_kind"] for target in attention["focus_targets"]}
    )

    assert gate["surface_id"] == "hive-sparse-expert-gate-ledger-v0"
    assert gate["attention_ref"] == attention["attention_ledger_id"]
    assert gate["router_ref"] == result["route_decision"]["router_id"]
    assert gate["top_k"] == result["route_decision"]["sparse_top_k"]
    assert gate["selected_expert_node_ids"] == result["route_decision"]["selected_node_ids"]
    assert gate["gate_integrity"]["gate_distribution_normalized"] is True
    assert gate["gate_integrity"]["non_selected_nodes_visible_idle"] is True
    assert gate["gate_integrity"]["active_production_routing_mutated"] is False
    assert abs(sum(route["gate_weight"] for route in gate["expert_gate_distribution"]) - 1.0) <= 0.01

    assert backprop["surface_id"] == "hive-loss-backpropagation-ledger-v0"
    assert backprop["sparse_gate_ref"] == gate["gate_ledger_id"]
    assert backprop["attention_ref"] == attention["attention_ledger_id"]
    assert backprop["embedding_tensor_ref"] == embedding["embedding_ledger_id"]
    assert backprop["neuroplastic_weight_ref"] == result["neuroplastic_weight_ledger"]["weight_ledger_id"]
    assert backprop["neuromodulatory_state_ref"] == result["neuromodulatory_state_ledger"]["neuromodulator_id"]
    assert {term["loss_name"] for term in backprop["loss_terms"]} >= {
        "route_quality_loss",
        "policy_risk_loss",
        "uncertainty_loss",
        "federation_privacy_loss",
    }
    assert backprop["gradient_integrity"]["gradient_clipping_applied"] is True
    assert backprop["gradient_integrity"]["active_model_weights_mutated"] is False
    assert backprop["optimizer_step"]["optimizer_state"] == "shadow_only"
    assert backprop["optimizer_step"]["active_route_mutated"] is False

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["embedding_tensor_ref"] == embedding["embedding_ledger_id"]
    assert runtime["artifact_refs"]["attention_routing_ref"] == attention["attention_ledger_id"]
    assert runtime["artifact_refs"]["sparse_expert_gate_ref"] == gate["gate_ledger_id"]
    assert runtime["artifact_refs"]["loss_backpropagation_ref"] == backprop["backpropagation_id"]
    assert runtime["input_contract"] == (
        "neural-bus-blackboard-sensory-temporal-memory-embedding-attention-normalization-gate-feedforward-"
        "microcircuit-pathway-transmission-plasticity-neuromodulator-latent-loop-kv-cache-backprop-"
        "optimizer-school-ledger-only"
    )


def test_hive_neural_network_internal_ledgers_are_replayable_and_scorecard_visible(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-internals-replay-session",
            intent="Replay the internal neural pathway ledgers for operator inspection.",
            requested_capabilities=["routing", "memory", "evaluation"],
            max_loops=2,
        )
    )

    replay = substrate.replay(session_id="neural-internals-replay-session")
    assert replay["embedding_tensor_chain"][0]["embedding_ledger_id"] == result["embedding_tensor_ledger"]["embedding_ledger_id"]
    assert replay["attention_routing_chain"][0]["attention_ledger_id"] == result["attention_routing_ledger"]["attention_ledger_id"]
    assert replay["sparse_expert_gate_chain"][0]["gate_ledger_id"] == result["sparse_expert_gate_ledger"]["gate_ledger_id"]
    assert replay["loss_backpropagation_chain"][0]["backpropagation_id"] == result["loss_backpropagation_ledger"]["backpropagation_id"]
    assert "embedding_tensor_chain" in replay["control_panel_replay"]["available_chains"]
    assert "attention_routing_chain" in replay["control_panel_replay"]["available_chains"]
    assert "sparse_expert_gate_chain" in replay["control_panel_replay"]["available_chains"]
    assert "loss_backpropagation_chain" in replay["control_panel_replay"]["available_chains"]
    assert replay["control_panel_replay"]["chain_counts"]["embedding_tensor_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["attention_routing_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["sparse_expert_gate_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["loss_backpropagation_chain"] == 1

    summary = substrate.summary(session_id="neural-internals-replay-session")
    assert summary["embedding_tensor_ledger"]["embedding_ledger_count"] == 1
    assert summary["attention_routing_ledger"]["attention_ledger_count"] == 1
    assert summary["sparse_expert_gate_ledger"]["gate_ledger_count"] == 1
    assert summary["loss_backpropagation_ledger"]["backpropagation_ledger_count"] == 1

    scorecard = substrate.scorecard(session_id="neural-internals-replay-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert {"HiveEmbeddingTensorLedger", "HiveAttentionRoutingLedger", "HiveSparseExpertGateLedger", "HiveLossBackpropagationLedger"}.issubset(component_ids)
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-060" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-061" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-062" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-063" in scorecard["source_documents"]


def test_hive_forward_pass_materializes_normalization_feedforward_loop_and_kv_cache_ledgers(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-runtime-internals-session",
            task_id="neural-runtime-internals",
            intent="Run transformer-style normalization feedforward latent loop and KV cache internals.",
            requested_capabilities=["routing", "runtime", "kv_cache", "quantization", "evaluation"],
            memory_refs=["memory::kv-cache-research"],
            max_loops=4,
        )
    )

    residual = result["residual_normalization_ledger"]
    feedforward = result["feedforward_expert_ledger"]
    latent_loop = result["latent_loop_exit_ledger"]
    kv_cache = result["kv_cache_compression_ledger"]

    assert residual["surface_id"] == "hive-residual-normalization-ledger-v0"
    assert residual["embedding_tensor_ref"] == result["embedding_tensor_ledger"]["embedding_ledger_id"]
    assert residual["attention_ref"] == result["attention_routing_ledger"]["attention_ledger_id"]
    assert residual["normalization_policy"]["normalization_kind"] == "rmsnorm-symbolic-v0"
    assert residual["normalization_integrity"]["residual_stream_preserved"] is True
    assert residual["normalization_integrity"]["active_tensor_values_mutated"] is False
    assert {stream["stream_kind"] for stream in residual["normalized_streams"]} >= {
        "embedding_residual",
        "attention_residual",
        "blackboard_residual",
    }

    assert feedforward["surface_id"] == "hive-feedforward-expert-ledger-v0"
    assert feedforward["residual_normalization_ref"] == residual["normalization_ledger_id"]
    assert feedforward["sparse_gate_ref"] == result["sparse_expert_gate_ledger"]["gate_ledger_id"]
    assert feedforward["expert_unit_count"] == len(result["route_decision"]["selected_node_ids"])
    assert feedforward["feedforward_policy"]["activation_function"] == "geglu-symbolic"
    assert feedforward["feedforward_integrity"]["active_expert_weights_mutated"] is False
    assert all(unit["expansion_factor"] == 4 for unit in feedforward["expert_units"])

    assert latent_loop["surface_id"] == "hive-latent-loop-exit-ledger-v0"
    assert latent_loop["attention_ref"] == result["attention_routing_ledger"]["attention_ledger_id"]
    assert latent_loop["sparse_gate_ref"] == result["sparse_expert_gate_ledger"]["gate_ledger_id"]
    assert latent_loop["feedforward_ref"] == feedforward["feedforward_ledger_id"]
    assert latent_loop["loop_step_count"] == result["loop_summary"]["loop_count"]
    assert latent_loop["exit_gate_policy"]["probability_model"] == "hazard-survival-cdf"
    assert latent_loop["exit_gate_integrity"]["final_step_forced_exit_if_needed"] is True
    assert latent_loop["exit_gate_integrity"]["vocabulary_chain_of_thought_required"] is False
    assert latent_loop["exit_steps"][-1]["cdf_exit_mass"] <= 1.0

    assert kv_cache["surface_id"] == "hive-kv-cache-compression-ledger-v0"
    assert kv_cache["attention_ref"] == result["attention_routing_ledger"]["attention_ledger_id"]
    assert kv_cache["latent_loop_ref"] == latent_loop["latent_loop_id"]
    assert kv_cache["kv_cache_integrity"]["raw_kv_values_stored"] is False
    assert kv_cache["kv_cache_integrity"]["active_inference_backend_mutated"] is False
    assert kv_cache["selected_shadow_policy"]["policy_id"] == "hybrid-heavy-hitter-quantized-low-rank"
    assert kv_cache["selected_shadow_policy"]["requires_sandbox_benchmark"] is True

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["residual_normalization_ref"] == residual["normalization_ledger_id"]
    assert runtime["artifact_refs"]["feedforward_expert_ref"] == feedforward["feedforward_ledger_id"]
    assert runtime["artifact_refs"]["latent_loop_exit_ref"] == latent_loop["latent_loop_id"]
    assert runtime["artifact_refs"]["kv_cache_compression_ref"] == kv_cache["kv_cache_ledger_id"]


def test_hive_runtime_internal_ledgers_are_replayable_and_scorecard_visible(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-runtime-replay-session",
            intent="Replay normalization feedforward loop and kv cache internals.",
            requested_capabilities=["runtime", "kv_cache", "evaluation"],
            max_loops=3,
        )
    )

    replay = substrate.replay(session_id="neural-runtime-replay-session")
    assert replay["residual_normalization_chain"][0]["normalization_ledger_id"] == result["residual_normalization_ledger"]["normalization_ledger_id"]
    assert replay["feedforward_expert_chain"][0]["feedforward_ledger_id"] == result["feedforward_expert_ledger"]["feedforward_ledger_id"]
    assert replay["latent_loop_exit_chain"][0]["latent_loop_id"] == result["latent_loop_exit_ledger"]["latent_loop_id"]
    assert replay["kv_cache_compression_chain"][0]["kv_cache_ledger_id"] == result["kv_cache_compression_ledger"]["kv_cache_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["residual_normalization_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["feedforward_expert_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["latent_loop_exit_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["kv_cache_compression_chain"] == 1

    summary = substrate.summary(session_id="neural-runtime-replay-session")
    assert summary["residual_normalization_ledger"]["normalization_ledger_count"] == 1
    assert summary["feedforward_expert_ledger"]["feedforward_ledger_count"] == 1
    assert summary["latent_loop_exit_ledger"]["latent_loop_ledger_count"] == 1
    assert summary["kv_cache_compression_ledger"]["kv_cache_ledger_count"] == 1

    scorecard = substrate.scorecard(session_id="neural-runtime-replay-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert {"HiveResidualNormalizationLedger", "HiveFeedForwardExpertLedger", "HiveLatentLoopExitLedger", "HiveKVCacheCompressionLedger"}.issubset(component_ids)
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-064" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-065" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-066" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-067" in scorecard["source_documents"]


def test_hive_forward_pass_materializes_sensory_temporal_memory_optimizer_and_output_ledgers(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-plane-completion-session",
            task_id="neural-plane-completion",
            intent="Bind sensory inputs, temporal positions, memory engrams, optimizer school, and output decoder.",
            requested_capabilities=["memory", "routing", "evaluation", "teacher", "output"],
            memory_refs=["memory::source-canon", "memory::operator-history"],
            requested_actions=[
                {
                    "action_id": "render-plane-proof",
                    "action_type": "read",
                    "target_ref": "runtime/artifacts/hive/proof.md",
                }
            ],
            max_loops=3,
        )
    )

    sensory = result["sensory_input_ledger"]
    temporal = result["temporal_positional_ledger"]
    memory = result["memory_engram_ledger"]
    optimizer = result["optimizer_school_ledger"]
    output = result["action_output_decoder_ledger"]

    assert sensory["surface_id"] == "hive-sensory-input-ledger-v0"
    assert sensory["activation_ref"] == result["activation"]["activation_id"]
    assert sensory["normalized_channel_count"] >= 4
    assert sensory["tokenizer_policy"]["tokenizer_ref"] == "metadata-estimator-v0"
    assert sensory["input_integrity"]["raw_intent_stored"] is False
    assert sensory["input_integrity"]["raw_action_targets_stored"] is False
    assert {"operator_intent", "capability_signals", "memory_refs", "action_refs"}.issubset(
        {channel["channel_kind"] for channel in sensory["normalized_channels"]}
    )

    assert temporal["surface_id"] == "hive-temporal-positional-ledger-v0"
    assert temporal["sensory_input_ref"] == sensory["sensory_ledger_id"]
    assert temporal["embedding_tensor_ref"] == result["embedding_tensor_ledger"]["embedding_ledger_id"]
    assert temporal["position_policy"]["position_encoding"] == "rotary-golden-angle-symbolic"
    assert temporal["temporal_integrity"]["active_context_order_mutated"] is False
    assert temporal["position_count"] == len(temporal["position_records"])

    assert memory["surface_id"] == "hive-memory-engram-ledger-v0"
    assert memory["temporal_positional_ref"] == temporal["temporal_ledger_id"]
    assert memory["memory_ref_count"] == 2
    assert memory["retrieval_policy"]["retrieval_mode"] == "reference-only-engram-binding"
    assert memory["memory_integrity"]["raw_memory_content_stored"] is False
    assert all(record["raw_memory_content_stored"] is False for record in memory["retrieval_records"])

    assert optimizer["surface_id"] == "hive-optimizer-school-ledger-v0"
    assert optimizer["backpropagation_ref"] == result["loss_backpropagation_ledger"]["backpropagation_id"]
    assert optimizer["memory_engram_ref"] == memory["memory_ledger_id"]
    assert optimizer["optimizer_policy"]["update_mode"] == "shadow-curriculum-proposal"
    assert optimizer["optimizer_integrity"]["active_model_weights_mutated"] is False
    assert optimizer["optimizer_integrity"]["human_governance_required"] is True

    assert output["surface_id"] == "hive-action-output-decoder-ledger-v0"
    assert output["downstream_runtime_ref"] == result["downstream_node_runtime"]["runtime_id"]
    assert output["optimizer_school_ref"] == optimizer["optimizer_ledger_id"]
    assert output["decoded_output_count"] == result["downstream_node_runtime"]["node_output_count"]
    assert output["decoder_policy"]["decoder_mode"] == "artifact-bound-output-decoder"
    assert output["output_integrity"]["raw_outputs_exported"] is False
    assert output["output_integrity"]["active_external_delivery_mutated"] is False


def test_hive_plane_completion_ledgers_are_replayable_and_scorecard_visible(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-plane-completion-replay-session",
            intent="Replay the completed neural plane internals.",
            requested_capabilities=["memory", "output", "evaluation"],
            memory_refs=["memory::canon"],
            max_loops=2,
        )
    )

    replay = substrate.replay(session_id="neural-plane-completion-replay-session")
    assert replay["sensory_input_chain"][0]["sensory_ledger_id"] == result["sensory_input_ledger"]["sensory_ledger_id"]
    assert replay["temporal_positional_chain"][0]["temporal_ledger_id"] == result["temporal_positional_ledger"]["temporal_ledger_id"]
    assert replay["memory_engram_chain"][0]["memory_ledger_id"] == result["memory_engram_ledger"]["memory_ledger_id"]
    assert replay["optimizer_school_chain"][0]["optimizer_ledger_id"] == result["optimizer_school_ledger"]["optimizer_ledger_id"]
    assert replay["action_output_decoder_chain"][0]["output_decoder_id"] == result["action_output_decoder_ledger"]["output_decoder_id"]
    assert replay["control_panel_replay"]["chain_counts"]["sensory_input_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["temporal_positional_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["memory_engram_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["optimizer_school_chain"] == 1
    assert replay["control_panel_replay"]["chain_counts"]["action_output_decoder_chain"] == 1

    summary = substrate.summary(session_id="neural-plane-completion-replay-session")
    assert summary["sensory_input_ledger"]["sensory_ledger_count"] == 1
    assert summary["temporal_positional_ledger"]["temporal_ledger_count"] == 1
    assert summary["memory_engram_ledger"]["memory_ledger_count"] == 1
    assert summary["optimizer_school_ledger"]["optimizer_ledger_count"] == 1
    assert summary["action_output_decoder_ledger"]["output_decoder_count"] == 1

    scorecard = substrate.scorecard(session_id="neural-plane-completion-replay-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert {
        "HiveSensoryInputLedger",
        "HiveTemporalPositionalLedger",
        "HiveMemoryEngramLedger",
        "HiveOptimizerSchoolLedger",
        "HiveActionOutputDecoderLedger",
    }.issubset(component_ids)
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-068" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-069" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-070" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-071" in scorecard["source_documents"]
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-072" in scorecard["source_documents"]


def test_hive_neural_pathway_map_exposes_full_plane_adjacency_matrix(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-pathway-matrix-session",
            intent="Prove the full hive neural network plane adjacency matrix.",
            requested_capabilities=["routing", "memory", "evaluation", "output"],
            memory_refs=["memory::canon"],
            max_loops=3,
        )
    )

    pathway = result["neural_pathway_map"]
    matrix = pathway["plane_adjacency_matrix"]

    assert matrix["surface_id"] == "hive-plane-adjacency-matrix-v0"
    assert matrix["matrix_shape"] == [result["plane_trace"]["record_count"], result["plane_trace"]["record_count"]]
    assert matrix["node_order"][0] == "sensory-input"
    assert matrix["node_order"][-1] == "checkpoint-rewind"
    assert matrix["edge_count"] == len(matrix["weighted_edges"])
    assert matrix["matrix_integrity"]["fully_connected_visibility"] is True
    assert matrix["matrix_integrity"]["active_production_mutated"] is False
    assert matrix["matrix_integrity"]["direct_local_state_reads"] == []

    edge_pairs = {(edge["from_plane"], edge["to_plane"]) for edge in matrix["weighted_edges"]}
    assert ("sensory-input", "embedding-representation") in edge_pairs
    assert ("embedding-representation", "temporal-positional") in edge_pairs
    assert ("temporal-positional", "memory-engram") in edge_pairs
    assert ("learning-eval-loss", "optimizer-school") in edge_pairs
    assert ("action-output", "checkpoint-rewind") in edge_pairs

    artifact_refs = matrix["plane_artifact_refs"]
    assert artifact_refs["sensory-input"] == result["sensory_input_ledger"]["sensory_ledger_id"]
    assert artifact_refs["embedding-representation"] == result["embedding_tensor_ledger"]["embedding_ledger_id"]
    assert artifact_refs["temporal-positional"] == result["temporal_positional_ledger"]["temporal_ledger_id"]
    assert artifact_refs["memory-engram"] == result["memory_engram_ledger"]["memory_ledger_id"]
    assert artifact_refs["optimizer-school"] == result["optimizer_school_ledger"]["optimizer_ledger_id"]
    assert artifact_refs["action-output"] == result["action_output_decoder_ledger"]["output_decoder_id"]

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["plane_adjacency_matrix_ref"] == matrix["matrix_id"]
    assert all(matrix["matrix_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-pathway-matrix-session")
    assert replay["neural_pathway_chain"][0]["plane_adjacency_matrix"]["matrix_id"] == matrix["matrix_id"]

    summary = substrate.summary(session_id="neural-pathway-matrix-session")
    assert summary["neural_pathway_ledger"]["latest_plane_adjacency_matrix_ref"] == matrix["matrix_id"]

    scorecard = substrate.scorecard(session_id="neural-pathway-matrix-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HivePlaneAdjacencyMatrix" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-073" in scorecard["source_documents"]


def test_hive_forward_propagation_ledger_records_all_plane_state_handoffs(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-forward-propagation-session",
            intent="Record state-vector propagation through the entire hive neural substrate.",
            requested_capabilities=["routing", "memory", "evaluation", "output", "checkpoint"],
            memory_refs=["memory::canon", "memory::runtime"],
            max_loops=3,
        )
    )

    propagation = result["forward_propagation_ledger"]
    matrix = result["neural_pathway_map"]["plane_adjacency_matrix"]

    assert propagation["surface_id"] == "hive-forward-propagation-ledger-v0"
    assert propagation["plane_adjacency_matrix_ref"] == matrix["matrix_id"]
    assert propagation["step_count"] == result["plane_trace"]["record_count"]
    assert propagation["propagation_steps"][0]["plane_id"] == "sensory-input"
    assert propagation["propagation_steps"][-1]["plane_id"] == "checkpoint-rewind"
    assert propagation["propagation_steps"][0]["artifact_ref"] == result["sensory_input_ledger"]["sensory_ledger_id"]
    assert propagation["propagation_steps"][-1]["artifact_ref"] == result["checkpoint"]["checkpoint_id"]
    assert all(step["raw_private_content_stored"] is False for step in propagation["propagation_steps"])
    assert all(step["active_production_mutated"] is False for step in propagation["propagation_steps"])
    assert propagation["propagation_integrity"]["all_planes_covered"] is True
    assert propagation["propagation_integrity"]["direct_local_state_reads"] == []
    assert propagation["propagation_integrity"]["active_production_mutated"] is False

    output = result["action_output_decoder_ledger"]
    assert output["forward_propagation_ref"] == propagation["propagation_id"]

    replay = substrate.replay(session_id="neural-forward-propagation-session")
    assert replay["forward_propagation_chain"][0]["propagation_id"] == propagation["propagation_id"]
    assert replay["control_panel_replay"]["chain_counts"]["forward_propagation_chain"] == 1

    summary = substrate.summary(session_id="neural-forward-propagation-session")
    assert summary["forward_propagation_ledger"]["propagation_ledger_count"] == 1
    assert summary["forward_propagation_ledger"]["latest_plane_adjacency_matrix_ref"] == matrix["matrix_id"]

    scorecard = substrate.scorecard(session_id="neural-forward-propagation-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveForwardPropagationLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-074" in scorecard["source_documents"]


def test_hive_backward_propagation_ledger_records_reverse_credit_assignment_path(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-backward-propagation-session",
            intent="Record reverse gradient credit assignment across the whole hive neural substrate.",
            requested_capabilities=["routing", "memory", "evaluation", "teacher", "federation"],
            memory_refs=["memory::canon", "memory::eval"],
            max_loops=3,
        )
    )

    backward = result["backward_propagation_ledger"]
    forward = result["forward_propagation_ledger"]
    backprop = result["loss_backpropagation_ledger"]

    assert backward["surface_id"] == "hive-backward-propagation-ledger-v0"
    assert backward["forward_propagation_ref"] == forward["propagation_id"]
    assert backward["loss_backpropagation_ref"] == backprop["backpropagation_id"]
    assert backward["plane_adjacency_matrix_ref"] == forward["plane_adjacency_matrix_ref"]
    assert backward["step_count"] == forward["step_count"]
    assert backward["reverse_steps"][0]["plane_id"] == "checkpoint-rewind"
    assert backward["reverse_steps"][-1]["plane_id"] == "sensory-input"
    assert backward["reverse_steps"][0]["source_forward_step_ref"] == forward["propagation_steps"][-1]["step_id"]
    assert backward["reverse_steps"][-1]["source_forward_step_ref"] == forward["propagation_steps"][0]["step_id"]
    assert all(step["raw_private_content_stored"] is False for step in backward["reverse_steps"])
    assert all(step["active_model_weights_mutated"] is False for step in backward["reverse_steps"])
    assert backward["backward_integrity"]["all_forward_steps_covered"] is True
    assert backward["backward_integrity"]["direct_local_state_reads"] == []
    assert backward["backward_integrity"]["active_model_weights_mutated"] is False

    replay = substrate.replay(session_id="neural-backward-propagation-session")
    assert replay["backward_propagation_chain"][0]["backward_propagation_id"] == backward["backward_propagation_id"]
    assert replay["control_panel_replay"]["chain_counts"]["backward_propagation_chain"] == 1

    summary = substrate.summary(session_id="neural-backward-propagation-session")
    assert summary["backward_propagation_ledger"]["backward_propagation_count"] == 1
    assert summary["backward_propagation_ledger"]["latest_forward_propagation_ref"] == forward["propagation_id"]

    scorecard = substrate.scorecard(session_id="neural-backward-propagation-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveBackwardPropagationLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-075" in scorecard["source_documents"]


def test_hive_parameter_tensor_ledger_maps_symbolic_weights_biases_and_gates(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-parameter-tensor-session",
            intent="Map symbolic parameter tensors for every neural substrate plane without storing raw weights.",
            requested_capabilities=["routing", "memory", "evaluation", "quantization", "teacher"],
            memory_refs=["memory::canon", "memory::parameter-policy"],
            max_loops=4,
        )
    )

    parameter = result["parameter_tensor_ledger"]
    backward = result["backward_propagation_ledger"]

    assert parameter["surface_id"] == "hive-parameter-tensor-ledger-v0"
    assert parameter["backward_propagation_ref"] == backward["backward_propagation_id"]
    assert parameter["neuroplastic_weight_ref"] == result["neuroplastic_weight_ledger"]["weight_ledger_id"]
    assert parameter["plane_adjacency_matrix_ref"] == result["forward_propagation_ledger"]["plane_adjacency_matrix_ref"]
    assert parameter["parameter_tensor_count"] == len(parameter["parameter_tensors"])
    assert parameter["parameter_tensor_count"] >= result["plane_trace"]["record_count"]
    assert {"weight", "bias", "gate", "norm", "adapter", "output_projection"}.issubset(
        {tensor["tensor_role"] for tensor in parameter["parameter_tensors"]}
    )
    assert all(tensor["raw_tensor_values_stored"] is False for tensor in parameter["parameter_tensors"])
    assert all(tensor["active_parameter_mutated"] is False for tensor in parameter["parameter_tensors"])
    assert parameter["parameter_integrity"]["raw_tensor_values_stored"] is False
    assert parameter["parameter_integrity"]["active_parameter_mutated"] is False
    assert parameter["parameter_integrity"]["all_planes_have_parameter_refs"] is True

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["parameter_tensor_ref"] == parameter["parameter_ledger_id"]
    assert all(parameter["parameter_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-parameter-tensor-session")
    assert replay["parameter_tensor_chain"][0]["parameter_ledger_id"] == parameter["parameter_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["parameter_tensor_chain"] == 1

    summary = substrate.summary(session_id="neural-parameter-tensor-session")
    assert summary["parameter_tensor_ledger"]["parameter_ledger_count"] == 1
    assert summary["parameter_tensor_ledger"]["latest_backward_propagation_ref"] == backward["backward_propagation_id"]

    scorecard = substrate.scorecard(session_id="neural-parameter-tensor-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveParameterTensorLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-076" in scorecard["source_documents"]


def test_hive_activation_function_ledger_maps_neural_nonlinearities(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-activation-function-session",
            intent="Map nonlinear activation functions across attention, gates, loops, and output decoding.",
            requested_capabilities=["routing", "evaluation", "dreaming", "output"],
            memory_refs=["memory::nonlinear-kernel"],
            max_loops=4,
        )
    )

    functions = result["activation_function_ledger"]
    parameter = result["parameter_tensor_ledger"]

    assert functions["surface_id"] == "hive-activation-function-ledger-v0"
    assert functions["parameter_tensor_ref"] == parameter["parameter_ledger_id"]
    assert functions["forward_propagation_ref"] == result["forward_propagation_ledger"]["propagation_id"]
    assert functions["activation_function_count"] == len(functions["activation_functions"])
    assert functions["activation_function_count"] >= 6
    assert {"softmax", "sigmoid", "geglu", "rmsnorm", "rotary_phase", "hazard_exit"}.issubset(
        {function["function_family"] for function in functions["activation_functions"]}
    )
    assert all(function["raw_activation_values_stored"] is False for function in functions["activation_functions"])
    assert all(function["active_kernel_mutated"] is False for function in functions["activation_functions"])
    assert functions["activation_function_integrity"]["raw_activation_values_stored"] is False
    assert functions["activation_function_integrity"]["active_kernel_mutated"] is False

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["activation_function_ref"] == functions["activation_function_ledger_id"]
    assert all(functions["activation_function_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-activation-function-session")
    assert replay["activation_function_chain"][0]["activation_function_ledger_id"] == functions["activation_function_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["activation_function_chain"] == 1

    summary = substrate.summary(session_id="neural-activation-function-session")
    assert summary["activation_function_ledger"]["activation_function_ledger_count"] == 1
    assert summary["activation_function_ledger"]["latest_parameter_tensor_ref"] == parameter["parameter_ledger_id"]

    scorecard = substrate.scorecard(session_id="neural-activation-function-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveActivationFunctionLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-077" in scorecard["source_documents"]


def test_hive_computational_graph_ledger_links_operations_and_gradients(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-computational-graph-session",
            intent="Build the computational graph for forward operations and backward credit assignment.",
            requested_capabilities=["routing", "memory", "evaluation", "quantization", "output"],
            memory_refs=["memory::graph-kernel"],
            max_loops=4,
        )
    )

    graph = result["computational_graph_ledger"]
    functions = result["activation_function_ledger"]
    parameter = result["parameter_tensor_ledger"]

    assert graph["surface_id"] == "hive-computational-graph-ledger-v0"
    assert graph["activation_function_ref"] == functions["activation_function_ledger_id"]
    assert graph["parameter_tensor_ref"] == parameter["parameter_ledger_id"]
    assert graph["forward_propagation_ref"] == result["forward_propagation_ledger"]["propagation_id"]
    assert graph["backward_propagation_ref"] == result["backward_propagation_ledger"]["backward_propagation_id"]
    assert graph["operation_node_count"] == len(graph["operation_nodes"])
    assert graph["operation_edge_count"] == len(graph["operation_edges"])
    assert graph["operation_node_count"] >= result["plane_trace"]["record_count"]
    assert graph["topological_order"][0] == "sensory-input"
    assert graph["topological_order"][-1] == "checkpoint-rewind"
    assert {"matmul", "attention", "gate", "activation", "normalization", "loss", "optimizer"}.issubset(
        {node["operation_family"] for node in graph["operation_nodes"]}
    )
    assert all(node["raw_tensor_values_stored"] is False for node in graph["operation_nodes"])
    assert all(node["active_runtime_mutated"] is False for node in graph["operation_nodes"])
    assert graph["graph_integrity"]["acyclic_forward_order"] is True
    assert graph["graph_integrity"]["backward_edges_present"] is True
    assert graph["graph_integrity"]["direct_local_state_reads"] == []

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["computational_graph_ref"] == graph["graph_ledger_id"]
    assert all(graph["graph_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-computational-graph-session")
    assert replay["computational_graph_chain"][0]["graph_ledger_id"] == graph["graph_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["computational_graph_chain"] == 1

    summary = substrate.summary(session_id="neural-computational-graph-session")
    assert summary["computational_graph_ledger"]["graph_ledger_count"] == 1
    assert summary["computational_graph_ledger"]["latest_activation_function_ref"] == functions["activation_function_ledger_id"]

    scorecard = substrate.scorecard(session_id="neural-computational-graph-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveComputationalGraphLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-078" in scorecard["source_documents"]


def test_hive_optimizer_state_vector_ledger_tracks_shadow_optimizer_internals(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-optimizer-state-session",
            intent="Track optimizer state vectors for shadow learning without mutating active parameters.",
            requested_capabilities=["routing", "evaluation", "teacher", "federation", "quantization"],
            memory_refs=["memory::optimizer-kernel"],
            max_loops=4,
        )
    )

    optimizer_state = result["optimizer_state_vector_ledger"]
    graph = result["computational_graph_ledger"]

    assert optimizer_state["surface_id"] == "hive-optimizer-state-vector-ledger-v0"
    assert optimizer_state["computational_graph_ref"] == graph["graph_ledger_id"]
    assert optimizer_state["parameter_tensor_ref"] == result["parameter_tensor_ledger"]["parameter_ledger_id"]
    assert optimizer_state["optimizer_school_ref"] == result["optimizer_school_ledger"]["optimizer_ledger_id"]
    assert optimizer_state["state_vector_count"] == len(optimizer_state["state_vectors"])
    assert {"momentum_m", "variance_v", "learning_rate", "weight_decay", "gradient_clip", "trust_region"}.issubset(
        {vector["state_vector_kind"] for vector in optimizer_state["state_vectors"]}
    )
    assert all(vector["raw_gradient_values_stored"] is False for vector in optimizer_state["state_vectors"])
    assert all(vector["active_optimizer_state_mutated"] is False for vector in optimizer_state["state_vectors"])
    assert optimizer_state["optimizer_state_integrity"]["raw_gradient_values_stored"] is False
    assert optimizer_state["optimizer_state_integrity"]["active_optimizer_state_mutated"] is False
    assert optimizer_state["optimizer_state_integrity"]["active_parameter_mutated"] is False

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["optimizer_state_vector_ref"] == optimizer_state["optimizer_state_ledger_id"]
    assert all(optimizer_state["optimizer_state_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-optimizer-state-session")
    assert replay["optimizer_state_vector_chain"][0]["optimizer_state_ledger_id"] == optimizer_state["optimizer_state_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["optimizer_state_vector_chain"] == 1

    summary = substrate.summary(session_id="neural-optimizer-state-session")
    assert summary["optimizer_state_vector_ledger"]["optimizer_state_ledger_count"] == 1
    assert summary["optimizer_state_vector_ledger"]["latest_computational_graph_ref"] == graph["graph_ledger_id"]

    scorecard = substrate.scorecard(session_id="neural-optimizer-state-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveOptimizerStateVectorLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-079" in scorecard["source_documents"]


def test_hive_model_genome_ledger_records_distillation_ready_architecture_blueprint(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-model-genome-session",
            intent="Record the distillation-ready genome for the evolving hive neural network.",
            requested_capabilities=["routing", "teacher", "evaluation", "dreaming", "federation", "output"],
            memory_refs=["memory::model-genome"],
            max_loops=4,
        )
    )

    genome = result["model_genome_ledger"]
    optimizer_state = result["optimizer_state_vector_ledger"]

    assert genome["surface_id"] == "hive-model-genome-ledger-v0"
    assert genome["optimizer_state_ref"] == optimizer_state["optimizer_state_ledger_id"]
    assert genome["computational_graph_ref"] == result["computational_graph_ledger"]["graph_ledger_id"]
    assert genome["parameter_tensor_ref"] == result["parameter_tensor_ledger"]["parameter_ledger_id"]
    assert genome["activation_function_ref"] == result["activation_function_ledger"]["activation_function_ledger_id"]
    assert genome["architecture_gene_count"] == len(genome["architecture_genes"])
    assert {"embedding_dimension", "attention_heads", "moe_top_k", "layer_block_count", "activation_suite", "optimizer_family", "federation_policy"}.issubset(
        {gene["gene_id"] for gene in genome["architecture_genes"]}
    )
    assert genome["distillation_blueprint"]["teacher_review_required"] is True
    assert genome["distillation_blueprint"]["candidate_child_expert_generation_allowed"] is True
    assert genome["genome_integrity"]["raw_model_weights_stored"] is False
    assert genome["genome_integrity"]["active_model_architecture_mutated"] is False
    assert genome["genome_integrity"]["human_governance_required"] is True

    runtime = result["downstream_node_runtime"]
    assert runtime["artifact_refs"]["model_genome_ref"] == genome["genome_ledger_id"]
    assert all(genome["genome_ledger_id"] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])

    replay = substrate.replay(session_id="neural-model-genome-session")
    assert replay["model_genome_chain"][0]["genome_ledger_id"] == genome["genome_ledger_id"]
    assert replay["control_panel_replay"]["chain_counts"]["model_genome_chain"] == 1

    summary = substrate.summary(session_id="neural-model-genome-session")
    assert summary["model_genome_ledger"]["model_genome_count"] == 1
    assert summary["model_genome_ledger"]["latest_optimizer_state_ref"] == optimizer_state["optimizer_state_ledger_id"]

    scorecard = substrate.scorecard(session_id="neural-model-genome-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}
    assert "HiveModelGenomeLedger" in component_ids
    assert "docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#PB-2026-05-03-080" in scorecard["source_documents"]


def test_hive_runtime_completion_ledgers_cover_remaining_neural_substrate_gaps(tmp_path: Path):
    substrate = HiveNeuralSubstrate(artifacts_dir=tmp_path)

    result = substrate.run_forward_pass(
        HiveForwardPassRequest(
            session_id="neural-runtime-completion-session",
            intent=(
                "Execute the remaining hive neural substrate runtime stack: tensor kernel, layer blocks, "
                "distillation, federation influence, dreaming, replay, storage, checkpoint coverage, "
                "runtime decisions, and backend quantization."
            ),
            requested_capabilities=[
                "routing",
                "teacher",
                "evaluation",
                "dreaming",
                "federation",
                "quantization",
                "runtime",
                "storage",
            ],
            memory_refs=["memory::runtime-completion", "memory::federated-priors"],
            max_loops=4,
        )
    )

    expected_runtime_ledgers = {
        "tensor_runtime_kernel_ledger": (
            "hive-tensor-runtime-kernel-ledger-v0",
            "tensor_kernel_ledger_id",
            "HiveTensorRuntimeKernelLedger",
            "tensor_runtime_kernel_chain",
            "PB-2026-05-03-081",
        ),
        "layer_block_stack_ledger": (
            "hive-layer-block-stack-ledger-v0",
            "layer_stack_ledger_id",
            "HiveLayerBlockStackLedger",
            "layer_block_stack_chain",
            "PB-2026-05-03-082",
        ),
        "distillation_loop_ledger": (
            "hive-distillation-loop-ledger-v0",
            "distillation_loop_id",
            "HiveDistillationLoopLedger",
            "distillation_loop_chain",
            "PB-2026-05-03-083",
        ),
        "federated_influence_ledger": (
            "hive-federated-influence-ledger-v0",
            "federated_influence_id",
            "HiveFederatedInfluenceLedger",
            "federated_influence_chain",
            "PB-2026-05-03-084",
        ),
        "executable_dream_cycle_ledger": (
            "hive-executable-dream-cycle-ledger-v0",
            "dream_cycle_id",
            "HiveExecutableDreamCycleLedger",
            "executable_dream_cycle_chain",
            "PB-2026-05-03-085",
        ),
        "deep_replay_drilldown_ledger": (
            "hive-deep-replay-drilldown-ledger-v0",
            "replay_drilldown_id",
            "HiveDeepReplayDrilldownLedger",
            "deep_replay_drilldown_chain",
            "PB-2026-05-03-086",
        ),
        "durable_storage_ledger": (
            "hive-durable-storage-ledger-v0",
            "storage_ledger_id",
            "HiveDurableStorageLedger",
            "durable_storage_chain",
            "PB-2026-05-03-087",
        ),
        "checkpoint_coverage_ledger": (
            "hive-checkpoint-coverage-ledger-v0",
            "coverage_ledger_id",
            "HiveCheckpointCoverageLedger",
            "checkpoint_coverage_chain",
            "PB-2026-05-03-088",
        ),
        "runtime_decision_ledger": (
            "hive-runtime-decision-ledger-v0",
            "runtime_decision_id",
            "HiveRuntimeDecisionLedger",
            "runtime_decision_chain",
            "PB-2026-05-03-089",
        ),
        "backend_quantization_execution_ledger": (
            "hive-backend-quantization-execution-ledger-v0",
            "backend_execution_id",
            "HiveBackendQuantizationExecutionLedger",
            "backend_quantization_execution_chain",
            "PB-2026-05-03-090",
        ),
    }

    runtime = result["downstream_node_runtime"]
    replay = substrate.replay(session_id="neural-runtime-completion-session")
    summary = substrate.summary(session_id="neural-runtime-completion-session")
    scorecard = substrate.scorecard(session_id="neural-runtime-completion-session")
    component_ids = {component["component_id"] for component in scorecard["substrate_components"]}

    for result_key, (surface_id, id_key, component_id, chain_key, pb_id) in expected_runtime_ledgers.items():
        ledger = result[result_key]
        assert ledger["surface_id"] == surface_id
        assert ledger[id_key] in runtime["artifact_refs"].values()
        assert all(ledger[id_key] in receipt["source_artifact_refs"] for receipt in runtime["receipts"])
        assert replay[chain_key][0][id_key] == ledger[id_key]
        assert replay["control_panel_replay"]["chain_counts"][chain_key] == 1
        assert summary[result_key]["ledger_count"] == 1
        assert component_id in component_ids
        assert f"docs/NEXUSNET_POST_BOOK_CANON_ADDENDUM_2026-05-01.md#{pb_id}" in scorecard["source_documents"]

    tensor_kernel = result["tensor_runtime_kernel_ledger"]
    assert tensor_kernel["model_genome_ref"] == result["model_genome_ledger"]["genome_ledger_id"]
    assert tensor_kernel["executed_shadow_ops"] is True
    assert tensor_kernel["runtime_integrity"]["raw_tensor_values_stored"] is False
    assert tensor_kernel["runtime_integrity"]["active_runtime_mutated"] is False

    layer_stack = result["layer_block_stack_ledger"]
    assert layer_stack["tensor_kernel_ref"] == tensor_kernel["tensor_kernel_ledger_id"]
    assert layer_stack["block_count"] == len(layer_stack["layer_blocks"])
    assert {"embedding_block", "transformer_moe_block", "output_head"}.issubset(
        {block["block_kind"] for block in layer_stack["layer_blocks"]}
    )

    distillation = result["distillation_loop_ledger"]
    assert distillation["layer_stack_ref"] == layer_stack["layer_stack_ledger_id"]
    assert distillation["distillation_gate"]["teacher_panel_required"] is True
    assert distillation["distillation_gate"]["active_child_promoted"] is False
    assert distillation["distillation_gate"]["parent_retirement_mutated"] is False

    federation = result["federated_influence_ledger"]
    assert federation["federated_prior_update_ref"] == result["federated_prior_update"]["prior_update_id"]
    assert federation["federation_integrity"]["raw_personal_data_shared"] is False
    assert federation["federation_integrity"]["active_router_prior_mutated"] is False
    assert federation["shadow_prior_update_count"] == len(federation["shadow_prior_updates"])

    dream_cycle = result["executable_dream_cycle_ledger"]
    assert dream_cycle["model_genome_ref"] == result["model_genome_ledger"]["genome_ledger_id"]
    assert dream_cycle["dream_integrity"]["active_architecture_mutated"] is False
    assert dream_cycle["dream_integrity"]["low_temperature_review_required"] is True
    assert dream_cycle["dream_candidate_count"] == len(dream_cycle["dream_candidates"])

    replay_drilldown = result["deep_replay_drilldown_ledger"]
    assert replay_drilldown["drilldown_view_count"] == len(replay_drilldown["drilldown_views"])
    assert {"graph_nodes", "parameter_refs", "optimizer_vectors", "genome_genes", "promotion_readiness"}.issubset(
        {view["view_id"] for view in replay_drilldown["drilldown_views"]}
    )

    storage = result["durable_storage_ledger"]
    assert storage["storage_policy"]["project_root_only"] is True
    assert storage["storage_policy"]["user_profile_cache_allowed"] is False
    assert storage["storage_integrity"]["checksums_present"] is True
    assert storage["storage_integrity"]["restore_query_plan_present"] is True

    checkpoint_coverage = result["checkpoint_coverage_ledger"]
    assert checkpoint_coverage["coverage_integrity"]["all_new_ledgers_covered"] is True
    assert checkpoint_coverage["coverage_integrity"]["diff_preview_required_for_all"] is True
    assert checkpoint_coverage["coverage_integrity"]["restore_validation_required_for_all"] is True

    runtime_decision = result["runtime_decision_ledger"]
    assert runtime_decision["runtime_integrity"]["direct_local_state_reads"] == []
    assert runtime_decision["runtime_integrity"]["artifact_refs_consumed"] is True
    assert runtime_decision["decision_count"] == len(runtime_decision["runtime_decisions"])

    backend_execution = result["backend_quantization_execution_ledger"]
    assert backend_execution["tensor_kernel_ref"] == tensor_kernel["tensor_kernel_ledger_id"]
    assert backend_execution["backend_integrity"]["active_backend_mutated"] is False
    assert backend_execution["backend_integrity"]["raw_kv_values_stored"] is False
    assert backend_execution["benchmark_scorecard_count"] == len(backend_execution["benchmark_scorecards"])

