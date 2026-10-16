---
name: ppir-context
description: generate task-specific ai context packs from ppir atom graphs. use when ai needs to update screens, policies, tests, handoffs, drift analysis, explanations, or implementation review without reading the entire repository.
---

# PPIR Context

## Purpose

Create AI Context Packs for bounded PPIR tasks. AI should receive the minimum authoritative graph needed for the task, not the entire repository.

## Load when needed

- Read `references/ppir-core.md` before filtering tracks and authority.
- Read `references/runtime-commands.md` for context command patterns.

## Inputs

- target atom or scope
- task type
- optional role or output schema

## Task types

- legacy_migration
- screen_update
- policy_update
- api_gap_analysis
- qa_test_generation
- developer_handoff
- change_impact_analysis
- as_built_to_policy_review
- decision_explanation

## Outputs

- ContextPack
- prompt fragments
- output schema reference
- excluded items and why

## Workflow

1. Resolve target atom.
2. Determine task type.
3. Include required atom kinds for that task.
4. Expand dependencies and selected reverse dependencies.
5. Exclude rejected, deprecated, and superseded atoms unless needed for explanation.
6. Include OpenQuestions and blockers.
7. Include source summaries, not raw restricted sources.
8. Attach prompt fragments and output schema.
9. Save ContextPack under `/compiled/ai-context` when runtime exists.

## Decision targets — use the computed authority (plan9)

When the task concerns a `DecisionTarget`, do NOT assemble context by retrieving related passages (that is the chunk-RAG failure mode). Instead use the compiled decision graph:

- Run `compile_decision_projection` → `CurrentDecisionProjection` (the authoritative current option, computed by `reduce(events, governance_rules)`, not latest timestamp).
- Run `compile_context_pack` → the ContextPack, which already fences inactive options with `must_not_use_as_current` and emits `forbidden_inferences` ("do not present option X as the current decision").
- Ground the AI in that pack. A newer Source with no accepted `DecisionEvent` is a signal, never the current decision.

## Safety rules

- Do not include the whole repository.
- Do not include raw restricted source text by default.
- Do not allow the AI to infer missing API support.
- Do not hide OpenQuestions.
- Do not include unapproved Proposal content unless the task is explicitly proposal review.
