---
name: wf-phase1-iterate
description: Phase 1 iteration - quick 3-agent review of a DRAFT spec before formal Phase 2 review. Catches issues early with specialized perspectives.
model: opus
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion, Bash
---

# Phase 1: Iterate on Specification

Quick review with 3 specialized agents to catch issues before committing to formal Phase 2 review.

**Purpose**: Specialized critical review to find gaps the spec creator may have missed.

## Spec to Review

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
   - Check if `lastPhase` is `wf-phase1-spec` (expected previous phase)
   - If valid, use AskUserQuestion:
     - header: "Continue workflow?"
     - question: "Found context from wf-phase1-spec. Continue with this spec?"
     - option1: label="Yes, continue with {specPath}", description="Use saved context from wf-phase1-spec"
     - option2: label="No, start fresh", description="Ignore context and auto-detect specs"
   - If user selects "Yes": use `specPath` from context
   - If user selects "No": delete context file and continue to step 1b

#### 1b: Auto-Detect (if no context or user chose fresh start)

1. Use Glob to find specs: `{specDir}/*/*.md`
2. Filter for `*_SPEC.md` files only
3. For each spec found, check its Status and phase progress:
   - Read the spec to get its Status
   - Check if `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE2_REVIEW.md` exists

4. **Phase-aware filtering**:
   - **Include**: Specs with Status: DRAFT and NO Phase 2 review
   - **Exclude**: Specs that already have a Phase 2 review (suggest `/wf-phase3-consolidate`)
   - **Exclude**: Specs with Status: IMPLEMENTED

5. If no eligible specs found: suggest running `/wf-phase1-spec` to create one.

6. If multiple eligible specs found, use AskUserQuestion to ask which to iterate on

7. If exactly one eligible spec, confirm with user: "Found DRAFT spec: {path}. Review this spec?"

### Step 2: Validate Phase

Before proceeding, verify:

1. The spec has Status: DRAFT (or similar pre-review status)
2. No `{FEATURE-ID}_PHASE2_REVIEW.md` exists in archive

If Phase 2 review already exists:
```
⚠️ This spec has already completed Phase 2 review.

- To address Phase 2 feedback: /wf-phase3-consolidate
- To re-review after major changes: Delete the Phase 2 review first

Aborting iteration.
```

### Step 3: Read the Spec and Available Agents

1. Read the spec file to understand the feature
2. Use Glob to find available agents: `.claude/agents/*.md`
3. Read the `name:` and `description:` frontmatter from each agent file
4. Select the 3 most relevant agents for this spec based on their descriptions and the spec content
5. If fewer than 3 agents exist, use all available agents

**Selection guidance**: Choose agents whose descriptions best match the spec's concerns.
For example, a spec touching API design should include an `api-designer` or `backend-dev`
if available; a spec with database changes should include `database-dev` if available.
`qa-engineer` is almost always one of the 3 if available.

### Step 4: Spawn 3 Review Agents in Parallel

Use the Task tool to spawn the 3 selected agents **in parallel**.

For each agent, provide the full spec content and ask for a **focused quick review**:
- Top 2-3 concerns (blocking issues only)
- Top 2-3 suggestions
- Quick verdict: PROCEED / REVISE

Explicitly ask each agent to check:
- **Implementability**: Can this spec be implemented from what's written? Are there logic gaps or missing detail that would block a developer?
- **Testability**: Is the Test Strategy section specific enough to actually write the tests listed, or are the requirements too vague to verify?

### Step 5: Summary (No File Written)

After all agents complete, display the full results:

---

## Phase 1 Iteration Results

**Spec**: {spec path}
**Status**: {DRAFT}

### Blocking Issues
{List any critical issues that must be fixed, or "None found"}

### Top Suggestions
1. {most important suggestion}
2. {next most important}
3. {etc.}

### Agent Verdicts

| Agent | Verdict | Key Concern |
|-------|---------|-------------|
| {agent1} | {PROCEED/REVISE} | {one-liner or "None"} |
| {agent2} | {PROCEED/REVISE} | {one-liner or "None"} |
| {agent3} | {PROCEED/REVISE} | {one-liner or "None"} |

### Detailed Agent Feedback

#### {Agent 1}
**Strengths**: {full list from agent}
**Concerns**: {full list from agent}
**Recommendations**: {full list from agent}
**Full Rationale**: {agent's reasoning}

#### {Agent 2}
{same structure}

#### {Agent 3}
{same structure}

---

Then proceed to the Next Step section.

### Next Step: Write Context and Prompt

#### Write Context File

Create/update `.claude/workflow/phase-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase1-iterate",
  "timestamp": "{current ISO datetime}",
  "context": {
    "agentVerdicts": {
      "{agent1}": "{PROCEED/REVISE}",
      "{agent2}": "{PROCEED/REVISE}",
      "{agent3}": "{PROCEED/REVISE}"
    },
    "blockingIssues": {count or 0},
    "topSuggestions": ["{list top 3 suggestions}"],
    "areasOfAgreement": ["{what all agents agreed on}"]
  }
}
```

#### Phase Complete — Next Steps

**If any REVISE verdicts or blocking issues** — display:
> Phase 1.5 complete. Blocking issues found — context saved.
>
> **Before continuing**: Fix the blocking issues in the spec, then start a new session and
> run `/wf-phase1-iterate` again (or skip to `/wf-phase2-review` if the issues are minor).

**If all PROCEED and no blocking issues** — display:
> Phase 1.5 complete. All agents approved. Context saved.
>
> **Next**: Start a new session and run `/wf-phase2-review` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
