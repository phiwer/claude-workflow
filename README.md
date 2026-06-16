# claude-workflow

A structured 6-phase feature development workflow for Claude Code, designed to keep work organised and reduce token usage through clear phase separation.

## Install

```
/plugin install github:phiwer/claude-workflow
```

## Phases

| Skill | Description |
|-------|-------------|
| `/claude-workflow:wf-init` | Initialize workflow for a project — detects tech stack, creates agent files |
| `/claude-workflow:wf-phase1-spec` | Create an initial feature specification from a roadmap item |
| `/claude-workflow:wf-phase1-iterate` | Quick 3-agent review of a DRAFT spec before formal review |
| `/claude-workflow:wf-phase2-review` | Formal design review with 2-6 subagents |
| `/claude-workflow:wf-phase3-consolidate` | Address review feedback, make decisions, finalize spec |
| `/claude-workflow:wf-phase4-implement` | Thorough implementation (Opus) |
| `/claude-workflow:wf-phase4-implement-sonnet` | Faster implementation (Sonnet) |
| `/claude-workflow:wf-phase5-verify` | Verify implementation against spec |
| `/claude-workflow:wf-phase5-6-complete` | Verify + retrospective in one session |
| `/claude-workflow:wf-phase6-retrospective` | Document lessons learned |
| `/claude-workflow:wf-clear-context` | Clear saved workflow context to start fresh |

## Typical flow

```
/claude-workflow:wf-init                  # once per project
/claude-workflow:wf-phase1-spec           # new feature
/claude-workflow:wf-phase2-review         # review the spec
/claude-workflow:wf-phase3-consolidate    # address feedback
/claude-workflow:wf-phase4-implement      # implement
/claude-workflow:wf-phase5-6-complete     # verify + retro
```
