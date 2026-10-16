"""Context Pack (plan8 Phase 4). The AI-facing payload built from a projection.

The whole point vs chunk RAG: it does not just surface related text — it states
the current authoritative decision, marks inactive options must_not_use_as_current,
and emits forbidden_inferences so an agent cannot present a superseded option (a)
as the plan.
"""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_context_pack import build, render_markdown

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"
OPT_A = "SHOP.OPTION.business_need_x.a"
OPT_A2 = "SHOP.OPTION.business_need_x.a2"


def _pack():
    return build(load_atoms(FIXTURE), TARGET)


def test_authority_current_is_a2_only():
    pack = _pack()
    current_ids = [c["option"] for c in pack["authority"]["current"]]
    assert current_ids == [OPT_A2]


def test_inactive_a_is_marked_must_not_use():
    pack = _pack()
    inactive = {i["option"]: i for i in pack["authority"]["inactive"]}
    assert OPT_A in inactive
    assert inactive[OPT_A]["must_not_use_as_current"] is True
    assert inactive[OPT_A]["reason"] == "replaced_by_a2"


def test_forbidden_inferences_block_option_a():
    pack = _pack()
    joined = " ".join(pack["forbidden_inferences"])
    assert "a" in joined
    assert any("current decision" in f for f in pack["forbidden_inferences"])
    assert any("Do not present option a " in f for f in pack["forbidden_inferences"])


def test_history_and_open_questions_and_sources():
    pack = _pack()
    assert len(pack["history"]) == 4
    assert any(q["id"] == "SHOP.OQ.business_need_x.a2_scope" for q in pack["open_questions"])
    assert pack["source_refs"]                      # provenance carried


def test_no_contamination_current_excludes_inactive():
    """The defining anti-chunk property: no inactive option leaks into authority.current."""
    pack = _pack()
    current_ids = {c["option"] for c in pack["authority"]["current"]}
    inactive_ids = {i["option"] for i in pack["authority"]["inactive"]}
    assert current_ids.isdisjoint(inactive_ids)
    assert OPT_A not in current_ids


def test_markdown_render_is_self_contained():
    md = render_markdown(_pack())
    assert "a2" in md
    assert "must_not_use_as_current" in md or "MUST NOT" in md
    assert "Forbidden" in md or "forbidden" in md
