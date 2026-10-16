"""Kind-constrained references: a field naming another atom must point at an
atom of the allowed kind(s). Only refs that resolve are kind-checked."""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from ppir import registry

# (kind, dotted-field-path) -> allowed target kinds. Single source:
# kind-registry.yaml (each kind's `typed_refs:` block).
_RULES = registry.typed_ref_rules()


def _resolve(data, path: str):
    cur = data
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        data = entry["data"]
        for kind, path, allowed in _RULES:
            if data.get("kind") != kind:
                continue
            value = _resolve(data, path)
            refs = value if isinstance(value, list) else ([value] if value else [])
            for ref in refs:
                target = atoms.get(ref)
                if target and target["data"].get("kind") not in allowed:
                    out.append(f"{atom_id}.{path} -> {ref}: expects "
                               f"{'/'.join(sorted(allowed))} but is {target['data'].get('kind')}")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
