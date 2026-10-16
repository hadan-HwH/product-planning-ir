"""Shared skill references must stay in sync with their single source in
skills-shared/ (P1-4). If this fails, run `python scripts/build_skills.py`.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_build_skills():
    spec = importlib.util.spec_from_file_location(
        "build_skills", REPO_ROOT / "scripts" / "build_skills.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_shared_skill_references_are_in_sync():
    bs = _load_build_skills()
    assert bs.check() == 0, "skill reference copies drifted from skills-shared/"


def test_every_shared_file_has_at_least_one_consumer():
    """A file in skills-shared/ that no skill uses is dead weight."""
    bs = _load_build_skills()
    shared = bs._shared_files()
    used = {name for _, name, _, _ in bs._targets(shared)}
    orphan = set(shared) - used
    assert not orphan, f"skills-shared files with no consumer: {sorted(orphan)}"
