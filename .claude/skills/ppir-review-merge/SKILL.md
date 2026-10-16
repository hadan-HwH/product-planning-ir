---
name: ppir-review-merge
description: review and merge approved ppir proposals into accepted ir using staging, validation, graph rebuild, audit, and impacted compiled view refresh. use only when the user explicitly approves a proposal or asks to merge approved changes.
---

# PPIR Review Merge

## Purpose

Apply approved PPIR Proposal changes to accepted `/ir` through a staged, auditable merge. This is the only skill in this pack allowed to modify accepted IR content.

## Load when needed

- Read `references/ppir-core.md` before enforcing the write boundary.
- Read `references/review-packet-template.md` when the Proposal lacks review metadata.

## Inputs

- Proposal ID or Proposal file path
- explicit approval decision
- reviewer identity or role when available

## Outputs

- accepted IR changes
- MergeReport
- updated graph indexes
- AuditReport
- refreshed impacted compiled views when compilers exist

## Workflow

1. Confirm the Proposal is approved. Prefer `workflow_state: approved` over overloading `status`.
2. Create a staging copy of the current IR.
3. Apply Proposal operations to staging.
4. Run schema, id, ref, typed_ref, lifecycle, and atomicity validation on staging.
5. If validation fails, do not modify accepted IR. Return MergeReport with failures.
6. If validation passes, apply changes to accepted IR.
7. Preserve deprecated or superseded atoms; do not delete them.
8. Rebuild graph indexes.
9. Run audit.
10. Regenerate impacted compiled views if compilers are available.
11. Move Proposal to merged state.

## Merge policy

- pending Proposal merge is forbidden.
- audit fail merge is forbidden.
- accepted atoms must not be physically deleted.
- every breaking change requires ImpactAnalysis or ReviewNote.
- every supersession must identify the replaced atom or decision.

## Output format

Return:

- what changed
- validation result
- graph rebuild result
- impacted compiled views
- unresolved OpenQuestions
- next recommended workflow
