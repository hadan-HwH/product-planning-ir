"""STEP 5 — compile: regenerate human-readable views from ir/ into compiled/.
Currently: a screen definition per Screen atom. (Other views — policy/FE/BE/QA/
PM/context-pack — plug in here as they are built.)"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT                       # noqa: E402
from ppir.atoms import load_atoms                        # noqa: E402
from compilers.loaders import AtomStore                 # noqa: E402
from compilers import provenance                        # noqa: E402
from compilers import compile_screen_definition as csd  # noqa: E402
from compilers import compile_decision_projection as cdp  # noqa: E402
from compilers import compile_context_pack as ccp         # noqa: E402


def main() -> int:
    ir = REPO_ROOT / "ir"
    atoms = load_atoms(ir)
    store = AtomStore(ir)
    screens = store.by_kind("Screen")
    if not screens:
        print("STEP 5 compile — no Screen atoms")
    for screen in screens:
        md = provenance.stamp(csd.render(ir, screen["id"]), "screen_definition", atoms)
        out = csd._out(screen, screen["id"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"STEP 5 compile — {screen['id']} -> {out.relative_to(REPO_ROOT)}")

    # CurrentDecisionProjection per DecisionTarget (plan8). No-op until targets land
    # in ir/ (pilot promotion, Phase 2); the a→a2 fixture lives under tests/.
    projections = cdp.run(REPO_ROOT / "ir",
                          REPO_ROOT / "compiled" / "reports" / "decision-projections")
    for p in projections:
        print(f"STEP 5 compile — projection -> {p.relative_to(REPO_ROOT)}")

    # Context Pack per DecisionTarget (plan8 Phase 4) — the AI-facing authority payload.
    packs = ccp.run(REPO_ROOT / "ir", REPO_ROOT / "compiled" / "context-packs")
    for p in packs:
        print(f"STEP 5 compile — context-pack -> {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
