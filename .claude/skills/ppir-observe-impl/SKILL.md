---
name: ppir-observe-impl
description: observe backend mvp, openapi specs, code behavior, database schemas, runtime samples, or implemented screens and compare them against ppir intent without treating implementation facts as accepted product policy.
---

# PPIR Observe Implementation

> **Reality track (plan9 B).** Emit `ImplementationFact` atoms (`track: reality`, `commitment_level: observed`) for what was actually built — an endpoint, field, or behavior. Link each fact to the `DecisionTarget` it implements and the `SolutionOption` it matches (`implements_option`). A fact is a signal, NOT policy: `validate_drift` flags a fact whose option ≠ the current decision, but only a human `DecisionEvent` (via `ppir-reflect`) turns a fact into intent. Do not author accepted Intent from implementation.

## Purpose

Extract Reality Track facts from backend MVP, OpenAPI, code, DB schemas, or runtime behavior, then compare reality against accepted Intent.

## Load when needed

- Read `references/ppir-core.md` before separating Reality from Intent.
- Read `references/review-packet-template.md` when recommending adoption proposals.
- Read `references/runtime-commands.md` for observe implementation command patterns.

## Inputs

- OpenAPI file
- code path or snippets
- API sample response
- DB schema
- implemented screen or MVP description
- target app/feature scope

## Outputs

- ImplementationFact
- AsBuiltAPI or AsBuiltBehavior
- SpecGap
- ImplementationGap
- DriftReport
- optional adoption Proposal for review

## Workflow

1. Register implementation evidence as Source.
2. Extract implementation facts.
3. Create AsBuiltContract artifacts where structure is clear.
4. Compare Reality against accepted Intent.
5. Classify each finding:
   - match: implementation agrees with intent
   - undocumented_as_built: implementation exists but no policy/spec exists
   - missing_implementation: policy exists but implementation is missing
   - conflict: implementation contradicts accepted policy
6. For undocumented as-built behavior, create SpecGap, not accepted policy.
7. For missing implementation, create ImplementationGap.
8. For conflict, create DriftReport and recommend `ppir-reflect` or future `ppir-change` workflow.
9. Only create Intent Proposal when the user explicitly asks to adopt as-built behavior as policy.

## Hard rule

ImplementationFact is not product policy. Backend MVP behavior must not become accepted Intent without an adoption decision and review-merge.

## Output format

```markdown
# Implementation Observation Report

## Reality facts
...

## Matches
...

## Spec gaps
...

## Implementation gaps
...

## Conflicts
...

## Recommended next workflow
...
```
