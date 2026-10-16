"""Every ID-shaped reference must resolve to an existing, non-dead atom."""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms, iter_id_refs

_DEAD = {"deprecated", "rejected"}


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        for ref in sorted(set(iter_id_refs(entry["data"]))):
            if ref == atom_id:
                continue
            target = atoms.get(ref)
            if target is None:
                out.append(f"{atom_id}: references missing atom {ref}")
            elif target["data"].get("status") in _DEAD:
                out.append(f"{atom_id}: references {target['data']['status']} atom {ref}")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
