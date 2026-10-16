"""Warn on atoms of a deprecated kind (plan9). Decision/Supersession are kept for
back-compat but superseded by the Decision Evolution Graph — new instances should
not be authored. Advisory (warn), not hard: existing data isn't broken, but the
direction is signalled."""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from ppir import registry

_DEPRECATED = registry.deprecated_kinds()


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        kind = entry["data"].get("kind")
        if kind in _DEPRECATED:
            out.append(f"[warn] {atom_id}: kind {kind!r} is deprecated "
                       f"(use the Decision Evolution Graph — DecisionEvent/Target)")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
