---
name: ppir-explain
description: explain why a ppir rule, field, screen, action, message, decision, or behavior exists by tracing atom, decision, rationale, source, and open question chains. use when the user asks for reasons or provenance.
---

# PPIR Explain

## Purpose

Answer why a PPIR artifact exists by tracing the authoritative graph. This skill is read-only.

## Load when needed

- Read `references/ppir-core.md` before distinguishing accepted intent, implementation reality, and discovery signals.
- Read `references/runtime-commands.md` for explain command patterns.

## Inputs

- natural language question
- atom ID
- screen, field, rule, decision, or feature name

## Outputs

- answer
- atom chain
- decision chain
- source chain
- unresolved OpenQuestions
- missing evidence notice when applicable

## Workflow

1. Resolve the question to candidate atoms.
2. Prefer accepted Intent atoms for policy explanations.
3. Follow links: atom → rule/field/action → decision/rationale → source.
4. Include superseded/deprecated chain when explaining changed behavior.
5. If the answer depends on Reality, state that it is implemented behavior, not necessarily policy.
6. If the answer depends on Discovery, state that it is a signal or candidate, not accepted policy.
7. If no support exists, say the graph has no evidence and recommend `/adopt` or `/change`.

## Decision targets — `--mode` (plan8)

For a `DecisionTarget`, "what is the decision now?" and "how did it change?" are different questions. Use `runtime/explain_decision.py`:

- `--mode current` — the authoritative option + summary ("지금 결정이 뭐야?")
- `--mode why-current` — summary + reason chain + what's inactive and why ("왜 지금 이게 결정이야?")
- `--mode timeline` — the ordered DecisionEvent stream ("여기까지 어떻게 바뀌었어?")

```
python runtime/explain_decision.py --mode why-current SHOP.TARGET.<slug>
```

Never present a superseded/deferred/signal-only option as current — the projection is computed by `reduce(events, governance_rules)`, not by latest timestamp. A newer Source with no accepted DecisionEvent is a signal, not the current decision.

## Answer rules

- Do not guess missing rationale.
- Do not convert implementation facts into policy.
- Do not cite raw restricted sources unless permitted.
- Mention OpenQuestions that affect the answer.

## Output format

```markdown
## Answer
...

## Evidence chain
- Atom: ...
- Decision: ...
- Source: ...

## Caveats
...

## Suggested next workflow
...
```
