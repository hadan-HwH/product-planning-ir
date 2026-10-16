---
name: ppir-router
description: route product planning ir requests to the correct ppir workflow skill. use when the user asks how to process a legacy document, meeting decision, proposal merge, audit, publish request, ai context pack, explanation request, change impact, or backend mvp and openapi comparison.
---

# PPIR Router

## Purpose

Select the correct PPIR workflow and tell the user what inputs are required, what output will be produced, and which workflow should run next.

## Load when needed

- Read `references/router-matrix.md` when the request type is ambiguous.
- Read `references/ppir-core.md` when the request may cross Discovery, Intent, Reality, or Governance tracks.

## Routing workflow

1. Classify the input source.
2. Identify the track: Discovery, Intent, Reality, or Governance.
3. Select exactly one primary PPIR skill.
4. If another skill must follow, name it as the next step instead of executing it silently.
5. State the required inputs and expected outputs.
6. Preserve the write boundary: only `ppir-review-merge` may change accepted `/ir` atoms.

## Routing rules

- Existing human-written policy or screen-definition document → `ppir-legacy-migration`.
- Meeting, Slack, Notion note, or verbal decision → `ppir-adopt`.
- **Discussion where a decision was made and *changed over time* (adopted → deferred → reopened → replaced/rejected)** → `ppir-adopt --mode decisions` (extract the Decision Evolution Graph).
- **"What is the current decision on X?" / "How did decision X evolve?"** → `ppir-explain` (`--mode current | why-current | timeline`, reads the projection).
- Approved proposal merge → `ppir-review-merge`.
- Change impact or downstream propagation → `ppir-reflect`.
- Consistency, schema, references, or quality check → `ppir-audit`.
- Human-readable document generation → `ppir-publish`.
- AI task context generation → `ppir-context`.
- Why or source trace explanation → `ppir-explain`.
- Backend MVP, OpenAPI, code, DB, or runtime behavior comparison → `ppir-observe-impl`.

## Output format

```markdown
## Selected workflow
- Skill: `ppir-...`
- Reason: ...
- Track: Discovery | Intent | Reality | Governance

## Required inputs
- ...

## Expected outputs
- ...

## Next step
Run `...` after review or validation.
```

## Stop conditions

Stop and ask for scope if the request mixes more than two tracks and the primary objective is unclear.
