---
name: wf-phase1-spec-write
description: Phase 1b - Explore the codebase and write the feature spec. Run after wf-phase1-spec has collected the user's scoping answer.
allowed-tools: Read, Glob, Grep, Bash, Write
model: sonnet
---

<!--
Model Selection Guide:
- Use Sonnet (default) for novel features or unclear requirements
- Haiku is fine for pattern-following features where the template is obvious.
  Any gaps get caught by Phase 2 agents anyway.
-->

# Phase 1b: Write Feature Specification

## Step 1: Load context

1. Read `.claude/workflow/project-config.json` (for `specDir`, `archiveDir`, `roadmapFile`, `worktreeBase`)
2. Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`
3. Read `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`

The context file contains:
- `featureId` — the feature to spec
- `userDescription` — the user's own description of the feature (primary source of truth)

If the context file is missing or `lastPhase` is not `wf-phase1-spec`, stop and tell the user to run `/phiwer:wf-phase1-spec` first.

Also read `{roadmapFile}` to find any additional requirements listed there, but treat `userDescription` as the primary definition of the feature.

## Step 2: Gather codebase context

Using `featureId` and `userDescription` as your guide:

1. Read `CLAUDE.md` to understand existing patterns and implemented features
2. Check for reference documentation in the repo (e.g., `docs/`, `references/`)
3. Review related existing specs in `{specDir}/` for format and patterns
4. Check existing code for partial implementations or related systems

## Step 3: Analyze dependencies

Identify:
- Which existing systems this feature integrates with
- Required modifications to existing files
- New files/classes needed
- Database schema changes (if any)
- Configuration/constants to add

## Step 4: Create spec directory

Create: `{specDir}/{feature-id-lowercase}/`
(e.g., `{specDir}/sf14/` for SF-14)

## Step 5: Generate spec file

Create `{specDir}/{feature-dir}/{FEATURE-ID}_{NAME}_SPEC.md`.

**Omit any section marked "(if applicable)" that is not relevant — do not include the header with placeholder content.**

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

## Step 6: Output summary

Display:
1. Spec file path
2. Each component with a 1-2 sentence description
3. Configuration/constants being added
4. Files being added/modified
5. Each open question
6. Any HTTP endpoints

## Step 7: Write context file and prompt for next step

### 7a: Update context file

Write `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec-write",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "worktreeBase": "{worktreeBase or null}",
  "context": {
    "complexityTier": "{Simple | Medium | Complex}",
    "complexityJustification": "{brief reason}",
    "components": ["{component names}"],
    "openQuestions": {count},
    "properties": ["{constants/config names}"],
    "filesAffected": {count of files added + modified},
    "recommendedNextPhase": "{wf-phase1-iterate | wf-phase2-review | wf-phase4-implement-sonnet}"
  }
}
```

### 7b: Create git worktree (if configured)

If `worktreeBase` is non-null:

1. Derive project dir name from last path component of `GIT_MAIN_ROOT`
2. Compute feature ID in lowercase (e.g., `SF-14` → `sf-14`)
3. Run:
   ```bash
   git worktree add "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}" -b "feature/{feature-id-lowercase}"
   ```
4. Add to context file:
   - `"worktreePath": "{worktreeBase}/{project-dir-name}-{feature-id-lowercase}"`
   - `"branchName": "feature/{feature-id-lowercase}"`
5. Display:
   ```
   Git worktree created: {worktreePath}
   Branch: {branchName}
   Implementation phases will run from this directory.
   ```

### 7c: Next steps

Display based on `complexityTier`:

**Simple:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase4-implement-sonnet` — context will auto-load.

**Medium:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase2-review` — context will auto-load.
> (For an early sanity-check first, run `/wf-phase1-iterate` instead.)

**Complex:**
> Phase 1 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase1-iterate` for early agent feedback — context will auto-load.
> After iterate, start another new session and run `/wf-phase2-review`.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
