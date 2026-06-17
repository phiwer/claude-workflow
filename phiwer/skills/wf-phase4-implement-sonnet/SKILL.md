---
name: wf-phase4-implement-sonnet
description: Phase 4 implementation (Sonnet) - faster implementation with less analysis. Use /wf-phase4-implement for thorough Opus implementation.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Task, AskUserQuestion
model: sonnet
---

# Phase 4: Implementation (Sonnet - Fast Mode)

Implement a feature according to its specification. Faster, more direct approach.

For thorough implementation with detailed analysis, use `/wf-phase4-implement` (Opus).

## Spec to Implement

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
3. Find the main worktree root:
   ```
   Run: git worktree list 2>/dev/null | head -1 | awk '{print $1}'
   Use the result as GIT_MAIN_ROOT. All context files live at:
     {GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json
   Falls back to .claude/workflow/ if git command fails.
   ```

### Step 1: Auto-Detect Spec (if not provided)

If no spec path was provided:

1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`. If multiple found, ask the user which feature to continue (AskUserQuestion). If one found, use it as the context file.
   - **Reconcile before trusting it.** The on-disk artifacts are the source of truth; the context file is only a cache a prior phase may have failed to update (interrupted, errored, or you took over manually). Before relying on `lastPhase`, check it against reality — the spec `Status`, which `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE*.md` documents exist, and whether the implementation and tests are present. If they disagree, **trust the artifacts**, tell the user about the drift, and rewrite the context to match before continuing.
2. Check the context file for recent context (within 24 hours, `lastPhase=wf-phase3-consolidate`)
3. If valid context found, ask user if they want to continue with it
   - **Worktree note**: If `worktreePath` is set in the context, note this to the user and display the worktree path. Implementation should run from that directory.
4. Otherwise, use Glob to find specs: `{specDir}/*/*.md`
5. Filter for `*_SPEC.md` files with Phase 3 consolidation but no Phase 5 verification
6. If multiple eligible specs, use AskUserQuestion to select one

Validate Phase 3 is complete before proceeding.

### Step 2: Read Documents

Read:
1. Main spec file
2. Phase 3 consolidation
3. CLAUDE.md (skim for patterns)

### Step 3: Implement

Follow the spec directly:

1. Create files listed in "Files Added"
2. Modify files listed in "Files Modified"
3. Add configuration/constants if specified
4. Update integration points if specified
5. Add HTTP endpoint if specified
6. Write tests from Test Strategy

### Step 4: Test

Run the project's test suite (see CLAUDE.md for the specific commands):

```bash
# Replace with your project's actual test command
```

Fix any failures, re-run until passing.

### Step 5: Summary

```
## Implementation Complete

**Feature**: {FEATURE-ID}

### Created
- {files}

### Modified
- {files}

### Tests
- {count} tests, all passing
```

### Step 6: Record the implementation (durable state)

Persist a durable record so Phase 5/6 — and anyone glancing at the folder — can see Phase 4 ran and what it did. **Do this even if you reached this point after manual fixes or an interrupted run**; it is what makes the workflow state survive a non-clean finish. Phase 4 is otherwise the only phase that leaves no on-disk marker.

**6a — Lightweight implementation record.** Write `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md`. Keep it short — it exists for quick visual inspection of what happened, not as a report:

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

**6b — Update the context file.** Create/update `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json` with `lastPhase: "wf-phase4-implement-sonnet"` and a short summary, so Phase 5 has a clean handoff instead of reconstructing the deviations. Preserve existing keys such as `worktreePath` / `branchName`:

```json
{
  "specPath": "{spec path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase4-implement-sonnet",
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

**6c — Record token usage.** Append this phase's token usage (main session + any spawned subagents) to the implementation record and context:

```bash
TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
[ -n "$TU" ] && python3 "$TU" --phase wf-phase4-implement-sonnet \
  --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" \
  --artifact "{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md" \
  || echo "token-usage: script not found, skipping (best-effort)"
```

### Step 7: Phase Complete — Next Steps

Display:
> Phase 4 complete. Implementation done.
>
> **Next**: Start a new session and run `/wf-phase5-verify` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
