---
name: ppir-publish
description: compile ppir ir atoms into human-readable policy documents, screen definitions, developer handoffs, qa test plans, pm briefings, notion mirrors, and generated views. use when the user asks to create or refresh readable documents from accepted ir.
---

# PPIR Publish

## Purpose

Generate role-specific human-readable outputs from accepted PPIR IR. Publishing must not create or change source-of-truth atoms.

## Load when needed

- Read `references/ppir-core.md` before checking authority boundaries.
- Read `references/runtime-commands.md` for compiler command patterns.

## Inputs

- target atom, feature, app, or platform
- role: pm, fe, be, qa, executive, notion
- format: markdown, notion, yaml, json when supported

## Outputs

- compiled policy doc
- compiled screen definition
- developer handoff
- QA test plan
- PM briefing
- change memo
- generated metadata

## Workflow

1. Resolve the target atom or scope.
2. Run audit or require latest passing audit.
3. Load required atom graph for the requested role.
4. Run the appropriate compiler.
5. Insert generated metadata: target, generated_at, compiler_version, source_graph_hash.
6. Write output under `/compiled`.
7. State that compiled output must not be manually edited.

## Role projections

- `fe`: screens, components, fields, databindings, actions, messages, validation, state behavior.
- `be`: API contracts, gaps, required endpoints, query params, error cases.
- `qa`: test cases, rules, exceptions, state transitions, messages.
- `pm`: decisions, rationale, changes, open questions, scope.
- `executive`: business impact, release scope, risks, unresolved choices.
- `notion`: readable mirror only, never source of truth.

## Stop conditions

Do not publish when:

- audit has blockers
- target is unresolved
- source graph is stale
- output would rely on unapproved Proposal content unless explicitly marked draft
