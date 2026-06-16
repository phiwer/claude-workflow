---
name: wf-phase6-retrospective
description: Run Phase 6 retrospective - document lessons learned, what went well, what could improve. Produces PHASE6_RETROSPECTIVE.md and updates project docs.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
model: opus
---

# Phase 6: Retrospective

Document lessons learned, what went well, and what could be improved for future features.

## Spec for Retrospective

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
   - `roadmapFile` = `ROADMAP.md`

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Use Glob to find active specs: `{specDir}/*/*.md`
2. Filter for `*_SPEC.md` files with Status: "IMPLEMENTED"
3. Check which specs have PHASE5_VERIFICATION.md but no PHASE6_RETROSPECTIVE.md
4. If multiple found, use AskUserQuestion to ask which to retrospect
5. If a spec has no Phase 5 verification, warn and suggest running `/wf-phase5-verify` first

### Step 2: Read All Phase Documents

Read:
1. The main spec file
2. Phase 2 review document (if exists)
3. Phase 3 consolidation document (if exists)
4. Phase 5 verification document
5. CLAUDE.md for context

### Step 3: Extract Actionable Insights

Before writing anything, systematically extract findings from each prior document. For each, answer the specific questions below, then produce a list of **CLAUDE.md candidates** — concrete additions worth carrying forward.

**From Phase 2 Review** (if it exists):
- What concerns did reviewers raise that revealed a gap in project knowledge?
- Were patterns discussed that are not in CLAUDE.md already?
- Did any reviewer flag a pitfall specific to this project's architecture or conventions?

**From Phase 3 Consolidation** (if it exists):
- What decisions were made that represent new project conventions?
- Were any approaches considered but rejected? Should the reason be documented to prevent re-litigating later?
- What open questions were resolved in a non-obvious way?
- For each item in the "Deferred Items" section: did the implementation reveal it is unnecessary, or is it still valid future work? If still valid, draft a roadmap entry for it.

**From Phase 5 Verification** (if it exists):
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

### Step 4: Analyze the Development Process

Using the candidates from Step 3 as grounding, evaluate:

**What Went Well**: spec clarity, review effectiveness, implementation accuracy, test quality

**What Could Be Improved**: gaps in spec, missed edge cases, process inefficiencies — trace each back to a root cause

**Key Learnings**: patterns discovered, best practices, pitfalls to avoid

### Step 5: Identify Project Documentation Updates

Using the CLAUDE.md candidates from Step 3, determine what to update:
- **CLAUDE.md**: apply candidates that passed the project-general test — use the drafted text from Step 3 directly
- **Roadmap**: feature completion status
- **Architecture docs**: new architectural decisions made
- **API docs**: new endpoints added
- **Domain reference docs** (e.g., GAME_MECHANICS.md): new formulas, constants, or rules discovered

### Step 6: Create Retrospective Document

Create `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE6_RETROSPECTIVE.md`:

```markdown
# {FEATURE-ID} Phase 6: Retrospective

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 6 of 6 (Retrospective)

---

## Executive Summary

**Status**: ✅ **COMPLETE**

{Brief summary of the feature and its implementation}

---

## What Went Well

### 1. {Title} ⭐

**Impact**: {Critical / High / Medium / Low}
**Description**: {What went well}
**Learning**: {What to continue doing}

### 2. {Next item}

{same structure}

---

## What Could Be Improved

### 1. {Title}

**Impact**: {Critical / High / Medium / Low}
**Description**: {What could have been better}
**Root Cause**: {Why this happened}
**Improvement**: {What to do differently next time}

---

## Key Learnings

### For Specifications
1. {Learning}

### For Implementation
1. {Learning}

### For Testing
1. {Learning}

### For Process
1. {Learning}

---

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Test Count | {target} | {actual} | {✅/⚠️} |
| Phase 2 Issues | - | {count} | - |
| Deviations | 0 | {count} | {✅/⚠️} |

---

## Project Documentation Updates

{List updates made}

---

**Retrospective Completed**: {date}
**Feature Status**: ✅ COMPLETE
```

### Step 7: Update Project Documentation

Edit the relevant project docs based on what was identified in Step 5:

1. **CLAUDE.md**: Add new conventions, patterns, or pitfalls discovered
2. **{roadmapFile}**: Mark feature as complete in all relevant sections
3. **Domain reference docs** (e.g., GAME_MECHANICS.md if applicable): Add new formulas/constants
4. **README.md** (if it tracks implemented features): Update feature list

### Step 8: Archive Feature Spec

Move the main spec from `{specDir}/{feature-dir}/` to `{archiveDir}/{feature-dir}/` if
the spec dir and archive dir are different. Update spec status to "IMPLEMENTED".
Remove `{specDir}/{feature-dir}/` directory if now empty.

### Step 9: Clear Workflow Context

Delete `.claude/workflow/phase-context.json` — feature workflow is complete.

### Step 10: Output Summary

Display:
1. Confirm documents were created/updated
2. Summarize key learnings
3. List project documentation updates made
4. 🎉 Feature workflow complete!

### Step 11: Feature Complete

Display:
> Feature workflow complete! 🎉
>
> **{FEATURE-ID}** is implemented, verified, and documented.
>
> Start a new session when you're ready for the next feature — run `/wf-phase1-spec`.
