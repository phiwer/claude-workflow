---
name: wf-phase1-spec
description: Phase 1 - Create an initial feature specification. Pass the feature ID and your description as arguments (with any images attached). Explores the codebase and generates a structured spec. Use /wf-phase1-spec-haiku instead for a feature that clearly repeats an existing pattern.
argument-hint: [feature-id] [your description of what the feature should do]
allowed-tools: Read, Glob, Grep, Bash, Write
model: sonnet
---

<!--
Model Selection Guide:
- Use Sonnet (this command, default) for novel features or unclear requirements
- Use /wf-phase1-spec-haiku instead when the pattern is obvious before you start — a feature
  that clearly repeats an existing, already-implemented shape. Any gaps get caught by Phase 2
  agents anyway, but that's expensive insurance to lean on routinely — the Haiku variant exists
  for the genuinely-obvious case, not as a default.
-->

# Phase 1: Write Feature Specification

## Input

$ARGUMENTS

The arguments contain the feature ID and the user's description of what the feature should do — including any constraints, edge cases, or context. Any attached images (wireframes, diagrams, screenshots) are also part of the input. **Treat this as the primary definition of the feature.**

## Step 1: Read project config

Read `.claude/workflow/project-config.json`. Extract:
- `specDir` (default: `docs/specs`)
- `archiveDir` (default: `docs/specs/archive`)
- `roadmapFile` (default: `ROADMAP.md`)
- `worktreeBase` (default: `null`)

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`.

## Step 2: Read roadmap for supplementary context

Read `{roadmapFile}` and find the entry for the feature ID. Use any additional requirements listed there to supplement the user's description — but the user's description takes precedence.

## Step 3: Gather codebase context

Using the user's description as your guide:

1. Read `CLAUDE.md` to understand existing patterns and implemented features
2. Check for reference documentation in the repo (e.g., `docs/`, `references/`)
3. Review related existing specs in `{specDir}/` for format and patterns
4. Check existing code for partial implementations or related systems

## Step 4: Analyze dependencies

Identify:
- Which existing systems this feature integrates with
- Required modifications to existing files
- New files/classes needed
- Database schema changes (if any)
- Configuration/constants to add

## Step 4.5: Identify Unverified Assumptions

Before drafting, separate what you've directly verified (read from source, ran, tested, cross-
checked against actual behavior) from what you're assuming or inferring (trusted documentation,
inferred from a similar-looking pattern, taken from the user's description without checking).

This matters because it's the single most expensive failure mode observed in this workflow so
far: two of the costliest corrections on record both traced to an unverified claim that got
treated as established fact and built on — one inverted a measurement-based conclusion, the
other asserted two operations were "the same" without checking. Neither was hard to verify; the
gap was not flagging that it hadn't been.

If the spec's design hinges on any claim you have NOT directly verified against source — not
"this is probably how it works" but specifically the load-bearing kind, where being wrong would
change the design — set `hingesOnUnverifiedClaim: true` for Step 9a and list each such claim
under a "Verification Status" section in the spec (Step 7). Otherwise set it `false`.

## Step 5: Create spec directory

Create: `{specDir}/{feature-id-lowercase}/`
(e.g., `{specDir}/sf14/` for SF-14)

## Step 6: Preserve and transcribe attached design assets

If the input includes attached images (wireframes, diagrams, screenshots, photos of hand-drawn
notes) — or the user points at such assets — capture them durably **before** drafting. Images
attached to a chat live only in the current session: every later session (Phase 1 iterate, Phase 2
review, Phase 4 implementation) starts fresh without them, so anything not written into the repo is
lost, and the reviewers end up working from prose alone.

1. Create `{specDir}/{feature-dir}/design/`.
2. Save each attached image into that folder under a descriptive, stable name with consistent
   numbering you can cite from the spec (e.g. `image-1-{short-topic}.ext`, `image-2-{short-topic}.ext`).
3. Create `{specDir}/{feature-dir}/design/DESIGN_SOURCE.md`. For each image, write a full text
   transcription: every label, box, arrow, and annotation, **plus the design decision it encodes**.
   Include a cross-reference table mapping each file to how the spec cites it (e.g. `Image #N`) — and
   note that the asset's own internal numbering may differ from the citation order.
4. Read each image carefully and extract **all** of its information before you draft — never draft
   from a partial reading. The transcription, not the image, is what every later phase reads.

Skip this step only when no design assets were provided.

## Step 7: Generate spec file

Create `{specDir}/{feature-dir}/{FEATURE-ID}_{NAME}_SPEC.md`.

**Omit any section marked "(if applicable)" that is not relevant — do not include the header with placeholder content.**

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

## Complexity Tier

**Tier**: {Spike | Simple | Medium | Complex}
**Justification**: {Why this tier - be specific}

| Tier | Criteria | Recommended Phases |
|------|----------|-------------------|
| Spike | Exploratory/de-risking work — the branch name, ticket, or user's description says "spike", "poc", "explore", or the goal is to de-risk an unknown rather than ship production-grade code | 1 → 4 (sonnet) → 5 |
| Simple | Single pattern, <100 LOC, follows existing templates | 1 → 4 → 5 |
| Medium | 2-5 files, follows existing patterns, some integration | 1 → 2 (3 agents) → 3 → 4 → 5 |
| Complex | New patterns, architecture, 5+ files, novel mechanics | 1 → (1.5) → 2 → 3 → 4 → 5 → 6 |

**Spike is not "Complex work done carelessly."** It's a distinct signal — the goal is answering
a question or de-risking an unknown, not shipping a fully reviewed production feature — so it
skips the design-review and consolidation ceremony (Phases 2/3) even when the code itself would
otherwise look architecturally novel enough to qualify as Complex. If mid-implementation the
spike's outcome turns into "ship this for real," treat that as scope change: stop, and re-run
`/wf-phase1-spec` (or hand-consolidate) at the appropriate tier for the production version rather
than retrofitting review onto the spike's spec after the fact.

---

## Verification Status (only if any unverified claim is load-bearing — omit otherwise)

**Confirmed** (directly verified against source/tests/actual behavior):
- {claim} — {how it was verified}

**Assumed** (not directly verified — treat as risk if wrong):
- {claim} — {why it's load-bearing; what would change if it's wrong}

---

## Overview

{Brief description of what this feature does and why it matters}

---

## Application Interface (if applicable)

The public contracts this feature exposes to the rest of the system. Define these
before components — the interface is the contract; components are the internals.

### {InterfaceName}

**Type**: {Interface / Abstract Class / Protocol / Service Contract}

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `methodName` | `param: Type` | `ReturnType` | What it does |

### {DTOName / Record / Value Object} (if crossing layer boundaries)

| Field | Type | Description |
|-------|------|-------------|
| `fieldName` | `Type` | What it represents |

---

## Components

### 1. {Component Name}

{Description of this component}

**Formula / Logic** (if applicable):
```
result = baseValue × modifier × efficiency
```

Where:
- `baseValue` = description
- `modifier` = description

### 2. {Next Component}

{Continue for each component}

---

## Configuration / Constants (if applicable)

| Name | Value | Description |
|------|-------|-------------|
| `CONSTANT_NAME` | value | What this controls |

---

## Architecture Integration (if applicable)

{Where this fits in the system — e.g., processing order, event pipeline, request lifecycle}

---

## Files

### Added
- `NewComponent.ext` - Core logic for {feature}
- `NewResult.ext` - Result type for {operation}

### Modified
- `ExistingFile.ext` - {What changes and why}

---

## HTTP Endpoints (if applicable)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/{resource}/{action}` | {description} |

---

## Test Strategy

| Test | Focus | Estimated Cases |
|------|-------|-----------------|
| `{Feature}Test` | Core logic verification | 10-15 |
| `{Feature}IntegrationTest` | End-to-end integration | 5-8 |
| `{Feature}EdgeCaseTest` | Boundary conditions | 8-12 |

---

## Key Implementation Notes

1. {Important architectural decision or constraint}
2. {Performance consideration}
3. {Integration note with existing systems}

---

## Related Specifications

- [{Related Feature}]({path}) - {How it relates}

---

## Open Questions

- [ ] {Question needing resolution before implementation}
- [ ] {Another open question}

---

**Last Updated**: {date}
```

## Step 8: Output summary

Display:
1. Spec file path
2. Each component with a 1-2 sentence description
3. Configuration/constants being added
4. Files being added/modified
5. Each open question
6. Any HTTP endpoints

## Step 9: Write context file and prompt for next step

### 9a: Write context file

Write `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "worktreeBase": "{worktreeBase or null}",
  "context": {
    "complexityTier": "{Spike | Simple | Medium | Complex}",
    "complexityJustification": "{brief reason}",
    "hingesOnUnverifiedClaim": {true | false},
    "components": ["{component names}"],
    "openQuestions": {count},
    "properties": ["{constants/config names}"],
    "filesAffected": {count of files added + modified},
    "recommendedNextPhase": "{wf-phase1-iterate | wf-phase2-review | wf-phase4-implement-sonnet}"
  }
}
```

#### Record token usage

Record this phase's token usage into the context (Phase 1 has no report doc, so no `--artifact`; it surfaces in the Phase 6 grand total):

```bash
TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
[ -n "$TU" ] && python3 "$TU" --phase wf-phase1-spec --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}" || echo "token-usage: script not found, skipping (best-effort)"
```

### 9b: Create git worktree (if configured)

If `worktreeBase` is non-null:

1. Derive project dir name from last path component of `GIT_MAIN_ROOT`
2. Compute feature ID in lowercase (e.g., `SF-14` → `sf-14`)
3. Run:
   ```bash
   git worktree add "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}" -b "feature/{feature-id-lowercase}"
   ```
4. Add to context file:
   - `"worktreePath": "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}"`
   - `"branchName": "feature/{feature-id-lowercase}"`
5. Display:
   ```
   Git worktree created: {worktreePath}
   Branch: {branchName}
   Implementation phases will run from this directory.
   ```

### 9c: Next steps

Display based on `complexityTier`:

**Spike:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.
> This tier skips design review/consolidation by design (exploratory work) — rely on PMD/tests
> as the gate. If the spike turns into shipped production work, treat that as a scope change
> rather than retrofitting review after the fact.

**Simple:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.

**Medium:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase2-review` — context will auto-load.
> (For an early sanity-check first, run `/wf-phase1-iterate` instead.)

**Complex, with `hingesOnUnverifiedClaim: true`:**
> Phase 1 complete. Context saved. This spec's design hinges on a claim you haven't directly
> verified (see "Verification Status") — that's exactly the shape of the two costliest
> corrections on record for this workflow.
>
> **Next**: Start a new session and run `/wf-phase1-iterate` for a cheap early check before
> committing Phase 2's larger review to a spec that might be built on a wrong premise. After
> iterate, start another new session and run `/wf-phase2-review`.

**Complex, with `hingesOnUnverifiedClaim: false`:**
> Phase 1 complete. Context saved. This spec doesn't hinge on an unverified claim, so
> `/wf-phase1-iterate` is unlikely to earn its cost here — a comparable Complex-tier feature
> skipped it and Phase 2 alone still caught issues just fine on its own.
>
> **Next**: Start a new session and run `/wf-phase2-review` directly — context will auto-load.
> (Run `/wf-phase1-iterate` first anyway if you'd still like an early sanity check.)

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
