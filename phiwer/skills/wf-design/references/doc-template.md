# Design doc template

This is the plugin's generic template. A project can replace it by setting `designTemplate` in
`.claude/workflow/project-config.json` to a file of its own; a project template may add
sections, but must keep the frontmatter fields, Gates, Alternatives, Implementation (table and
chunk progress) and As-built, because /wf-design, /wf-build and /wf-close depend on them.

Copy the block below into `{designDir}/{ticket-lower}-{short-name}.md`. Create it with
headings only at the start of planning and fill it in as decisions are made. Write for a reader
with no access to the planning conversation.

````markdown
---
title: <Feature name>
ticket: <TICKET-ID>
status: draft        # draft | approved | built. Only the user sets approved.
tier: medium         # medium | large
updated: <YYYY-MM-DD>
---

# <Feature name>

## Gates
- [ ] 1. Problem stated and agreed
- [ ] 2. Assumptions challenged
- [ ] 3. First design proposed by Claude, argued to a choice
- [ ] 4. Alternatives recorded
- [ ] 5. File-level plan and acceptance criteria
- [ ] 6. Goldfish clean (large: critic clean too)

## Problem
3–5 plain sentences: what is wrong or missing, for whom, and why it matters now.

## Context
How the relevant parts of the system work today, with file references
(`path/to/file.ext:line` where useful). Only what a reader needs to understand this change.

## Assumptions
- <assumption>: verified in `<file>` / accepted risk / removed

## Plan
Jargon-light description of the approach and how the pieces fit together.
Block diagram if it helps (ASCII or Mermaid).

## Alternatives
### <Option>
What it was, and why it lost.

## Implementation
Every file created or changed, grouped into chunks. A chunk is a unit one implementer can
complete and verify on its own; later chunks may depend on earlier ones.

| Chunk | File | Change | Why |
|-------|------|--------|-----|
| 1 | `path/to/file` | <concrete change> | <reason> |

Chunk notes: dependencies between chunks, and which (if any) can run in parallel.

### Chunk progress
Ticked by /wf-build after each chunk is reviewed and committed; this is how a new session
knows where to resume.
- [ ] Chunk 1: <one-line name>

## Verification
- Tests to add or change
- Behaviour to observe
- What must not change (compatibility, performance, existing callers)

## Open questions
- <question> (owner, if not the user)

## As-built
Filled in after implementation: deviations from the plan and why, and anything a future
reader would otherwise be misled by.
````
