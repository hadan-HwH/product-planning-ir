"""Golden test for the Decision Evolution Graph (plan8).

The a->a2 fixture encodes the core thesis:

    Chunking finds the latest *related sentence* (S5, 2026-07-15: "a is needed").
    DecisionGraph computes the current *authoritative decision* (a2, from event 004).

The falsifiable gap: naive "latest source text" answers `a`; the reducer answers `a2`.
"""
from __future__ import annotations

import re

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_decision_projection import project_target

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"
OPT_A = "SHOP.OPTION.business_need_x.a"
OPT_A2 = "SHOP.OPTION.business_need_x.a2"


def _atoms():
    return load_atoms(FIXTURE)


def _naive_latest_source_option(atoms: dict) -> str:
    """Baseline a chunk-RAG would produce: the option mentioned in the source with
    the latest date. Models 'retrieve the freshest topical passage'."""
    best_date, best_opt = None, None
    for e in atoms.values():
        d = e["data"]
        if d.get("kind") != "Source":
            continue
        m = re.search(r"(\d{4})_(\d{2})_(\d{2})", d["id"])
        date = tuple(int(x) for x in m.groups()) if m else (0, 0, 0)
        text = d.get("captured_text", "")
        opt = OPT_A2 if "a2" in text else (OPT_A if "기능 a" in text else None)
        if opt and (best_date is None or date > best_date):
            best_date, best_opt = date, opt
    return best_opt


# ---- the projection (reducer) ------------------------------------------------

def test_current_option_is_a2():
    proj = project_target(_atoms(), TARGET)
    assert proj["current_option"] == [OPT_A2]
    assert proj["current_state"] == "accepted"


def test_a_is_inactive_because_replaced_by_a2():
    proj = project_target(_atoms(), TARGET)
    inactive = {i["option"]: i["reason"] for i in proj["inactive_options"]}
    assert OPT_A in inactive
    assert inactive[OPT_A] == "replaced_by_a2"


def test_decision_chain_has_four_steps():
    proj = project_target(_atoms(), TARGET)
    assert len(proj["decision_chain"]) == 4  # adopt -> defer -> reopen -> replace


def test_projection_carries_provenance():
    proj = project_target(_atoms(), TARGET)
    assert len(proj["generated_from_events"]) == 4
    assert proj["current_summary"]  # must explain current state (validator (d))


# ---- the whole point: reduce != max-timestamp --------------------------------

def test_reduce_beats_naive_latest():
    atoms = _atoms()
    naive = _naive_latest_source_option(atoms)
    reduced = project_target(atoms, TARGET)["current_option"]
    assert naive == OPT_A, "chunk baseline should be fooled by the 07-15 signal"
    assert reduced == [OPT_A2], "reducer should compute the authoritative decision"
    assert naive not in reduced  # the two genuinely disagree


# ---- acceptance questions (spec section 10) ----------------------------------

def test_acceptance_q1_build_a_or_a2():
    # Q1. 현재 만들어야 하는 것은 a인가 a2인가? -> a2
    assert project_target(_atoms(), TARGET)["current_option"] == [OPT_A2]


def test_acceptance_q4_reopen_is_not_adopt():
    # Q4. S3(reopen)만 보면 a를 다시 만드는 것 아닌가? -> reopen != adopt; 최종은 a2
    proj = project_target(_atoms(), TARGET)
    assert OPT_A not in proj["current_option"]
    assert proj["current_option"] == [OPT_A2]
