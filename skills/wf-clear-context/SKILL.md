---
name: wf-clear-context
description: Clear the workflow context file to start fresh on a new feature
model: haiku
allowed-tools: Bash
---

# Clear Workflow Context

Use this command to clear the saved workflow context and start fresh.

## Instructions

1. Delete the context file if it exists:

```bash
rm -f .claude/workflow/phase-context.json
```

2. Output confirmation:

```
Workflow context cleared.

You can now run any phase skill to start fresh:
- /wf-phase1-spec       Create a new specification
- /wf-phase1-iterate    Iterate on an existing DRAFT spec
- /wf-phase2-review     Run formal design review
- /wf-phase3-consolidate Address feedback and finalize spec
- /wf-phase4-implement  Implement (Opus, thorough)
- /wf-phase4-implement-sonnet  Implement (Sonnet, faster)
- /wf-phase5-verify     Verify implementation
- /wf-phase5-6-complete Verify + retrospective combined
- /wf-phase6-retrospective Document lessons learned
```
