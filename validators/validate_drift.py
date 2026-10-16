"""Drift: 'built != policy' (plan9 B, Reality track). Advisory.

An ImplementationFact records what was actually built and which SolutionOption it
matches. If that option is not the target's current authoritative decision, the
build has drifted from policy. This never changes the projection — a fact is a
signal (reducer rule 1), so drift is surfaced, not silently reconciled. Turning a
fact into policy requires a human DecisionEvent (see ppir-reflect)."""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_decision_projection import project_target


def _short(x: str) -> str:
    return x.split(".")[-1]


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        data = entry["data"]
        if data.get("kind") != "ImplementationFact":
            continue
        target_id = data.get("target_ref")
        built = data.get("implements_option")
        if not target_id or target_id not in atoms:
            continue
        proj = project_target(atoms, target_id)
        current = proj.get("current_option") or []
        if built and built not in current:
            cur = "/".join(_short(o) for o in current) or "(none)"
            out.append(f"[warn] {atom_id}: drift — built {_short(built)} but the current "
                       f"decision on {target_id} is {cur} (route to ppir-reflect)")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
