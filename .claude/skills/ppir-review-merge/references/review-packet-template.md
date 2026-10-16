# PPIR Review Packet Template

Use this structure whenever a skill produces a Proposal that needs human review.

```yaml
kind: ReviewPacket
proposal_id: ""
source_summary: ""
track: intent | reality | discovery | governance
mode: legacy_migration | adopt | observe_impl | reflect
extracted_claims:
  - id: ""
    type: ""
    text: ""
    confidence: high | medium | low
proposed_changes:
  create: []
  update: []
  deprecate: []
  supersede: []
open_questions: []
conflicts: []
duplicates: []
affected_atoms: []
affected_compiled_views: []
validation:
  schema: pass | fail | not_run
  ids: pass | fail | not_run
  refs: pass | fail | not_run
  typed_refs: pass | fail | not_run
  lifecycle_matrix: pass | fail | not_run
human_decision_required:
  - item: ""
    reason: ""
```

Human review options:

- approve as-is
- approve with edits
- reject
- defer
- split proposal
- request more source evidence
- convert uncertain item to OpenQuestion
```
