# Windows ML pack research evidence — 2026-07-18

Task 4 was constrained to current primary Microsoft and ONNX Runtime documentation.

## Sources checked

- Microsoft, **Get started with Windows ML**: <https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/get-started>
- Microsoft, **Install Windows ML execution providers**: <https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/initialize-execution-providers>
- Microsoft, **Select execution providers using the ONNX Runtime included in Windows ML**: <https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/select-execution-providers>
- Microsoft, **Windows ML execution providers**: <https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/supported-execution-providers>
- Microsoft, **ONNX Runtime versions shipped in Windows ML**: <https://learn.microsoft.com/en-us/windows/ai/new-windows-ml/onnx-versions>
- ONNX Runtime, **DirectML Execution Provider**: <https://onnxruntime.ai/docs/execution-providers/DirectML-ExecutionProvider.html>
- ONNX Runtime, **Execution Providers**: <https://onnxruntime.ai/docs/execution-providers/>
- ONNX Runtime, **Get started with ONNX Runtime for Windows**: <https://onnxruntime.ai/docs/get-started/with-windows.html>

## Implementation decisions

- Dynamic Windows ML execution-provider catalog acquisition is gated at Windows 11 24H2, build 26100.
- Providers are enumerated and selected explicitly before a route can be verified. Provider order is not treated as proof.
- Provider name and version are part of the evidence identity because Windows and driver updates can change the available provider/device list.
- DirectML remains an eligible broad-hardware GPU path, but is labeled as sustained-engineering rather than the future-facing provider strategy.
- `DmlExecutionProvider` is configured for sequential execution with memory patterns disabled, matching the ONNX Runtime requirements.
- Forced DirectML never falls back. Only `Auto` may choose the CPU provider when DirectML is unavailable.
- Windows ML/ONNX libraries stay inside the worker process. Core projects observations and unverified candidates without importing them.
- System-wide provider acquisition is not performed automatically by NexusNet; it remains an explicit installer/catalog action because first-run acquisition may download and install shared providers.

## Current-machine probe

The bounded read-only probe on 2026-07-18 reported:

- Windows 11 Home, version `10.0.26200`, build `26200` — the OS build gate passes.
- Windows App Runtime 2.x packages are present.
- The isolated development interpreter exposes ONNX Runtime `1.27.0`.
- Registered providers are `AzureExecutionProvider` and `CPUExecutionProvider`.
- The ONNX worker health probe selected `CPUExecutionProvider` successfully.
- `DmlExecutionProvider` and the Python `winml` binding are absent, so no Windows ML/DirectML GPU route is verified on this machine.
