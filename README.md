# claude-workflow

A design-first feature workflow for Claude Code, based on Dave Rensin's
[Elephant-Goldfish model](https://drensin.medium.com/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874).
One live session co-designs a change with you and keeps a design doc as the source of truth;
fresh-context subagents research the codebase, test that the doc stands on its own, critique
it, and later implement it chunk by chunk from the doc alone.

## Install

```
/plugin marketplace add phiwer/claude-workflow
/plugin install phiwer@phiwer
/reload-plugins
```

Skills are namespaced as `/phiwer:wf-init`, `/phiwer:wf-design`, etc.

**Updating** after the repo changes:

```
/plugin marketplace update phiwer
/plugin update phiwer
/reload-plugins
```

The old six-phase pipeline (`wf-plan`, `wf-phase1-spec` … `wf-phase6-retrospective`) was
removed in 2.0.0. It is still available at the git tag `v1-final`.

---

## Setup

Run once per project to detect the tech stack, create project-specific domain agents, and write `project-config.json`:

```
/phiwer:wf-init
```

This creates `.claude/agents/` (e.g. `qa-engineer.md`, `backend-dev.md`) and `.claude/context/` (CLAUDE.md excerpts per agent). `/wf-close` refreshes the excerpts when it updates the project's rules.

### What to commit vs. ignore

- **Commit** `.claude/agents/` and `.claude/context/` — the domain agents are project-shared, so the whole team gets the same specialists.
- **Ignore** `.claude/workflow/` — it holds machine-local config (`project-config.json`) and transient per-feature state (`{FEATURE-ID}-context.json`) that should not be shared. Add this to your project's `.gitignore`:

  ```gitignore
  .claude/workflow/
  ```

  Because `project-config.json` is ignored, each fresh checkout regenerates it by running `/phiwer:wf-init` once (or recreate the small JSON by hand — see Config below).

---

## The flow

| Skill | Model | What it does |
|---|---|---|
| `/phiwer:wf-design` | Opus | The **Elephant**: proposes a tier (small / medium / large), creates the design doc early and keeps it current, argues the design with you toward six gates, dispatches **researchers**, tests the doc with a **goldfish** (fresh subagent given only the doc path), runs a **critic** for large tier (plus up to two opt-in lens critics, e.g. security or data, when the design has those risks), and gets your approval. |
| `/phiwer:wf-build` | Sonnet | New session. Resumes from the doc, dispatches one fresh **implementer** per chunk (Opus if the doc sets `implementer: opus`), reviews and commits each chunk, handles STOPPED escalations with you, then runs a capped rule-compliance review (**code-reviewer**). |
| `/phiwer:wf-close` | Sonnet | Verifies against the doc, fills in As-built, sets `status: built`, writes a short retrospective into the doc, feeds lessons into CLAUDE.md / `.claude/rules`, records token totals. |

```
/phiwer:wf-design TRA-1 [description + attach images]
# new session
/phiwer:wf-build TRA-1
# new session
/phiwer:wf-close TRA-1
```

The five agents ship with the plugin (`phiwer:researcher`, `phiwer:goldfish`, `phiwer:critic`,
`phiwer:implementer`, `phiwer:code-reviewer`). Project agents from `/wf-init` are domain
specialists that `/wf-design` can use for research or as a lens critic.

### Tiers

| Tier | Typical | Ceremony |
|---|---|---|
| Small | Clear bug fix, config change, local refactor | No doc; state the files and proceed |
| Medium | A feature within one module, an internal interface change | Doc, goldfish (≤ 2 rounds), critic optional |
| Large | Public/cross-team APIs, migrations, security or money paths | Doc, goldfish (≤ 3 rounds), critic plus optional lens critics (≤ 2 rounds), Opus implementer optional |

Size by risk and blast radius, not lines of code. Review loops are capped; when a cap is hit,
the residue goes to you instead of looping again.

### Config

`.claude/workflow/project-config.json`:

```json
{
  "designDir": "docs/design",
  "designTemplate": "optional/path/to/project-template.md",
  "specDir": "docs/specs",
  "archiveDir": "docs/specs/archive",
  "roadmapFile": "ROADMAP.md",
  "worktreesEnabled": false
}
```

`specDir` holds the token ledger; `archiveDir` holds older specs, still scanned for rule
citations by `/wf-close`.

### Worktrees

With `worktreesEnabled: true`, `/wf-design` enters a native worktree (`EnterWorktree`) for the
ticket before creating the doc, so the doc is born on the feature branch; `/wf-build` and
`/wf-close` re-enter it from the path recorded in the context file. The context file always
lives in the main checkout (`git worktree list` locates it), so several tickets can be in
flight at once without overwriting each other.

---

## Token usage

Each session (design, build, close, and any resumed `-s2`, `-s3` sessions) records its token
usage — main session **plus every subagent it spawned** — into the context file and a row in
`{specDir}/TOKEN_LEDGER.csv`. `/wf-close` writes an all-phases total into the doc and a final
`ALL_PHASES_TOTAL` ledger row. Commit the ledger: it is the only durable, cross-feature record
of what each ticket cost and who ran it. Best-effort: if the helper
(`scripts/record-token-usage.py`) is missing, the session proceeds without recording.

## Session cost & hygiene

Design and build run in separate sessions so the Opus context never pays for diffs and test
output. Two habits handle the rest, because **cache-read on a large accumulated context is the
dominant cost driver** (far more than generation):

- **Start a fresh session when a build gets long.** `/wf-build` suggests this every 3–4
  chunks; it resumes from the doc and git history.
- **`/clear` between unrelated ad-hoc tasks**, so you're not re-reading the previous task's
  transcript.

Run `/usage` to see this directly.

---

**`/phiwer:wf-clear-context`** — clears saved workflow context for a ticket. Design docs are untouched.
