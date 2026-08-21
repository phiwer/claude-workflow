---
name: wf-plan
description: Default entry point for spec creation - one live, human-in-the-loop session that collapses Phase 1, 1.5, 2, and 3 into one for tickets that fit. Escalates to /wf-phase1-spec (the full multi-session reviewed pipeline) for genuine outliers it can't responsibly handle in one sitting.
argument-hint: [feature-id] [your description of what the feature should do]
allowed-tools: Read, Glob, Grep, Bash, Write, Task, AskUserQuestion
model: opus
---

<!--
SYNC NOTE: this file shares its spec template with wf-phase1-spec and wf-phase1-spec-haiku.
The following must stay byte-identical across all three: the "Decisions Requiring Your
Judgment" section (renamed from "Verification Status"), the rest of the spec template body,
the context.json base schema (specPath/featureId/specDir/archiveDir/context block shape), and
the token-ledger invocation shape (--ledger/--ticket flags). If you change one, change all three
or note explicitly why this file deliberately diverges.

Model: Opus, deliberately — matches Claude Code's own `opusplan` alias pattern (Opus for
planning, Sonnet for execution). Planning is the low-volume side of a ticket (research this
session: ~15% of a ticket's tokens vs. ~70% for implementation), so defaulting it to Opus
doesn't reproduce the cost blowup that came from defaulting the *high-volume* implementation
phase to Opus — that's what /wf-phase4-implement-sonnet already fixed, and stays fixed. The
reasoning-quality case matters more here too: research found AI output that's subtly wrong
often "passes a casual read" rather than getting caught by human review, which undercuts the
assumption that Step 9's live human iteration is a safety net strong enough to justify a
cheaper model on the draft it's reviewing.
-->

# Plan a Feature (default entry point)

One live session: research → draft → self-review → your judgment on the few things that need it
→ one mechanical check → done. Replaces `/wf-phase1-spec` → `/wf-phase1-iterate` →
`/wf-phase2-review` → `/wf-phase3-consolidate` for tickets that fit in one sitting — which is
most of them. If a spec grows past what one session can responsibly hand you to review, this
skill says so directly and offers to split the ticket or escalate to the full pipeline, rather
than silently handing you a long document to read.

**Not for this**: if you already know the pattern isn't obvious, requirements are genuinely
unclear, or you expect this to be architecturally novel — use `/wf-phase1-spec` directly instead
of `/wf-plan`. This skill's own Step 7.5 will also catch it if a spec grows too large after the
fact, but starting with the right command saves the research/draft cost of finding that out.

## Input

$ARGUMENTS

The arguments contain the feature ID and the user's description of what the feature should do —
including any constraints, edge cases, or context. Any attached images (wireframes, diagrams,
screenshots) are also part of the input. **Treat this as the primary definition of the feature.**

## Instructions

### Step 0: Read Project Config

Read `.claude/workflow/project-config.json`. Extract:
- `specDir` (default: `docs/specs`)
- `archiveDir` (default: `docs/specs/archive`)
- `roadmapFile` (default: `ROADMAP.md`)
- `worktreesEnabled` (default: `false`) — whether to use Claude Code's native worktree
  mechanism (`EnterWorktree`) for this feature.

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`.

### Step 1: Read Roadmap for Supplementary Context

Read `{roadmapFile}` and find the entry for the feature ID. Use any additional requirements
listed there to supplement the user's description — but the user's description takes precedence.

### Step 2: Light Size Check (non-blocking)

Skim the user's description for signals this might not fit one session: does it name several
clearly unrelated systems, or does it read as "and also" a list of distinct sub-features rather
than one coherent change? If so, say so now and suggest splitting into separate `/wf-plan`
invocations — but **do not block**. This is a light, unreliable heuristic (specs can just as
easily balloon during research as start big) — the real gate is Step 7.5, after drafting.

### Step 3: Parallel Research Fan-Out

Instead of researching alone, identify relevant custom agents and spawn them concurrently:

1. Use Glob to list `.claude/agents/*.md`. For each found, read its `name:`/`description:`
   frontmatter.
2. Reason about which agents' focus areas are relevant to this feature (same relevance-matching
   approach as `/wf-phase2-review`'s agent selection).
3. For each relevant agent, formulate one **specific, answerable question** this feature needs
   answered before drafting — not "review this," but e.g. "does the existing X pattern
   generalize to Y, or are there edge cases that don't map over?"
4. Spawn all selected agents **in parallel** (single message, multiple Task calls), each with
   its specific question plus enough context to answer it (relevant file paths, the feature
   description).
5. If no agents are relevant or none exist, fall back to direct research yourself: read
   `CLAUDE.md`, check `docs/`/`references/` for relevant material, review related existing specs
   in `{specDir}/`, check existing code for partial implementations or related systems.

Collect all findings — from agents and/or direct research — before drafting.

### Step 4: Identify Unverified Assumptions

Separate what you've directly verified (read from source, ran, tested, cross-checked against
actual behavior) from what you're assuming or inferring (trusted documentation, inferred from a
similar-looking pattern, taken from the user's description without checking).

This matters because it's the single most expensive failure mode observed in this workflow:
the costliest corrections on record both traced to an unverified claim treated as established
fact and built on. Neither was hard to verify; the gap was not flagging that it hadn't been.

Every such claim that's load-bearing for the design — not "this is probably how it works" but
specifically the kind where being wrong changes the design — becomes an item in the "Decisions
Requiring Your Judgment" section (Step 7), alongside any genuine architectural tradeoff.

### Step 5: Create Spec Directory

Create: `{specDir}/{feature-id-lowercase}/`

### Step 6: Preserve and Transcribe Attached Design Assets

If the input includes attached images (wireframes, diagrams, screenshots, photos of hand-drawn
notes) — or the user points at such assets — capture them durably **before** drafting. Images
attached to a chat live only in the current session; anything not written into the repo is lost.

1. Create `{specDir}/{feature-dir}/design/`.
2. Save each attached image under a descriptive, stable name with consistent numbering.
3. Create `{specDir}/{feature-dir}/design/DESIGN_SOURCE.md`. For each image, write a full text
   transcription: every label, box, arrow, and annotation, plus the design decision it encodes.
4. Read each image carefully and extract all of its information before you draft.

Skip this step only when no design assets were provided.

### Step 7: Draft the Spec

Create `{specDir}/{feature-dir}/{FEATURE-ID}_{NAME}_SPEC.md`.

**Omit any section marked "(if applicable)" that is not relevant.**

```markdown
# {FEATURE-ID}: {Feature Name} Specification

**Status**: DRAFT
**Created**: {date}
**Complexity**: {Spike | Simple | Medium | Complex}

---

## Design Source (if design assets were attached)

The design assets that informed this spec are saved and transcribed under
[`design/DESIGN_SOURCE.md`](design/DESIGN_SOURCE.md). Every `Image #N` reference in this document
resolves there.

---

## Decisions Requiring Your Judgment

The load-bearing calls in this spec — unverified assumptions (Step 4) and any real architectural
tradeoff. This is the only section you need to read carefully; everything below is detail. Keep
this to what genuinely needs a human call — file lists and standard test strategy don't belong
here.

1. **{Decision title}** — {what's being decided, and why it's load-bearing: what changes in the
   design if this is wrong}. {Confirmed against source, or: Assumed — not directly verified}.

---

## Overview

{Brief description of what this feature does and why it matters}

---

## Application Interface (if applicable)

The public contracts this feature exposes to the rest of the system.

### {InterfaceName}

**Type**: {Interface / Abstract Class / Protocol / Service Contract}

| Method | Parameters | Returns | Description |
|--------|------------|---------|--------------|
| `methodName` | `param: Type` | `ReturnType` | What it does |

### {DTOName / Record / Value Object} (if crossing layer boundaries)

| Field | Type | Description |
|-------|------|--------------|
| `fieldName` | `Type` | What it represents |

---

## Components

### 1. {Component Name}

{Description of this component}

### 2. {Next Component}

{Continue for each component}

---

## Configuration / Constants (if applicable)

| Name | Value | Description |
|------|-------|--------------|
| `CONSTANT_NAME` | value | What this controls |

---

## Files

### Added
- `NewComponent.ext` - Core logic for {feature}

### Modified
- `ExistingFile.ext` - {What changes and why}

---

## HTTP Endpoints (if applicable)

| Method | Path | Description |
|--------|------|--------------|
| POST | `/api/{resource}/{action}` | {description} |

---

## Test Strategy

| Test | Focus | Estimated Cases |
|------|-------|-----------------|
| `{Feature}Test` | Core logic verification | 10-15 |
| `{Feature}EdgeCaseTest` | Boundary conditions (including anything raised in Decisions Requiring Your Judgment) | 8-12 |

---

## Key Implementation Notes

1. {Important architectural decision or constraint}

---

## Open Questions

- [ ] {Anything genuinely still open after Step 9 — should be empty or near-empty by Step 12}

---

**Last Updated**: {date}
```

### Step 7.5: The Real Gate

Count the items in "Decisions Requiring Your Judgment." **If it exceeds ~8 items, or the draft
overall reads unusually long/broad, stop here — before Step 9 asks the user to review anything.**

Tell the user directly: this has grown past what one live-reviewed session handles well. Use
AskUserQuestion:
- header: "Spec grew large"
- question: "This spec has {N} judgment-level decisions — more than one session should ask you
  to review live. How do you want to proceed?"
- option1: label="Split into smaller tickets", description="Recommend how to split; run
  /wf-plan separately on each piece"
- option2: label="Escalate to the full pipeline", description="Hand this draft to
  /wf-phase1-spec's reviewed multi-session pipeline instead — better fit for genuine complexity"
- option3: label="Proceed anyway", description="I'll review the full list live — continue in
  this session"

If "Split": suggest a concrete split based on the draft's own component/decision boundaries and
stop — do not draft further until the user re-invokes `/wf-plan` per split ticket.

If "Escalate": leave the draft in place (it's a reasonable starting point), tell the user to run
`/wf-phase1-spec` referencing this draft, and stop.

If "Proceed anyway": continue to Step 8. Never make this choice for the user.

If the item count is within range, continue to Step 8 without comment.

### Step 8: Free Self-Review (no subagent)

Before spending anything more — the user's attention or a subagent call — review your own draft
directly, the same way you'd want a careful engineer to:

1. **Coverage**: for each requirement/constraint in the user's original description, can you
   point to a section that addresses it? List any gap.
2. **Placeholder scan**: search your own draft for "TBD", "TODO", "add appropriate error
   handling", "handle edge cases" (without saying how), "similar to above" (without repeating
   the content), or any section that describes what to do without saying how.
3. **Consistency**: do names, types, and method signatures match across sections — the same
   method name in Application Interface as in Components as in Files?

Fix what you find directly in the draft. No need to re-review after fixing — just fix and move
on. This step is free (same session, no extra spawn) and exists to catch the easy issues before
Step 9 spends the user's time or Step 10 spends a subagent call on them.

### Step 9: Live Human Iteration (capped at 2 rounds)

Present **only** the "Decisions Requiring Your Judgment" section — not the whole document — to
the user, and work through it via AskUserQuestion or direct conversation. As each item is
resolved, **update the spec inline immediately**, writing both the resolution and its rationale
into the section — this is what lets Phase 4 later recover "why," the same job Phase 3's
consolidation document does in the full pipeline. Do not just track the answer in conversation.

If the user's answers surface new open questions, present those too, in the same session —
that's round 2. **Cap at 2 rounds total.** If genuine open items remain after round 2, stop and
tell the user directly rather than looping further — itself a signal this ticket may need
`/wf-phase1-spec`'s fuller pipeline. Offer that escalation explicitly rather than grinding a
third round.

### Step 10: One Narrow Mechanical-Completeness Check

Spawn **one** fresh subagent (general-purpose, via Task) — not a panel, not open-ended feedback.
Its job is completeness and consistency, not judgment:

> You are reviewing a feature specification for completeness and consistency — not offering
> design feedback or opinions. Read the spec at {spec path}.
>
> Check specifically:
> - Does every item in "Decisions Requiring Your Judgment" actually get reflected somewhere in
>   the rest of the spec (Files, Test Strategy, Components)?
> - Does the Files section match what the Components/Application Interface sections describe —
>   no component without a file, no file without a described purpose?
> - Is anything internally inconsistent — a name, type, or signature that differs between
>   sections?
>
> **Only flag issues that would cause real problems during implementation.** An implementer
> getting stuck or building the wrong thing is an issue. Minor wording or stylistic preferences
> are not — approve unless there are serious gaps.
>
> Output: `CLEAN` (nothing found), or a numbered list of specific gaps, each naming the section
> and what's missing/inconsistent. Do not rewrite the spec — report only.

Fix every gap raised, directly in the spec.

**Cap at 2 passes.** If the first pass finds gaps, fix them and re-spawn once, scoped to what
changed (Step 11) rather than the whole spec again. If pass 2 isn't clean, stop and report the
residual items to the user rather than looping further.

### Step 11: Scoped Re-Check

If Step 10 needs a second pass, scope it to the sections that changed since pass 1 — not a full
re-read of the spec. Same principle as this plugin's other review loops: re-reviewing what
already passed wastes the pass without adding signal.

### Step 12: Finalize

1. Update Status to `READY FOR IMPLEMENTATION` and the "Last Updated" date. No separate DRAFT
   period — consolidation already happened live in Steps 9-11.
2. Display output summary: spec file path, each component with a 1-2 sentence description,
   files being added/modified, the resolved Decisions Requiring Your Judgment (decision +
   rationale), any HTTP endpoints.
3. Write `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:
   ```json
   {
     "specPath": "{full spec file path}",
     "featureId": "{FEATURE-ID}",
     "lastPhase": "wf-plan",
     "specDir": "{specDir}",
     "archiveDir": "{archiveDir}",
     "context": {
       "complexityTier": "{Spike | Simple | Medium | Complex}",
       "judgmentItemCount": {count},
       "selfReviewFindings": {count fixed in Step 8, or 0},
       "mechanicalCheckPasses": {1 or 2},
       "filesAffected": {count of files added + modified},
       "recommendedNextPhase": "wf-phase4-implement-sonnet"
     }
   }
   ```
4. If `worktreesEnabled` is `true`: use the **`EnterWorktree`** tool to create/enter a worktree
   named `{feature-id-lowercase}` (same as `/wf-phase1-spec`'s Step 9b) — creates it at
   `.claude/worktrees/{feature-id-lowercase}/`, blocks Edit/Write/Bash against the main checkout
   from this point on, auto-copies `.worktreeinclude`-matched gitignored files. Read back the
   actual path/branch and add `worktreePath`/`branchName` to the context file. Display the path,
   branch, and resume command (`claude --worktree {feature-id-lowercase}`) — cleanup is
   automatic, no manual removal needed.
5. Record token usage as **separate sub-phase entries**, so the ledger can later show whether
   the parallel-research fan-out is earning its cost:
   ```bash
   TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
   if [ -n "$TU" ]; then
     python3 "$TU" --phase wf-plan-research --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}"
     python3 "$TU" --phase wf-plan-draft --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}"
     python3 "$TU" --phase wf-plan-check --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}"
   else
     echo "token-usage: script not found, skipping (best-effort)"
   fi
   ```
   (Each call sums the same session transcript — the sub-phase split is for ledger readability,
   not separate measurement; treat the three rows as one phase's total when reading the ledger.)
6. Display:
   > Plan complete. Context saved.
   >
   > **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will
   > auto-load. Phase 1.5/2/3 are skipped for this ticket — consolidation already happened live.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new
session.
