# PPIR Verify — Runtime Command Patterns

Prefer repository scripts. If a script does not exist yet, output the designed
artifact text and mark the command **pending implementation**. Never invent a
successful run.

```bash
# Level 0 — hard validators (schema, id, ref, typed_ref, lifecycle, evidence, graph-health)
python runtime/audit.py --scope all
python runtime/audit.py --scope app:shop-admin

# Level 1 — traceability report (근거 chain: source→decision→atom→affects)
python compilers/compile_traceability.py                       # whole repo
python compilers/compile_traceability.py --feature warehouses
#   → compiled/reports/traceability-report.md
#   exit 1 if any broken chain (orphan / dangling_source / idle_decision / idle_test)

# Level 6/7 — regression + mutation suite
python -m pytest tests/ -q

# One-shot gate — audit + traceability + tests (STEP 6)
python pipeline/06_verify.py

# Level 4 (pending kind) — answer acceptance questions via explain
python runtime/explain.py "why is warehouse available read only?"
```

## Gate mapping (docs/08 §12)

| Gate | Command | Blocks merge? |
|---|---|---|
| 1 hard audit | `runtime/audit.py` (hard only) | yes |
| 3 traceability | `compile_traceability.py` | yes |
| tests | `pytest tests/` | yes |
| 4 acceptance | `explain.py` vs expected (pending) | advisory until kind lands |
| 6 human approval | — | yes (outside script) |

Advisory (`[warn]`) findings — `decision_required`, `test_required`,
`no_orphan` — are reported but never block.
