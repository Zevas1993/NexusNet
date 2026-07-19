from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Literal
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator, model_validator


TorchFamily = Literal["torch-cpu", "torch-cuda", "torch-xpu", "torch-rocm-windows"]
_TRUSTED_WHEEL_HOSTS = {
    "download-r2.pytorch.org",
    "download.pytorch.org",
    "files.pythonhosted.org",
    "repo.radeon.com",
}


class LockedWheel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project: StrictStr = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    version: StrictStr = Field(min_length=1)
    url: StrictStr = Field(min_length=1)
    sha256: StrictStr = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: StrictInt = Field(gt=0)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        decoded_path = unquote(parsed.path)
        if (
            parsed.scheme != "https"
            or parsed.hostname not in _TRUSTED_WHEEL_HOSTS
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or ".." in decoded_path.split("/")
            or "\\" in decoded_path
            or any(character.isspace() for character in decoded_path)
        ):
            raise ValueError("locked wheel URL is not trusted and sanitized")
        return value


class WorkerEnvironmentLock(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lock_id: StrictStr = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    family: TorchFamily
    pack_version: StrictStr = Field(min_length=1)
    python_abi: StrictStr = Field(pattern=r"^cp[0-9]{3}$")
    platform_tag: Literal["win_amd64"] = "win_amd64"
    architecture: Literal["amd64"] = "amd64"
    index_url: StrictStr = Field(min_length=1)
    include_system_site_packages: Literal[False] = False
    wheels: tuple[LockedWheel, ...] = Field(min_length=1)
    source_url: StrictStr = Field(min_length=1)

    @field_validator("index_url", "source_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("lock source URL must be HTTPS")
        return value

    @model_validator(mode="after")
    def validate_torch_family(self) -> "WorkerEnvironmentLock":
        torch_wheels = [wheel for wheel in self.wheels if wheel.project == "torch"]
        if len(torch_wheels) != 1:
            raise ValueError("environment lock must contain exactly one torch distribution")
        wheel = torch_wheels[0]
        marker = {
            "torch-cpu": "+cpu",
            "torch-cuda": "+cu",
            "torch-xpu": "+xpu",
            "torch-rocm-windows": "+rocm",
        }[self.family]
        if marker not in wheel.version or self.python_abi not in wheel.url or self.platform_tag not in wheel.url:
            raise ValueError("torch wheel does not match its environment family")
        return self

    def requirement_lines(self) -> tuple[str, ...]:
        return tuple(
            f"{wheel.project} @ {wheel.url} --hash=sha256:{wheel.sha256}"
            for wheel in self.wheels
        )

    def materialize(self, root: str | Path) -> Path:
        root_path = Path(root).resolve(strict=False)
        root_path.mkdir(parents=True, exist_ok=True)
        destination = root_path / f"{self.lock_id}.requirements.txt"
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                prefix=f".{self.lock_id}.",
                suffix=".partial",
                dir=root_path,
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write("\n".join(self.requirement_lines()) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, destination)
            return destination
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()


_COMMON_PURE_WHEELS = (
    LockedWheel(
        project="annotated-types",
        version="0.7.0",
        url=(
            "https://files.pythonhosted.org/packages/78/b6/"
            "6307fbef88d9b5ee7421e68d78a9f162e0da4900bc5f5793f6d3d0e34fb8/"
            "annotated_types-0.7.0-py3-none-any.whl"
        ),
        sha256="1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53",
        size_bytes=13_643,
    ),
    LockedWheel(
        project="filelock",
        version="3.29.0",
        url=(
            "https://files.pythonhosted.org/packages/81/47/"
            "dd9a212ef6e343a6857485ffe25bba537304f1913bdbed446a23f7f592e1/"
            "filelock-3.29.0-py3-none-any.whl"
        ),
        sha256="96f5f6344709aa1572bbf631c640e4ebeeb519e08da902c39a001882f30ac258",
        size_bytes=39_812,
    ),
    LockedWheel(
        project="fsspec",
        version="2026.4.0",
        url=(
            "https://files.pythonhosted.org/packages/d5/0c/"
            "043d5e551459da400957a1395e0febbf771446ff34291afcbe3d8be2a279/"
            "fsspec-2026.4.0-py3-none-any.whl"
        ),
        sha256="11ef7bb35dab8a394fde6e608221d5cf3e8499401c249bebaeaad760a1a8dec2",
        size_bytes=203_402,
    ),
    LockedWheel(
        project="jinja2",
        version="3.1.6",
        url=(
            "https://files.pythonhosted.org/packages/62/a1/"
            "3d680cbfd5f4b8f15abc1d571870c5fc3e594bb582bc3b64ea099db13e56/"
            "jinja2-3.1.6-py3-none-any.whl"
        ),
        sha256="85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67",
        size_bytes=134_899,
    ),
    LockedWheel(
        project="mpmath",
        version="1.3.0",
        url=(
            "https://files.pythonhosted.org/packages/43/e3/"
            "7d92a15f894aa0c9c4b49b8ee9ac9850d6e63b03c9c32c0367a13ae62209/"
            "mpmath-1.3.0-py3-none-any.whl"
        ),
        sha256="a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c",
        size_bytes=536_198,
    ),
    LockedWheel(
        project="networkx",
        version="3.6.1",
        url=(
            "https://files.pythonhosted.org/packages/9e/c9/"
            "b2622292ea83fbb4ec318f5b9ab867d0a28ab43c5717bb85b0a5f6b3b0a4/"
            "networkx-3.6.1-py3-none-any.whl"
        ),
        sha256="d47fbf302e7d9cbbb9e2555a0d267983d2aa476bac30e90dfbe5669bd57f3762",
        size_bytes=2_068_504,
    ),
    LockedWheel(
        project="pydantic",
        version="2.13.4",
        url=(
            "https://files.pythonhosted.org/packages/fd/7b/"
            "122376b1fd3c62c1ed9dc80c931ace4844b3c55407b6fb2d199377c9736f/"
            "pydantic-2.13.4-py3-none-any.whl"
        ),
        sha256="45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba",
        size_bytes=472_262,
    ),
    LockedWheel(
        project="setuptools",
        version="78.1.0",
        url=(
            "https://files.pythonhosted.org/packages/54/21/"
            "f43f0a1fa8b06b32812e0975981f4677d28e0f3271601dc88ac5a5b83220/"
            "setuptools-78.1.0-py3-none-any.whl"
        ),
        sha256="3e386e96793c8702ae83d17b853fb93d3e09ef82ec62722e61da5cd22376dcd8",
        size_bytes=1_256_108,
    ),
    LockedWheel(
        project="sympy",
        version="1.14.0",
        url=(
            "https://files.pythonhosted.org/packages/a2/09/"
            "77d55d46fd61b4a135c444fc97158ef34a095e5681d0a6c10b75bf356191/"
            "sympy-1.14.0-py3-none-any.whl"
        ),
        sha256="e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5",
        size_bytes=6_299_353,
    ),
    LockedWheel(
        project="typing-extensions",
        version="4.15.0",
        url=(
            "https://files.pythonhosted.org/packages/18/67/"
            "36e9267722cc04a6b9f15c7f3441c2363321a3ea07da7ae0c0707beb2a9c/"
            "typing_extensions-4.15.0-py3-none-any.whl"
        ),
        sha256="f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548",
        size_bytes=44_614,
    ),
    LockedWheel(
        project="typing-inspection",
        version="0.4.2",
        url=(
            "https://files.pythonhosted.org/packages/dc/9b/"
            "47798a6c91d8bdb567fe2698fe81e0c6b7cb7ef4d13da4114b41d239f65d/"
            "typing_inspection-0.4.2-py3-none-any.whl"
        ),
        sha256="4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7",
        size_bytes=14_611,
    ),
)


def _markupsafe_wheel(python_abi: Literal["cp311", "cp312"]) -> LockedWheel:
    if python_abi == "cp311":
        return LockedWheel(
            project="markupsafe",
            version="3.0.3",
            url=(
                "https://files.pythonhosted.org/packages/83/8a/"
                "4414c03d3f891739326e1783338e48fb49781cc915b2e0ee052aa490d586/"
                "markupsafe-3.0.3-cp311-cp311-win_amd64.whl"
            ),
            sha256="de8a88e63464af587c950061a5e6a67d3632e36df62b986892331d4620a35c01",
            size_bytes=15_077,
        )
    return LockedWheel(
        project="markupsafe",
        version="3.0.3",
        url=(
            "https://files.pythonhosted.org/packages/aa/5b/"
            "bec5aa9bbbb2c946ca2733ef9c4ca91c91b6a24580193e891b5f7dbe8e1e/"
            "markupsafe-3.0.3-cp312-cp312-win_amd64.whl"
        ),
        sha256="26a5784ded40c9e318cfc2bdb30fe164bdb8665ded9cd64d500a34fb42067b1c",
        size_bytes=15_105,
    )


def _pydantic_core_wheel(python_abi: Literal["cp311", "cp312"]) -> LockedWheel:
    if python_abi == "cp311":
        return LockedWheel(
            project="pydantic-core",
            version="2.46.4",
            url=(
                "https://files.pythonhosted.org/packages/aa/e6/"
                "c505f83dfeda9a2e5c995cfd872949e4d05e12f7feb3dca72f633daefa94/"
                "pydantic_core-2.46.4-cp311-cp311-win_amd64.whl"
            ),
            sha256="6f2eeda33a839975441c86a4119e1383c50b47faf0cbb5176985565c6bb02c33",
            size_bytes=2_071_114,
        )
    return LockedWheel(
        project="pydantic-core",
        version="2.46.4",
        url=(
            "https://files.pythonhosted.org/packages/40/8c/"
            "985c1d41ea1107c2534abd9870e4ed5c8e7669b5c308297835c001e7a1c4/"
            "pydantic_core-2.46.4-cp312-cp312-win_amd64.whl"
        ),
        sha256="e9c26f834c65f5752f3f06cb08cb86a913ceb7274d0db6e267808a708b46bc89",
        size_bytes=2_072_919,
    )


def _pyyaml_wheel(python_abi: Literal["cp311", "cp312"]) -> LockedWheel:
    if python_abi == "cp311":
        return LockedWheel(
            project="pyyaml",
            version="6.0.3",
            url=(
                "https://files.pythonhosted.org/packages/da/e3/"
                "ea007450a105ae919a72393cb06f122f288ef60bba2dc64b26e2646fa315/"
                "pyyaml-6.0.3-cp311-cp311-win_amd64.whl"
            ),
            sha256="9f3bfb4965eb874431221a3ff3fdcddc7e74e3b07799e0e84ca4a0f867d449bf",
            size_bytes=158_763,
        )
    return LockedWheel(
        project="pyyaml",
        version="6.0.3",
        url=(
            "https://files.pythonhosted.org/packages/86/bf/"
            "899e81e4cce32febab4fb42bb97dcdf66bc135272882d1987881a4b519e9/"
            "pyyaml-6.0.3-cp312-cp312-win_amd64.whl"
        ),
        sha256="5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b",
        size_bytes=154_003,
    )


_BUILT_IN_LOCKS = (
    WorkerEnvironmentLock(
        lock_id="torch-cpu-2.11.0-cp311-win-amd64",
        family="torch-cpu",
        pack_version="1.0.0",
        python_abi="cp311",
        index_url="https://download.pytorch.org/whl/cpu",
        source_url="https://download.pytorch.org/whl/cpu/torch/",
        wheels=(
            LockedWheel(
                project="torch",
                version="2.11.0+cpu",
                url="https://download-r2.pytorch.org/whl/cpu/torch-2.11.0%2Bcpu-cp311-cp311-win_amd64.whl",
                sha256="51a221769d4a316f4b47a786c12e67c3f4807db8ed13c7b8817ebe73786acbbc",
                size_bytes=114_432_833,
            ),
            *_COMMON_PURE_WHEELS,
            _markupsafe_wheel("cp311"),
            _pydantic_core_wheel("cp311"),
            _pyyaml_wheel("cp311"),
        ),
    ),
    WorkerEnvironmentLock(
        lock_id="torch-cuda-2.11.0-cu128-cp311-win-amd64",
        family="torch-cuda",
        pack_version="1.0.0",
        python_abi="cp311",
        index_url="https://download.pytorch.org/whl/cu128",
        source_url="https://download.pytorch.org/whl/cu128/torch/",
        wheels=(
            LockedWheel(
                project="torch",
                version="2.11.0+cu128",
                url="https://download-r2.pytorch.org/whl/cu128/torch-2.11.0%2Bcu128-cp311-cp311-win_amd64.whl",
                sha256="90ef0c2454e5296a9fb021ddd42252e4ce1abe2c0a4988a173ef90a6cded0bf5",
                size_bytes=2_753_148_611,
            ),
            *_COMMON_PURE_WHEELS,
            _markupsafe_wheel("cp311"),
            _pydantic_core_wheel("cp311"),
            _pyyaml_wheel("cp311"),
        ),
    ),
    WorkerEnvironmentLock(
        lock_id="torch-xpu-2.10.0-cp311-win-amd64",
        family="torch-xpu",
        pack_version="1.0.0",
        python_abi="cp311",
        index_url="https://download.pytorch.org/whl/xpu",
        source_url="https://download.pytorch.org/whl/xpu/torch/",
        wheels=(
            LockedWheel(
                project="torch",
                version="2.10.0+xpu",
                url="https://download-r2.pytorch.org/whl/xpu/torch-2.10.0%2Bxpu-cp311-cp311-win_amd64.whl",
                sha256="cb9d37f21cb9fb7df67d62863f021c3144e8d8832b9ea8e8523ac308bc620ea1",
                size_bytes=705_454_034,
            ),
            *_COMMON_PURE_WHEELS,
            _markupsafe_wheel("cp311"),
            _pydantic_core_wheel("cp311"),
            _pyyaml_wheel("cp311"),
        ),
    ),
    WorkerEnvironmentLock(
        lock_id="torch-rocm-windows-2.9.1-rocm7.2.1-cp312-win-amd64",
        family="torch-rocm-windows",
        pack_version="1.0.0",
        python_abi="cp312",
        index_url="https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1",
        source_url="https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/install/installryz/windows/install-pytorch.html",
        wheels=(
            LockedWheel(
                project="torch",
                version="2.9.1+rocm7.2.1",
                url=(
                    "https://repo.radeon.com/rocm/windows/rocm-rel-7.2.1/"
                    "torch-2.9.1%2Brocm7.2.1-cp312-cp312-win_amd64.whl"
                ),
                sha256="e88bf270163b48f7f27f7ea3db5ffb3be4ba107301933022bcb3c6ddedfeeabb",
                size_bytes=821_065_907,
            ),
            *_COMMON_PURE_WHEELS,
            _markupsafe_wheel("cp312"),
            _pydantic_core_wheel("cp312"),
            _pyyaml_wheel("cp312"),
        ),
    ),
)


def built_in_environment_locks() -> tuple[WorkerEnvironmentLock, ...]:
    return _BUILT_IN_LOCKS


def environment_lock_for(
    family: TorchFamily,
    *,
    python_abi: str,
    platform_tag: str,
) -> WorkerEnvironmentLock | None:
    return next(
        (
            lock
            for lock in _BUILT_IN_LOCKS
            if lock.family == family and lock.python_abi == python_abi and lock.platform_tag == platform_tag
        ),
        None,
    )
