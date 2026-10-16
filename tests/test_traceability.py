"""Level 1 Traceability (docs/08 §4): for every atom, where did it come from
(source/decision) and what does it affect (reverse index), plus the four
broken-chain issues — orphan, dangling_source, idle_decision, idle_test."""
from compilers import compile_traceability as tr


def _atoms(*datas):
    return {d["id"]: {"path": None, "data": d} for d in datas}


def test_atom_entry_lists_source_decision_and_affects():
    atoms = _atoms(
        {"id": "SHOP.RULE.x", "kind": "Rule", "track": "intent",
         "commitment_level": "accepted", "source_refs": ["SHOP.SRC.a"],
         "decision_refs": ["SHOP.DEC.d"]},
        {"id": "SHOP.SCREEN.s", "kind": "Screen", "track": "intent",
         "commitment_level": "accepted", "rules": ["SHOP.RULE.x"]},
    )
    rep = tr.build(atoms)
    e = rep["atoms"]["SHOP.RULE.x"]
    assert e["sources"] == ["SHOP.SRC.a"]
    assert e["decisions"] == ["SHOP.DEC.d"]
    assert "SHOP.SCREEN.s" in e["affects"]


def test_accepted_decision_referenced_by_nobody_is_idle():
    atoms = _atoms({"id": "SHOP.DEC.d", "kind": "Decision", "track": "governance",
                    "commitment_level": "accepted", "source_refs": ["SHOP.SRC.a"]})
    assert "SHOP.DEC.d" in tr.build(atoms)["issues"]["idle_decision"]


def test_decision_referenced_by_rule_is_not_idle():
    atoms = _atoms(
        {"id": "SHOP.DEC.d", "kind": "Decision", "track": "governance",
         "commitment_level": "accepted", "source_refs": ["SHOP.SRC.a"]},
        {"id": "SHOP.RULE.x", "kind": "Rule", "track": "intent",
         "commitment_level": "accepted", "decision_refs": ["SHOP.DEC.d"]},
    )
    assert "SHOP.DEC.d" not in tr.build(atoms)["issues"]["idle_decision"]


def test_superseded_decision_is_exempt_from_idle():
    atoms = _atoms({"id": "SHOP.DEC.d", "kind": "Decision", "track": "governance",
                    "commitment_level": "superseded", "source_refs": ["SHOP.SRC.a"]})
    assert "SHOP.DEC.d" not in tr.build(atoms)["issues"]["idle_decision"]


def test_source_referenced_by_nobody_is_dangling():
    atoms = _atoms({"id": "SHOP.SRC.a", "kind": "Source", "track": "governance",
                    "commitment_level": "observed"})
    assert "SHOP.SRC.a" in tr.build(atoms)["issues"]["dangling_source"]


def test_testcase_targeting_a_rule_is_not_idle():
    atoms = _atoms(
        {"id": "SHOP.RULE.x", "kind": "Rule", "track": "intent",
         "commitment_level": "accepted", "source_refs": ["SHOP.SRC.a"]},
        {"id": "SHOP.TEST.t", "kind": "TestCase", "track": "intent",
         "commitment_level": "accepted", "target_refs": ["SHOP.RULE.x"]},
    )
    assert "SHOP.TEST.t" not in tr.build(atoms)["issues"]["idle_test"]


def test_testcase_targeting_nothing_is_idle():
    atoms = _atoms({"id": "SHOP.TEST.t", "kind": "TestCase", "track": "intent",
                    "commitment_level": "accepted", "target_refs": []})
    assert "SHOP.TEST.t" in tr.build(atoms)["issues"]["idle_test"]


def test_render_returns_markdown_with_banner_and_atom_id():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule", "track": "intent",
                    "commitment_level": "accepted", "source_refs": ["SHOP.SRC.a"]})
    md = tr.render(tr.build(atoms))
    assert "DO NOT EDIT" in md
    assert "SHOP.RULE.x" in md
