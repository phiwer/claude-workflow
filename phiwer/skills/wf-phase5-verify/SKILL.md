---
name: wf-phase5-verify
description: Run Phase 5 verification after implementation - verify spec was implemented correctly, check tests pass, document any deviations. Produces PHASE5_VERIFICATION.md.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Bash, AskUserQuestion
model: opus
---

# Phase 5: Implementation Verification

Verify the implementation matches the specification, all tests pass, and document any deviations.

## Spec to Verify

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

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`. If multiple found, ask the user which feature to continue (AskUserQuestion). If one found, check it for a recent `specPath` to use.
   - **Reconcile before trusting it.** The on-disk artifacts are the source of truth; the context file is only a cache a prior phase may have failed to update (interrupted, errored, or you took over manually). Before relying on `lastPhase`, check it against reality — the spec `Status`, which `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE*.md` documents exist, and whether the implementation and tests are present. If they disagree, **trust the artifacts**, tell the user about the drift, and rewrite the context to match before continuing.
2. Use Glob to find active specs: `{specDir}/*/*.md`
2. Filter for `*_SPEC.md` files with Status: "READY FOR IMPLEMENTATION" or similar
3. Check which specs have PHASE3_CONSOLIDATION.md but no PHASE5_VERIFICATION.md
4. If multiple found, use AskUserQuestion to ask which to verify
5. If a spec has no Phase 3 consolidation, warn and suggest running `/wf-phase3-consolidate` first

### Step 2: Read Required Documents

Read:
1. The main spec file
2. The Phase 3 consolidation document
3. The Phase 4 implementation record (`{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md`), if present — use its deviations list as the handoff rather than reconstructing it
4. CLAUDE.md for implementation context

### Step 3: Build and Run Tests

Run the project's build and test suite (check CLAUDE.md for the specific commands):

```bash
# See CLAUDE.md "Build & Test Commands" section for project-specific commands
# Typical patterns:
# mvn clean install -DskipTests && mvn test
# npm run build && npm test
# pytest
```

Capture:
- Total tests run
- Tests passed/failed
- Any new test classes added

### Step 4: Verify Implementation Checklist

Check each item from the spec:

1. **Files Added**: Verify all specified files exist
2. **Files Modified**: Verify changes were made to specified files
3. **Configuration/Constants Added**: Check relevant config files
4. **HTTP Endpoints**: Verify endpoints work (if applicable)
5. **Integration Points**: Check pipeline/factory integration
6. **Test Coverage**: Verify test files exist and pass

### Step 5: Document Deviations

If the implementation differs from the spec:
1. Document what changed
2. Explain why the deviation was necessary
3. Determine if the spec should be updated

### Step 6: Create Verification Document

Create `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE5_VERIFICATION.md`:

```markdown
# {FEATURE-ID} Phase 5: Verification

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 5 of 6 (Verification)

---

## Executive Summary

{Brief summary of implementation status}

**Status**: {✅ VERIFIED - Ready for Retrospective / ⚠️ ISSUES FOUND / ❌ FAILED}

---

## Verification Checklist

### 1. Files Added

**Status**: {PASS ✅ / FAIL ❌}

| Expected File | Status | Notes |
|---------------|--------|-------|
| {File} | ✅ | {location} |

### 2. Files Modified

**Status**: {PASS ✅ / FAIL ❌}

| File | Expected Change | Status |
|------|-----------------|--------|
| {File} | {change} | ✅ |

### 3. HTTP Endpoints (if applicable)

**Status**: {PASS ✅ / FAIL ❌ / N/A}

{Endpoint verification details}

---

## Test Coverage Analysis

### Test Count Summary

**Target**: {from spec}
**Delivered**: {actual count}

### Test Classes

| Test | Focus | Tests | Status |
|------|-------|-------|--------|
| {TestClass} | {focus} | {count} | ✅ |

### Test Run Results

```
{paste test output summary}
```

---

## Deviations from Specification

### Deviation 1: {Title}

**Spec Said**: {what spec specified}
**Implementation**: {what was actually done}
**Reason**: {why the change}
**Spec Update Needed**: {Yes/No}

---

## Phase 5 Verdict

**Status**: ✅ **VERIFIED - Ready for Retrospective**

**Test Summary**: {X} tests, all passing

**Deviations**: {count} documented

---

**Verification Completed**: {date}
**Next Phase**: Phase 6 - Retrospective (`/wf-phase6-retrospective`)
```

### Step 7: Update Main Spec Status

Edit the main spec to update Status to "IMPLEMENTED".

### Step 8: Output Summary

1. Confirm the verification document was created
2. Report overall status
3. Summarize test results
4. List any deviations

### Step 9: Record token usage

Append this phase's token usage to the verification document and context:

```bash
TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
[ -n "$TU" ] && python3 "$TU" --phase wf-phase5-verify \
  --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" \
  --artifact "{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE5_VERIFICATION.md" \
  || echo "token-usage: script not found, skipping (best-effort)"
```

### Step 10: Phase Complete — Next Steps

**If VERIFIED** — display:
> Phase 5 complete. Implementation verified. ✅
>
> **Next**: Start a new session and run `/wf-phase6-retrospective` — context will auto-load.
> (Skip retrospective if the feature is trivial and no lessons need documenting.)

**If ISSUES FOUND** — use AskUserQuestion for the within-phase decision only:
- header: "Issues found"
- question: "Verification found issues. How do you want to proceed?"
- option1: label="Fix and re-verify", description="Address issues, then re-run /wf-phase5-verify in a new session"
- option2: label="Proceed to retrospective", description="Continue despite issues — document them in the retrospective"

Then display: "After deciding, start a new session to continue."

Do NOT offer AskUserQuestion for the VERIFIED path. The user must manually start a new session.
