# claude-workflow

A structured 6-phase feature development workflow for Claude Code. Each phase runs in its own session, keeping context focused and token usage low. Phases produce artifact files (specs, reviews, decisions) that carry context forward without re-loading everything each time.

## Install

```
/plugin marketplace add phiwer/claude-workflow
/plugin install phiwer@phiwer
/reload-plugins
```

Skills are namespaced as `/phiwer:wf-init`, `/phiwer:wf-phase1-spec`, etc.

**Updating** after the repo changes:

```
/plugin marketplace update phiwer
/plugin update phiwer
/reload-plugins
```

---

## Setup

Run once per project to detect the tech stack, create project-specific review agents, and write `project-config.json`:

```
/phiwer:wf-init
```

This creates `.claude/agents/` (e.g. `qa-engineer.md`, `backend-dev.md`) and `.claude/context/` (CLAUDE.md excerpts per agent). Agent context is automatically refreshed at the end of every phase6 retrospective — no manual re-run needed.

---

## Phases

### Phase 1 — Specification

**`/phiwer:wf-phase1-spec [feature-id] [description]`**

Pass the feature ID and your own description of what the feature should do. Include constraints, edge cases, and any relevant context. Attach images (wireframes, diagrams, screenshots) to the same message if you have them. The skill treats your description as the primary definition of the feature, cross-references the roadmap, explores the codebase, and produces a structured spec.

**Example:**
```
/phiwer:wf-phase1-spec TRA-1468

Track deleted users and their dependants in delta reports. When a user
is soft-deleted in the HR system, the delta report should emit a leaver
event for them and for any active dependants on their policy. The event
should follow the same structure as existing leaver events (TRA-1417).
Edge case: dependants with their own active policies should not be closed.
```
*(Attach a diagram or screenshot to the same message if helpful.)*

The spec covers:
- Application interface (public contracts, method signatures, DTOs)
- Components and internal logic
- Files to add/modify
- Test strategy with estimated case counts
- Open questions

Assigns a complexity tier (Simple / Medium / Complex) that determines the recommended phase path.

**`/phiwer:wf-phase1-iterate`** *(optional, recommended for Complex)*

Spawns 3 specialized agents in parallel for a quick pre-review of the draft spec before committing to a full Phase 2 review. Agents explicitly check:
- Whether the spec has enough detail to implement without guessing
- Whether the Test Strategy is specific enough to actually write the listed tests
- Top 2–3 blocking concerns each

Produces a PROCEED / REVISE verdict. Fix blocking issues before moving on.

---

### Phase 2 — Design Review

**`/phiwer:wf-phase2-review`**

Formal review with 2–6 specialized subagents selected based on what the spec touches (backend, database, API design, QA, etc.). You confirm which agents to include. Each agent produces structured feedback (Strengths / Concerns / Recommendations / Verdict). The phase produces a consolidated `PHASE2_REVIEW.md` artifact listing critical issues, recommended changes, and open questions for Phase 3.

---

### Phase 3 — Consolidation

**`/phiwer:wf-phase3-consolidate`**

Addresses Phase 2 feedback and makes decisions on all open questions. Before marking the spec READY FOR IMPLEMENTATION, verifies every Open Question checkbox is resolved — anything unresolved must be explicitly decided or moved to Deferred Items.

Optionally creates **application interface files** (actual source files with method signatures, no implementation logic) for team review before implementation begins. Configurable via `"interfaceFirst": true` in `project-config.json` — asked once and remembered.

Produces `PHASE3_CONSOLIDATION.md` with each decision, its rationale, and spec changes.

---

### Phase 4 — Implementation

**`/phiwer:wf-phase4-implement`** *(Opus — thorough)*  
**`/phiwer:wf-phase4-implement-sonnet`** *(Sonnet — faster)*

Implements the feature against the finalized spec and Phase 3 decisions. If `interfaceFirst` is set, implements against the already-agreed interface files rather than redefining them. Deviations from the spec are documented immediately as they happen, not reconstructed after the fact.

Produces a lightweight `PHASE4_IMPLEMENTATION.md` (files changed, test counts, deviations — for quick visual inspection) and updates the workflow context with `lastPhase`. This gives Phase 5 a durable record and a clean deviation handoff even if the run was interrupted or you took over manually mid-phase — Phase 4 is no longer the one phase that leaves no on-disk trace.

---

### Phase 5 — Verification

**`/phiwer:wf-phase5-verify`**

Verifies the implementation against the spec: checks all listed files exist, runs the test suite, and documents any deviations with reasoning. Produces `PHASE5_VERIFICATION.md` with a checklist verdict.

**`/phiwer:wf-phase5-6-complete`** *(Phase 5 + 6 combined)*

Runs verification and retrospective in one session, saving ~4–6K tokens from context reload. Useful when the feature is straightforward and you want to close it out in one go.

---

### Phase 6 — Retrospective

**`/phiwer:wf-phase6-retrospective`**

Documents lessons learned and — more importantly — extracts actionable improvements from the full history of the feature (Phase 2 review, Phase 3 decisions, Phase 5 deviations). For each finding, decides whether it is project-general (worth adding to CLAUDE.md) or feature-specific (not reusable). Drafts concrete CLAUDE.md additions with target sections before writing anything. Also evaluates Deferred Items from Phase 3 — marks them unnecessary or drafts a roadmap entry for each.

Archives the spec and clears workflow context.

---

## Parallel development with git worktrees

Each feature gets its own git branch and worktree, so you can work on multiple features simultaneously without branches interfering.

**Enable during setup:** `wf-init` asks whether to enable worktrees and what base directory to use (e.g. `..` creates worktrees as siblings to the project).

**Enable on an existing project:** add `worktreeBase` to `.claude/workflow/project-config.json`:

```json
{
  "specDir": "docs/specs",
  "archiveDir": "docs/specs/archive",
  "roadmapFile": "ROADMAP.md",
  "worktreeBase": ".."
}
```

**How it works:** when `worktreeBase` is set, `wf-phase1-spec` automatically creates a worktree and branch (`feature/{feature-id}`) after generating the spec. Each feature has its own context file (`{FEATURE-ID}-context.json`), so phases for SF-14 and SF-15 never overwrite each other.

**Typical worktree flow:**

```
# In your main project directory
/phiwer:wf-phase1-spec SF-14 [description]
# → spec written, worktree created at ../myproject-sf-14 on branch feature/sf-14

/phiwer:wf-phase2-review
/phiwer:wf-phase3-consolidate
# → spec is READY FOR IMPLEMENTATION

# Open a NEW Claude Code session in the worktree directory:
cd ../myproject-sf-14
/phiwer:wf-phase4-implement
# → implementation phases run here, on the feature branch

# Back in the worktree directory
/phiwer:wf-phase5-6-complete
# → phase6 offers to remove the worktree and merge/delete the branch
```

Spec and review phases (1–3) run in the main project directory because they read the roadmap, existing specs, and project config. Implementation phases (4–6) run in the worktree directory so changes land on the feature branch and stay isolated from `main`.

All phases find the shared context automatically — each skill runs `git worktree list` to locate the main root regardless of which directory you're in, then reads `{FEATURE-ID}-context.json` from there.

Worktrees are fully optional — omit `worktreeBase` (or set it to `null`) and the workflow behaves exactly as before.

---

## Typical flows

**Complex feature (full workflow):**
```
/phiwer:wf-init                    # once per project
/phiwer:wf-phase1-spec TRA-1 [description + attach images]
/phiwer:wf-phase1-iterate          # quick pre-review (catch issues early)
/phiwer:wf-phase2-review           # formal agent review
/phiwer:wf-phase3-consolidate      # decisions + optional interface files
/phiwer:wf-phase4-implement        # implement
/phiwer:wf-phase5-6-complete       # verify + retrospective
```

**Medium feature:**
```
/phiwer:wf-phase1-spec TRA-1 [description]
/phiwer:wf-phase2-review
/phiwer:wf-phase3-consolidate
/phiwer:wf-phase4-implement-sonnet
/phiwer:wf-phase5-6-complete
```

**Simple feature:**
```
/phiwer:wf-phase1-spec TRA-1 [description]
/phiwer:wf-phase4-implement-sonnet
/phiwer:wf-phase5-verify
```

**Interface-first (review contracts before implementation):**
```
/phiwer:wf-phase1-spec TRA-1 [description]   # include Application Interface section
/phiwer:wf-phase2-review                      # review interface design with agents
/phiwer:wf-phase3-consolidate                 # creates actual interface files for team review
# → review interface files with team / open a PR
/phiwer:wf-phase4-implement                   # implement against agreed interfaces
/phiwer:wf-phase5-6-complete
```

---

## Complexity tiers

| Tier | Criteria | Recommended path |
|------|----------|-----------------|
| Simple | Single pattern, <100 LOC, follows existing templates | 1 → 4 → 5 |
| Medium | 2–5 files, follows existing patterns, some integration | 1 → 2 → 3 → 4 → 5 |
| Complex | New patterns, 5+ files, novel architecture | 1 → 1.5 → 2 → 3 → 4 → 5 → 6 |

---

## Token usage

Every phase records its token usage — main session **plus any subagents it spawned** (Phase 2 reviewers, Phase 1.5 agents) — into its artifact and the workflow context. Phase 6 (and the combined Phase 5+6) writes an all-phases grand-total table into the retrospective. Counts cover input, output, and cache read/creation tokens, read from the session transcripts. Best-effort: if the helper (`scripts/record-token-usage.py`) is missing, the phase proceeds without recording.

---

## Session cost & hygiene

Running each phase in its own session already keeps context tight — that's the main reason the workflow insists on a new session per phase. Two habits handle the rest, because **cache-read on a large accumulated context is the dominant cost driver** (far more than generation):

- **`/compact` during a long phase.** A heavy Phase 4 implementation can grow past ~150k context and get expensive even when cached — every turn re-reads the whole thing. Compact mid-task to trim it.
- **`/clear` between unrelated ad-hoc tasks.** The per-phase discipline doesn't cover long free-form sessions that drift across many tasks; clear when you switch to something unrelated so you're not re-reading the previous task's transcript.

Run `/usage` to see this directly — if ">150k context" or "subagent-heavy sessions" dominate your spend, these two habits are the fix.

---

**`/phiwer:wf-clear-context`** — clears saved workflow context to start fresh on a new feature.
