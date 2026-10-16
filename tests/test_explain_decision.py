"""ppir-explain --mode current|why-current|timeline (plan8 Step 7)."""
from __future__ import annotations

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from runtime.explain_decision import explain

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"


def _atoms():
    return load_atoms(FIXTURE)


def test_current_names_a2_not_a():
    out = explain(_atoms(), TARGET, "current")
    assert "a2" in out
    assert "accepted" in out


def test_why_current_gives_the_reason_chain():
    out = explain(_atoms(), TARGET, "why-current")
    assert "Why:" in out
    assert "공수" in out and "다시 검토" in out      # the middle of the evolution (defer, reopen)
    assert "replaced_by_a2" in out                 # a is inactive, and why


def test_timeline_is_ordered_and_ends_at_a2():
    out = explain(_atoms(), TARGET, "timeline")
    order = [out.index(k) for k in
             ["adopt_option", "defer_option", "reopen_target", "replace_option"]]
    assert order == sorted(order)                  # chronological
    assert out.rstrip().endswith("Current: a2")
