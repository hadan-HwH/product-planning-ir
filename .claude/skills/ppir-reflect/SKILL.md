---
name: ppir-reflect
description: analyze downstream impact of changed ppir atoms such as rules, decisions, fields, api contracts, screens, or proposals. use when the user asks what is affected or wants changes propagated without directly editing accepted ir.
---

# PPIR Reflect

> **Decision-graph aware (plan9 B).** A `validate_drift` warning (an `ImplementationFact` whose `implements_option` ≠ the target's current decision) is the primary reflect trigger. Resolve drift by proposing a **`DecisionEvent`** (e.g. `propose_option` to adopt as-built, or `confirm_current` to keep policy and flag the build as non-compliant) — never by silently rewriting Intent. "구현된 것 ≠ 정책": the human decides which side moves.

## Purpose

Find the downstream impact of a changed atom and create a Proposal for affected updates. This skill does not directly modify accepted IR.

## Load when needed

- Read `references/ppir-core.md` for write boundary and track separation.
- Read `references/review-packet-template.md` before outputting Proposal review material.
- Read `references/runtime-commands.md` for graph and reflect command patterns.

## Inputs

- atom ID, Decision ID, APIContract ID, Field ID, Screen ID, or merged Proposal ID
- description of the change when not already encoded

## Outputs

- AffectedAtomList
- ImpactSummary
- Proposal for propagated changes
- OpenQuestions or ReviewNotes for judgment-required areas

## Workflow

1. Resolve the changed atom.
2. Load reverse dependencies from graph index.
3. Classify change type: additive, breaking, semantic, naming, deprecation, or implementation drift.
4. Identify affected screens, databindings, actions, messages, tests, compiled views, and context packs.
5. Separate mechanical updates from judgment-required updates.
6. Generate a Proposal for mechanical updates.
7. Generate OpenQuestions or ReviewNotes for judgment-required updates.
8. Do not apply changes directly.

## Special cases

- APIContract change: check DataBinding response paths, query params, actions, and BE/FE handoffs.
- Rule change: check screens, actions, validators, messages, tests, and context packs.
- Decision change: check justified rules, supersessions, policy docs, and explain chains.
- Field change: check DataBindings, validators, messages, API contracts, and test cases.

## Stop conditions

Stop and require human judgment if:

- policy and implementation conflict
- multiple downstream interpretations are valid
- the change would supersede an accepted decision
- the affected atom identity is ambiguous
