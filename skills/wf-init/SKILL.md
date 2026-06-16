---
name: wf-init
description: Initialize the feature workflow for a project — detects tech stack, proposes review agents (asks user to confirm), creates agent files and project-config.json.
allowed-tools: Read, Glob, Grep, Bash, Write, AskUserQuestion
model: sonnet
---

# Workflow Init: Bootstrap Project Workflow

Set up the 6-phase feature development workflow for this project by detecting the tech stack,
proposing appropriate review agents, and creating the necessary config files.

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
description: {agent focus area — used to decide relevance in phase2 agent selection}
tools: Read, Glob, Grep
model: opus
---

# {Agent Role} Review Agent

Review implementation plans for {focus area} in this project.

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
or generic best practices for the stack if CLAUDE.md is absent.}

## Review Process

1. Read the spec thoroughly
2. Identify concerns in your focus areas
3. Check against key patterns above
4. Provide structured feedback

## Output Format

**Strengths**: What's done well in the spec
**Concerns**: Issues to address (mark CRITICAL for blocking issues)
**Recommendations**: Suggestions for improvement
**Verdict**: APPROVED / APPROVED WITH REVISIONS / NEEDS REVISION
```

Generate content for each agent using what you know about the detected stack and any
conventions in CLAUDE.md. Make the agent content specific to this project's tech stack,
not generic boilerplate.

### Step 4: Write Project Config

Ask the user to confirm path defaults:

Use AskUserQuestion:
- header: "Project paths"
- question: "Confirm or adjust the workflow paths for this project:"
- option1: label="Use defaults (docs/specs, ROADMAP.md)", description="specDir=docs/specs, archiveDir=docs/specs/archive, roadmapFile=ROADMAP.md"
- option2: label="Customize paths", description="Enter custom paths for spec directory, archive, and roadmap file"

If "Use defaults" — write config with defaults.
If "Customize paths" — ask a follow-up for each path (or accept an "Other" text input).

Before writing, check:
- Does `{specDir}` directory exist? Warn if not (it will be created by wf-phase1-spec)
- Does `{roadmapFile}` exist? Warn if not (wf-phase1-spec needs it to suggest features)

Then ask about git worktrees:

Use AskUserQuestion:
- header: "Git worktrees?"
- question: "Enable git worktrees for parallel feature development? Specify a base directory where worktrees will be created (e.g. `..` for sibling directories)."
- option1: label="Yes — set base dir", description="Enter path relative to project root. E.g. `..` creates worktrees as siblings."
- option2: label="No — skip", description="Work on one feature at a time without worktrees"

If "Yes — set base dir": prompt for the base directory path and set `worktreeBase` to that value.
If "No — skip": set `worktreeBase` to `null`.

Write `.claude/workflow/project-config.json`:
```json
{
  "specDir": "{specDir}",
  "archiveDir": "{archiveDir}",
  "roadmapFile": "{roadmapFile}",
  "worktreeBase": {worktreeBase or null}
}
```

### Step 5: Write Skill Permissions

Update `.claude/settings.local.json` to allow all `wf-*` skills to run without permission
prompts. If the file does not exist, create it.

Read the file (or start with `{"permissions": {"allow": [], "deny": []}}` if absent). Add
each of these entries to the `allow` array if not already present:

```
"Skill(wf-init)"
"Skill(wf-phase1-spec)"
"Skill(wf-phase1-iterate)"
"Skill(wf-phase2-review)"
"Skill(wf-phase3-consolidate)"
"Skill(wf-phase4-implement)"
"Skill(wf-phase4-implement-sonnet)"
"Skill(wf-phase5-verify)"
"Skill(wf-phase5-6-complete)"
"Skill(wf-phase6-retrospective)"
"Skill(wf-clear-context)"
```

Write the updated file. Do not remove any existing entries.

### Step 6: Create Context Excerpts

If `CLAUDE.md` exists and is longer than 100 lines:

1. Read `CLAUDE.md`
2. For each agent file in `.claude/agents/` (not just agents created in this run), create
   or overwrite `.claude/context/{agent-name}.md` with only the CLAUDE.md sections most
   relevant to that agent's domain. Always regenerate — even for existing agents that were
   not replaced — so excerpts stay current as CLAUDE.md accumulates conventions over time.

   - `backend-dev.md` — API patterns, service layer conventions, async pipelines, DB patterns, Spring patterns
   - `frontend-dev.md` — React/TypeScript conventions, component patterns, test patterns, UI conventions
   - `database-dev.md` — Schema conventions, migration patterns, JSONB usage, index patterns
   - `api-designer.md` — HTTP semantics, endpoint naming, auth patterns, error handling
   - `game-engine-dev.md` — Game loop, tick system, action/system patterns, lazy evaluation
   - `game-designer.md` — Game mechanics formulas, balance constants, rule references
   - `devops.md` — Deployment patterns, CI/CD, health checks, config management
   - `ux-designer.md` — UI/UX patterns, accessibility, responsive design, user flows
   - `qa-engineer.md` — Test patterns, integration test setup, test isolation, coverage targets

   Extract verbatim relevant sections. Keep each excerpt under 200 lines.

3. For each agent file **newly created** in Step 3, append this line to its
   "## Project Context" section:
   > For compact project-convention reference, read `.claude/context/{name}.md`.
   Skip this for existing agents — they already have the line.

If `CLAUDE.md` is absent or short (≤100 lines), skip this step — the agent files already
inline sufficient context.

### Step 7: Output Summary

Display:

```
## Workflow initialized for {project name or directory}

### Agents created
{list each .claude/agents/{name}.md created or skipped}

### Config
- Spec directory: {specDir}
- Archive directory: {archiveDir}
- Roadmap file: {roadmapFile}

### Available commands
- /wf-phase1-spec       Create a feature spec from the roadmap
- /wf-phase1-iterate    Quick pre-review of a DRAFT spec
- /wf-phase2-review     Full design review with selected agents
- /wf-phase3-consolidate Address feedback, finalize spec
- /wf-phase4-implement  Implement the feature (Opus, thorough)
- /wf-phase4-implement-sonnet  Implement (Sonnet, faster)
- /wf-phase5-verify     Verify implementation matches spec
- /wf-phase5-6-complete Verify + retrospective in one session
- /wf-phase6-retrospective Document lessons learned
- /wf-clear-context     Clear workflow context to start fresh
```

If `CLAUDE.md` was absent or under 100 lines during this run, also display:

```
⚠️  CLAUDE.md missing or thin — agent context is generic

Agents were created with inferred tech-stack content rather than project-specific
conventions. To get the most out of the review phases, create a CLAUDE.md with at minimum:

  - Build and test commands
  - Project description and key architectural decisions
  - Coding conventions and patterns to enforce

Then re-run /wf-init and select "Re-run full setup" to regenerate agents with
project-specific context and refresh the .claude/context/ excerpts.
```
