from pathlib import Path
import json
import subprocess
import sys


def test_windows_bootstrap_builds_private_core_without_global_python_mutation():
    script = Path("install/windows/bootstrap.ps1").read_text(encoding="utf-8")

    assert "NEXUSNET_HOME" in script
    assert "private" in script.casefold()
    assert "pyproject.toml" in script
    assert "--system-site-packages" not in script
    assert "python -m venv .venv" not in script
    assert "requirements-windows.txt" not in script
    assert "$env:PATH =" not in script


def test_runtime_pack_cli_executes_when_invoked_as_a_module(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nexusnet.cli.runtime_packs",
            "status",
            "--home",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "active_pack_ids": [],
        "command": "status",
        "downloads_require_consent": True,
        "pack_count": 0,
    }
