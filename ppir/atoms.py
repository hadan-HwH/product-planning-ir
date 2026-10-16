"""Discover and load atom YAML files under ir/."""
from __future__ import annotations

from pathlib import Path

import yaml

from ppir.config import ID_RE, KIND_TOKEN_MAP


def load_atoms(ir_dir: Path) -> dict:
    """Return {atom_id: {"path": Path, "data": dict}} for every atom under ir_dir.

    Only files whose top-level YAML is a dict with an "id" are treated as atoms,
    so Proposal wrapper files ({proposal:…, claimset:…}) are skipped.
    """
    atoms: dict = {}
    for path in sorted(ir_dir.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "id" not in data:
            continue
        atoms[data["id"]] = {"path": path, "data": data}
    return atoms


def iter_id_refs(value):
    """Yield every string anywhere in `value` that looks like a known atom ID."""
    if isinstance(value, str):
        if ID_RE.match(value) and value.split(".")[1] in KIND_TOKEN_MAP:
            yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from iter_id_refs(v)
    elif isinstance(value, list):
        for v in value:
            yield from iter_id_refs(v)
