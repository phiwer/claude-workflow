---
name: wf-close
description: Close a ticket built with /wf-build - verify it against the design doc's Verification section, make the doc match what was actually built (As-built, status built), write a short retrospective into the doc, feed project-general lessons into CLAUDE.md / .claude/rules, and record the token totals. Use after /wf-build finishes.
argument-hint: [TICKET-ID or doc path]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task, AskUserQuestion, EnterWorktree
model: sonnet
---

# Close a design-first ticket

A doc that describes a system that doesn't exist is worse than no doc, because future sessions
will trust it. This session makes the doc true, then harvests what the ticket taught.

## Input

$ARGUMENTS

## Step 0: Config and doc

Same as `/wf-build` Step 0: read config (`designDir`, `specDir`, `archiveDir` =
`docs/specs/archive`, `roadmapFile` = `ROADMAP.md`), find the doc
and context file, enter the worktree if one is recorded. The doc must be `approved` with every
chunk ticked; if not, point the user at `/wf-build` and stop.

## Step 1: Verify against the doc

1. Read the doc's Verification section and the `/wf-build` review verdict (ask the user if it
   isn't in the conversation or git log; don't re-run a full review that already came back
   CLEAN).
2. For each Verification item, confirm it is covered: the test exists and asserts the stated
   behaviour, or the behaviour was observed. List any gap.
3. Compare the changed files (`git diff --stat $(git merge-base HEAD {base})..HEAD`) against the
   Implementation table. Every difference must be explained in As-built.
4. If `/wf-build`'s review was never run or never came back CLEAN, dispatch a fresh
   `phiwer:code-reviewer` with the doc path and the range now, and triage with the user.

Gaps are the user's call: fix now (small: here; larger: `/wf-build` for a new chunk added to the
doc), or accept and record under Open questions.

## Step 2: Make the doc true

- Fill in As-built: deviations from the plan and why, anything a future reader would otherwise
  be misled by. Remove nothing from Alternatives.
- Set `status: built`, bump `updated:`.

## Step 3: Retrospective (short, in the doc)

Append a `## Retrospective` section to the doc, at most ~15 lines:
- **Goldfish/implementer gaps:** what the doc missed that a STOPPED, a doc gap or a review
  finding exposed, and at which stage it was caught.
- **What went well / what to change** in the process, each traced to a cause.
- **CLAUDE.md candidates:** only project-general lessons a future, unrelated ticket would
  benefit from, each drafted as the exact text and target file. Tag each with the ticket, e.g.
  `(TRA-1234)`, so the citation check can track it.

## Step 4: Update project rules

Show the candidates to the user and apply the approved ones. A test rule goes in
`.claude/rules/test-rules.md`, a production-code rule in `.claude/rules/architecture-rules.md`
(if those files exist); root CLAUDE.md only for genuinely universal rules. Then do a surgical
consolidation pass across CLAUDE.md and `.claude/rules/*.md`: merge duplicates, resolve
contradictions (keep the newer/more specific), condense bloat. Report every change.

Check rule citations first:
```bash
CC="{SKILL_DIR}/../../scripts/check-rule-citations.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
[ -f "$CC" ] && python3 "$CC" --rules CLAUDE.md .claude/rules/*.md --archive-dir "{archiveDir}" --design-dir "{designDir}" \
  || echo "check-rule-citations: script not found, skipping (best-effort)"
```
Never-cited rules are candidates for the user to reconsider, not automatic deletions.

If `.claude/context/` exists, regenerate `.claude/context/{agent}.md` for each agent in
`.claude/agents/` from the updated rules (same as `/wf-init` Step 6).

## Step 5: Roadmap

If `{roadmapFile}` exists, mark the ticket complete. If `{specDir}/SPECS_INDEX.md` exists, add
or update the ticket's row (status `COMPLETE`, linked to the design doc), matching the existing
columns.

## Step 6: Token totals

Before deleting the context file:
```bash
TU="{SKILL_DIR}/../../scripts/record-token-usage.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
CTX="{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json"
LEDGER="{specDir}/TOKEN_LEDGER.csv"
if [ -f "$TU" ]; then
  python3 "$TU" --phase wf-close --context "$CTX" --ledger "$LEDGER" --ticket "{TICKET}"
  python3 "$TU" --mode total --context "$CTX" --artifact "{doc path}" --ledger "$LEDGER" --ticket "{TICKET}"
else
  echo "token-usage: script not found, skipping (best-effort)"
fi
```
This appends a "Token Usage (all phases)" table to the doc. Check that the table lists every
phase the ledger has for the ticket (`wf-design*`, `wf-build*`, `wf-close`); if one is missing,
the script's stderr says where it looked, so fix the table from the ledger rows before
committing.

## Step 7: Commit and finish

1. Commit the doc, rule, roadmap and ledger changes following the project's commit rules (one
   commit for the doc close-out including `{specDir}/TOKEN_LEDGER.csv`, a separate one for rule
   changes). The ledger is the only durable per-phase record once the context file is deleted,
   so it must be committed, even if it was untracked before.
2. Delete `{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json`.
3. Display: verification result, As-built summary, rule changes, never-cited rules flagged,
   token total. Then:
   > **{TICKET}** is built and closed. Start a new session with `/wf-design` for the next one.
