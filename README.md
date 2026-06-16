# claude-workflow

A structured 6-phase feature development workflow for Claude Code, designed to keep work organised and reduce token usage through clear phase separation.

## Install

```
/plugin install github:phiwer/claude-workflow
```

## Phases

| Skill | Description |
|-------|-------------|
| `/phiwer:wf-init` | Initialize workflow for a project — detects tech stack, creates agent files |
| `/phiwer:wf-phase1-spec` | Create an initial feature specification from a roadmap item |
| `/phiwer:wf-phase1-iterate` | Quick 3-agent review of a DRAFT spec before formal review |
| `/phiwer:wf-phase2-review` | Formal design review with 2-6 subagents |
| `/phiwer:wf-phase3-consolidate` | Address review feedback, make decisions, finalize spec |
| `/phiwer:wf-phase4-implement` | Thorough implementation (Opus) |
| `/phiwer:wf-phase4-implement-sonnet` | Faster implementation (Sonnet) |
| `/phiwer:wf-phase5-verify` | Verify implementation against spec |
| `/phiwer:wf-phase5-6-complete` | Verify + retrospective in one session |
| `/phiwer:wf-phase6-retrospective` | Document lessons learned |
| `/phiwer:wf-clear-context` | Clear saved workflow context to start fresh |

## Typical flow

```
/phiwer:wf-init                  # once per project
/phiwer:wf-phase1-spec           # new feature
/phiwer:wf-phase2-review         # review the spec
/phiwer:wf-phase3-consolidate    # address feedback
/phiwer:wf-phase4-implement      # implement
/phiwer:wf-phase5-6-complete     # verify + retro
```
