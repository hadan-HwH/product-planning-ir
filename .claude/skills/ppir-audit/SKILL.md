---
name: ppir-audit
description: audit ppir repositories for schema, id, reference, typed reference, lifecycle, atomicity, duplicate, conflict, terminology, generated staleness, and drift issues. use before merge, before publish, or when the user asks for consistency review.
---

# PPIR Audit

## Purpose

Validate PPIR structure and report violations before merge, publish, or further automation.

## Load when needed

- Read `references/ppir-core.md` for quality gates.
- Read `references/runtime-commands.md` for command patterns.

## Inputs

- scope: all, product, platform, app, feature, atom
- optional mode: strict, warning, report-only

## Outputs

- AuditReport
- ViolationList
- suggested fixes
- merge/publish blocker status

## Required checks

Run these when corresponding scripts exist:

1. schema validation
2. id validation
3. reference validation
4. typed reference validation
5. lifecycle matrix validation
6. atomicity validation
7. duplicate validation
8. conflict validation
9. terminology validation
10. generated staleness validation
11. openapi drift validation when reality inputs exist
12. evidence + graph-health validation
13. decision-graph guards: decision-projection (no multiple-active / no superseded-or-signal-as-current), product-isolation (no cross-product refs), deprecated-kinds (no new Decision/Supersession)
14. semantic LLM validation only after machine checks

## Audit rules

- Machine validation runs before LLM semantic validation.
- Warnings may be reported, but merge blockers must be explicit.
- Do not auto-fix accepted IR unless routed through Proposal and review-merge.
- For generated staleness, compare source graph hash and compiler version when available.

## Output format

```markdown
# Audit Report

## Scope
...

## Summary
- blockers: 0
- warnings: 0
- info: 0

## Blockers
...

## Warnings
...

## Suggested next workflow
- `ppir-review-merge`, `ppir-reflect`, or `ppir-publish`
```
