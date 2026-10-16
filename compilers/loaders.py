"""Shared atom-access helpers for compilers."""
from __future__ import annotations

from pathlib import Path

from ppir.atoms import load_atoms


class AtomStore:
    def __init__(self, ir_dir: Path):
        self._atoms = load_atoms(ir_dir)

    def get(self, atom_id: str):
        entry = self._atoms.get(atom_id)
        return entry["data"] if entry else None

    def many(self, ids) -> list:
        return [self.get(i) for i in (ids or []) if self.get(i)]

    def by_kind(self, kind: str) -> list:
        return [e["data"] for e in self._atoms.values() if e["data"].get("kind") == kind]

    def by_kind_in_app(self, kind: str, app: str) -> list:
        return [a for a in self.by_kind(kind) if (a.get("scope") or {}).get("app") == app]
