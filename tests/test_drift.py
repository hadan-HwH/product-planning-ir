"""Reality track (plan9 B): 'built != policy' as a machine check.

An ImplementationFact records what was actually built (Reality, observed). Drift =
the fact implements an option that is NOT the target's current authoritative
decision. This is the same isolation rule 1 as the reducer (a fact is a signal,
not a decision) — it never moves the projection, it only surfaces the gap.
"""
from __future__ import annotations

from validators import validate_drift as VD

T = "D2IR.TARGET.t"
A = "D2IR.OPTION.t.a"
B = "D2IR.OPTION.t.b"


def _base():
    """Target whose decision moved A -> B (current = B)."""
    atoms = {
        T: {"data": {"kind": "DecisionTarget", "id": T, "track": "governance",
                     "status": "accepted", "commitment_level": "accepted",
                     "statement": "t?", "current_resolution_policy": "single", "scope": {}}},
    }
    for o in (A, B):
        atoms[o] = {"data": {"kind": "SolutionOption", "id": o, "track": "governance",
                             "status": "proposed", "commitment_level": "candidate",
                             "target_ref": T, "summary": o, "scope": {}}}
    atoms["D2IR.DEVENT.t.001"] = {"data": {"kind": "DecisionEvent", "id": "D2IR.DEVENT.t.001",
        "track": "governance", "status": "accepted", "commitment_level": "accepted",
        "target_ref": T, "event_type": "adopt_option", "decision_time": "2026-01-01",
        "selects": [A], "scope": {}}}
    atoms["D2IR.DEVENT.t.002"] = {"data": {"kind": "DecisionEvent", "id": "D2IR.DEVENT.t.002",
        "track": "governance", "status": "accepted", "commitment_level": "accepted",
        "target_ref": T, "event_type": "replace_option", "decision_time": "2026-02-01",
        "replaces": [A], "selects": [B], "scope": {}}}
    return atoms


def _fact(implements):
    return {"kind": "ImplementationFact", "id": "D2IR.IMPL.t.built", "track": "reality",
            "status": "accepted", "commitment_level": "observed", "scope": {},
            "target_ref": T, "implements_option": implements, "observed": "as-built"}


def test_built_old_option_is_drift():
    atoms = _base()
    atoms["D2IR.IMPL.t.built"] = {"data": _fact(A)}   # built A, but current decision is B
    v = VD.check(atoms)
    assert any(x.startswith("[warn]") and "drift" in x.lower() and A.split(".")[-1] in x for x in v)


def test_built_current_option_is_no_drift():
    atoms = _base()
    atoms["D2IR.IMPL.t.built"] = {"data": _fact(B)}   # built B, matches current decision
    assert VD.check(atoms) == []


def test_fact_never_changes_the_projection():
    """A Reality fact is a signal, not a decision — projection stays B regardless."""
    from compilers.compile_decision_projection import project_target
    atoms = _base()
    atoms["D2IR.IMPL.t.built"] = {"data": _fact(A)}
    assert project_target(atoms, T)["current_option"] == [B]
