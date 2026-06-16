---
name: wf-phase1-spec
description: Phase 1 - Create an initial feature specification from a roadmap item. Generates a structured spec file ready for Phase 2 review.
argument-hint: [feature-id] (e.g., SF-14)
allowed-tools: Read, Glob, Grep, Bash, Write, AskUserQuestion
model: sonnet
---

<!--
Model Selection Guide:
- Use Sonnet (default) for novel features or unclear requirements
- Consider asking user if they want to use Haiku for pattern-following features
  (e.g., new entries following an established template pattern in the codebase)

Any gaps in Haiku's spec get caught by Phase 2 agents anyway.
-->

# Phase 1: Create Feature Specification

## Feature to Specify

$ARGUMENTS

---

## YOUR ONLY JOB RIGHT NOW: Ask the user one question. Then stop.

Do not explore the codebase. Do not read CLAUDE.md. Do not look at existing specs or code.
The spec writing happens later, after the user responds. Ignore that you know how to write specs.

### Step 1: Read config and roadmap (these two reads only)

1. Read `.claude/workflow/project-config.json` — extract `specDir`, `archiveDir`, `roadmapFile`, `worktreeBase` (defaults: `docs/specs`, `docs/specs/archive`, `ROADMAP.md`, `null`).
2. Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` to get `GIT_MAIN_ROOT`.
3. Read `{roadmapFile}`.

### Step 2: Ask the user

- **If no feature ID in arguments:** use `AskUserQuestion` to list up to 4 unimplemented (⬜) features from the roadmap. After the user picks one, continue.
- **Once you have a feature ID:** extract its name, description, and requirements from the roadmap.

Display a brief summary (ID, name, description, key requirements), then use `AskUserQuestion`:

> **"Does this look right? Anything to add, clarify, or constrain before I write the spec?"**
> - "Looks good — proceed as-is"
> - (Other = free text for additional context)

**Stop here. Output nothing more. Wait for the user's response.**

---

## PART 2 — After the user has responded: Codebase Exploration and Spec Generation

**Do not begin this section until the user's answer is in the conversation above.**
**Incorporate any additional context the user provided throughout the steps below.**

### Step 3: Gather Codebase Context

1. Read `CLAUDE.md` to understand existing patterns and implemented features
2. Check for any reference documentation in the repo (e.g., `docs/`, `references/`, `specs/`)
3. Review related existing specs in `{specDir}/` for format and patterns
4. Check existing code for any partial implementations or related systems

### Step 4: Analyze Dependencies

Identify:
- Which existing systems this feature integrates with
- Required modifications to existing files
- New files/classes needed
- Database schema changes (if any)
- Configuration/constants to add

### Step 5: Create Spec Directory

Create the directory: `{specDir}/{feature-id-lowercase}/`
(e.g., `{specDir}/sf14/` for SF-14)

### Step 6: Generate Spec File

Create `{specDir}/{feature-dir}/{FEATURE-ID}_{NAME}_SPEC.md` using this template.

**Note on optional sections**: If a section header is marked "(if applicable)" and is not relevant to this feature, omit it entirely from the generated spec — do not include the header with placeholder content.

```markdown
# {FEATURE-ID}: {Feature Name} Specification

**Status**: DRAFT
**Created**: {date}
**Complexity**: {Simple | Medium | Complex}

---

## Complexity Tier

**Tier**: {Simple | Medium | Complex}
**Justification**: {Why this tier - be specific}

| Tier | Criteria | Recommended Phases |
|------|----------|-------------------|
| Simple | Single pattern, <100 LOC, follows existing templates | 1 → 4 → 5 |
| Medium | 2-5 files, follows existing patterns, some integration | 1 → 2 (3 agents) → 3 → 4 → 5 |
| Complex | New patterns, architecture, 5+ files, novel mechanics | 1 → (1.5) → 2 → 3 → 4 → 5 → 6 |

---

## Overview

{Brief description of what this feature does and why it matters}

---

## Application Interface (if applicable)

The public contracts this feature exposes to the rest of the system. Define these
before components — the interface is the contract; components are the internals.

### {InterfaceName}

**Type**: {Interface / Abstract Class / Protocol / Service Contract}

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `methodName` | `param: Type` | `ReturnType` | What it does |

### {DTOName / Record / Value Object} (if crossing layer boundaries)

| Field | Type | Description |
|-------|------|-------------|
| `fieldName` | `Type` | What it represents |

---

## Components

### 1. {Component Name}

{Description of this component}

**Formula / Logic** (if applicable):
```
result = baseValue × modifier × efficiency
```

Where:
- `baseValue` = description
- `modifier` = description

### 2. {Next Component}

{Continue for each component}

---

## Configuration / Constants (if applicable)

| Name | Value | Description |
|------|-------|-------------|
| `CONSTANT_NAME` | value | What this controls |

---

## Architecture Integration (if applicable)

{Where this fits in the system — e.g., processing order, event pipeline, request lifecycle}

---

## Files

### Added
- `NewComponent.ext` - Core logic for {feature}
- `NewResult.ext` - Result type for {operation}

### Modified
- `ExistingFile.ext` - {What changes and why}

---

## HTTP Endpoints (if applicable)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/{resource}/{action}` | {description} |

---

## Test Strategy

| Test | Focus | Estimated Cases |
|------|-------|-----------------|
| `{Feature}Test` | Core logic verification | 10-15 |
| `{Feature}IntegrationTest` | End-to-end integration | 5-8 |
| `{Feature}EdgeCaseTest` | Boundary conditions | 8-12 |

---

## Key Implementation Notes

1. {Important architectural decision or constraint}
2. {Performance consideration}
3. {Integration note with existing systems}

---

## Related Specifications

- [{Related Feature}]({path}) - {How it relates}

---

## Open Questions

- [ ] {Question needing resolution before implementation}
- [ ] {Another open question}

---

**Last Updated**: {date}
```

### Step 7: Output Summary

After creating the spec, display:

1. Confirm the file was created with its path
2. List each component with a 1-2 sentence description
3. List all configuration/constants being added
4. List all files being added/modified
5. List each open question with context
6. Show any HTTP endpoints being added

Then proceed to Step 8.

### Step 8: Write Context and Prompt for Next Step

#### 8a: Write Context File

Create/update `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec",
  "timestamp": "{current ISO datetime}",
  "context": {
    "complexityTier": "{Simple | Medium | Complex}",
    "complexityJustification": "{brief reason for tier selection}",
    "components": ["{list component names identified}"],
    "openQuestions": {count of open questions},
    "properties": ["{list constants/config names being added}"],
    "filesAffected": {count of files added + modified},
    "recommendedNextPhase": "{wf-phase1-iterate | wf-phase2-review | wf-phase4-implement-sonnet}"
  }
}
```

#### 8b: Create Git Worktree (if configured)

If `worktreeBase` is set (non-null) in `project-config.json`:

1. Derive the project directory name from the current repo root (last path component of `GIT_MAIN_ROOT`).
2. Compute the feature ID in lowercase (e.g., `SF-14` → `sf-14`).
3. Run:
   ```bash
   git worktree add "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}" -b "feature/{feature-id-lowercase}"
   ```
4. Save `worktreePath` and `branchName` to the context file written in 8a:
   - `"worktreePath": "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}"`
   - `"branchName": "feature/{feature-id-lowercase}"`
5. Display the worktree path to the user:
   ```
   Git worktree created: {worktreePath}
   Branch: {branchName}
   Implementation phases will run from this directory.
   ```

#### 8c: Phase Complete — Next Steps

Display the recommended next command based on the `complexityTier` saved to `{FEATURE-ID}-context.json`:

**Simple tier** — display:
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.

**Medium tier** — display:
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase2-review` — context will auto-load.
> (For an early sanity-check first, run `/wf-phase1-iterate` instead.)

**Complex tier** — display:
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase1-iterate` for early agent feedback — context will auto-load.
> After iterate, start another new session and run `/wf-phase2-review`.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
