---
name: ppir-verify
description: verify a ppir feature the way a human can trust without reading YAML — run the docs/08 verification pyramid (Level 0 audit, Level 1 traceability, Level 6/7 regression & mutation tests) and produce human-facing verification views (Traceability Report, Quality Dashboard). use before merge, before publish, or when the user asks "is this feature correct / did we miss anything / can I trust this".
---

# PPIR Verify

## Purpose

PPIR's原本 is an AI-facing atom graph — a human cannot read it directly, so a
single bad atom can propagate silently. This skill does NOT ask a human to read
YAML. It **generates human-checkable verification artifacts from the graph** and
runs the machine + regression checks behind them. Design spec: `docs/08-verification-and-testing.md`.

Read-only with one exception: it writes generated reports under
`compiled/reports/`. It never edits `ir/`, and it is not a merge path.

## Load when needed

- Read `references/verify-commands.md` for the exact runtime commands.
- Read `../ppir-audit/references/ppir-core.md` for the write boundary and quality gates.
- Read `docs/08-verification-and-testing.md` for the full pyramid and gate policy.

## Inputs

- scope: all | feature:{name} | atom:{id}
- optional: which levels to run (default: 0, 1, 6, 7 — the implemented set)

## Outputs

- AuditReport (Level 0: hard blockers + advisory warnings)
- Traceability Report → `compiled/reports/traceability-report.md`
- Regression + mutation test result
- Quality Dashboard (summary a human reads instead of the graph)
- merge-gate verdict (blockers vs advisories)

## Implemented vs pending

- **Implemented now:** Level 0 (`validate_evidence`, `validate_graph_health` +
  the existing schema/id/ref/typed_ref/lifecycle), Level 1 traceability
  (`compilers/compile_traceability.py`), Level 6/7 (`tests/`), gate
  (`pipeline/06_verify.py`).
- **Pending (design only in docs/08 — do NOT fake results):** Level 2 source
  coverage, Level 3 review-view enrichment, Level 4 `AcceptanceQuestionSet`
  (needs a new kind + schema, answered via `ppir-explain`), Level 5 cross-view.
  When asked for these, produce the designed artifact text and mark it
  **"pending implementation"**. Never invent a passing run.

## Workflow

1. Run Level 0 audit (`python runtime/audit.py --scope {scope}`). Separate hard
   blockers from `[warn]` advisories. Hard blockers block merge.
2. Regenerate the Level 1 Traceability Report
   (`python compilers/compile_traceability.py [--feature {name}]`). A broken
   근거 chain (orphan / dangling_source / idle_decision / idle_test) is a blocker.
3. Run the regression + mutation suite (`python -m pytest tests/ -q`). Any
   failure is a blocker. `pipeline/06_verify.py` does steps 1–3 in one shot.
4. For Level 4 (if requested), draft the `AcceptanceQuestionSet` questions,
   answer each via `ppir-explain`, and compare against `expected_answer_contains`.
   Until the kind exists, mark pending.
5. Emit the Quality Dashboard and the gate verdict.

## Verify rules

- Machine checks (Level 0) run before any semantic/LLM check.
- `source_required` is a hard blocker; `decision_required`/`test_required`/
  `no_orphan` are advisory — report them, do not block on them.
- `audit PASS` alone does not authorize merge — traceability and tests must also
  pass, then a human approves (Gate 6). Merge itself is `ppir-review-merge`.
- Do not auto-fix `ir/`. Route fixes through a Proposal.
- An OpenQuestion that blocks an accepted atom is a hard warning; never answer it
  by guessing (README rule 4).

## Output format

```markdown
# PPIR Quality Dashboard — {feature}

## Summary
- Atoms: N | Current Rules: N | Superseded Decisions: N | Open Questions: N | Test Cases: N
- Level 0 audit: PASS/FAIL (H hard, W advisory)
- Level 1 traceability: PASS/FAIL (orphan/dangling/idle counts)
- Level 6/7 tests: PASS/FAIL

## Blockers
- ...

## Advisories
- ... (undecided normative rules, untested rules, orphans)

## Open Questions
- ...

## Merge gate
- Gate 1 (hard audit): ...
- Gate 3 (traceability): ...
- Gate 6 (human approval): required

## Next
- `ppir-review-merge` when all gates green, or a Proposal to fix findings.
```
