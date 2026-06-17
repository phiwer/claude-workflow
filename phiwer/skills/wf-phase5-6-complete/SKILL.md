---
name: wf-phase5-6-complete
description: Combined Phase 5+6 - verify implementation and write retrospective in one session. Saves ~4-6K tokens by avoiding context reload.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
model: opus
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
3. Filter for `*_SPEC.md` files with Status: "READY FOR IMPLEMENTATION" or "IMPLEMENTED"
4. Check which specs have PHASE3_CONSOLIDATION.md but no PHASE5_VERIFICATION.md
5. If multiple found, use AskUserQuestion to ask which to verify

---

## PART A: Verification (Phase 5)

### Step 2: Read Required Documents

Read:
1. The main spec file
2. The Phase 2 review document (if exists)
3. The Phase 3 consolidation document (if exists)
4. The Phase 4 implementation record (`{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md`), if present — use its deviations list as the handoff rather than reconstructing it
5. CLAUDE.md for implementation context

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

### Step 6: Extract Actionable Insights

Before writing anything, systematically extract findings from the documents read in Step 2 and the verification just completed. Answer the specific questions below, then produce a list of **CLAUDE.md candidates**.

**From Phase 2 Review** (if it exists):
- What concerns did reviewers raise that revealed a gap in project knowledge?
- Were patterns discussed that are not in CLAUDE.md already?
- Did any reviewer flag a pitfall specific to this project's architecture or conventions?

**From Phase 3 Consolidation** (if it exists):
- What decisions were made that represent new project conventions?
- Were any approaches considered but rejected? Should the reason be documented to prevent re-litigating later?
- What open questions were resolved in a non-obvious way?
- For each item in the "Deferred Items" section: did the implementation reveal it is unnecessary, or is it still valid future work? If still valid, draft a roadmap entry for it.

**From Phase 5 Verification** (just completed above):
- What deviations from spec occurred, and why did they happen?
- Were there implementation surprises that would have been avoided with better project context?
- What test patterns, infrastructure, or edge-case handling was discovered or created?

**Synthesis — CLAUDE.md candidates**:
For each finding above, decide:
1. Is this **project-general** (useful for any future feature) or **feature-specific** (not reusable)?
2. Does CLAUDE.md already cover this? (Check the version read in Step 2.)
3. If general and not already covered: draft the specific text to add, with the target section.

Produce a numbered list of candidates:
```
[CANDIDATE 1] Section: "Testing" — "When adding X always include Y because Z." (Source: Phase 5 deviation)
[CANDIDATE 2] Section: "Architecture" — "Prefer the A pattern over B because reviewers flagged B causes C." (Source: Phase 2 review)
```

Discard anything that is only true for this specific feature. Keep only what a future Claude instance working on an unrelated feature would benefit from knowing.

### Step 7: Analyze Development Process

Evaluate:

**What Went Well**: spec clarity, review effectiveness, implementation accuracy, test quality

**What Could Be Improved**: gaps in spec, missed edge cases, process inefficiencies — trace each back to a root cause

**Key Learnings**: patterns discovered, best practices, pitfalls to avoid

### Step 8: Identify Project Documentation Updates

Using the CLAUDE.md candidates from Step 6, determine what to update:
- **CLAUDE.md**: apply candidates that passed the project-general test — use the drafted text from Step 6 directly
- Roadmap/issue tracker (feature completion)
- Architecture docs (if new patterns were introduced)
- API docs (if new endpoints were added)

---

## Step 9: Create Combined Documentation

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

## Step 10: Update Project Files

### 10a: Update main project documentation
- Apply CLAUDE.md candidates identified in Step 6
- Update roadmap/project tracker to mark feature complete
- Update architecture docs if new patterns were introduced

### 10b: Archive Spec

Move the main spec from `{specDir}/{feature-dir}/` to `{archiveDir}/{feature-dir}/`
(if the archive dir differs from spec dir). Update spec status to "IMPLEMENTED".

### 10c: Update ROADMAP.md (if it exists)

Mark the feature as complete in all relevant sections.

### 10d: Clear Workflow Context

Delete `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json` — feature workflow is complete.

---

## Step 11: Optimize CLAUDE.md

After adding new entries, read the full CLAUDE.md and do a consolidation pass:

1. **Duplicates**: Find entries that say the same thing twice or near-identically — merge into one, keeping the more specific or complete phrasing
2. **Contradictions**: Find entries that conflict — keep the newer or more specific one, remove the superseded one, note what was removed
3. **Bloat**: Find sections that have grown unwieldy — condense without losing meaning

Make surgical edits only. Do not restructure or rewrite sections that are fine. Report every change made (merged, removed, condensed) so the user can verify nothing important was lost.

## Step 12: Refresh Agent Context Excerpts

After CLAUDE.md is finalized, regenerate `.claude/context/{agent-name}.md` for every agent file in `.claude/agents/` — extract only the sections relevant to each agent's domain from the updated CLAUDE.md. This keeps review agents current without requiring a manual `/wf-init` re-run.

If `.claude/agents/` is empty or `.claude/context/` does not exist, skip silently.

---

## Step 13: Output Summary

Display:
1. ✅ Verification passed with test summary
2. ✅ Retrospective complete with key learnings
3. ✅ Project docs updated
4. ✅ CLAUDE.md optimized (list merges, removals, condensations)
5. ✅ Agent context excerpts refreshed
6. ✅ Spec archived
7. 🎉 Feature workflow complete!

---

## Step 14: Feature Complete

Display:
> Feature workflow complete! 🎉
>
> **{FEATURE-ID}** is implemented, verified, and retrospective is done.
>
> Start a new session when you're ready for the next feature — run `/wf-phase1-spec`.
