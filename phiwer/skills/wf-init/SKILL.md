---
name: wf-init
description: Initialize or upgrade the feature workflow for a project — detects tech stack, proposes review agents (asks user to confirm), creates agent files and project-config.json. Re-run after a plugin update to refresh generated agents to the current template without touching project-specific content.
allowed-tools: Read, Glob, Grep, Bash, Write, AskUserQuestion
model: sonnet
---

# Workflow Init: Bootstrap Project Workflow

Set up the feature workflow for this project by detecting the tech stack, proposing
appropriate project agents, and creating the necessary config files. The default flow is
`/wf-design` → `/wf-build` → `/wf-close` (design-first, Elephant-Goldfish); the plugin ships
its own researcher, goldfish, critic, implementer and code-reviewer agents, so the project
agents created here are domain specialists that `/wf-design` can call on for research and
review.

## Instructions

### Step 0: Check for Existing Setup

1. Check if `.claude/workflow/project-config.json` exists
2. Check if `.claude/agents/` directory has any `.md` files

**If `.claude/agents/` has files** — whether or not the config exists — the project has agents
worth protecting, so never fall through to a silent full setup. Ask first.

`.claude/workflow/` is git-ignored, so a fresh clone or a new git worktree has the agents but
no `project-config.json`. Gating on both would make the upgrade option unreachable exactly
where this plugin expects you to work, and would regenerate tuned agents without asking. The
upgrade path does not read `project-config.json` at all.

- Use AskUserQuestion. If the config is missing, say so in the question text and note that
  "Re-run full setup" will recreate it:
  - header: "Already configured"
  - question: "This project already has agents{, but no project-config.json (normal in a fresh clone or worktree)}. What would you like to do?"
  - option1: label="Upgrade agents to current template", description="Refresh the generated boilerplate in existing agents to this plugin version. Project-specific content is never rewritten."
  - option2: label="Add missing agents only", description="Keep existing agents, generate any that are missing"
  - option3: label="Re-run full setup", description="Regenerate all agents and overwrite project-config.json"
  - option4: label="Cancel", description="Exit without changes"
- Exit if user selects "Cancel"
- If only `project-config.json` is missing and the user picks an option other than "Re-run full
  setup", carry on without it: Step 4 writes it if absent, and Step 3U does not need it.
- Set a flag `replaceAgents=true` if user selects "Re-run full setup"
- Set a flag `upgradeOnly=true` if user selects "Upgrade agents to current template". In that
  case **skip Steps 1, 2 and 3** (no stack detection, no agent proposal, no generation — the
  agent roster is whatever the project already has) and run Step 3U instead, then continue
  from Step 5. Leave `project-config.json` untouched.

### Step 1: Detect Tech Stack

Read as many of these as exist (use Glob and Read in parallel):

- `package.json` — Node/TypeScript stack, frontend framework, scripts
- `pom.xml` — Java/Maven, Spring Boot version
- `build.gradle` or `build.gradle.kts` — Java/Gradle
- `requirements.txt` or `pyproject.toml` — Python stack
- `go.mod` — Go
- `Cargo.toml` — Rust
- `CLAUDE.md` — Project-specific conventions and patterns
- `README.md` — High-level project description

Also glob to confirm languages present:
- `find . -name "*.java" -not -path "*/target/*" | head -5`
- `find . -name "*.ts" -not -path "*/node_modules/*" | head -5`
- `find . -name "*.py" | head -5`
- `find . -name "*.go" | head -5`

Note frameworks detected (Spring Boot, React, FastAPI, Django, Express, Vue, etc.).
Note if this is a game project (look for: tick, game loop, mechanics, combat, etc. in CLAUDE.md or README).

### Step 2: Propose Agents to User

Based on the detected tech stack, build a candidate agent list. Show only agents that are
relevant — don't list all 9 for a simple single-language project.

**Candidate signals**:
- `backend-dev` — Java/Spring, Python/FastAPI, Node/Express, Go, Rust server code
- `frontend-dev` — React, Vue, Angular, `.tsx`/`.jsx` files, TypeScript frontend
- `database-dev` — SQL migration files (Flyway, Alembic, etc.), ORM config, schema files
- `api-designer` — REST controllers, OpenAPI/Swagger, HTTP endpoint definitions
- `game-engine-dev` — Game loop, tick system, game mechanics (in CLAUDE.md or README)
- `game-designer` — Game balance formulas, rule documentation, mechanics docs
- `devops` — `Dockerfile`, `docker-compose.yml`, CI/CD config (`.github/workflows/`, etc.)
- `ux-designer` — Frontend project + user-facing flows, forms, UI components
- `qa-engineer` — Always included automatically; always note this to the user

**`qa-engineer` is always auto-included** — do not ask about it; just note in the question
preamble that it will always be available.

For the remaining candidates (up to 8), use a single AskUserQuestion with batched multi-select
questions — up to 4 agents per question, up to 4 questions total. This ensures every agent
is explicitly listed, not hidden behind a vague "Other".

- Each question: `multiSelect: true`, up to 4 options
- Group by domain for the question label (e.g., "Backend/data agents", "Frontend/UX agents")
- Pre-select candidates that match detected signals

**Suggested groupings** (only include groups with ≥1 detected candidate):
- Group A ("Backend / data"): backend-dev, database-dev, api-designer, devops
- Group B ("Frontend / domain"): frontend-dev, ux-designer, game-engine-dev, game-designer

Example for a full-stack game project (8 candidates → 2 questions):
- Question 1 (multiSelect): "Backend/data agents" — options: [backend-dev, database-dev, api-designer, devops]
- Question 2 (multiSelect): "Frontend/domain agents" — options: [frontend-dev, ux-designer, game-engine-dev, game-designer]

Example for a simple API project (3 candidates → 1 question):
- Question 1 (multiSelect): "Review agents — select relevant" — options: [backend-dev, database-dev, api-designer]

Note in the preamble: "I detected [summarize stack in 1 line]. `qa-engineer` will always be
included. Select additional agents for this project:"

### Step 3: Generate Agent Files

For each confirmed agent, check if `.claude/agents/{name}.md` already exists.
- Skip if it exists AND `replaceAgents` is not set
- Otherwise generate it

To generate an agent file, write `.claude/agents/{name}.md` with this structure:

```markdown
---
name: {agent-name}
description: Research & review of {focus area} — {3-5 concrete topics}. {Optional routing hint: either "Use as the {security|data|api|concurrency} lens" if this agent covers one of the four lenses in wf-design/references/critic-lenses.md, or a boundary against the agent it is most often confused with, e.g. "Not domain modelling".}
tools: Read, Glob, Grep
model: sonnet
---

# {Agent Role} Review Agent

Answer research questions and review design docs for {focus area} in this project.

## Project Context

{Summarize the relevant tech stack for this agent — e.g. for backend-dev: "Spring Boot 3.x,
Java 25, NATS messaging, PostgreSQL" or for frontend-dev: "React 18, TypeScript, Vite".
Pull from what you detected in Step 1. If CLAUDE.md exists, pull the most relevant
conventions for this agent's domain.}

## Focus Areas

{List 4-6 specific things this agent should check, tailored to the detected stack.
Examples for backend-dev in a Spring Boot project:
- Service layer design and transaction boundaries
- REST API contract correctness
- Spring patterns (constructor injection, @Transactional, etc.)
- Error handling and HTTP status codes
- Security (JWT validation, input sanitization)}

## Key Patterns to Enforce

{List 3-5 project-specific patterns from CLAUDE.md that this agent should watch for,
or generic best practices for the stack if CLAUDE.md is absent.

Express each as a **concrete smell test the agent must actively flag** — a detectable
anti-pattern phrased so it can be spotted and called out (e.g. "X that does A then B"),
not an aspirational statement the reviewer can rationalize around. A principle the reviewer
can talk itself past is not a gate.}

## Review Process

1. Read the brief. A brief leading with `Question:` is research; one leading with `Doc:` is
   a review, possibly with a lens checklist.
2. Read the doc or the code in scope.
3. For a research question, answer it; use the focus areas and key patterns above only to
   interpret what you find, not to audit beyond the question. For a review, check against
   your focus areas and the key patterns above.
4. Report in the format the brief asks for.

## Output Format

Use the format the brief asks for. If it gives none:

- **Research question:** Answer (1-3 sentences), Evidence (`file:line` for each claim),
  Inferred, not seen (anything you concluded without direct evidence), Not found (what you
  looked for and could not locate). Never fill a gap with a plausible guess.
- **Review:** findings grouped by severity (Blocker / Major / Minor / Nit), each with what, a
  concrete failure scenario, and evidence (doc section or `file:line`). Report nothing for
  areas that are sound.

<!-- wf-init template: {plugin version from phiwer/.claude-plugin/plugin.json} -->
```

Everything from `## Review Process` to the trailing `<!-- wf-init template: ... -->` comment is
the **fixed zone**: verbatim boilerplate, identical in every project, written exactly as above
with no per-project wording. Everything before it — description, Project Context, Focus Areas,
Key Patterns — is the **custom zone**, which is project-specific from the moment it is written.
Step 3U relies on that split.

Generate content for each agent using what you know about the detected stack and any
conventions in CLAUDE.md. Make the agent content specific to this project's tech stack,
not generic boilerplate.

The descriptions are how `/wf-design` picks between these agents, so make them discriminating.
`references/critic-lenses.md` in `wf-design` defines four lenses — security, data, api and
concurrency — and a project agent may stand in for a lens critic when it covers the same risk.
Work out which agent covers each lens and say so in that agent's description; a lens with no
claimant silently falls back to the general critic, which carries no project context. Where a
lens does not apply to this project, leave it unclaimed rather than forcing a fit.

### Step 3U: Upgrade Existing Agents (upgradeOnly only)

Run this only when `upgradeOnly` is set. It refreshes generated boilerplate and **never
rewrites project-specific content** — the whole point is that an upgrade is safe to run on
agents someone has spent months tuning.

For each `.claude/agents/*.md` (every file, not just ones this plugin generated):

1. **Locate the fixed zone**: from the line `## Review Process` to end of file. If the file has
   no `## Review Process` heading, it was not generated from this template — leave it entirely
   alone and list it under "Skipped" in the report. Never guess at a boundary.
2. **Read the stamp**, if present: the trailing `<!-- wf-init template: X.Y.Z -->` comment. A
   file with no stamp predates stamping; treat its vintage as unknown and carry on.
3. **Compare** the file's fixed zone against the Step 3 template's fixed zone. If they already
   match byte for byte (stamp aside), record "already current" and change nothing.
4. **Replace** the fixed zone with the Step 3 template's version, stamped with this plugin's
   version. Preserve everything above `## Review Process` byte for byte — frontmatter,
   description, Project Context, Focus Areas, Key Patterns. Do not reflow, reword or reorder
   any of it, even if it looks stale or inconsistent with the current template's guidance.

Then **report, without editing**, on the custom zone. These are findings for the user to act on,
not changes to make:

- A `description` that does not start with `Research & review of` — it predates the dual-mode
  wording and may not route correctly.
- Any of the four lenses in `wf-design/references/critic-lenses.md` (security, data, api,
  concurrency) that no agent's description claims.
- An agent with no `.claude/context/{name}.md` companion, or a Project Context section with no
  "For compact project-convention reference" line, when `.claude/context/` exists.

Output a table: agent | fixed zone (upgraded from X / already current / skipped) | findings.
Then state plainly that custom-zone findings were reported only, and that fixing one is an
ordinary edit the user can ask for.

Continue with Step 5 (permissions) and Step 6 (context excerpts), both of which are already
idempotent. Skip Step 4 — `project-config.json` is the user's, and an upgrade must not reset
paths they chose.

### Step 4: Write Project Config

Ask the user to confirm path defaults:

Use AskUserQuestion:
- header: "Project paths"
- question: "Confirm or adjust the workflow paths for this project:"
- option1: label="Use defaults (docs/design, docs/specs, ROADMAP.md)", description="designDir=docs/design, specDir=docs/specs (token ledger), archiveDir=docs/specs/archive (older specs, scanned for rule citations), roadmapFile=ROADMAP.md"
- option2: label="Customize paths", description="Enter custom paths for design docs, spec directory, archive, and roadmap file"

If "Use defaults" — write config with defaults.
If "Customize paths" — ask a follow-up for each path (or accept an "Other" text input).

Before writing, check:
- Does `{designDir}` exist? Note it will be created by the first `/wf-design`.
- Does `{roadmapFile}` exist? Optional; `/wf-design` uses a ticket's roadmap entry when present.

Then ask about the design doc template:

Use AskUserQuestion:
- header: "Doc template"
- question: "Design docs use the plugin's generic template. Use a project-specific template instead? (It may add sections, e.g. domain language or aggregate invariants, but must keep the frontmatter, Gates, Alternatives, Implementation with Chunk progress, and As-built.)"
- option1: label="Plugin default", description="Leave designTemplate unset"
- option2: label="Project template", description="Give a path to an existing template file in the repo"

Then ask about git worktrees:

Use AskUserQuestion:
- header: "Git worktrees?"
- question: "Isolate each feature in its own git worktree for parallel development? Uses Claude Code's native worktree mechanism (EnterWorktree) — creates each feature's worktree at .claude/worktrees/{feature-id}/ and blocks accidental edits to the main checkout while working in one. Location and base-branch behavior are configured at the Claude Code level (worktree.baseRef in settings.json, or a WorktreeCreate hook for a custom location), not by this plugin."
- option1: label="Yes — enable worktrees", description="Each feature gets an isolated native worktree from /wf-design onward"
- option2: label="No — skip", description="Work on one feature at a time in the main checkout"

Set `worktreesEnabled` to `true` or `false` accordingly.

Write `.claude/workflow/project-config.json`:
```json
{
  "designDir": "{designDir}",
  "designTemplate": "{path, or omit}",
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "roadmapFile": "{roadmapFile}",
  "worktreesEnabled": {true or false}
}
```

Then ensure `.claude/workflow/` is git-ignored. This directory holds machine-local config
(`project-config.json`) and transient per-feature state (`{FEATURE-ID}-context.json`) that
must not be shared — unlike `.claude/agents/` and `.claude/context/`, which are committed.

1. Run `git rev-parse --is-inside-work-tree 2>/dev/null` — if it does not print `true`,
   skip this (not a git repo).
2. Read `.gitignore` at the repo root (or start empty if absent).
3. If no existing line matches `.claude/workflow/` (or a broader `.claude/` ignore that
   already covers it), append `.claude/workflow/` on its own line. Do not duplicate an entry
   that is already present, and do not remove or reorder existing lines.

### Step 5: Write Skill Permissions

Update `.claude/settings.local.json` to allow all `wf-*` skills to run without permission
prompts. If the file does not exist, create it.

Read the file (or start with `{"permissions": {"allow": [], "deny": []}}` if absent). Add
each of these entries to the `allow` array if not already present:

```
"Skill(wf-init)"
"Skill(wf-design)"
"Skill(wf-build)"
"Skill(wf-close)"
"Skill(wf-clear-context)"
```

Write the updated file. Do not remove any existing entries.

### Step 5b: Working Agreement in CLAUDE.md

Check whether `CLAUDE.md` already has a "Working agreement" section. If not, use
AskUserQuestion (header: "Working rules") to offer appending this block (append only; never
overwrite or reorder existing content):

```markdown
## Working agreement
- Design before implementation. For anything beyond a small, obvious, reversible change,
  use /wf-design; don't write or edit code until the user approves the design.
- Your value is finding what I've missed. Before agreeing with a claim or proposal, state the
  strongest objection to it. If there is none worth raising, say so briefly and move on.
- When unsure how the system works, say so, then read the code or dispatch a researcher.
  Never guess about existing behaviour.
- Before editing, name the files you intend to change and why.
- The design doc is the source of truth and the recovery point. Keep it current as decisions
  are made; if this session is lost, a fresh one must be able to resume from the doc alone.
```

### Step 6: Create Context Excerpts

Read `CLAUDE.md` **and** every file matching `.claude/rules/*.md` — a project may have split
path-scoped rule content out of CLAUDE.md (see its own Overview table, if present, for whether
it does this), and excerpts must draw from wherever the substantive rules actually live, not
just the root file. If neither source has more than 100 lines combined, skip this step — the
agent files already inline sufficient context.

Otherwise:

1. For each agent file in `.claude/agents/` (not just agents created in this run), create
   or overwrite `.claude/context/{agent-name}.md` with only the sections most relevant to
   that agent's domain, drawn from CLAUDE.md and `.claude/rules/*.md` combined. Always
   regenerate — even for existing agents that were not replaced — so excerpts stay current as
   the rule content accumulates conventions over time.

   - `backend-dev.md` — API patterns, service layer conventions, async pipelines, DB patterns, Spring patterns
   - `frontend-dev.md` — React/TypeScript conventions, component patterns, test patterns, UI conventions
   - `database-dev.md` — Schema conventions, migration patterns, JSONB usage, index patterns
   - `api-designer.md` — HTTP semantics, endpoint naming, auth patterns, error handling
   - `game-engine-dev.md` — Game loop, tick system, action/system patterns, lazy evaluation
   - `game-designer.md` — Game mechanics formulas, balance constants, rule references
   - `devops.md` — Deployment patterns, CI/CD, health checks, config management
   - `ux-designer.md` — UI/UX patterns, accessibility, responsive design, user flows
   - `qa-engineer.md` — Test patterns, integration test setup, test isolation, coverage targets

   Extract verbatim relevant sections — including a worked example's content if the rule file
   only links to one under `docs/architecture/examples/`, since the excerpt should be
   self-contained for the agent reading it. Keep each excerpt under 200 lines.

2. For each agent file **newly created** in Step 3, append this line to its
   "## Project Context" section:
   > For compact project-convention reference, read `.claude/context/{name}.md`.
   Skip this for existing agents — they already have the line.

### Step 7: Output Summary

In `upgradeOnly` mode, display the Step 3U table instead of the block below, followed by the
Config and Available commands sections, and note that `project-config.json` was left as it was.

Otherwise display:

```
## Workflow initialized for {project name or directory}

### Agents created
{list each .claude/agents/{name}.md created or skipped}

### Config
- Design directory: {designDir} (template: {designTemplate}, if set)
- Spec directory: {specDir}
- Archive directory: {archiveDir}
- Roadmap file: {roadmapFile}
- Token ledger: {specDir}/TOKEN_LEDGER.csv (created on the first /wf-design — commit it like
  any other file; it's the only durable, structured, cross-feature record of what each phase
  cost and who ran it, unlike the per-feature context.json which is gitignored and deleted by
  /wf-close)

### Available commands
- /wf-design            Plan a ticket (default) — design doc, goldfish test, critic, your approval
- /wf-build             Implement the approved doc chunk by chunk (fresh session)
- /wf-close             Verify against the doc, as-built, retrospective, rule updates, token totals
- /wf-clear-context     Clear workflow context to start fresh
```

If `CLAUDE.md` was absent or under 100 lines during this run, also display:

```
⚠️  CLAUDE.md missing or thin — agent context is generic

Agents were created with inferred tech-stack content rather than project-specific
conventions. To get the most out of research and review, create a CLAUDE.md with at minimum:

  - Build and test commands
  - Project description and key architectural decisions
  - Coding conventions and patterns to enforce

Then re-run /wf-init and select "Re-run full setup" to regenerate agents with
project-specific context and refresh the .claude/context/ excerpts.
```
