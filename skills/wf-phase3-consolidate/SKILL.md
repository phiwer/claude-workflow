---
name: wf-phase3-consolidate
description: Run Phase 3 consolidation - address Phase 2 feedback, make decisions on open questions, update the spec. Produces PHASE3_CONSOLIDATION.md.
model: opus
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash
---

# Phase 3: Consolidation & Decisions

Address feedback from Phase 2 reviews, make decisions on open questions, and update the specification.

## Spec to Consolidate

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
3. Use `{specDir}` and `{archiveDir}` throughout this skill

### Step 1: Handle Missing Arguments / Auto-Detect Spec

#### 1a: Check for Context File

If no spec path was provided in arguments:

1. Check if `.claude/workflow/phase-context.json` exists
2. If exists:
   - Read and parse the JSON
   - Check if timestamp is within 24 hours (ignore if older)
   - Check if `lastPhase` is `wf-phase2-review`
   - If valid, use AskUserQuestion:
     - header: "Continue workflow?"
     - question: "Found context from wf-phase2-review. Continue with this spec?"
     - option1: label="Yes, continue with {specPath}", description="Use saved context from wf-phase2-review"
     - option2: label="No, start fresh", description="Ignore context and auto-detect specs"
   - If user selects "Yes":
     - Use `specPath` from context
     - Display context summary: verdict, critical issues count, questions for Phase 3
   - If user selects "No": delete context file and continue to step 1b

#### 1b: Auto-Detect (if no context or user chose fresh start)

1. Use Glob to find active specs: `{specDir}/*/*.md`
2. Filter for `*_SPEC.md` files
3. Check which specs have a corresponding PHASE2_REVIEW.md in `{archiveDir}/`
4. If multiple specs found, use AskUserQuestion to ask the user which spec to consolidate
5. If a spec has no Phase 2 review, warn and suggest running `/wf-phase2-review` first

### Step 2: Read Required Documents

Read:
1. The main spec file
2. The Phase 2 review (`{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE2_REVIEW.md`)

### Step 3: Extract Issues and Questions

From the Phase 2 review, extract:
1. **Critical Issues** that must be addressed
2. **Questions for Phase 3** that need decisions
3. **Recommended Changes** to consider

### Step 4: Make Decisions

For each critical issue and open question:

1. Analyze the issue/question
2. Research existing code patterns if needed
3. Make a decision with rationale
4. If the decision requires user input, use AskUserQuestion

Document each decision with:
- **Issue**: What was the problem
- **Decision**: What we're doing
- **Rationale**: Why this approach
- **Impact**: What changes in the spec

### Step 5: Update the Main Spec

Edit the main spec file to:
1. Address all critical issues
2. Incorporate recommended changes (where appropriate)
3. Update the Status to "READY FOR IMPLEMENTATION"
4. Update the version number (e.g., v1.0 → v1.1)
5. Update the "Last Updated" date

### Step 6: Create Consolidation Document

Create `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE3_CONSOLIDATION.md`:

```markdown
# {FEATURE-ID} Phase 3: Consolidation & Decisions

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 3 of 6 (Consolidation)
**Specification Version**: v1.1 (Updated)

---

## Purpose

This document addresses feedback from Phase 2 reviews, makes decisions on open questions,
and produces the final specification for implementation.

---

## Critical Decisions

### Decision 1: {Issue Title} ✅

**Issue**: {Description of the issue from Phase 2}

**Decision**: {What we decided}

**Rationale**: {Why this approach}

**Impact**:
- {Change 1 to spec}
- {Change 2 to spec}

---

### Decision 2: {Next Issue} ✅

{same structure for each decision}

---

## Spec Changes Summary

### Updated Sections
1. {Section name} - {What changed}

### New Sections Added
1. {Section name} - {Why added}

### Removed/Changed
1. {What was removed or significantly changed}

---

## Deferred Items

Items intentionally not addressed in this phase:

1. {Item} - {Why deferred, when to address}

---

## Phase 3 Verdict

**Status**: ✅ **READY FOR IMPLEMENTATION**

**Specification Version**: v1.1

**Key Changes from v1.0**:
{numbered list of major changes}

---

**Consolidation Completed**: {date}
**Next Phase**: Phase 4 - Implementation
```

### Step 7: Output Summary

After completing consolidation, display:

1. Confirm both files were updated/created with their paths
2. For each decision made: issue, decision, rationale, what changed
3. Full list of deferred items with reasons
4. Version change summary
5. Any unresolved questions that may come up during implementation

Then proceed to Step 8.

### Step 8: Write Context and Prompt for Next Step

#### 8a: Write Context File

Create/update `.claude/workflow/phase-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase3-consolidate",
  "timestamp": "{current ISO datetime}",
  "context": {
    "specVersion": "{version number, e.g., v1.1}",
    "decisionsMade": ["{list decision titles}"],
    "deferredItems": {count or 0},
    "implementationReady": true,
    "integrationPoints": ["{key systems to integrate with}"]
  }
}
```

#### 8b: Phase Complete — Next Steps

Read `complexityTier` from `.claude/workflow/phase-context.json` and display:

**Simple or Medium tier** — display:
> Phase 3 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.
> (For a more thorough Opus implementation, run `/wf-phase4-implement` instead.)

**Complex tier** — display:
> Phase 3 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement` (Opus) — context will auto-load.
> (For faster implementation at the cost of depth, use `/wf-phase4-implement-sonnet`.)

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
