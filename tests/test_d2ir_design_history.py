"""D2IR product — the design history of building this very system, as real ir/ data.

Dogfooding: the decisions that produced the decision graph are themselves modeled
as a decision graph. These targets exercise the harder event types the a→a2 golden
fixture does not (cancel_target, propose+reject, 3-step replace, multiple_allowed),
on real data, run through the real pipeline (audit + projection).
"""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_decision_projection import project_target
from runtime import audit

IR = REPO_ROOT / "ir"


def _atoms():
    return load_atoms(IR)


def _short(ids):
    return sorted(x.split(".")[-1] for x in ids)


def test_ir_has_no_hard_audit_violations():
    hard = [v for v in audit.run_all(IR) if not v.startswith("[warn]")]
    assert hard == [], hard


def test_knowledge_representation_is_decision_graph_now():
    p = project_target(_atoms(), "D2IR.TARGET.knowledge_representation")
    assert _short(p["current_option"]) == ["decision_graph"]
    assert p["current_state"] == "accepted"
    assert len(p["decision_chain"]) == 3            # markdown -> typed_ir -> decision_graph
    inactive = {i["option"].split(".")[-1]: i["reason"] for i in p["inactive_options"]}
    assert inactive["markdown_clause"] == "replaced_by_typed_ir_ssot"
    assert inactive["typed_ir_ssot"] == "replaced_by_decision_graph"


def test_legacy_pilot_was_cancelled():
    p = project_target(_atoms(), "D2IR.TARGET.pilot_data")
    assert p["current_state"] == "cancelled"
    assert p["current_option"] == []


def test_demo_data_is_both_synthetic_and_self_history_audit_rejected():
    p = project_target(_atoms(), "D2IR.TARGET.demo_data_source")
    assert _short(p["current_option"]) == ["self_design_history", "synthetic_a_a2"]
    inactive = {i["option"].split(".")[-1]: i["reason"] for i in p["inactive_options"]}
    assert inactive.get("audit_realdata") == "rejected"
    # self-referential: this very fixture is the current demo data
    assert "self_design_history" in _short(p["current_option"])


def test_ssot_repo_is_product_planning_ir():
    p = project_target(_atoms(), "D2IR.TARGET.ssot_repo")
    assert _short(p["current_option"]) == ["product_planning_ir"]


def test_reducer_scope_is_all_16():
    p = project_target(_atoms(), "D2IR.TARGET.reducer_scope")
    assert _short(p["current_option"]) == ["all_16"]


def test_phase2_pilot_promotion_was_cancelled():
    p = project_target(_atoms(), "D2IR.TARGET.pilot_promotion_phase2")
    assert p["current_state"] == "cancelled"


def test_product_isolation_is_domain_plus_validator():
    # propose folder-only -> reject -> adopt the validator (the decision we then built)
    p = project_target(_atoms(), "D2IR.TARGET.product_isolation")
    assert _short(p["current_option"]) == ["domain_plus_validator"]
    assert len(p["decision_chain"]) == 3


def test_system_is_domain_agnostic_not_software_specific():
    # the system is general-purpose; software-specific kinds/role-views are a domain
    # pack, not core (FE/BE/QA/PM publish is not a core gap).
    p = project_target(_atoms(), "D2IR.TARGET.system_generality")
    assert _short(p["current_option"]) == ["domain_agnostic"]


def test_option_authoring_reversal():
    # finer decision extracted via the adopt `decisions` method: authoring an option's
    # outcome on the atom was adopted, hit audit's referencing-rejected, then reversed
    # to "outcome computed by projection".
    p = project_target(_atoms(), "D2IR.TARGET.option_authoring")
    assert _short(p["current_option"]) == ["computed_by_projection"]
    inactive = {i["option"].split(".")[-1]: i["reason"] for i in p["inactive_options"]}
    assert inactive.get("on_option") == "rejected"
