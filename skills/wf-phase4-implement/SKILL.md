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

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Check `.claude/workflow/phase-context.json` for recent context (within 24 hours, lastPhase=wf-phase3-consolidate)
2. If valid context found, ask user if they want to continue with it
3. Otherwise, use Glob to find specs: `{specDir}/*/*.md`
4. Filter for `*_SPEC.md` files with Phase 3 consolidation but no Phase 5 verification
5. If multiple eligible specs, use AskUserQuestion to select one

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

### Step 4: Create Implementation Plan

Before writing code, outline:

1. Files to create (from spec "Files Added" section)
2. Files to modify (from spec "Files Modified" section)
3. Dependencies between changes
4. Implementation order: typically model/data types → core logic → integration → tests

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

### Step 9: Phase Complete — Next Steps

Display:
> Phase 4 complete. Implementation done.
>
> **Next**: Start a new session and run `/wf-phase5-verify` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
