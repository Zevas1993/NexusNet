# Private Federated Learning Spec

Status: P2 online assimilation target. Research-only until NexusNet has a narrow, opt-in learning signal worth federating.

## Source Evidence

- Flower secure aggregation docs: https://flower.ai/docs/framework/explanation-ref-secure-aggregation-protocols.html
- Flower differential privacy docs: https://flower.ai/docs/framework/main/en/how-to-use-differential-privacy.html
- NVIDIA FLARE developer page: https://developer.nvidia.com/flare?ncid=no-ncid
- OpenDP docs: https://docs.opendp.org/en/stable/index.html
- TensorFlow Federated docs: https://www.tensorflow.org/federated
- Source status: official framework and privacy-library docs.

## Finding

Federated learning frameworks keep raw training data local while sharing updates, and secure aggregation or differential privacy can reduce the exposure of individual updates. This is useful for NexusNet only if the learning signal is carefully scoped, opt-in, and resistant to poisoning.

## NexusNet Assimilation Target

Design a private learning lane for route tuning, eval scoring, prompt suggestions, or local preference adapters where raw operator traces stay local. This should not become automatic production self-training.

## Proposed NexusNet Components

- `LocalLearningSignal`: local metric or preference signal with privacy class and consent record.
- `FederatedUpdateEnvelope`: clipped/noised update, schema version, provenance, and validation metrics.
- `SecureAggregationPolicy`: aggregate-only visibility rules and minimum participant thresholds.
- `DifferentialPrivacyBudget`: epsilon, delta, clipping, sampling, and cumulative budget ledger.
- `FederatedPromotionReview`: human and eval review before a learned update affects production behavior.

## Promotion Gates

- Explicit opt-in per workspace and signal type.
- Never upload raw prompts, private traces, source text, or files.
- Require poisoning and outlier detection before accepting updates.
- Record privacy budget use and allow revocation from future rounds.
- Keep learned changes shadow-only until eval and review pass.

## Risks

- Federated updates can still leak information without strong privacy controls.
- Malicious or low-quality clients can poison shared behavior.
- Infrastructure complexity may outweigh value unless the target metric is narrow.
