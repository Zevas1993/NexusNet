from __future__ import annotations

from pathlib import Path

from .loader import TeacherCatalogLoader


def build_default_teacher_profiles(config_dir: str | Path) -> list:
    return TeacherCatalogLoader(Path(config_dir)).load().profiles


def build_default_teacher_assignments(config_dir: str | Path) -> list:
    return TeacherCatalogLoader(Path(config_dir)).load().assignments
