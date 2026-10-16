"""Phase 5 evaluation harness — quantify the two systems over the a→a2 fixture.

Both are scored against the human-authored authoritative timeline (the fixture's
events). The DecisionGraph is faithful and un-contaminated; the chunk baseline is
neither."""
from ppir.atoms import load_atoms
from ppir.config import REPO_ROOT
from evaluation import harness as H

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"


def _m():
    return H.evaluate(load_atoms(FIXTURE), TARGET)


def test_graph_timeline_faithfulness_is_perfect():
    assert _m()["graph"]["timeline_faithfulness"] == 1.0


def test_baseline_timeline_faithfulness_is_two_of_five():
    assert _m()["baseline"]["timeline_faithfulness"] == 0.4


def test_baseline_context_is_contaminated():
    assert _m()["baseline"]["contamination_rate"] == 0.8


def test_graph_context_has_zero_contamination():
    assert _m()["graph"]["contamination_rate"] == 0.0


def test_headline_disagreement_at_now():
    m = _m()
    assert m["baseline"]["answer_now"] == "a"
    assert m["graph"]["answer_now"] == "a2"


def test_report_names_both_metrics_and_systems():
    md = H.render_report(_m())
    assert "Timeline Faithfulness" in md
    assert "Contamination" in md
    assert "chunk" in md.lower() and "graph" in md.lower()
