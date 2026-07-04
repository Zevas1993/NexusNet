# Task Scope: 2026 Dataset Radar And Growth Lineage

## Objective

Build the Living Dataset Radar into a governed NexusNet substrate component that can discover dataset candidates, gate source usage, broker teacher material requests, feed DatasetForge and the Hive Model Growth Engine, and expose replayable lineage in the Control Panel and blackbox recorder.

## Scope

- Dataset Radar source registry, refreshes, batch refreshes, candidate gate previews, and teacher material requests.
- DatasetForge material-request lineage and split-gated manifests.
- Hive Model Growth Engine material-request lineage through growth cycles, model genomes, student birth records, and dataset manifests.
- Control Panel Dataset Radar operator surfaces and Dataset Flow View.
- Blackbox recorder replay frames for Dataset Radar, DatasetForge, and Growth Engine.

## Boundaries

- No automatic dataset downloads.
- No raw private-data federation.
- No automatic source approval from Hugging Face or external discovery.
- No real weight mutation from DatasetForge or Growth Engine in this lane.
- No teacher ejection without reviewer consistency windows and human approval.

## Validation

- Dataset Radar tests.
- DatasetForge tests.
- Hive Model Growth Engine tests.
- NexusNet visualizer tests.
- Blackbox recorder and Control Panel focused tests.
- GitNexus analyze and detect-changes after meaningful implementation slices.

