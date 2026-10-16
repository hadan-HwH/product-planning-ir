# PPIR Skill Router Matrix

Use this matrix before choosing a workflow.

| User request | Route to skill | Typical output |
|---|---|---|
| migrate this old policy or screen definition | ppir-legacy-migration | Source, ClaimSet, LegacyExtractionMap, Proposal |
| reflect this meeting, slack, or verbal decision | ppir-adopt | Source, ClaimSet, Proposal, OpenQuestion |
| capture a decision that changed over time (adopt/defer/reopen/replace/reject) | ppir-adopt (mode: decisions) | DecisionTarget, SolutionOption, DecisionEvent |
| what is the current decision on X / how did it evolve | ppir-explain | current option, why-current, timeline (from projection) |
| approve and apply this proposal | ppir-review-merge | accepted IR changes, MergeReport, AuditReport |
| what breaks if this atom/API/rule changes | ppir-reflect | affected atoms, impact summary, Proposal |
| check consistency or validity | ppir-audit | AuditReport, ViolationList |
| generate screen definition, handoff, QA plan, PM brief | ppir-publish | compiled role-specific view |
| create AI context for a task | ppir-context | ContextPack, prompt fragments, output schema |
| explain why this exists | ppir-explain | atom chain, decision chain, source chain |
| compare backend mvp/openapi/code to policy | ppir-observe-impl | ImplementationFact, AsBuiltContract, GapReport |

Do not use discovery/prioritization/change/reconciliation workflows in this pack; those are phase 3 skills.
