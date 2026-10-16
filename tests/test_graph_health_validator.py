"""Level 0 graph-health (docs/08 §3, §4): an accepted policy atom that nothing
references is a dangling/orphan atom. Advisory ([warn]) — root/leaf kinds
(Screen, TestCase, Supersession, OpenQuestion, Source, ClaimSet, ...) are
legitimately unreferenced and exempt."""
from validators import validate_graph_health


def _atoms(*datas):
    return {d["id"]: {"path": None, "data": d} for d in datas}


def test_unreferenced_rule_is_orphan_warn():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted"})
    v = validate_graph_health.check(atoms)
    assert any(x.startswith("[warn]") and "SHOP.RULE.x" in x and "orphan" in x.lower()
               for x in v)


def test_rule_referenced_by_screen_is_not_orphan():
    atoms = _atoms(
        {"id": "SHOP.RULE.x", "kind": "Rule", "commitment_level": "accepted"},
        {"id": "SHOP.SCREEN.s", "kind": "Screen", "commitment_level": "accepted",
         "rules": ["SHOP.RULE.x"]},
    )
    v = validate_graph_health.check(atoms)
    assert not any("SHOP.RULE.x" in x for x in v)


def test_root_kind_screen_is_exempt_from_orphan():
    atoms = _atoms({"id": "SHOP.SCREEN.s", "kind": "Screen",
                    "commitment_level": "accepted"})
    v = validate_graph_health.check(atoms)
    assert not any("SHOP.SCREEN.s" in x for x in v)


def test_root_kind_testcase_is_exempt_from_orphan():
    atoms = _atoms({"id": "SHOP.TEST.x", "kind": "TestCase",
                    "commitment_level": "accepted", "target_refs": ["SHOP.RULE.x"]})
    v = validate_graph_health.check(atoms)
    assert not any("SHOP.TEST.x" in x for x in v)


def test_non_accepted_orphan_is_not_warned():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "draft"})
    v = validate_graph_health.check(atoms)
    assert not any("SHOP.RULE.x" in x for x in v)
