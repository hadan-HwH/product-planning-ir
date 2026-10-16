"""Adversarial / negative tests for the Decision Evolution Graph (plan8 §5).

Proves the reducer + guards are not over-fit to the happy path: a superseded or
signal-only option can never present as current, a single target can't hold two
active options, and dropping the decisive event drops the current answer.
"""
from __future__ import annotations

import copy

from ppir.config import REPO_ROOT
from ppir.atoms import load_atoms
from compilers.compile_decision_projection import project_target
from validators import validate_decision_projection as V

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"
OPT_A = "SHOP.OPTION.business_need_x.a"
OPT_A2 = "SHOP.OPTION.business_need_x.a2"
EV_REPLACE = "SHOP.DEVENT.business_need_x.004_replace_a_with_a2"


def _atoms():
    return load_atoms(FIXTURE)


# ---- positive: the clean fixture is valid ------------------------------------

def test_clean_fixture_has_no_violations():
    assert V.check(_atoms()) == []


# ---- (§5 음성 4) reduce is load-bearing: drop the decisive event -------------

def test_dropping_replace_event_drops_a2():
    atoms = _atoms()
    del atoms[EV_REPLACE]                       # remove event 004
    proj = project_target(atoms, TARGET)
    assert proj["current_option"] != [OPT_A2]   # a2 is no longer authoritative
    # after reopen with nothing re-selected, the target is open (not silently a)
    assert proj["current_state"] in {"open", "deferred"}
    assert OPT_A not in proj["current_option"]


# ---- (a) single-resolution target must not hold two active options -----------

def test_two_active_options_is_hard_fail():
    atoms = _atoms()
    # make event 004 adopt a2 WITHOUT replacing a, and un-defer a -> both active
    ev = atoms[EV_REPLACE]["data"]
    ev["event_type"] = "adopt_option"
    ev["selects"] = [OPT_A2]
    ev.pop("replaces", None)
    atoms["SHOP.DEVENT.business_need_x.001_adopt_a"]["data"]["selects"] = [OPT_A]
    # neutralize the defer so a stays active
    atoms["SHOP.DEVENT.business_need_x.002_defer_a"]["data"]["event_type"] = "confirm_current"
    atoms["SHOP.DEVENT.business_need_x.002_defer_a"]["data"].pop("affects", None)
    proj = project_target(atoms, TARGET)
    assert set(proj["current_option"]) == {OPT_A, OPT_A2}
    assert proj["current_state"] == "conflict"
    viol = V.violations_for(atoms[TARGET]["data"], proj, atoms)
    assert any("single-resolution" in v for v in viol)


# ---- (b) a current option cannot itself be in an inactive lifecycle state ----

def test_current_option_with_superseded_status_is_hard_fail():
    atoms = _atoms()
    atoms[OPT_A2]["data"]["commitment_level"] = "superseded"   # stale status, still current
    proj = project_target(atoms, TARGET)                       # reducer still yields a2
    viol = V.violations_for(atoms[TARGET]["data"], proj, atoms)
    assert any("inactive commitment_level" in v for v in viol)


# ---- (c) a signal-only option must never be current (guard on any projection) -

def test_signal_only_current_is_hard_fail():
    atoms = _atoms()
    fake = copy.deepcopy(project_target(atoms, TARGET))
    fake["current_option"] = ["SHOP.OPTION.business_need_x.a3_from_signal"]  # never accepted-selected
    viol = V.violations_for(atoms[TARGET]["data"], fake, atoms)
    assert any("signal-only leak" in v for v in viol)


# ---- (d) a projection that asserts a summary must carry a decision_chain ------

def test_summary_without_chain_is_hard_fail():
    atoms = _atoms()
    proj = {"current_option": [], "current_summary": "무언가 결정됨", "decision_chain": []}
    viol = V.violations_for(atoms[TARGET]["data"], proj, atoms)
    assert any("empty decision_chain" in v for v in viol)
