---
name: wf-phase6-retrospective
description: Run Phase 6 retrospective - document lessons learned, what went well, what could improve. Produces PHASE6_RETROSPECTIVE.md and updates project docs.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion
model: sonnet
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

### Step 3: Analyze the Development Process

Evaluate:

**What Went Well**: spec clarity, review effectiveness, implementation accuracy, test quality

**What Could Be Improved**: gaps in spec, missed edge cases, process inefficiencies

**Key Learnings**: patterns discovered, best practices, pitfalls to avoid

### Step 4: Identify Project Documentation Updates

Determine what should be updated:
- CLAUDE.md: new patterns, conventions, pitfalls discovered
- Roadmap: feature completion status
- Architecture docs: new architectural decisions made
- API docs: new endpoints added
- GAME_MECHANICS.md or equivalent domain reference (if applicable to the project)

### Step 5: Create Retrospective Document

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

### Step 6: Update Project Documentation

Edit the relevant project docs based on what was identified in Step 4:

1. **CLAUDE.md**: Add new conventions, patterns, or pitfalls discovered
2. **{roadmapFile}**: Mark feature as complete in all relevant sections
3. **Domain reference docs** (e.g., GAME_MECHANICS.md if applicable): Add new formulas/constants
4. **README.md** (if it tracks implemented features): Update feature list

### Step 7: Archive Feature Spec

Move the main spec from `{specDir}/{feature-dir}/` to `{archiveDir}/{feature-dir}/` if
the spec dir and archive dir are different. Update spec status to "IMPLEMENTED".
Remove `{specDir}/{feature-dir}/` directory if now empty.

### Step 8: Clear Workflow Context

Delete `.claude/workflow/phase-context.json` — feature workflow is complete.

### Step 9: Output Summary

Display:
1. Confirm documents were created/updated
2. Summarize key learnings
3. List project documentation updates made
4. 🎉 Feature workflow complete!

### Step 10: Feature Complete

Display:
> Feature workflow complete! 🎉
>
> **{FEATURE-ID}** is implemented, verified, and documented.
>
> Start a new session when you're ready for the next feature — run `/wf-phase1-spec`.
