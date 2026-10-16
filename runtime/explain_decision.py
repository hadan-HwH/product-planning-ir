"""Explain a DecisionTarget's evolution (plan8 — ppir-explain --mode).

Three questions are different and get three modes:

  current      "지금 결정이 뭐야?"      -> the authoritative option + summary
  why-current  "왜 지금 이게 결정이야?"  -> summary + the reason chain + what's inactive & why
  timeline     "여기까지 어떻게 바뀌었어?" -> the ordered event stream

Read-only. Never presents a superseded/signal-only option as current.

Usage: python runtime/explain_decision.py --mode current --ir <dir> <TARGET_ID>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT                                   # noqa: E402
from ppir.atoms import load_atoms                                   # noqa: E402
from compilers.compile_decision_projection import (                 # noqa: E402
    project_target, _events_for_target, _short)


def _summary(atoms: dict, proj: dict) -> str:
    return proj.get("current_summary") or "(결정된 옵션 없음)"


def explain(atoms: dict, target_id: str, mode: str) -> str:
    proj = project_target(atoms, target_id)
    current = ", ".join(_short(o) for o in proj["current_option"]) or "(없음)"

    if mode == "current":
        return f"Current [{proj['current_state']}]: {_summary(atoms, proj)}\n" \
               f"Option: {current}"

    if mode == "why-current":
        lines = [f"Current [{proj['current_state']}]: {_summary(atoms, proj)}", "Why:"]
        lines += [f"  - {step}" for step in proj["decision_chain"]]
        if proj["inactive_options"]:
            lines.append("Inactive:")
            lines += [f"  - {_short(i['option'])} — {i['reason']}"
                      for i in proj["inactive_options"]]
        return "\n".join(lines)

    if mode == "timeline":
        lines = [f"Timeline — {target_id}:"]
        for e in _events_for_target(atoms, target_id):
            when = (e.get("decision_time") or "")[:10]
            detail = ""
            if e.get("replaces") or e.get("selects"):
                frm = "/".join(_short(x) for x in (e.get("replaces") or []))
                to = "/".join(_short(x) for x in (e.get("selects") or []))
                detail = f"  {frm + ' → ' if frm else ''}{to}".rstrip()
            lines.append(f"  {when}  {e.get('event_type'):16}{detail}")
        lines.append(f"→ Current: {current}")
        return "\n".join(lines)

    raise SystemExit(f"unknown mode {mode!r} (current | why-current | timeline)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target_id")
    ap.add_argument("--mode", default="current",
                    choices=["current", "why-current", "timeline"])
    ap.add_argument("--ir", default="ir")
    args = ap.parse_args()
    atoms = load_atoms(REPO_ROOT / args.ir)
    if args.target_id not in atoms:
        raise SystemExit(f"no such DecisionTarget: {args.target_id}")
    print(explain(atoms, args.target_id, args.mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
