---
name: wf-phase1-spec
description: Phase 1 - the full, multi-session reviewed pipeline (1 -> 1.5 -> 2 -> 3). Use /wf-plan instead by default - it's a single live session that handles most tickets; reserve this for genuine outliers /wf-plan's own gate flags as too large for one sitting, or when you already know upfront a feature is architecturally novel or requirements are genuinely unclear.
argument-hint: [feature-id] [your description of what the feature should do]
allowed-tools: Read, Glob, Grep, Bash, Write, Task
model: sonnet
---

<!--
SYNC NOTE: this file shares its spec template with wf-plan and wf-phase1-spec-haiku. The
following must stay byte-identical across all three: the "Decisions Requiring Your Judgment"
section, the rest of the spec template body, the context.json base schema
(specPath/featureId/specDir/archiveDir/context block shape), and the token-ledger invocation
shape (--ledger/--ticket flags). If you change one, change all three or note explicitly why
this file deliberately diverges.

Model Selection Guide:
- Default to /wf-plan for most tickets — one live session, human reviews only the judgment-tier
  decisions, not the whole document. See its own SKILL.md for why.
- Use this command when you already know upfront a feature is architecturally novel,
  requirements are genuinely unclear, or /wf-plan's own Step 7.5 gate already told you the spec
  grew too large for one session.
- Use /wf-phase1-spec-haiku instead of either when the pattern is obvious before you start — a
  feature that clearly repeats an existing, already-implemented shape.

Note this command runs on Sonnet while /wf-plan runs on Opus — not a downgrade for the harder
case, a deliberate difference in how each gets its rigor. /wf-plan is one agent's solo judgment,
so it needs the stronger model directly. This command's rigor comes from the review panel that
follows (Phase 2's 2-4 agents cross-checking), not from the drafting model alone — matching
Claude Code's own `opusplan` alias pattern of Opus for planning/judgment, Sonnet for the
higher-volume mechanical work, here the multi-session pipeline machinery around the draft.
-->

# Phase 1: Write Feature Specification (full pipeline)

## Input

$ARGUMENTS

The arguments contain the feature ID and the user's description of what the feature should do — including any constraints, edge cases, or context. Any attached images (wireframes, diagrams, screenshots) are also part of the input. **Treat this as the primary definition of the feature.**

## Step 1: Read project config

Read `.claude/workflow/project-config.json`. Extract:
- `specDir` (default: `docs/specs`)
- `archiveDir` (default: `docs/specs/archive`)
- `roadmapFile` (default: `ROADMAP.md`)
- `worktreesEnabled` (default: `false`) — whether to use Claude Code's native worktree
  mechanism (`EnterWorktree`) for this feature. Location and base-branch behavior are Claude
  Code's own concerns (`.claude/worktrees/{name}/` by default; base branch via the project's
  `worktree.baseRef` setting) — this plugin does not configure them.

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`.

## Step 2: Read roadmap for supplementary context

Read `{roadmapFile}` and find the entry for the feature ID. Use any additional requirements listed there to supplement the user's description — but the user's description takes precedence.

## Step 3: Gather codebase context

Prefer parallel research over researching alone:

1. Use Glob to list `.claude/agents/*.md`. For each found, read its `name:`/`description:`
   frontmatter and reason about whether its focus area is relevant to this feature.
2. For each relevant agent, formulate one specific, answerable question this feature needs
   answered before drafting, and spawn all selected agents **in parallel** (single message,
   multiple Task calls).
3. If no agents are relevant or none exist, research directly instead:
   - Read `CLAUDE.md` to understand existing patterns and implemented features
   - Check for reference documentation in the repo (e.g., `docs/`, `references/`)
   - Review related existing specs in `{specDir}/` for format and patterns
   - Check existing code for partial implementations or related systems

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
change the design — set `hingesOnUnverifiedClaim: true` for Step 9a and list each such claim as
an item in the "Decisions Requiring Your Judgment" section (Step 7). Otherwise set it `false`.

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

## Decisions Requiring Your Judgment

The load-bearing calls in this spec — unverified assumptions (see Step 4.5) and any real
architectural tradeoff. This is the only section a human needs to read carefully; everything
below is detail. Keep this to what genuinely needs a human call — file lists and standard test
strategy don't belong here.

1. **{Decision title}** — {what's being decided, and why it's load-bearing: what changes in the
   design if this is wrong}. {Confirmed against source, or: Assumed — not directly verified}.

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
TU="{SKILL_DIR}/../../scripts/record-token-usage.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
[ -f "$TU" ] && python3 "$TU" --phase wf-phase1-spec --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}" || echo "token-usage: script not found, skipping (best-effort)"
```

### 9b: Create git worktree (if enabled)

If `worktreesEnabled` is `true` in project-config.json:

1. Compute feature ID in lowercase (e.g., `SF-14` → `sf-14`) as the worktree name.
2. Use the **`EnterWorktree`** tool to create/enter a worktree named `{feature-id-lowercase}` —
   this is Claude Code's native worktree mechanism (not a manual `git worktree add`): it creates
   the worktree at `.claude/worktrees/{feature-id-lowercase}/` by default, branches per the
   project's `worktree.baseRef` setting (`fresh` from the remote default branch, or `head` from
   local HEAD), and — critically — from this point on blocks any Edit/Write/Bash call that
   targets the main checkout instead of the worktree, which a manual `git worktree add` gives you
   no protection against. Gitignored files matching `.worktreeinclude` (if the project has one)
   are copied in automatically; no separate step needed.
3. Read back the actual worktree path and branch name the tool reports and add to context file:
   - `"worktreePath": "{path the tool reports}"`
   - `"branchName": "{branch the tool reports}"`
4. Display:
   ```
   Entered worktree: {worktreePath}
   Branch: {branchName}

   To resume work on this feature in a later session, start with:
     claude --worktree {feature-id-lowercase}
   (or ask Claude to "work in the {feature-id-lowercase} worktree" once a session is open).
   Cleanup is automatic — Claude Code removes a clean worktree on exit and periodically sweeps
   abandoned ones; you don't need to remove it by hand.
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
> verified (see "Decisions Requiring Your Judgment") — that's exactly the shape of the two
> costliest corrections on record for this workflow.
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
