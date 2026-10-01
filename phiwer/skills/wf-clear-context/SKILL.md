---
name: wf-clear-context
description: Clear the workflow context file to start fresh on a new feature
argument-hint: [feature-id] (e.g., SF-14)
model: haiku
allowed-tools: Read, Glob, Bash, AskUserQuestion
---

# Clear Workflow Context

Use this command to clear saved workflow context and start fresh.

## Arguments

$ARGUMENTS

## Instructions

### Step 0: Find Main Worktree Root

```
Run: git worktree list 2>/dev/null | head -1 | awk '{print $1}'
Use the result as GIT_MAIN_ROOT. Context files live at:
  {GIT_MAIN_ROOT}/.claude/workflow/*-context.json
Falls back to .claude/workflow/ if git command fails.
```

### Step 1: Determine Which Context File to Clear

**If a feature ID was provided in arguments** (e.g., `SF-14`):
- Target file: `{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json`
- Delete it if it exists, report if not found

**If no feature ID was provided**:
1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`
2. **If no files found**: report that no context files exist
3. **If exactly one file found**: delete it and report
4. **If multiple files found**: use AskUserQuestion:
   - header: "Which context to clear?"
   - question: "Multiple feature context files found. Which would you like to clear?"
   - List each file as an option (label = filename, description = full path)
   - Include a final option: label="Clear all", description="Delete all context files listed above"

   Based on user selection:
   - If a specific file: delete only that file
   - If "Clear all": delete all listed context files

### Step 2: Delete and Confirm

For each file to delete:
```bash
rm -f "{context-file-path}"
```

Then output:
```
Workflow context cleared: {filename(s) deleted}

Design docs are untouched. Run /wf-design to start a new ticket; /wf-build and /wf-close
still resume an existing ticket from its doc, but token usage recorded for it so far is gone
from the context (the ledger rows remain).
```
