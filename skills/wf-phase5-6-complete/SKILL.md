---
name: wf-phase5-6-complete
description: Combined Phase 5+6 - verify implementation and write retrospective in one session. Saves ~4-6K tokens by avoiding context reload.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
model: sonnet
---

# Phase 5+6: Verification & Retrospective (Combined)

Verify implementation matches spec, run tests, and immediately write retrospective if verification passes.

**Token Savings**: Combines two phases into one session, saving ~4-6K tokens from context reload.

## Spec to Process

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Check `.claude/workflow/phase-context.json` for recent context
2. Use Glob to find active specs: `{specDir}/*/*.md`
3. Filter for `*_SPEC.md` files with Status: "READY FOR IMPLEMENTATION" or "IMPLEMENTED"
4. Check which specs have PHASE3_CONSOLIDATION.md but no PHASE5_VERIFICATION.md
5. If multiple found, use AskUserQuestion to ask which to verify

---

## PART A: Verification (Phase 5)

### Step 2: Read Required Documents

Read:
1. The main spec file
2. The Phase 3 consolidation document (if exists)
3. CLAUDE.md for implementation context

### Step 3: Build and Run Tests

Run the project's build and test suite (check CLAUDE.md for the specific commands):

```bash
# See CLAUDE.md "Build & Test Commands" section for project-specific commands
```

Capture:
- Total tests run
- Tests passed/failed
- Any new test files added

### Step 4: Verify Implementation Checklist

Check each item from the spec:

1. **Files Added**: Verify all specified files exist
2. **Files Modified**: Verify changes were made to specified files
3. **Configuration/Constants**: Check relevant files
4. **HTTP Endpoints**: Verify endpoints work (if applicable)
5. **Integration Points**: Check pipeline/factory integration
6. **Test Coverage**: Verify test files exist and pass

### Step 5: Determine Verification Status

- **✅ VERIFIED**: Tests pass, all checklist items complete
- **⚠️ ISSUES FOUND**: Minor issues but can proceed
- **❌ FAILED**: Tests fail or major issues — stop here

**If FAILED**:
- Create only PHASE5_VERIFICATION.md documenting the failure
- Use AskUserQuestion to ask if user wants to fix issues or stop
- Do NOT proceed to Phase 6

**If VERIFIED or ISSUES FOUND**: Continue to Part B

---

## PART B: Retrospective (Phase 6)

### Step 6: Analyze Development Process

Evaluate:

**What Went Well**: spec clarity, review effectiveness, implementation accuracy, test quality

**What Could Be Improved**: gaps in spec, missed edge cases, process inefficiencies

**Key Learnings**: patterns discovered, best practices, pitfalls to avoid

### Step 7: Identify Project Documentation Updates

Determine what should be updated in project docs:
- Main project docs (CLAUDE.md, README, etc.)
- Roadmap/issue tracker (feature completion)
- Architecture docs (if new patterns were introduced)
- API docs (if new endpoints were added)

---

## Step 8: Create Combined Documentation

Create TWO documents in `{archiveDir}/{feature-dir}/`:

### Document 1: `{FEATURE-ID}_PHASE5_VERIFICATION.md`

```markdown
# {FEATURE-ID} Phase 5: Verification

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 5 of 6 (Verification)

---

## Executive Summary

**Status**: ✅ VERIFIED

---

## Verification Checklist

### 1. Files Added
| Expected File | Status | Notes |
|---------------|--------|-------|
| {File} | ✅ | {location} |

### 2. Files Modified
| File | Expected Change | Status |
|------|-----------------|--------|
| {File} | {change} | ✅ |

### 3. Test Coverage
| Test | Focus | Tests | Status |
|------|-------|-------|--------|
| {TestClass} | {focus} | {count} | ✅ |

---

## Test Results

```
{test output summary}
```

---

## Deviations from Specification

{List deviations or "None"}

---

**Verification Completed**: {date}
**Status**: ✅ VERIFIED - Proceeding to Retrospective
```

### Document 2: `{FEATURE-ID}_PHASE6_RETROSPECTIVE.md`

```markdown
# {FEATURE-ID} Phase 6: Retrospective

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 6 of 6 (Retrospective)

---

## Executive Summary

**Status**: ✅ **COMPLETE**

---

## What Went Well

### 1. {Title} ⭐
**Impact**: {High / Medium / Low}
**Description**: {What went well}
**Learning**: {What to continue doing}

---

## What Could Be Improved

### 1. {Title}
**Impact**: {High / Medium / Low}
**Description**: {What could have been better}
**Improvement**: {What to do differently}

---

## Key Learnings

### For Specifications
1. {Learning}

### For Implementation
1. {Learning}

### For Process
1. {Learning}

---

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Test Count | {target} | {actual} | ✅ |
| Deviations | 0 | {count} | ✅ |

---

## Project Documentation Updates

{List updates made to project docs}

---

**Retrospective Completed**: {date}
**Feature Status**: ✅ COMPLETE
```

---

## Step 9: Update Project Files

### 9a: Update main project documentation
- Update feature status in CLAUDE.md (or equivalent)
- Update roadmap/project tracker to mark feature complete
- Update architecture docs if new patterns were introduced

### 9b: Archive Spec

Move the main spec from `{specDir}/{feature-dir}/` to `{archiveDir}/{feature-dir}/`
(if the archive dir differs from spec dir). Update spec status to "IMPLEMENTED".

### 9c: Update ROADMAP.md (if it exists)

Mark the feature as complete in all relevant sections.

### 9d: Clear Workflow Context

Delete `.claude/workflow/phase-context.json` — feature workflow is complete.

---

## Step 10: Output Summary

Display:
1. ✅ Verification passed with test summary
2. ✅ Retrospective complete with key learnings
3. ✅ Project docs updated
4. ✅ Spec archived
5. 🎉 Feature workflow complete!

---

## Step 11: Feature Complete

Display:
> Feature workflow complete! 🎉
>
> **{FEATURE-ID}** is implemented, verified, and retrospective is done.
>
> Start a new session when you're ready for the next feature — run `/wf-phase1-spec`.
