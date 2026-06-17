---
name: wf-phase4-implement
description: Phase 4 implementation (Opus) - thorough implementation with detailed analysis. Use /wf-phase4-implement-sonnet for faster implementation.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Task, AskUserQuestion
model: opus
---

# Phase 4: Implementation (Opus - Thorough)

Implement a feature according to its specification and Phase 3 consolidation decisions.

**For faster implementation**: Use `/wf-phase4-implement-sonnet` instead.

## Spec to Implement

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
3. Use `{specDir}` and `{archiveDir}` throughout this skill
4. Find the main worktree root:
   ```
   Run: git worktree list 2>/dev/null | head -1 | awk '{print $1}'
   Use the result as GIT_MAIN_ROOT. All context files live at:
     {GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json
   Falls back to .claude/workflow/ if git command fails.
   ```

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`. If multiple found, ask the user which feature to continue (AskUserQuestion). If one found, use it as the context file.
   - **Reconcile before trusting it.** The on-disk artifacts are the source of truth; the context file is only a cache a prior phase may have failed to update (interrupted, errored, or you took over manually). Before relying on `lastPhase`, check it against reality — the spec `Status`, which `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE*.md` documents exist, and whether the implementation and tests are present. If they disagree, **trust the artifacts**, tell the user about the drift, and rewrite the context to match before continuing.
2. Check the context file for recent context (within 24 hours, lastPhase=wf-phase3-consolidate)
3. If valid context found, ask user if they want to continue with it
   - **Worktree note**: If `worktreePath` is set in the context, note this to the user and display the worktree path. Implementation should run from that directory.
4. Otherwise, use Glob to find specs: `{specDir}/*/*.md`
5. Filter for `*_SPEC.md` files with Phase 3 consolidation but no Phase 5 verification
6. If multiple eligible specs, use AskUserQuestion to select one

### Step 2: Validate Phase

Verify:
1. `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE3_CONSOLIDATION.md` exists
2. `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE5_VERIFICATION.md` does NOT exist

If Phase 3 not complete:
```
⚠️ This spec has not completed Phase 3 consolidation.

Run /wf-phase3-consolidate first to address Phase 2 feedback.
```

### Step 3: Read Required Documents

Read thoroughly:

1. **Main Spec**: `{specDir}/{feature-dir}/{FEATURE-ID}_*_SPEC.md`
2. **Phase 3 Consolidation**: `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE3_CONSOLIDATION.md`
3. **CLAUDE.md**: For project patterns and conventions
4. **Related existing code**: Based on "Files Modified" section of spec
5. **Interface files** (if `"interfaceFirst": true` in project-config): read the files listed in the consolidation's `interfaceFilesCreated` — these are the agreed contracts to implement against

### Step 4: Create Implementation Plan

Before writing code, outline:

1. Files to create (from spec "Files Added" section)
2. Files to modify (from spec "Files Modified" section)
3. Dependencies between changes
4. Implementation order: typically model/data types → core logic → integration → tests

If `interfaceFirst` is true: interface/abstract files already exist and have been reviewed by the team. Mark them as "Files Modified" (add implementations) rather than "Files Added" — do not redefine the signatures.

### Step 5: Implement the Feature

Follow the spec precisely:

1. **Create new files** as specified, following existing code patterns
2. **Modify existing files** — read each before editing, make minimal focused changes
3. **Add configuration/constants** if specified
4. **Update integration points** as specified (processing pipelines, factories, etc.)
5. **Create HTTP endpoint** if specified
6. **Write tests** as specified in Test Strategy

**Deviations**: If at any point the implementation diverges from the spec, document it immediately — what the spec said, what you're doing instead, and why. Add it to the Step 8 summary as you go; don't try to reconstruct it at the end.

### Step 6: Run Tests

Run the project's test suite (see CLAUDE.md or project docs for specific commands):

```bash
# Example — replace with your project's actual test command:
# mvn test -pl game-server
# npm test
# pytest
```

Fix any failures, re-run until passing.

### Step 7: Verify Completeness

Check off each item from the spec:

- [ ] All files added
- [ ] All files modified
- [ ] All configuration/constants added
- [ ] Integration points updated
- [ ] HTTP endpoint working (if applicable)
- [ ] Tests written and passing

### Step 8: Output Summary

```
## Phase 4 Implementation Complete

**Feature**: {FEATURE-ID} - {Feature Name}
**Spec**: {spec path}

### Files Created
- {file1}
- {file2}

### Files Modified
- {file1} - {what changed}

### Tests
- {X} test classes created
- {Y} tests total
- All passing ✅

### Notes
{Any deviations from spec or issues encountered}
```

### Step 9: Record the implementation (durable state)

Persist a durable record so Phase 5/6 — and anyone glancing at the folder — can see Phase 4 ran and what it did. **Do this even if you reached this point after manual fixes or an interrupted run**; it is what makes the workflow state survive a non-clean finish. Phase 4 is otherwise the only phase that leaves no on-disk marker.

**9a — Lightweight implementation record.** Write `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md`. Keep it short — it exists for quick visual inspection of what happened, not as a report:

```markdown
# {FEATURE-ID} Phase 4: Implementation

**Date**: {date}
**Spec**: {spec path}
**Status**: ✅ IMPLEMENTED

## Files Created
- {file} — {one-line purpose}

## Files Modified
- {file} — {what changed}

## Tests
- {X} classes, {Y} tests — {all passing | N failing}

## Deviations from Spec
- {deviation and why — or "None"}
```

**9b — Update the context file.** Create/update `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json` with `lastPhase: "wf-phase4-implement"` and a short summary, so Phase 5 has a clean handoff instead of reconstructing the deviations. Preserve existing keys such as `worktreePath` / `branchName`:

```json
{
  "specPath": "{spec path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase4-implement",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "context": {
    "filesCreated": {count},
    "filesModified": {count},
    "testCount": {count},
    "deviations": ["{short deviation, omit if none}"],
    "recommendedNextPhase": "wf-phase5-verify"
  }
}
```

### Step 10: Phase Complete — Next Steps

Display:
> Phase 4 complete. Implementation done.
>
> **Next**: Start a new session and run `/wf-phase5-verify` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
