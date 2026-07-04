from __future__ import annotations

import json
from pathlib import Path

from nexus.config import build_paths, load_user_settings


def test_user_settings_ignore_home_and_load_project_local_layers(tmp_path, monkeypatch):
    fake_home = tmp_path / "fake-home"
    fake_home.mkdir()
    (fake_home / ".nexus.json").write_text(
        json.dumps({"source": "home", "unsafe": True, "home_only": "must-not-leak"}),
        encoding="utf-8",
    )
    (fake_home / ".config" / "nexus").mkdir(parents=True)
    (fake_home / ".config" / "nexus" / "settings.json").write_text(
        json.dumps({"source": "home-config", "unsafe": True}),
        encoding="utf-8",
    )

    project_root = tmp_path / "project"
    (project_root / ".nexus").mkdir(parents=True)
    (project_root / ".nexus.json").write_text(json.dumps({"source": "project-root"}), encoding="utf-8")
    (project_root / ".nexus" / "settings.json").write_text(
        json.dumps({"nested": {"a": 1}, "unsafe": False}),
        encoding="utf-8",
    )
    (project_root / ".nexus" / "settings.local.json").write_text(
        json.dumps({"nested": {"b": 2}, "local": True}),
        encoding="utf-8",
    )

    monkeypatch.setattr(Path, "home", lambda: fake_home)

    settings = load_user_settings(build_paths(project_root))

    assert settings == {
        "source": "project-root",
        "unsafe": False,
        "nested": {"a": 1, "b": 2},
        "local": True,
    }


def test_capture_tools_default_to_project_runtime_artifacts():
    api_capture = Path("tools/chatgpt_project_api_capture.mjs").read_text(encoding="utf-8")
    dom_capture = Path("tools/chatgpt_project_dom_topscroll_capture.mjs").read_text(encoding="utf-8")

    for script in (api_capture, dom_capture):
        assert "process.env.USERPROFILE" not in script
        assert "Documents" not in script
        assert "NexusNet_ChatGPT_Project_Logs" not in script
        assert "'runtime'" in script
        assert "'artifacts'" in script
        assert "'chatgpt-project-captures'" in script
