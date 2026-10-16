"""Level 0 evidence checks (docs/08 §3): every accepted atom must carry a
provenance chain. source_required is HARD; decision_required and test_required
are advisory ([warn]) because the legacy pilot legitimately has law-from-source
rules without a separate Decision and rules without a TestCase yet."""
from validators import validate_evidence


def _atoms(*datas):
    return {d["id"]: {"path": None, "data": d} for d in datas}


def _hard(v):
    return [x for x in v if not x.startswith("[warn]")]


def _warn(v):
    return [x for x in v if x.startswith("[warn]")]


def test_accepted_atom_without_source_or_decision_is_hard_violation():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY"})
    hard = _hard(validate_evidence.check(atoms))
    assert any("SHOP.RULE.x" in x for x in hard)


def test_accepted_atom_with_source_ref_satisfies_source_required():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY",
                    "source_refs": ["SHOP.SRC.a"]})
    hard = _hard(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x for x in hard)


def test_accepted_atom_with_only_decision_ref_satisfies_source_required():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY",
                    "decision_refs": ["SHOP.DEC.a"]})
    hard = _hard(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x for x in hard)


def test_non_accepted_atom_is_exempt_from_source_required():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "draft", "normative": "MAY"})
    hard = _hard(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x for x in hard)


def test_must_rule_without_decision_is_advisory_warn():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MUST",
                    "source_refs": ["SHOP.SRC.a"]})
    warn = _warn(validate_evidence.check(atoms))
    assert any("SHOP.RULE.x" in x and "decision" in x.lower() for x in warn)


def test_may_rule_without_decision_is_not_warned():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY",
                    "source_refs": ["SHOP.SRC.a"]})
    warn = _warn(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x and "decision" in x.lower() for x in warn)


def test_rule_without_testcase_is_advisory_warn():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY",
                    "source_refs": ["SHOP.SRC.a"]})
    warn = _warn(validate_evidence.check(atoms))
    assert any("SHOP.RULE.x" in x and "test" in x.lower() for x in warn)


def test_rule_with_explicit_no_test_reason_is_not_warned():
    atoms = _atoms({"id": "SHOP.RULE.x", "kind": "Rule",
                    "commitment_level": "accepted", "normative": "MAY",
                    "source_refs": ["SHOP.SRC.a"], "no_test_reason": "trivial"})
    warn = _warn(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x and "test" in x.lower() for x in warn)


def test_rule_covered_by_testcase_is_not_warned():
    atoms = _atoms(
        {"id": "SHOP.RULE.x", "kind": "Rule", "commitment_level": "accepted",
         "normative": "MAY", "source_refs": ["SHOP.SRC.a"]},
        {"id": "SHOP.TEST.x", "kind": "TestCase", "commitment_level": "accepted",
         "target_refs": ["SHOP.RULE.x"], "source_refs": ["SHOP.SRC.a"]},
    )
    warn = _warn(validate_evidence.check(atoms))
    assert not any("SHOP.RULE.x" in x and "test" in x.lower() for x in warn)
