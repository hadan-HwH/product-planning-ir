---
name: ppir-adopt
description: adopt meeting notes, slack threads, notion notes, verbal decisions, conversations, or product discussions into ppir artifacts. `decisions` mode extracts the Decision Evolution Graph (DecisionTarget/SolutionOption/DecisionEvent); default mode extracts source/claimset/proposal/rule. use when new decisions or rules arise outside the ir repository.
---

# PPIR Adopt

## Purpose

Intake external discussion or decisions and convert them into PPIR candidate changes. Use this for meeting notes, Slack threads, Notion notes, or verbal decisions.

## Load when needed

- Read `references/ppir-core.md` before assigning track or commitment level.
- Read `references/review-packet-template.md` before outputting Proposal review material.

## Modes

Use `propose` by default.

- `extract-only`: create Source and ClaimSet only.
- `propose`: create Source, ClaimSet, typed Proposal changes, OpenQuestions, and ReviewPacket.
- `decisions`: extract the **Decision Evolution Graph** (DecisionTarget/SolutionOption/DecisionEvent/DecisionRelation). Use when the input is a discussion where things were **decided and changed over time** (adopted, deferred, reopened, replaced, rejected). See "Decision graph extraction" below.

---

## Decision graph extraction (mode: `decisions`)

Goal: turn a conversation/thread into the **governance decision graph** so the current authoritative decision is *computed*, not read off the latest message. This is the model of the decision-graph design spec (v3.0.0). Do NOT emit old `Decision`/`Supersession` (deprecated, plan9).

### What to produce (per decided question)
- **`DecisionTarget`** — the question being resolved. `statement` + `current_resolution_policy: single|multiple_allowed` + `source_refs`. NOT the answer — the question.
- **`SolutionOption`** — each competing answer. **`status: proposed`, `commitment_level: candidate`** — never author the outcome; the projection computes accepted/rejected/superseded/cancelled.
- **`DecisionEvent`** — each move on the target, in time order, typed (below). `decision_time` (from when it was said), `authority_level`, `selects`/`replaces`/`affects`, `reason` (the "왜"), `source_refs`.
- **`DecisionRelation`** — optional, for explicit cross-option/graph queries.
- **`Source`** — each turn/doc that drove a move (`source_type: meeting|verbal|slack|notion`). Events cite it. A later Source with no accepted event stays a **signal**, not the decision.

### Granularity — what counts as ONE DecisionTarget
- A target is a **question that was resolved *and could change*** — it has ≥1 adopted option, ideally ≥1 reversal (defer/reopen/replace/reject).
- **Too coarse** = a whole theme ("the architecture"). **Too fine** = a one-off fact with no alternative and no change — that is a Rule/Claim, adopt it via `propose` mode, not here.
- Litmus: *"Was there a competing option, or a reversal over time?"* Yes → DecisionTarget. No → not a decision-evolution target.
- One conversation usually yields **many** targets. Extract each distinct question — do not collapse into one summary. (Under-extraction is the common failure: a 3-hour thread is 15–30 targets, not 5.)

### Conversation move → `event_type`
adopt("만들기로/채택") · defer("보류/나중에") · reopen_target("다시 보자/재검토") · replace_option("A 말고 B로") · reject_option("기각/안 함") · propose_option("후보로 제안") · cancel_target("취소/폐기") · narrow_scope/expand_scope("범위 축소/확대") · confirm_current("재확인") · refine_option/amend_decision("정의 다듬기") · split_target/merge_target("쪼갬/합침").

### Authoring rules
- IDs stay within the product's DOMAIN (`{DOMAIN}.{TOKEN}.{slug}`) — cross-product refs are blocked by `validate_product_isolation`. New product = new DOMAIN.
- Never hand-author an option's outcome; run `compile_decision_projection` and let the projection + `compile_context_pack` express current/inactive/forbidden.
- Output as a Proposal for PM approval (or, when authoring directly, place under `ir/{product}/{feature}/{target,options,events,...}/` and run audit + compile).

### Self-check before returning
- Did I extract *every* distinct decided question, or only the headline ones? (Re-scan for smaller reversals.)
- Is each option `candidate` (outcome left to the projection)?
- Does each event cite the source turn that drove it, with a `reason`?

## Inputs

- text, link, or file containing the discussion
- source type: meeting, slack, notion, verbal, external_doc
- target scope if known

## Outputs

- Source
- ClaimSet
- Proposal
- OpenQuestion when uncertain
- ReviewPacket

## Workflow

1. Save the input as Source.
2. Extract claims.
3. Classify each claim as decision_candidate, rule_candidate, exception_candidate, message_candidate, api_candidate, screen_candidate, rationale, risk, open_question, or non_goal.
4. Link claims to existing atoms when possible.
5. Convert high-confidence claims into Proposal changes.
6. Convert medium-confidence claims into Proposal changes with ReviewNotes.
7. Convert low-confidence or missing-info claims into OpenQuestions.
8. Validate Proposal structure when runtime exists.
9. Output ReviewPacket.

## Adoption rules

- A discussion is not law until a Proposal is approved and merged.
- Exploratory ideas remain ClaimSet or OpenQuestion.
- A MUST/MUST_NOT Rule requires source or decision evidence.
- Do not use backend implementation as policy evidence here; route implementation inputs to `ppir-observe-impl`.
- Do not process sales or customer signals here; route them to phase 3 discovery skills when available.

## Output requirement

Do not create an empty Proposal in `propose` mode. If no safe atom proposal can be made, return `extract-only` output and explain the blocker.
