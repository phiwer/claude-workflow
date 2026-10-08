---
name: wf-build
description: Implement an approved /wf-design doc chunk by chunk. Runs in a fresh session, resumes from the doc alone, dispatches one fresh implementer subagent per chunk, reviews and commits each chunk, and ends with a capped rule-compliance review. Use after /wf-design approval, or to resume a build that was interrupted.
argument-hint: [TICKET-ID or doc path]
allowed-tools: Read, Glob, Grep, Bash, Edit, Task, AskUserQuestion, EnterWorktree
model: sonnet
---

# Build an approved design

This session is an orchestrator, not an author. The **implementer** subagent writes the code,
one chunk per dispatch, from the doc alone; that makes implementation the final goldfish test,
and keeps this context small. Your job: pick the next chunk, dispatch, review, commit, and keep
the doc true.

## Input

$ARGUMENTS

## Step 0: Config and doc

1. Read `.claude/workflow/project-config.json` (defaults: `designDir` = `docs/design`,
   `specDir` = `docs/specs`). `GIT_MAIN_ROOT` = `git worktree list 2>/dev/null | head -1 | awk '{print $1}'`.
2. Find the doc: the argument (path, or ticket → `{designDir}/{ticket-lower}-*.md`), else glob
   `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json` **and**
   `{GIT_MAIN_ROOT}/.claude/worktrees/*/.claude/workflow/*-context.json`, and ask which ticket
   if more than one. A session that planned from inside a worktree could only write the
   worktree copy, so the second glob is not optional. If both exist for one ticket, prefer the
   worktree copy — it is the one a worktree-isolated session was able to keep current.
3. If the context has `worktreePath` and you are not in it, `EnterWorktree` it before anything
   else.
4. Read the doc. **The doc is the source of truth; the context file is only a cache.** If
   `status` is not `approved`, stop and tell the user to finish `/wf-design` first.
5. Read the Implementation table, the chunk notes, the Chunk progress list and As-built. The
   next chunk is the first unticked one whose dependencies are ticked. Cross-check against
   `git log` for the ticket prefix: if a chunk's commit exists but it isn't ticked, tick it and
   tell the user about the drift.

Tell the user in two lines: which chunks are done, which one is next.

## Step 1: The chunk loop

Per chunk:

1. **Dispatch** a fresh `phiwer:implementer` subagent with exactly:
   ```
   Doc: {doc path}
   Chunk: {n}
   ```
   Pass nothing else. If it needs context the doc lacks, that is a doc gap to fix, not
   something to smuggle in through the brief.
   If the doc's frontmatter has `implementer: opus`, dispatch with the model set to `opus`;
   otherwise use the agent's default (Sonnet). Use the same model for every implementer
   dispatch on this ticket, including redispatches and review fixes.
2. **Review** its report, then read `git diff` against the chunk's rows. Check that only the
   chunk's files changed, and that small deviations were logged in As-built.
3. **Handle the outcome:**
   - **DONE**: fold any reported doc gaps into the doc. Commit the chunk as one commit,
     following the project's commit rules in CLAUDE.md (ticket prefix, subject/body style).
     Tick the chunk in Chunk progress (same commit). Summarize for the user in a line or two.
   - **STOPPED**: bring the escalation to the user with your recommendation. Once decided,
     update the doc (Implementation, Alternatives or As-built), then dispatch a *new*
     implementer for the same chunk. A decision that changes the design materially (a new
     public interface, a different aggregate or transaction boundary) means the doc should go
     back through `/wf-design`; say so and let the user choose.
   - **BLOCKED**: resolve the environment problem with the user, then redispatch.
4. Continue with the next chunk.

Dispatch chunks in parallel only when the doc's chunk notes say they are independent and their
files don't overlap; otherwise run them in order. When in doubt, sequential is cheaper than
untangling a conflict.

**Checkpoint long builds.** Every 3-4 chunks, record token usage (Step 3) and suggest the user
continue in a fresh session with `/wf-build {TICKET}`: it resumes from the doc and git history,
and a fresh context is cheaper than a long one. Guidance, not a hard stop.

## Step 2: Rule-compliance review (capped)

When all chunks are ticked:

1. Determine the base: `git symbolic-ref --quiet refs/remotes/origin/HEAD | sed 's@^refs/remotes/@@'`,
   falling back to `origin/main` → `main` → `master`. Range = `$(git merge-base HEAD "$BASE")..HEAD`.
2. Dispatch a fresh `phiwer:code-reviewer` (or the project's `.claude/agents/compliance-reviewer.md`
   if it exists) with the doc path and that range.
3. Fix every Blocker/Major. Small fixes you may make yourself; anything bigger, dispatch an
   implementer with the doc path, the chunk it belongs to, and nothing else, after first adding
   the finding to As-built so the doc carries it. Fold each fix into the commit of the chunk it
   corrects where practical (fixup + autosquash), otherwise a follow-up commit. Note
   `git rev-parse HEAD` before fixing.
4. **Second pass, scoped:** only the fix commits (`{sha-before-fixes}..HEAD`), with a new
   reviewer. Never re-review the whole range.
5. **Cap at 2 passes.** If pass 2 isn't CLEAN, stop and report the residual items to the user
   plainly; a human decides.
6. Run the project's full test and static-analysis commands (see CLAUDE.md). Delegate the run
   to a subagent that reports counts and failures only, not full logs.

## Step 3: Record and hand off

1. Record token usage with phase key `wf-build`, or `wf-build-s2`, `-s3`… if the context
   already has a `wf-build*` entry (each session records its own row):
   ```bash
   TU="{SKILL_DIR}/../../scripts/record-token-usage.py"  # {SKILL_DIR} = the "Base directory for this skill" shown when this skill loaded
   if [ -f "$TU" ]; then
     python3 "$TU" --phase {phase-key} --context "{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json" --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{TICKET}"
   else
     echo "token-usage: script not found, skipping (best-effort)"
   fi
   ```
   The ledger's `subagent_total` column is the implementers' and reviewers' share.
2. Set `lastPhase: "wf-build"` in `{GIT_MAIN_ROOT}/.claude/workflow/{TICKET}-context.json`
   (absolute path; a relative one resolves inside the worktree). If you entered a worktree in
   Step 0, this write is refused by worktree isolation — write the worktree's own
   `.claude/workflow/{TICKET}-context.json` instead and say so in the Step 3 summary, so the
   user knows the main-root copy is stale.
3. Display: chunks built, commits, review verdict and passes, test result, anything handed to
   the user. Then:
   > **Next**: start a new session and run `/wf-close {TICKET}`.
