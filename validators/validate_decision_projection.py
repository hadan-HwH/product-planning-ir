"""Decision Evolution Graph guards (plan8). Keeps a computed CurrentDecisionProjection
honest so a superseded/signal-only option can never present as the current decision.

Runs per DecisionTarget by folding its DecisionEvents through the reducer:

  (a) a `single`-resolution target must not end with >1 active option        -> HARD
  (b) a current option must not itself be in an inactive lifecycle state
      (superseded/rejected/deferred/deprecated)                              -> HARD
  (c) every current option must be selected by an accepted DecisionEvent
      (a raw source signal must never become current on its own)             -> HARD
  (d) a projection with a current_summary must carry a decision_chain        -> HARD

Inert until DecisionTargets exist in ir/ (the pilot promotion, Phase 2).
"""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_decision_projection import project_target

_INACTIVE_LEVELS = {"superseded", "rejected", "deferred", "deprecated"}


def _accepted_selected(atoms: dict, target_id: str) -> set:
    """Options selected by an accepted DecisionEvent for this target."""
    out: set = set()
    for e in atoms.values():
        d = e["data"]
        if (d.get("kind") == "DecisionEvent" and d.get("target_ref") == target_id
                and d.get("commitment_level") == "accepted"):
            out.update(d.get("selects") or [])
    return out


def violations_for(target: dict, proj: dict, atoms: dict) -> list:
    """Guards on one target's projection. Works on any projection dict — a reducer
    output or a hand-touched/materialized one — so the guards are independently testable."""
    out = []
    tid = target["id"]
    cur = proj.get("current_option") or []

    # (a) single-resolution target must not have >1 active option
    if target.get("current_resolution_policy") == "single" and len(cur) > 1:
        out.append(f"{tid}: {len(cur)} active options on a single-resolution target: {cur}")

    # (b) a current option must not itself be in an inactive lifecycle state
    for oid in cur:
        o = atoms.get(oid)
        lvl = o["data"].get("commitment_level") if o else None
        if lvl in _INACTIVE_LEVELS:
            out.append(f"{tid}: current option {oid} has inactive commitment_level '{lvl}'")

    # (c) a current option must be backed by an accepted DecisionEvent, not a signal
    selected = _accepted_selected(atoms, tid)
    for oid in cur:
        if oid not in selected:
            out.append(f"{tid}: current option {oid} is not selected by any accepted "
                       f"DecisionEvent (signal-only leak)")

    # (d) a projection that states a current summary must explain how it got there
    if proj.get("current_summary") and not proj.get("decision_chain"):
        out.append(f"{tid}: projection has current_summary but empty decision_chain")

    return out


def check(atoms: dict) -> list:
    out = []
    for entry in atoms.values():
        t = entry["data"]
        if t.get("kind") != "DecisionTarget":
            continue
        try:
            proj = project_target(atoms, t["id"])
        except NotImplementedError as ex:
            out.append(f"{t['id']}: projection could not be computed — {ex}")
            continue
        out += violations_for(t, proj, atoms)
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
