---
name: wf-phase1-spec
description: Phase 1a - Ask the user to describe the feature before writing the spec. Run wf-phase1-spec-write after answering.
argument-hint: [feature-id] (e.g., SF-14)
allowed-tools: Write, AskUserQuestion
model: sonnet
---

# Feature Scoping

Feature ID: $ARGUMENTS

## Step 1: Ask the user

If a feature ID was provided, use `AskUserQuestion` to ask:

> **"{FEATURE-ID}: Describe what this feature should do. Include any constraints, edge cases, or context that would help me write a good spec."**

If no feature ID was provided, use `AskUserQuestion` to ask:

> **"Which feature do you want to spec? Provide the feature ID and describe what it should do, including any constraints or context."**

## Step 2: Save context

Write `.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-spec",
  "userDescription": "{the user's answer verbatim}"
}
```

## Step 3: Prompt for next step

Output:

> Scoping saved. Run `/phiwer:wf-phase1-spec-write` to generate the spec.
