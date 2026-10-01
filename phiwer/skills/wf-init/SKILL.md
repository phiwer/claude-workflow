---
name: wf-init
description: Initialize the feature workflow for a project — detects tech stack, proposes review agents (asks user to confirm), creates agent files and project-config.json.
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

If both exist:
- Use AskUserQuestion:
  - header: "Already configured"
  - question: "This project already has workflow config and agents. What would you like to do?"
  - option1: label="Add missing agents only", description="Keep existing agents, generate any that are missing"
  - option2: label="Re-run full setup", description="Regenerate all agents and overwrite project-config.json"
  - option3: label="Cancel", description="Exit without changes"
- Exit if user selects "Cancel"
- Set a flag `replaceAgents=true` if user selects "Re-run full setup"

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
description: {agent focus area — used by /wf-design to pick a domain specialist for research or review}
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

1. Read the brief. It is either a research question with a scope, or a design doc path
   (possibly with a lens checklist) to review.
2. Read the doc or the code in scope.
3. Check against your focus areas and the key patterns above.
4. Report in the format the brief asks for.

## Output Format

Use the format the brief asks for. If it gives none: findings grouped by severity
(Blocker / Major / Minor / Nit), each with what, a concrete failure scenario, and evidence
(doc section or `file:line`). Report nothing for areas that are sound.
```

Generate content for each agent using what you know about the detected stack and any
conventions in CLAUDE.md. Make the agent content specific to this project's tech stack,
not generic boilerplate.

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

Display:

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
