"""plan9 P9-5 — reconciliation invariants: the old model is gone from ir/ and the
decision layer is the Decision Evolution Graph only."""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from validators import validate_deprecated_kinds as VD

IR = REPO_ROOT / "ir"


def _atoms():
    return load_atoms(IR)


def test_no_old_decision_or_supersession_in_ir():
    kinds = {e["data"]["kind"] for e in _atoms().values()}
    assert "Decision" not in kinds
    assert "Supersession" not in kinds


def test_ir_has_no_deprecated_kind_instances():
    assert VD.check(_atoms()) == []


def test_decision_layer_is_the_graph():
    kinds = {e["data"]["kind"] for e in _atoms().values()}
    # decisions are expressed as the graph (targets/events), not old Decision atoms
    assert "DecisionTarget" in kinds
    assert "DecisionEvent" in kinds
