# Isolated Torch Family Lock Evidence — 2026-07-18

## Decision

NexusNet uses four mutually exclusive private Windows worker environments:
`torch-cpu`, `torch-cuda`, `torch-xpu`, and `torch-rocm-windows`. Each lock has
one Torch distribution, the exact worker-protocol/runtime dependencies, exact
HTTPS wheel URLs, exact SHA-256 digests, reviewed byte sizes, and
`include-system-site-packages = false`. Training is not declared by these
inference worker packs.

## Reviewed primary sources

- PyTorch Windows install selector and accelerator guidance:
  https://pytorch.org/get-started/locally/
- PyTorch official CPU, CUDA 12.8, and XPU wheel indexes:
  https://download.pytorch.org/whl/cpu/torch/
  https://download.pytorch.org/whl/cu128/torch/
  https://download.pytorch.org/whl/xpu/torch/
- PyTorch XPU documentation:
  https://docs.pytorch.org/docs/stable/notes/get_start_xpu.html
- AMD Windows PyTorch/ROCm 7.2.1 installation and support guidance:
  https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/windows/install-pytorch.html
- PyPI JSON release records for the protocol and standard Torch dependencies:
  https://pypi.org/

## Torch artifacts

| Family | Python | Torch | Bytes | SHA-256 provenance |
| --- | --- | --- | ---: | --- |
| CPU | cp311 | 2.11.0+cpu | 114,432,833 | `51a221769d4a316f4b47a786c12e67c3f4807db8ed13c7b8817ebe73786acbbc` from official index fragment |
| CUDA | cp311 | 2.11.0+cu128 | 2,753,148,611 | `90ef0c2454e5296a9fb021ddd42252e4ce1abe2c0a4988a173ef90a6cded0bf5` from official index fragment |
| XPU | cp311 | 2.10.0+xpu | 705,454,034 | `cb9d37f21cb9fb7df67d62863f021c3144e8d8832b9ea8e8523ac308bc620ea1` from official index fragment |
| ROCm Windows | cp312 | 2.9.1+rocm7.2.1 | 821,065,907 | `e88bf270163b48f7f27f7ea3db5ffb3be4ba107301933022bcb3c6ddedfeeabb` locally computed over the exact reviewed AMD HTTPS artifact |

The dependency lock also pins the exact, hashed wheels for `filelock`,
`fsspec`, `jinja2`, `markupsafe`, `mpmath`, `networkx`, `setuptools`, `sympy`,
`typing-extensions`, `pydantic`, its exact compatible `pydantic-core`,
`annotated-types`, `typing-inspection`, and `pyyaml`. ABI-specific Windows
wheels are selected for `markupsafe`, `pydantic-core`, and `pyyaml`.

## Current-machine proof

The production private-environment builder created a clean CPython 3.11 venv
from the generated CPU lock. `pyvenv.cfg` reported
`include-system-site-packages = false`. Inside that environment:

- Torch reported `2.11.0+cpu` and the enforced family was `torch-cpu`.
- Worker health reported available, CPU, one device, and tensor execution.
- Self-test passed.
- Load/infer with scale 2 and bias 1 returned `[3.0, 5.0, 7.0]`.

The isolated CUDA development environment on this machine reported:

- Torch `2.11.0+cu128`, CUDA runtime `12.8`.
- NVIDIA GeForce RTX 5070 Ti, one CUDA device.
- Enforced `torch-cuda` health and self-test passed.
- The same load/infer vector returned `[3.0, 5.0, 7.0]`.

XPU and ROCm Windows handshakes rejected the installed CUDA family. They remain
unavailable and unverified here because this machine has no representative
Intel or AMD GPU. The catalog support-matrix match is only eligibility; it is
not activation or product certification.
