"""as_of must reflect when a decision took effect. An event with no
effective_from is in force from its decision_time — it must NOT leak into a
checkpoint earlier than when it was decided (needed for Timeline Faithfulness)."""
from __future__ import annotations

from compilers.compile_decision_projection import project_target

T = "SHOP.TARGET.t"
X = "SHOP.OPTION.t.x"
Y = "SHOP.OPTION.t.y"


def _atoms(*events):
    store = {T: {"data": {"kind": "DecisionTarget", "id": T, "track": "governance",
                          "status": "accepted", "commitment_level": "accepted",
                          "statement": "t?", "current_resolution_policy": "single",
                          "scope": {}}}}
    for o in (X, Y):
        store[o] = {"data": {"kind": "SolutionOption", "id": o, "track": "governance",
                             "status": "accepted", "commitment_level": "accepted",
                             "target_ref": T, "summary": o.split(".")[-1], "scope": {}}}
    for i, ev in enumerate(events):
        ev = {"kind": "DecisionEvent", "track": "governance", "status": "accepted",
              "commitment_level": "accepted", "target_ref": T, "scope": {},
              "id": f"SHOP.DEVENT.t.{i:03d}", **ev}
        store[ev["id"]] = {"data": ev}
    return store


def test_future_decided_event_excluded_before_its_decision_time():
    atoms = _atoms(
        {"event_type": "adopt_option", "decision_time": "2026-07-01T10:00:00+09:00",
         "effective_from": "2026-07-01", "selects": [X]},
        {"event_type": "replace_option", "decision_time": "2026-07-10T10:00:00+09:00",
         "replaces": [X], "selects": [Y]},   # no effective_from
    )
    # At 07-05 the replace (decided 07-10) has not happened yet -> still X.
    assert project_target(atoms, T, as_of="2026-07-05")["current_option"] == [X]
    # At 07-11 it is in force -> Y.
    assert project_target(atoms, T, as_of="2026-07-11")["current_option"] == [Y]
