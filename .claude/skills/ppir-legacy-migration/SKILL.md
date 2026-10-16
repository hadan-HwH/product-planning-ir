---
name: ppir-legacy-migration
description: convert existing human-written policy documents, screen definitions, markdown files, notion exports, or legacy product specs into ppir source, claimset, legacy extraction map, proposal, and review packet artifacts without directly creating accepted ir atoms.
---

# PPIR Legacy Migration

## Purpose

Convert legacy human-readable policy or screen-definition documents into PPIR migration artifacts. The skill must not treat the legacy document as current law by itself.

## Load when needed

- Read `references/ppir-core.md` before classifying claims.
- Read `references/review-packet-template.md` before producing review output.

## Inputs

Required:

- legacy document path or pasted content
- target platform/app/feature if known

Optional:

- migration scope
- known existing atom IDs
- authoritative version or date

## Outputs

Must produce:

- Source atom
- ClaimSet
- LegacyExtractionMap
- Proposal with typed atom changes
- ReviewPacket

Must not produce:

- accepted `/ir` atoms
- direct edits to the legacy source
- compiled views before merge

## Workflow

1. Register the document as a Source.
2. Segment the document by headings, tables, bullets, diagrams, examples, and change history.
3. Extract atomic claims.
4. Classify claims into candidate kinds: Feature, Screen, Component, Entity, Field, DataBinding, Action, Rule, Decision, Message, Validator, DerivedField, Relation, OpenQuestion, TestCase, Example, Supersession.
5. Separate current law, historical law, explanations, examples, deprecated content, and unknowns.
6. Perform semantic identity linking before creating new IDs.
7. Create a LegacyExtractionMap from source ranges to proposed atoms.
8. Create a Proposal with create/update/deprecate/supersede operations.
9. Run proposal-level validation if runtime scripts exist.
10. Output a ReviewPacket.

## Classification rules

- Table column definitions usually become DataBinding plus Field references.
- User input constraints become Validator or Rule, not prose.
- Computed values become DerivedField or MappingRule.
- Repeated actions become ActionPattern when the same behavior appears across screens.
- **A document's change history (v1.0 → v1.1, "was X, now Y") becomes a Decision Evolution Graph** — `DecisionTarget` + `SolutionOption`s + `DecisionEvent`s (adopt/replace/reject/…), not old `Decision`/`Supersession` (deprecated, plan9). Route this extraction through `ppir-adopt --mode decisions`.
- A single past-vs-current change without a documented evolution still becomes a `replace_option` event on its target.
- Example rows become Example, not accepted policy.
- Missing API details become OpenQuestion, APIGap, or ReviewNote.

## Failure conditions

Stop for review if:

- current law and historical law conflict
- the same screen/rule appears in multiple sources
- API support is assumed but not documented
- source authority is unclear
- a MUST/MUST_NOT rule lacks source or decision evidence
