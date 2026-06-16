# claude-workflow

A structured 6-phase feature development workflow for Claude Code. Each phase runs in its own session, keeping context focused and token usage low. Phases produce artifact files (specs, reviews, decisions) that carry context forward without re-loading everything each time.

## Install

As a plugin (namespaced commands):
```
/plugin install github:phiwer/claude-workflow
```

Or copy the `skills/` directory into `~/.claude/skills/` for bare-name commands (`/wf-init`, `/wf-phase1-spec`, etc.).

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

**`/phiwer:wf-phase1-spec`**

Creates a structured spec file from a roadmap item. Reads the roadmap, existing code, and CLAUDE.md to produce a document covering:
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

**How it works:** when `worktreeBase` is set, `wf-phase1-spec` automatically creates a worktree and branch (`feature/{feature-id}`) after generating the spec. Each feature has its own context file (`{FEATURE-ID}-context.json`), so phases for SF-14 and SF-15 never overwrite each other. For implementation, open a Claude Code session in the worktree directory — all phases find the shared context automatically via `git worktree list`. Phase6 offers to remove the worktree and branch when the feature is complete.

Worktrees are fully optional — omit `worktreeBase` (or set it to `null`) and the workflow behaves exactly as before.

---

## Typical flows

**Complex feature (full workflow):**
```
/phiwer:wf-init                    # once per project
/phiwer:wf-phase1-spec             # write spec
/phiwer:wf-phase1-iterate          # quick pre-review (catch issues early)
/phiwer:wf-phase2-review           # formal agent review
/phiwer:wf-phase3-consolidate      # decisions + optional interface files
/phiwer:wf-phase4-implement        # implement
/phiwer:wf-phase5-6-complete       # verify + retrospective
```

**Medium feature:**
```
/phiwer:wf-phase1-spec
/phiwer:wf-phase2-review
/phiwer:wf-phase3-consolidate
/phiwer:wf-phase4-implement-sonnet
/phiwer:wf-phase5-6-complete
```

**Simple feature:**
```
/phiwer:wf-phase1-spec
/phiwer:wf-phase4-implement-sonnet
/phiwer:wf-phase5-verify
```

**Interface-first (review contracts before implementation):**
```
/phiwer:wf-phase1-spec             # include Application Interface section
/phiwer:wf-phase2-review           # review interface design with agents
/phiwer:wf-phase3-consolidate      # creates actual interface files for team review
# → review interface files with team / open a PR
/phiwer:wf-phase4-implement        # implement against agreed interfaces
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

**`/phiwer:wf-clear-context`** — clears saved workflow context to start fresh on a new feature.
