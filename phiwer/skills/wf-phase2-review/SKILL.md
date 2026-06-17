---
name: wf-phase2-review
description: Run Phase 2 design review with 2-6 subagents (dynamic selection). Produces a PHASE2_REVIEW.md artifact in the archive directory.
model: opus
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Task, AskUserQuestion, Bash
---

# Phase 2 Design Review

Run a comprehensive design review using specialized subagents selected based on feature type.

## Spec to Review

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
3. Use `{specDir}` and `{archiveDir}` throughout this skill
4. Find the main worktree root:
   ```
   Run: git worktree list 2>/dev/null | head -1 | awk '{print $1}'
   Use the result as GIT_MAIN_ROOT. All context files live at:
     {GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json
   Falls back to .claude/workflow/ if git command fails.
   ```

### Step 1: Handle Missing Arguments / Auto-Detect Spec

#### 1a: Check for Context File

If no spec path was provided in arguments:

1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`. If multiple found, ask the user which feature to continue (AskUserQuestion). If one found, use it. Use the found file as the context file path below.
   - **Reconcile before trusting it.** The on-disk artifacts are the source of truth; the context file is only a cache a prior phase may have failed to update (interrupted, errored, or you took over manually). Before relying on `lastPhase`, check it against reality — the spec `Status`, which `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE*.md` documents exist, and whether the implementation and tests are present. If they disagree, **trust the artifacts**, tell the user about the drift, and rewrite the context to match before continuing.
2. Check if the context file exists
3. If exists:
   - Read and parse the JSON
   - Check if timestamp is within 24 hours (ignore if older)
   - Check if `lastPhase` is `wf-phase1-spec` or `wf-phase1-iterate`
   - If valid, use AskUserQuestion:
     - header: "Continue workflow?"
     - question: "Found context from {lastPhase}. Continue with this spec?"
     - option1: label="Yes, continue with {specPath}", description="Use saved context from {lastPhase}"
     - option2: label="No, start fresh", description="Ignore context and auto-detect specs"
   - If user selects "Yes":
     - Use `specPath` from context
     - Display: "Continuing from {lastPhase}: {featureId}"
     - If context includes agent verdicts (from wf-phase1-iterate), display them
   - If user selects "No": delete the context file and continue to step 1b

#### 1b: Auto-Detect (if no context or user chose fresh start)

1. Use Glob to find active specs: `{specDir}/*/*.md`
2. Filter out README.md and non-spec files (look for `*_SPEC.md` pattern)
3. If exactly one spec found with Status: DRAFT, use it
4. If multiple specs found, use AskUserQuestion to ask the user which spec to review

### Step 2: Read the Spec

Read the spec file to understand the feature.

### Step 3: Discover Available Agents

1. Use Glob to list all files in `.claude/agents/*.md`
2. For each agent file found, read its frontmatter to extract `name:` and `description:`
3. Build a list of available agents with their names and descriptions

If no agents are found in `.claude/agents/`, display:
```
⚠️ No review agents found in .claude/agents/.

Run /wf-init to set up agents for this project, then re-run /wf-phase2-review.
```
And stop.

### Step 4: Select Relevant Agents (Dynamic Selection)

Based on the spec content and available agent descriptions:

1. Analyze the spec to understand what domains it touches (API design, data layer,
   frontend, game mechanics, infrastructure, testing, etc.)
2. For each available agent, reason about whether its described focus area is relevant
   to this spec
3. Use a single AskUserQuestion call with all agents listed across batched questions:
   - Each question has `multiSelect: true` and up to 4 options
   - Batch agents into groups of up to 4; use one question per batch
   - Label each question clearly (e.g., "Review agents (1/2)", "Review agents (2/2)")
   - If groups have a natural domain split (backend vs. frontend), use that as the label
   - Pre-select agents whose descriptions best match the spec's concerns
   - Include ALL available agents — never hide agents behind "Other"

   Example for 6 agents:
   - Question 1 (multiSelect): "Review agents — backend/infra" with options [agent1, agent2, agent3, agent4]
   - Question 2 (multiSelect): "Review agents — frontend/quality" with options [agent5, agent6]

   Example for ≤4 agents:
   - Single question (multiSelect): "Which agents should review this spec?" with all agents listed

4. Collect all selected agents across all questions. Store combined selection for Step 5.

**Note**: An agent describing test coverage or QA is almost always relevant. Pre-select it
if available. Use your judgment — selecting 2-4 focused agents is better than selecting all
of them; narrow focus = sharper feedback.

**Token Savings**: Selecting 2-4 relevant agents instead of all saves 50%+ of Phase 2 tokens.

### Step 5: Extract Feature ID

From the spec path, extract:
- Feature ID (e.g., `SF-14` from `{specDir}/sf14/SF14_SCIENCES_SPEC.md`)
- Feature directory name (e.g., `sf14`)

### Step 6: Create Archive Directory

Create the archive directory if it doesn't exist:
`{archiveDir}/{feature-dir}/`

### Step 7: Spawn Selected Review Agents in Parallel

Use the Task tool to spawn the **selected agents** from Step 4 **in parallel** (single message,
multiple Task calls).

For each selected agent, provide the full spec content and ask for a structured review with:
- **Strengths** (what's good)
- **Concerns** (issues to address)
- **Recommendations** (suggestions)
- **Verdict** (APPROVED / APPROVED with revisions / NEEDS REVISION)

### Step 8: Create the Phase 2 Review Document

After all agents complete, create `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE2_REVIEW.md`:

```markdown
# {FEATURE-ID} Phase 2: Specification Review

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 2 of 6 (Specification Review)
**Specification Version**: v1.0

---

## Review Process

This document contains reviews from {count} specialized subagents analyzing the {FEATURE-ID}
specification from different perspectives.

---

## {Agent 1 Name} Review

**Focus**: {agent's described focus area}

### Strengths ✅
{from agent response}

### Concerns ⚠️
{from agent response}

### Recommendations 💡
{from agent response}

**Verdict**: {APPROVED / APPROVED with revisions / NEEDS REVISION}

---

{Repeat for each selected agent}

---

## Consolidated Feedback Summary

### Critical Issues (Must Address)
{numbered list of blocking issues from all agents}

### Recommended Changes
{numbered list of non-blocking improvements}

### Nice to Have
{numbered list of optional enhancements}

### Questions for Phase 3
{numbered list with checkboxes for items needing resolution}

---

## Phase 2 Verdict

**Status**: {APPROVED / APPROVED WITH REVISIONS / NEEDS REVISION}

**Required for Phase 3**:
{numbered list of must-do items before proceeding}

---

**Review Completed**: {date}
**Reviewers**: {list only selected agents, comma-separated}
**Agents Skipped**: {list skipped agents with reason, or "None (full review)"}
**Next Phase**: Phase 3 - Consolidation
```

### Step 9: Output Summary

After writing the file, display:

1. Confirmation the file was created at its path
2. The overall verdict with breakdown by agent
3. Full list of critical issues with which agent raised them
4. Full list of recommended changes with agent attribution
5. Full list of questions for Phase 3
6. Any areas of agreement/disagreement between agents

Then proceed to Step 10.

### Step 10: Write Context and Prompt for Next Step

#### 10a: Write Context File

Create/update `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`:

```json
{
  "specPath": "{full spec file path}",
  "featureId": "{FEATURE-ID}",
  "lastPhase": "wf-phase2-review",
  "timestamp": "{current ISO datetime}",
  "context": {
    "overallVerdict": "{APPROVED / APPROVED WITH REVISIONS / NEEDS REVISION}",
    "criticalIssues": {count of critical issues},
    "recommendedChanges": {count of recommended changes},
    "questionsForPhase3": ["{list key questions needing decisions}"],
    "agentConsensus": ["{areas where selected agents agreed}"],
    "selectedAgents": ["{list of agents that reviewed}"],
    "skippedAgents": ["{list of agents skipped}"]
  }
}
```

#### 10c: Record token usage

Append this phase's token usage to the review document and context. The selected review subagents are the bulk of Phase 2's cost and are captured automatically:

```bash
TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
[ -n "$TU" ] && python3 "$TU" --phase wf-phase2-review \
  --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" \
  --artifact "{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE2_REVIEW.md" \
  || echo "token-usage: script not found, skipping (best-effort)"
```

#### 10b: Phase Complete — Next Steps

Display:
> Phase 2 complete. Context saved.
>
> **Next**: Start a new session and run `/wf-phase3-consolidate` — context will auto-load.

Do NOT offer next-phase navigation via AskUserQuestion. The user must manually start a new session.
