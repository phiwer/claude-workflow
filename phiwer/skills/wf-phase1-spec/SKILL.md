---
name: wf-phase1-spec
description: Phase 1a - Read the roadmap entry for a feature and ask the user one scoping question. Run wf-phase1-spec-write after answering.
argument-hint: [feature-id] (e.g., SF-14)
allowed-tools: Read, Bash, Write, AskUserQuestion
model: sonnet
---

# Feature Scoping

Read the roadmap entry for the given feature, show it to the user, and ask one clarifying question. That is all this skill does.

## Step 1: Read config

Read `.claude/workflow/project-config.json`. Extract:
- `roadmapFile` (default: `ROADMAP.md`)
- `specDir` (default: `docs/specs`)
- `archiveDir` (default: `docs/specs/archive`)
- `worktreeBase` (default: `null`)

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` to get `GIT_MAIN_ROOT`.

## Step 2: Identify the feature

Read `{roadmapFile}`.

If no feature ID was provided in `$ARGUMENTS`:
- Find features marked ⬜ (not yet implemented)
- Use `AskUserQuestion` to let the user pick one (up to 4 options, ID + description each)

Once you have a feature ID, extract its name, description, and any listed requirements.

## Step 3: Ask the user

Display:
- Feature ID and name
- Description (verbatim or lightly condensed)
- Key requirements or bullets from the roadmap

Then use `AskUserQuestion`:

> **"Does this look right? Anything to add, clarify, or constrain before I write the spec?"**
> - "Looks good — proceed as-is"
> - (Other = free text)

## Step 4: Save partial context and prompt for next step

Write `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "worktreeBase": "{worktreeBase or null}",
  "roadmapSummary": "{the description and requirements you extracted}",
  "userClarification": "{the user's answer, or empty string if they picked proceed as-is}"
}
```

Then display:

> Scoping saved. Now run:
>
> `/phiwer:wf-phase1-spec-write`
