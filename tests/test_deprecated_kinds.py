"""plan9 P9-1: old Decision/Supersession are deprecated in favor of the Decision
Evolution Graph, and Intent (Rule) may now ground its decision_refs in a
DecisionEvent / CurrentDecisionProjection instead of the old Decision."""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from ppir import registry
from validators import validate_deprecated_kinds as VD
from validators import validate_typed_refs as VT


def test_decision_and_supersession_are_marked_deprecated():
    dep = registry.deprecated_kinds()
    assert "Decision" in dep
    assert "Supersession" in dep


def test_new_deprecated_kind_instance_warns():
    atoms = {"SHOP.DEC.x.y": {"data": {"kind": "Decision", "id": "SHOP.DEC.x.y",
                                     "track": "governance", "status": "accepted",
                                     "commitment_level": "accepted", "scope": {},
                                     "decision": "…"}}}
    v = VD.check(atoms)
    assert any(x.startswith("[warn]") and "deprecated" in x for x in v)


def test_rule_may_ground_in_a_decision_event():
    atoms = {
        "D2IR.RULE.x": {"data": {"kind": "Rule", "id": "D2IR.RULE.x", "track": "intent",
                                 "status": "accepted", "commitment_level": "accepted",
                                 "scope": {}, "decision_refs": ["D2IR.DEVENT.t.001"]}},
        "D2IR.DEVENT.t.001": {"data": {"kind": "DecisionEvent", "id": "D2IR.DEVENT.t.001",
                                       "track": "governance", "status": "accepted",
                                       "commitment_level": "accepted", "scope": {},
                                       "target_ref": "D2IR.TARGET.t", "event_type": "adopt_option",
                                       "decision_time": "2026-07-08"}},
    }
    assert VT.check(atoms) == []          # DecisionEvent is now an allowed decision_ref target


def test_real_ir_uses_the_new_model_only():
    # D2IR is authored as a decision graph — no deprecated Decision/Supersession instances
    assert VD.check(load_atoms(REPO_ROOT / "ir")) == []
