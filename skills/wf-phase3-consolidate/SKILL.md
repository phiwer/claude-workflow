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

Before editing, scan the spec's "Open Questions" section for any remaining `- [ ]` unchecked items. For each:
- If it was addressed in Step 4, mark it `- [x]` and note the decision inline
- If it was not addressed, decide now or explicitly move it to the Deferred Items section of the consolidation document with a reason — do not leave it unchecked and do not set status to READY FOR IMPLEMENTATION with unresolved questions

Then edit the main spec file to:
1. Address all critical issues
2. Incorporate recommended changes (where appropriate)
3. Mark all resolved Open Questions as `- [x]`
4. Update the Status to "READY FOR IMPLEMENTATION"
5. Update the version number (e.g., v1.0 → v1.1)
6. Update the "Last Updated" date

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

### Step 7: Create Application Interface Files (if applicable)

Check `project-config.json` for `"interfaceFirst": true`.

If not set, use AskUserQuestion:
- header: "Interface-first?"
- question: "Create application interface files now for team review before implementation? This generates the public contracts (interfaces, abstract classes, DTOs) from the consolidated spec — the team reviews and agrees on these before phase4 implements them."
- option1: label="Yes — create interfaces", description="Generate interface/contract files now; review with team before implementing in phase4"
- option2: label="No — go straight to implementation", description="Skip; proceed directly to /wf-phase4-implement"

**If yes** (from config flag or user choice):

1. If the flag was not already set, add `"interfaceFirst": true` to `project-config.json`
2. From the consolidated spec, identify the public application boundary:
   - Service interfaces and their methods
   - Controllers / API entry points
   - Repository / port interfaces
   - DTOs, records, value objects that cross layer boundaries
   - Event / message schemas if applicable
3. Infer the correct source directory from existing code structure or CLAUDE.md
4. Create each file with the full package/namespace declaration and contract-level content only:
   - Method signatures, parameter types, return types, checked exceptions
   - Javadoc / docstrings describing intent and contract
   - **No implementation logic** — bodies are empty, `abstract`, or `throw new UnsupportedOperationException()`
5. List all files created with full paths

Display:
```
## Interface Files Created

{list each file with full path}

### Next step
Review these files with your team. Once agreed, start a new session and
run `/wf-phase4-implement` to implement against them.
```

**If no**: proceed to Step 8.

### Step 8: Output Summary

After completing consolidation, display:

1. Confirm both files were updated/created with their paths
2. For each decision made: issue, decision, rationale, what changed
3. Full list of deferred items with reasons
4. Version change summary
5. Any unresolved questions that may come up during implementation
6. If interface files were created: list them and note they need team review before phase4

Then proceed to Step 9.

### Step 9: Write Context and Prompt for Next Step

#### 9a: Write Context File

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
    "interfaceFilesCreated": ["{list paths, or empty array}"],
    "integrationPoints": ["{key systems to integrate with}"]
  }
}
```

#### 9b: Phase Complete — Next Steps

If interface files were created in Step 7, display:
> Phase 3 complete. Interface files created — context saved.
>
> **Next**: Review the interface files with your team. Once agreed, start a new
> session and run `/wf-phase4-implement` — context will auto-load.

Otherwise, read `complexityTier` from `.claude/workflow/phase-context.json` and display:

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
