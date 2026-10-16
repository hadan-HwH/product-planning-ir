"""Reducer completeness (plan8 A): all 16 event_types reduce (none raise), plus the
two governance-order rules the first cut skipped — rule 3 (effective_from validity)
and rule 5 (authority_level can't be overridden by a lower authority).
"""
from __future__ import annotations

import pytest

from compilers.compile_decision_projection import project_target, _events_for_target

T = "SHOP.TARGET.t"
X = "SHOP.OPTION.t.x"
Y = "SHOP.OPTION.t.y"


def _atoms(*events, options=(X, Y), policy="single"):
    """Build an atoms dict: one target, some options, the given events (in any order)."""
    store = {
        T: {"data": {"kind": "DecisionTarget", "id": T, "track": "governance",
                     "status": "accepted", "commitment_level": "accepted",
                     "statement": "t?", "current_resolution_policy": policy,
                     "scope": {}}},
    }
    for o in options:
        store[o] = {"data": {"kind": "SolutionOption", "id": o, "track": "governance",
                             "status": "accepted", "commitment_level": "accepted",
                             "target_ref": T, "summary": f"opt {o.split('.')[-1]}",
                             "scope": {}}}
    for i, ev in enumerate(events):
        ev = {"kind": "DecisionEvent", "track": "governance", "status": "accepted",
              "commitment_level": "accepted", "target_ref": T, "scope": {},
              "id": ev.get("id", f"SHOP.DEVENT.t.{i:03d}"), **ev}
        store[ev["id"]] = {"data": ev}
    return store


def _ev(event_type, t, **kw):
    return {"event_type": event_type, "decision_time": t, **kw}


# ---- every event_type reduces; none raise ------------------------------------

ALL_TYPES = ["propose_option", "adopt_option", "defer_option", "reject_option",
             "reopen_target", "replace_option", "refine_option", "narrow_scope",
             "expand_scope", "supersede_decision", "amend_decision", "cancel_target",
             "split_target", "merge_target", "confirm_current"]


@pytest.mark.parametrize("et", ALL_TYPES)
def test_no_event_type_raises(et):
    atoms = _atoms(_ev("adopt_option", "2026-01-01", selects=[X]),
                   _ev(et, "2026-02-01", selects=[Y], replaces=[X], affects=[X]))
    proj = project_target(atoms, T)          # must not raise NotImplementedError
    assert proj["current_state"] in {"open", "accepted", "deferred", "conflict", "cancelled", "superseded"}


# ---- specific semantics ------------------------------------------------------

def test_propose_does_not_make_current():
    proj = project_target(_atoms(_ev("propose_option", "2026-01-01", selects=[X])), T)
    assert proj["current_option"] == []
    assert proj["current_state"] == "open"


def test_reject_marks_rejected_and_opens():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X]),
        _ev("reject_option", "2026-02-01", affects=[X])), T)
    assert proj["current_option"] == []
    assert {i["option"]: i["reason"] for i in proj["inactive_options"]}[X] == "rejected"


def test_refine_keeps_current():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X]),
        _ev("refine_option", "2026-02-01", affects=[X])), T)
    assert proj["current_option"] == [X]
    assert proj["current_state"] == "accepted"


def test_narrow_scope_drops_affected_option():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X, Y]),
        _ev("narrow_scope", "2026-02-01", affects=[Y]), policy="multiple_allowed"), T)
    assert proj["current_option"] == [X]
    assert {i["option"]: i["reason"] for i in proj["inactive_options"]}[Y] == "out_of_scope"


def test_supersede_decision_replaces():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X]),
        _ev("supersede_decision", "2026-02-01", replaces=[X], selects=[Y])), T)
    assert proj["current_option"] == [Y]
    assert {i["option"]: i["reason"] for i in proj["inactive_options"]}[X] == "superseded"


def test_cancel_target():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X]),
        _ev("cancel_target", "2026-02-01")), T)
    assert proj["current_state"] == "cancelled"
    assert proj["current_option"] == []


# ---- rule 5: authority_level ------------------------------------------------

def test_lower_authority_cannot_override_higher():
    # executive adopts X; a later team-level event tries to replace with Y -> X stands.
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X], authority_level="executive"),
        _ev("replace_option", "2026-02-01", replaces=[X], selects=[Y],
            authority_level="team")), T)
    assert proj["current_option"] == [X]


def test_equal_or_higher_authority_overrides():
    proj = project_target(_atoms(
        _ev("adopt_option", "2026-01-01", selects=[X], authority_level="team"),
        _ev("replace_option", "2026-02-01", replaces=[X], selects=[Y],
            authority_level="executive")), T)
    assert proj["current_option"] == [Y]


# ---- rule 3: effective_from --------------------------------------------------

def test_future_effective_event_excluded_by_as_of():
    atoms = _atoms(
        _ev("adopt_option", "2026-01-01", selects=[X], effective_from="2026-01-01"),
        _ev("replace_option", "2026-02-01", replaces=[X], selects=[Y],
            effective_from="2026-03-01"))
    # as of 2026-02-15 the replace is not yet effective -> X still current
    assert project_target(atoms, T, as_of="2026-02-15")["current_option"] == [X]
    # with no as_of (or a later one) the replace applies -> Y
    assert project_target(atoms, T)["current_option"] == [Y]
    assert project_target(atoms, T, as_of="2026-03-02")["current_option"] == [Y]


def test_events_for_target_filters_by_as_of():
    atoms = _atoms(_ev("adopt_option", "2026-01-01", selects=[X], effective_from="2026-05-01"))
    assert len(_events_for_target(atoms, T, as_of="2026-04-01")) == 0
    assert len(_events_for_target(atoms, T, as_of="2026-06-01")) == 1
