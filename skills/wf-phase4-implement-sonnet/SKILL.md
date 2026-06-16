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

### Step 1: Auto-Detect Spec (if not provided)

If no spec path was provided:

1. Check `.claude/workflow/phase-context.json` for recent context (within 24 hours, `lastPhase=wf-phase3-consolidate`)
2. If valid context found, ask user if they want to continue with it
3. Otherwise, use Glob to find specs: `{specDir}/*/*.md`
4. Filter for `*_SPEC.md` files with Phase 3 consolidation but no Phase 5 verification
5. If multiple eligible specs, use AskUserQuestion to select one

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

### Step 6: Phase Complete — Next Steps

Display:
> Phase 4 complete. Implementation done.
>
> **Next**: Start a new session and run `/wf-phase5-verify` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
