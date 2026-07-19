from __future__ import annotations

from urllib.parse import urlsplit

import pytest
from pydantic import ValidationError

from nexusnet.runtime.accelerator_packs.environment_locks import (
    LockedWheel,
    WorkerEnvironmentLock,
    built_in_environment_locks,
    environment_lock_for,
)


def test_builtin_locks_have_one_mutually_exclusive_torch_distribution() -> None:
    locks = built_in_environment_locks()

    assert [lock.family for lock in locks] == ["torch-cpu", "torch-cuda", "torch-xpu", "torch-rocm-windows"]
    for lock in locks:
        torch_wheels = [wheel for wheel in lock.wheels if wheel.project == "torch"]
        assert len(torch_wheels) == 1
        assert lock.include_system_site_packages is False
        assert len(torch_wheels[0].sha256) == 64
        int(torch_wheels[0].sha256, 16)
        assert urlsplit(torch_wheels[0].url).scheme == "https"


def test_builtin_locks_include_all_hash_locked_torch_runtime_dependencies() -> None:
    expected_projects = {
        "filelock",
        "fsspec",
        "jinja2",
        "markupsafe",
        "mpmath",
        "networkx",
        "pydantic",
        "pydantic-core",
        "pyyaml",
        "setuptools",
        "sympy",
        "torch",
        "annotated-types",
        "typing-extensions",
        "typing-inspection",
    }

    for lock in built_in_environment_locks():
        assert {wheel.project for wheel in lock.wheels} == expected_projects
        assert all(len(wheel.sha256) == 64 for wheel in lock.wheels)
        assert all(wheel.size_bytes > 0 for wheel in lock.wheels)
        markupsafe = next(wheel for wheel in lock.wheels if wheel.project == "markupsafe")
        assert lock.python_abi in markupsafe.url
        pydantic = next(wheel for wheel in lock.wheels if wheel.project == "pydantic")
        pydantic_core = next(wheel for wheel in lock.wheels if wheel.project == "pydantic-core")
        assert (pydantic.version, pydantic_core.version) == ("2.13.4", "2.46.4")
        pyyaml = next(wheel for wheel in lock.wheels if wheel.project == "pyyaml")
        assert lock.python_abi in pyyaml.url


def test_builtin_locks_pin_reviewed_indexes_urls_and_hashes() -> None:
    by_family = {lock.family: lock for lock in built_in_environment_locks()}

    assert by_family["torch-cpu"].index_url == "https://download.pytorch.org/whl/cpu"
    assert by_family["torch-cpu"].wheels[0].sha256 == "51a221769d4a316f4b47a786c12e67c3f4807db8ed13c7b8817ebe73786acbbc"
    assert by_family["torch-cuda"].index_url == "https://download.pytorch.org/whl/cu128"
    assert by_family["torch-cuda"].wheels[0].sha256 == "90ef0c2454e5296a9fb021ddd42252e4ce1abe2c0a4988a173ef90a6cded0bf5"
    assert by_family["torch-xpu"].index_url == "https://download.pytorch.org/whl/xpu"
    assert by_family["torch-xpu"].wheels[0].sha256 == "cb9d37f21cb9fb7df67d62863f021c3144e8d8832b9ea8e8523ac308bc620ea1"
    assert by_family["torch-rocm-windows"].index_url == "https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1"
    assert by_family["torch-rocm-windows"].wheels[0].sha256 == "e88bf270163b48f7f27f7ea3db5ffb3be4ba107301933022bcb3c6ddedfeeabb"


def test_lock_renders_hash_required_direct_requirements() -> None:
    lock = environment_lock_for("torch-cuda", python_abi="cp311", platform_tag="win_amd64")

    assert lock is not None
    assert lock.requirement_lines()[0] == (
        "torch @ https://download-r2.pytorch.org/whl/cu128/torch-2.11.0%2Bcu128-cp311-cp311-win_amd64.whl "
        "--hash=sha256:90ef0c2454e5296a9fb021ddd42252e4ce1abe2c0a4988a173ef90a6cded0bf5"
    )
    assert len(lock.requirement_lines()) == 15
    assert all(" --hash=sha256:" in line for line in lock.requirement_lines())


def test_lock_materializes_an_atomic_requirements_file(tmp_path) -> None:
    lock = environment_lock_for("torch-cpu", python_abi="cp311", platform_tag="win_amd64")

    assert lock is not None
    path = lock.materialize(tmp_path)

    assert path == tmp_path / f"{lock.lock_id}.requirements.txt"
    assert path.read_text(encoding="utf-8").splitlines() == list(lock.requirement_lines())
    assert list(tmp_path.glob("*.partial")) == []


def test_lock_lookup_is_exact_for_python_platform_and_architecture() -> None:
    assert environment_lock_for("torch-cpu", python_abi="cp311", platform_tag="win_amd64") is not None
    assert environment_lock_for("torch-cpu", python_abi="cp312", platform_tag="win_amd64") is None
    assert environment_lock_for("torch-rocm-windows", python_abi="cp312", platform_tag="win_amd64") is not None
    assert environment_lock_for("torch-rocm-windows", python_abi="cp311", platform_tag="win_amd64") is None


def test_lock_rejects_multiple_torch_families() -> None:
    cpu = built_in_environment_locks()[0]
    cuda_wheel = built_in_environment_locks()[1].wheels[0]

    with pytest.raises(ValidationError, match="exactly one torch distribution"):
        WorkerEnvironmentLock.model_validate(
            {
                **cpu.model_dump(mode="json"),
                "wheels": [cpu.wheels[0].model_dump(mode="json"), cuda_wheel.model_dump(mode="json")],
            }
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://download.pytorch.org/torch.whl",
        "https://evil.invalid/torch.whl",
        "https://download.pytorch.org/../torch.whl",
    ],
)
def test_locked_wheel_rejects_untrusted_or_unsanitized_urls(url: str) -> None:
    with pytest.raises(ValidationError):
        LockedWheel(project="torch", version="2.11.0+cpu", url=url, sha256="a" * 64, size_bytes=1)
