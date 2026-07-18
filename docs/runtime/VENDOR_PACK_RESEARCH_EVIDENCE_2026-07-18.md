# AMD and Intel pack research evidence — 2026-07-18

Task 5 used primary vendor and upstream runtime sources only.

## Sources checked

- AMD Radeon Windows ROCm compatibility: <https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/windows/windows_compatibility.html>
- AMD Ryzen Windows ROCm compatibility: <https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityryz/windows/windows_compatibility.html>
- AMD Windows ROCm limitations: <https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/limitations/limitationsrad.html>
- AMD Windows PyTorch installation: <https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/windows/install-pytorch.html>
- Intel oneAPI 2026.1 system requirements: <https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-toolkit/2026.html>
- OpenVINO 2026 system requirements: <https://docs.openvino.ai/2026/about-openvino/release-notes-openvino/system-requirements.html>
- OpenVINO GPU device behavior: <https://docs.openvino.ai/2026/openvino-workflow/running-inference/inference-devices-and-modes/gpu-device.html>
- llama.cpp supported backends: <https://github.com/ggml-org/llama.cpp>
- llama.cpp signed release assets: <https://github.com/ggml-org/llama.cpp/releases>
- llama.cpp SYCL backend notes: <https://github.com/ggml-org/llama.cpp/blob/master/docs/backend/SYCL.md>

## Encoded constraints

- AMD Windows ROCm `7.2.1` HIP/PyTorch eligibility is limited to the published `gfx1201`, `gfx1200`, `gfx1100`, `gfx1101`, `gfx1150`, and `gfx1151` architecture tuples.
- The AMD Windows PyTorch lane requires Python 3.12, is inference-only for this design, and must not be generalized to the full Linux ROCm stack.
- Vulkan is an independent native llama.cpp fallback candidate and is never treated as proof of HIP support.
- Intel SYCL/OpenVINO candidates require an observed matching API plus a supported Intel GPU family. Vendor ID alone is insufficient.
- Intel GPU drivers are external prerequisites; candidate projection is not activation evidence.
- Upstream llama.cpp publishes distinct Windows x64 Vulkan, HIP, SYCL, and OpenVINO assets. NexusNet preserves those as separate pack identities.
- No mixed-device observation implies hybrid offload. Every route remains bound to one device node until independently certified.
