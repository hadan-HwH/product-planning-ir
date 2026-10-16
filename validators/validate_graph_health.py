"""Graph-health checks (docs/08 §3 no_orphan, §4 dangling — Level 0/1).

An accepted *policy* atom that nothing else references is dangling — either a
mistake or dead weight that will silently mislead compiled views. Advisory
([warn]): root/leaf kinds are legitimately unreferenced and exempt.
"""
from __future__ import annotations

from ppir.atoms import iter_id_refs

# Kinds that are graph roots or leaves — legitimately pointed at by nothing.
_ROOT_KINDS = {
    "Screen", "TestCase", "Supersession", "OpenQuestion",
    "Source", "ClaimSet", "LegacyExtractionMap", "Proposal", "Relation",
    # Decision Evolution Graph: events are an append-only log (the latest is not
    # referenced back); targets/relations/projections are entry points, not leaves.
    "DecisionEvent", "DecisionTarget", "DecisionRelation", "CurrentDecisionProjection",
    "ImplementationFact",
}


def _reverse_index(atoms: dict) -> dict:
    rev: dict = {}
    for atom_id, entry in atoms.items():
        for ref in {r for r in iter_id_refs(entry["data"]) if r != atom_id}:
            rev.setdefault(ref, []).append(atom_id)
    return rev


def check(atoms: dict) -> list:
    out: list = []
    rev = _reverse_index(atoms)
    for atom_id, entry in atoms.items():
        data = entry["data"]
        if data.get("commitment_level") != "accepted":
            continue
        if data.get("kind") in _ROOT_KINDS:
            continue
        if not rev.get(atom_id):
            out.append(f"[warn] {atom_id}: orphan {data.get('kind')} — "
                       f"no atom references it")
    return out
