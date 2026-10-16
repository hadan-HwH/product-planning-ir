"""Product isolation (D2IR decision): products are one global graph separated only by
DOMAIN id-prefix + convention. This validator turns the convention into enforcement —
a product-domain atom may not reference another product's atoms (shared foundation
domains like TERM/MSG are the escape hatch)."""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from validators import validate_product_isolation as V


def _atoms(*atoms):
    return {a["id"]: {"data": a} for a in atoms}


def _d2ir(ref_field, ref_id):
    return {"kind": "DecisionEvent", "id": "D2IR.DEVENT.x.001", "track": "governance",
            "status": "accepted", "commitment_level": "accepted",
            "target_ref": "D2IR.TARGET.x", ref_field: [ref_id], "scope": {}}


def test_cross_product_ref_is_violation():
    atoms = _atoms(_d2ir("source_refs", "SHOP.SRC.something"))
    v = V.check(atoms)
    assert any("SHOP.SRC.something" in x and "D2IR" in x for x in v)


def test_ref_to_shared_foundation_is_ok():
    atoms = _atoms(_d2ir("source_refs", "TERM.TERM.warehouse"))
    assert V.check(atoms) == []


def test_same_product_ref_is_ok():
    atoms = _atoms(_d2ir("source_refs", "D2IR.SRC.session_2026_07_08"))
    assert V.check(atoms) == []


def test_foundation_may_not_depend_on_a_product():
    # a shared-domain atom reaching into a product is also a violation
    atoms = _atoms({"kind": "Message", "id": "MSG.MSG.generic", "track": "intent",
                    "status": "accepted", "commitment_level": "accepted",
                    "scope": {}, "tone_ref": ["SHOP.RULE.some_tone"]})
    assert any("SHOP.RULE.some_tone" in x for x in V.check(atoms))


def test_real_ir_is_isolated():
    assert V.check(load_atoms(REPO_ROOT / "ir")) == []
