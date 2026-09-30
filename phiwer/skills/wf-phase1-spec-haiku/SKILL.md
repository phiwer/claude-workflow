---
name: wf-phase1-spec-haiku
description: Create an initial feature specification for a template-following feature where the pattern is obvious. Use /wf-plan for most other tickets, or /wf-phase1-spec (Sonnet) for novel features or unclear requirements.
argument-hint: [feature-id] [your description of what the feature should do]
allowed-tools: Read, Glob, Grep, Bash, Write
model: haiku
---

<!--
SYNC NOTE: this file shares its spec template with wf-plan and wf-phase1-spec. The "Decisions
Requiring Your Judgment" section name and the context.json base schema must stay consistent
across all three. If you change one, change all three or note explicitly why this file
deliberately diverges.

This is the deliberate, explicit opt-in for template-following work — not a default. Use
/wf-plan for most tickets, or /wf-phase1-spec (Sonnet) when requirements are genuinely
unclear — unless you already know, before starting, that this feature is a clear repeat of an
existing pattern. Any gaps get caught downstream anyway, but that's expensive insurance to lean
on routinely — the judgment call of "is this actually template-following" is yours to make
before invoking this command, not something this skill infers from the description.
-->

# Phase 1: Write Feature Specification (Haiku - Template-Following Only)

**Use this only when the pattern is obvious before you start** — a feature that clearly repeats
an existing, already-implemented shape (e.g. "add a new trigger rule following the TRA-1465
Leaver pattern"), not a feature you're still reasoning through. If there's any real ambiguity
in what this should do, use `/wf-phase1-spec` (Sonnet) instead — Haiku's job here is to fill in
a template accurately, not to make judgment calls about an underspecified feature.

## Input

$ARGUMENTS

The arguments contain the feature ID and the user's description of what the feature should do — including any constraints, edge cases, or context. Any attached images (wireframes, diagrams, screenshots) are also part of the input. **Treat this as the primary definition of the feature.**

## Step 1: Read project config

Read `.claude/workflow/project-config.json`. Extract:
- `specDir` (default: `docs/specs`)
- `archiveDir` (default: `docs/specs/archive`)
- `roadmapFile` (default: `ROADMAP.md`)
- `worktreesEnabled` (default: `false`) — whether to use Claude Code's native worktree
  mechanism (`EnterWorktree`) for this feature.

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`.

## Step 2: Read roadmap for supplementary context

Read `{roadmapFile}` and find the entry for the feature ID. Use any additional requirements listed there to supplement the user's description — but the user's description takes precedence.

## Step 3: Find the pattern to follow

The user's description should already name (or clearly imply) the existing feature/pattern this
one repeats. Read that existing implementation directly — its spec if one exists under
`{specDir}/` or `{archiveDir}/`, and its actual code — rather than inferring conventions from
`CLAUDE.md` in the abstract. This is the core of what makes a template-following spec cheap to
write correctly: copy the proven shape, don't reason it out from first principles.

If no clear existing pattern is identifiable from the description, **stop and tell the user**:
this feature doesn't fit the template-following case this command is for. Suggest
`/wf-phase1-spec` instead rather than drafting a guess.

## Step 4: Analyze dependencies

Identify, by direct analogy to the pattern found in Step 3:
- Which existing systems this feature integrates with
- Required modifications to existing files
- New files/classes needed
- Database schema changes (if any)
- Configuration/constants to add

## Step 4.5: Identify Unverified Assumptions

Before drafting, separate what you've directly verified (read from source, ran, tested, cross-
checked against actual behavior) from what you're assuming or inferring.

If the spec's design hinges on any claim you have NOT directly verified against source — not
"this is probably how it works" but specifically the load-bearing kind, where being wrong would
change the design — **stop and tell the user this doesn't fit the template-following case**;
recommend `/wf-phase1-spec` instead. A spec resting on an unverified claim is exactly the
opposite of the low-ambiguity, closely-analogous case this command exists for.

## Step 5: Create spec directory

Create: `{specDir}/{feature-id-lowercase}/`
(e.g., `{specDir}/sf14/` for SF-14)

## Step 6: Preserve and transcribe attached design assets

If the input includes attached images (wireframes, diagrams, screenshots, photos of hand-drawn
notes) — or the user points at such assets — capture them durably **before** drafting.

1. Create `{specDir}/{feature-dir}/design/`.
2. Save each attached image into that folder under a descriptive, stable name.
3. Create `{specDir}/{feature-dir}/design/DESIGN_SOURCE.md`. For each image, write a full text
   transcription: every label, box, arrow, and annotation, **plus the design decision it encodes**.
4. Read each image carefully and extract **all** of its information before you draft.

Skip this step only when no design assets were provided.

## Step 7: Generate spec file

Create `{specDir}/{feature-dir}/{FEATURE-ID}_{NAME}_SPEC.md`, following the same structure as
`/wf-phase1-spec` — **Status**, **Complexity Tier** (this command should almost always produce
`Simple` or `Spike`; if your own analysis is pointing toward `Medium` or `Complex`, stop and
recommend `/wf-phase1-spec` instead — that's a signal this isn't template-following after all),
**Decisions Requiring Your Judgment** (omit unless a load-bearing claim exists — see Step 4.5),
**Overview**,
**Application Interface** (if applicable), **Components**, **Configuration/Constants** (if
applicable), **Architecture Integration** (if applicable), **Files**, **HTTP Endpoints** (if
applicable), **Test Strategy**, **Key Implementation Notes**, **Related Specifications**, **Open
Questions**. Omit any section marked "(if applicable)" that is not relevant.

Fill every section by direct reference to the pattern found in Step 3, not by generic inference.

## Step 8: Output summary

Display:
1. Spec file path
2. Which existing pattern this spec follows (from Step 3) and why it applies
3. Each component with a 1-2 sentence description
4. Files being added/modified
5. Each open question

## Step 9: Write context file and prompt for next step

### 9a: Write context file

Write `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec-haiku",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "context": {
    "complexityTier": "{Spike | Simple}",
    "complexityJustification": "{brief reason}",
    "followedPattern": "{the existing feature/file this spec was modeled on}",
    "hingesOnUnverifiedClaim": false,
    "components": ["{component names}"],
    "openQuestions": {count},
    "properties": ["{constants/config names}"],
    "filesAffected": {count of files added + modified},
    "recommendedNextPhase": "wf-phase4-implement-sonnet"
  }
}
```

#### Record token usage

```bash
TU="{SKILL_DIR}/../../scripts/record-token-usage.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
[ -f "$TU" ] && python3 "$TU" --phase wf-phase1-spec-haiku --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}" || echo "token-usage: script not found, skipping (best-effort)"
```

### 9b: Create git worktree (if enabled)

If `worktreesEnabled` is `true` in project-config.json:

1. Compute feature ID in lowercase (e.g., `SF-14` → `sf-14`) as the worktree name.
2. Use the **`EnterWorktree`** tool to create/enter a worktree named `{feature-id-lowercase}` —
   Claude Code's native worktree mechanism: creates it at `.claude/worktrees/{feature-id-lowercase}/`
   by default, and blocks any Edit/Write/Bash call that targets the main checkout from this
   point on.
3. Read back the actual worktree path and branch name the tool reports and add to context file:
   - `"worktreePath": "{path the tool reports}"`
   - `"branchName": "{branch the tool reports}"`
4. Display:
   ```
   Entered worktree: {worktreePath}
   Branch: {branchName}

   To resume work on this feature in a later session, start with:
     claude --worktree {feature-id-lowercase}
   Cleanup is automatic — no manual removal needed.
   ```

### 9c: Next steps

Display:
> Phase 1 complete (Haiku, template-following). Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.
> Phase 2/3 are skipped for this tier by design; PMD and the full test suite are the gate.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
