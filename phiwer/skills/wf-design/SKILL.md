---
name: wf-design
description: Design-first planning (Elephant-Goldfish). The default entry point for any ticket - one live session co-designs with the user and keeps a design doc as the source of truth, while fresh-context subagents research the codebase, test that the doc stands on its own (goldfish), and critique it. Ends with an approved doc that /wf-build implements chunk by chunk. Use when the user wants to plan, design or scope a change, says "let's plan", "design doc", "before we code", or resumes a doc in the design directory.
argument-hint: [TICKET-ID] [what the change should do]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task, AskUserQuestion, EnterWorktree
model: opus
---

<!--
Model: Opus, deliberately. Planning is the low-volume, high-judgment side of a ticket; the
high-volume side (implementation) runs in /wf-build on Sonnet in a separate session. Do not let
this session run the build: that is how an Opus context ends up paying for diffs and test output.
-->

# Design a change (Elephant-Goldfish)

This session is the **Elephant**: it holds the whole conversation, every argument and every
decision. That is its strength and its weakness, because anything it knows but the doc does
not say is invisible to everyone else, including the /wf-build session and a future session
after compaction.

The **design doc** is the durable state. The **Goldfish** is a subagent that sees nothing but
the doc and the files it references. If the Goldfish has to guess, the doc has a gap.

The goal of this skill is a doc that a stranger could implement from, with the user's judgment
encoded in it. Code comes after that, in a different session.

## Input

$ARGUMENTS

The arguments hold the ticket ID and the user's description of the change, plus any attached
images. Treat the description as the primary definition of the work. If no ticket ID is given,
ask for one (it names the doc, the worktree, the ledger row and the commit prefix).

## Step 0: Config

Read `.claude/workflow/project-config.json` (defaults if absent):
- `designDir` = `docs/design`
- `designTemplate` = unset (use `references/doc-template.md` from this skill)
- `specDir` = `docs/specs` (only used for the token ledger location)
- `roadmapFile` = `ROADMAP.md`
- `worktreesEnabled` = `false`

Run `git worktree list 2>/dev/null | head -1 | awk '{print $1}'` → `GIT_MAIN_ROOT`. The
context file is `{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json`.

If `{roadmapFile}` exists and has an entry for the ticket, use it to supplement (never
override) the user's description.

## Step 1: Resume or start

- If a doc for this ticket exists (glob `{designDir}/{ticket-lower}-*.md`, or `docPath` in the
  context file), read it and the files it references, then tell the user in a few sentences
  where things stand: status, which gates are met, what is open. If `worktreePath` is set in
  the context and you are not in it, `EnterWorktree` it first. Continue from there.
- If the doc is `approved` or `built`, say so and point at `/wf-build` or `/wf-close` instead
  of re-planning, unless the user wants to reopen the design (then set `status: draft`).
- Otherwise, start at Step 2.

## Step 2: Propose a tier

Read `references/tiers.md`. Propose small, medium or large with a one-line reason and let the
user confirm or override (AskUserQuestion). The user decides. Don't run large-tier ceremony on
small work; that is how a process gets abandoned.

For **small**: no doc. State the files you intend to touch and why, then implement directly in
this session, following CLAUDE.md and `.claude/rules/`, with tests. Stop using this skill's
remaining steps. Escalate to medium if the change turns out bigger than it looked.

## Step 3: Create the doc early

For medium and large:

1. If `worktreesEnabled`: use **`EnterWorktree`** with name `{ticket-lower}` now, so the doc is
   born on the feature branch. Read back the path and branch.
2. Create `{designDir}/{ticket-lower}-{short-name}.md` from `designTemplate` (or this skill's
   `references/doc-template.md`), headings and frontmatter only, `status: draft`.
3. If images were attached, save them under `{designDir}/{ticket-lower}-assets/` and transcribe
   every label, arrow and annotation into the doc's Context section. Chat images don't survive
   the session; the transcription is what the Goldfish and implementer will see.
4. Write the context file:
   ```json
   {
     "featureId": "{TICKET}",
     "docPath": "{doc path, relative to repo root}",
     "designDir": "{designDir}",
     "tier": "medium | large",
     "lastPhase": "wf-design",
     "worktreePath": "{if any}",
     "branchName": "{if any}"
   }
   ```

Update the doc whenever a decision is made, an assumption is settled or an alternative is
rejected, and bump `updated:`. A decision that lives only in the conversation is lost at
compaction. The test: if this session died now, could a fresh one resume from the doc?

## Step 4: Plan toward the gates

Read `references/gates.md`. The gates are exit criteria, not a script: work on them in
whatever order the conversation goes, and keep the checklist in the doc current. Approval
comes only when every gate for the tier is met.

How to behave while planning:

- **Interrogate before designing.** Ask a few pointed questions at a time rather than a
  twenty-item dump. Probe the edges: failure modes, scale, ownership, what happens to existing
  data and callers, what "done" means.
- **Disagree usefully.** Before agreeing with a claim or a proposal, state the strongest
  objection to it. If there is no good objection, say so briefly and move on; manufactured
  objections waste the user's attention.
- **Propose the first design yourself**, in prose and block diagrams, with short pseudocode
  only where it clarifies. Your first draft reveals whether you have understood the problem;
  reacting to the user's design would hide your blind spots.
- **Don't guess about the system.** If you are unsure how something works, say so and either
  read the code or dispatch the researcher. Wrong beliefs about the system at this stage turn
  into wrong code later. Unverified load-bearing claims go in Assumptions, marked as such.
- **Record the losers.** Every rejected alternative goes in the doc with the reason it lost.
  This prevents the same idea from being re-proposed during implementation.
- **Respect the project's rules.** The design must be implementable without breaking
  `CLAUDE.md` or `.claude/rules/*.md`. If it can't be, that is a decision for the user, recorded
  in the doc.
- **Chunk for review.** Cut the Implementation table into chunks that each form one logical,
  reviewable change (one commit) and can be verified on their own. Tests live in the same chunk
  as the code they cover.

## Step 5: Dispatch subagents

Subagent reports land back in this context, so keep briefs precise and demand compact output.
The plugin ships these agents as `phiwer:researcher`, `phiwer:goldfish`, `phiwer:critic`.

**researcher**: for questions about the existing system or external facts. For a
domain-specific question, a project agent from `.claude/agents/` (e.g. a DDD or security
agent) can be used instead, with the same brief shape.

```
Question: <one specific question>
Scope: <directories/files to look in>
Why it matters: <one sentence, so it knows what evidence is relevant>
```

Parallelize independent questions. Merge what comes back into the doc's Context or
Assumptions with file references, rather than leaving it only in the conversation.

**goldfish**: tests whether the doc stands alone. Pass it **only the doc path**, never a
summary, explanation or extra context. Anything you add is the Elephant's memory leaking in,
and it defeats the test.

```
Doc: {doc path}
```

**critic**: finds what the design missed. Again, pass only the doc path. Required for large,
optional for medium.

Run the goldfish first; there is no point critiquing a doc that cannot be understood. Loop:
fix the doc, spawn a *new* goldfish or critic (never reuse one; it is no longer a goldfish),
and stop when the goldfish's guess-list is empty or trivial and the critic returns no blocker
or major findings. **Respect the round caps in `references/tiers.md`**: when a cap is hit, stop
and hand the residue to the user instead of looping again.

## Step 6: Triage findings with the user

Critic findings are input to the user's judgment, not instructions. Present them grouped by
severity with your own recommendation for each: accept, reject with reason, or needs the
user's call. Record accepted changes in the doc and rejected ones under Alternatives or Open
questions. Expect a fair share of findings to be noise; filtering is the point.

## Step 7: Approval

Only the user approves. When all gates for the tier are met, summarize the design in a few
lines (problem, chosen approach, chunk list) and ask for approval via AskUserQuestion. On
approval, set `status: approved` in the frontmatter and tick the gates.

## Step 8: Record and hand off

1. Record token usage. Use phase key `wf-design`, or `wf-design-s2`, `-s3`… if the context
   file's `tokenUsage` already has a `wf-design*` entry (resumed planning):
   ```bash
   TU="{SKILL_DIR}/../../scripts/record-token-usage.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
   if [ -f "$TU" ]; then
     python3 "$TU" --phase {phase-key} --context "{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{TICKET}"
   else
     echo "token-usage: script not found, skipping (best-effort)"
   fi
   ```
   Also do this before suggesting the user continue planning in a fresh session.
2. Display:
   > Design approved: `{doc path}`
   >
   > **Next**: start a new session and run `/wf-build {TICKET}`. It works from the doc alone.

Do not start implementation in this session for medium or large tiers, and do not offer it via
AskUserQuestion. If the user explicitly insists, say that it defeats the cost split and the
final goldfish test, then comply.
