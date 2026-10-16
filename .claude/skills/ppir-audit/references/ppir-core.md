# PPIR Core Contract

## Authority model

PPIR treats typed IR atoms as the only source of truth.

- `/sources` stores evidence, not law.
- `/claims` or ClaimSet artifacts store extracted statements, not law.
- `/ir/proposals` stores proposed changes, not law.
- accepted atoms under `/ir/intent`, `/ir/reality`, `/ir/discovery`, and `/ir/governance` are the authoritative product knowledge graph.
- `/compiled` stores generated views and must not be manually edited.

## Four tracks

Classify every artifact into exactly one primary track.

| Track | Use for | Never confuse with |
|---|---|---|
| Discovery | sales, customer, marketing, business signals, ideas, requirement candidates | accepted product policy |
| Intent | accepted product policy, screen definition, rules, fields, actions, messages, tests | implementation facts |
| Reality | backend mvp, openapi, code behavior, database facts, runtime observations | accepted product policy |
| Governance | decisions, change requests, rationale, constraints, tradeoffs, deferrals, rejections | screen spec itself |

## Non-negotiable rules

1. Do not directly edit `/compiled`.
2. Do not directly edit accepted `/ir` atoms except through an approved merge workflow.
3. All external input must enter as Source, then ClaimSet, then Proposal or Report.
4. Missing or uncertain information must become OpenQuestion, SpecGap, ImplementationGap, or ReviewNote.
5. A sales signal is not a requirement.
6. A requirement candidate is not an accepted rule.
7. An implementation fact is not product policy.
8. Rejected and deferred ideas must remain searchable.
9. Superseded or deprecated decisions must be preserved, not deleted.
10. AI work must use task-specific Context Packs, not the entire repository.

## Commit level guide

Use `commitment_level` to indicate the knowledge status.

- `observed`: directly seen in source, implementation, or customer input.
- `interpreted`: analyzed but not product-approved.
- `candidate`: possible requirement or policy.
- `proposed`: included in a Proposal.
- `accepted`: product-approved source of truth.
- `planned`: on roadmap.
- `implemented`: built in reality.
- `shipped`: released to users.
- `deferred`: postponed with review or reopen condition.
- `rejected`: rejected with reason.
- `superseded`: replaced by a newer atom or decision.
- `deprecated`: historically valid but no longer active.

## Write boundary

Only the review-merge workflow may change accepted `/ir` content.
Other PPIR skills should output Source, ClaimSet, Proposal, Report, ContextPack, or compiled view artifacts.

## Quality gates

Run or require these checks before merge or publish:

- schema validation
- id validation
- reference validation
- typed reference validation
- lifecycle matrix validation
- atomicity validation where available
- duplicate and conflict checks where available
- generated output staleness check before using `/compiled`

## Atomicity rules

- Rule: one normative assertion, one primary subject, one violation behavior.
- DataBinding: one screen field bound to one field/API source.
- Action: one user intent and one permission/API outcome path.
- Decision: one actual choice, with alternatives and consequences separated.
- Message: one user-facing message purpose.
- DerivedField: one target field and one derivation policy.
- Validator: one coherent validation ruleset, shared by fields when appropriate.
