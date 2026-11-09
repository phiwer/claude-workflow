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

### Upgrading after a plugin update

Agent files are part generated boilerplate, part project-specific content you tune over time.
When a plugin release changes the generated part, re-run `/phiwer:wf-init` and choose
**"Upgrade agents to current template"**:

```
/phiwer:wf-init
```

It replaces the boilerplate — everything from `## Review Process` down, carrying a
`<!-- wf-init template: X.Y.Z -->` stamp — and leaves the description, Project Context, Focus
Areas and Key Patterns exactly as they are. Anything it notices about the project-specific
half (a description predating a format change, a critic lens no agent claims) is **reported,
never edited**. Files that were not generated from the template are skipped untouched.

`project-config.json` is left alone, so the upgrade can't reset paths you chose. The context
excerpts are regenerated, as they are on any run.

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
| `/phiwer:wf-design` | Opus | The **Elephant**: proposes a tier (small / medium / large), creates the spec (design doc) early and keeps it current, argues the design with you toward six gates, dispatches **researchers**, tests the doc with a **goldfish** (fresh subagent given only the doc path), runs a **critic** for large tier (plus up to two opt-in lens critics, e.g. security or data, when the design has those risks), and gets your approval. |
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
  "specDir": "docs/specs",
  "designTemplate": "default",
  "worktreesEnabled": false
}
```

`roadmapFile` is optional and unset by default. Set it (e.g. `"roadmapFile": "ROADMAP.md"`)
only if the project keeps its tickets in a file rather than an issue tracker: `/wf-design` then
reads a ticket's entry from it, and `/wf-close` marks the ticket complete. `/wf-init` offers it
when it finds a `ROADMAP.md`, `BACKLOG.md` or `TODO.md`.

`designTemplate` picks the design doc template. Three are bundled:

| Name | For |
|------|-----|
| `default` | Any project. Problem, context, plan, alternatives, chunks, verification. |
| `frontend` | Web frontends. Adds UI states, components, state and data flow, backend contract, routing and access, translations and accessibility. |
| `ddd-hexagonal` | **Only backends built with DDD and ports and adapters.** Adds domain language, aggregates and invariants, the transaction boundary, ports and failure semantics. For a plain layered backend, use `default`. |

Any other value is a path to a project template, relative to the repo root. It is read from the
main checkout, so an untracked template also works from a worktree. A project template must
keep the frontmatter, Gates, Alternatives, Implementation (with Chunk progress) and As-built.
The bundled templates give structure only; project conventions belong in `CLAUDE.md` and
`.claude/rules/`, which every phase already follows. `/wf-init` recommends a template from the
detected stack.

### Specs

A spec is the design doc `/wf-design` writes. Specs are grouped by ticket prefix, so each
team's specs share a folder, and the token ledger is one file per repo:

```
docs/specs/
  TOKEN_LEDGER.csv
  tra/
    tra-1544-schedule-without-file-proxy.md
    tra-1544-assets/          (only when the ticket had images)
  been/
    been-7192-retrigger-order-events.md
```

Specs are committed, so developers can review them and later sessions can read why the code is
the way it is: a commit's ticket prefix leads straight to its spec. `/wf-design` reads earlier
specs for the area it is changing and lists them under Earlier specs in Context.

Specs are never moved to an archive, because moving them breaks every link to them. Their
`status` says whether they still hold: `built` specs are history (As-built overrides Plan, and
the code wins when they disagree), and when a later ticket replaces one, `/wf-close` of that
ticket sets it to `superseded` with `superseded-by: <TICKET>`. A ticket that changes part of
an earlier spec adds a "Changed by" line to its As-built instead.

Before 2.5, specs went into a flat `designDir` (default `docs/design`). They are still found
there; `/wf-init` offers to move the finished ones, and `/wf-close` moves an in-flight ticket's
spec when it closes. `docs/specs/archive` from the pre-2.0 pipeline stays where it is and is
still scanned for rule citations.

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
