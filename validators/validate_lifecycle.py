"""Lifecycle matrix: each kind belongs to a track and admits only certain
commitment_levels. Kinds absent from the matrix are unconstrained."""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from ppir import registry

# kind -> (required_track, allowed_commitment_levels). Single source:
# kind-registry.yaml. Kinds without a `lifecycle:` block are unconstrained.
_MATRIX = registry.lifecycle_matrix()


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        data = entry["data"]
        rule = _MATRIX.get(data.get("kind"))
        if not rule:
            continue
        want_track, ok_levels = rule
        if data.get("track") != want_track:
            out.append(f"{atom_id}: {data['kind']} must be track '{want_track}' "
                       f"but is '{data.get('track')}'")
        if data.get("commitment_level") not in ok_levels:
            out.append(f"{atom_id}: {data['kind']} commitment_level "
                       f"'{data.get('commitment_level')}' not in {sorted(ok_levels)}")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
