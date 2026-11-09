# Design doc template: frontend

For changes to a web frontend: screens, components, client-side state and the calls to a
backend. It is the default template plus sections for UI states, components, state and data
flow, the backend contract, routing and access, translations and accessibility. Selected with
`"designTemplate": "frontend"` in `.claude/workflow/project-config.json`.

Keep the frontmatter, Gates, Alternatives, Implementation (table and chunk progress) and
As-built: /wf-design, /wf-build and /wf-close depend on them.

Copy the block below into `{designDir}/{ticket-lower}-{short-name}.md`. Create it with
headings only at the start of planning and fill it in as decisions are made. Write for a reader
with no access to the planning conversation. Delete every section marked *(if applicable)* that
does not apply; an empty heading invites the implementer to invent content.

This template gives the structure only. The project's own conventions (framework style, where
shared code lives, styling rules, how translations are added, which commands verify a change)
live in `CLAUDE.md` and `.claude/rules/`, and the design must respect them without restating
them here.

````markdown
---
title: <Feature name, as the user would describe it>
ticket: <TICKET-ID>
status: draft        # draft | approved | built. Only the user sets approved.
tier: medium         # medium | large
implementer: sonnet  # sonnet | opus. opus only for high-stakes tickets; see /wf-build.
apps: <the app(s) or shared package(s) this changes>
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
3–5 plain sentences: what is wrong or missing, for which kind of user, and why it matters now.

## Context
How the relevant screens and code work today, with file references (`path/to/file.ts:line`
where useful). Name the route, the components, where the data comes from, and the backend
endpoints involved.

## Assumptions
- <assumption>: verified in `<file>` / accepted risk / removed

## Screens and UI states (if applicable)
What the user sees and does, step by step. If mock-ups or screenshots were attached, they are
saved under `{designDir}/{ticket-lower}-assets/` and every label, button and annotation is
transcribed here; the images alone are not enough.

For each screen or component that loads or submits data:

| State | What the user sees | How to reach it |
|-------|--------------------|-----------------|
| Loading | | |
| Empty | | |
| Error (load / save) | | |
| No permission | | |
| Success | | |

Copy: every user-visible text, with its translation key if the project translates (see
Translations).

## Plan
Jargon-light description of the approach and how the pieces fit together.
Block diagram if it helps (ASCII or Mermaid); use a sequence diagram for anything that goes
UI → state/service → backend and back.

## Components (if applicable)
New and changed components and services, and where each lives: inside one app when only that
app uses it, in a shared package when more than one does. Respect the project's rules on what
may import what.

| Component | Location | Inputs / outputs | Responsibility |
|-----------|----------|------------------|----------------|
| `<Name>` | `<path>` | `<inputs>` / `<outputs>` | <one line> |

## State and data flow (if applicable)
Where each piece of state lives and which one is the source of truth: component-local, a
service, or a store (name the existing slice or module). What triggers each fetch, what is
cached and for how long, and what happens to stale data after a save (refetch, optimistic
update, or patch from the response).

## Backend contract (if applicable)
The endpoints this depends on, and whether they exist today.

| Method + path | Request | Response | Exists? |
|---------------|---------|----------|---------|
| `GET /...` | | | yes / backend PR <link> / not yet |

- Types: generated (from which schema, by which command) or hand-written (where).
- Error responses the UI must handle and what it shows for each (status → state above).
- If the backend is not ready: what the frontend does in the meantime (mock, feature flag,
  wait), and which chunk becomes unblocked when it lands.

## Routing and access (if applicable)
New or changed routes, lazy loading, guards, and which roles can see what. What a user without
access sees (hidden link, redirect, or a "no permission" state). Deep links and browser
back/refresh behaviour.

## Translations (if applicable)
New or changed keys, following the project's process for adding them:

| Key | Text (default language) | Where it is registered |
|-----|-------------------------|------------------------|
| `<area>.<key>` | | `<file or system>` |

If texts must exist somewhere outside the repo first (a translation service or database),
say who adds them and which chunk waits for that. No hard-coded user-visible text.

## Accessibility and RTL (if applicable)
Keyboard path through the flow, focus after open/close/submit/error, labels and `aria-*` for
non-text controls, and announcements for async results. If the product supports right-to-left
languages, styling uses logical properties (`margin-inline-start`, not `margin-left`).

## Alternatives
### <Option>
What it was, and why it lost.

## Out of scope
<Concern>, <concern>. Do not modify `<path>`, `<path>`.

## Implementation
Every file created or changed, grouped into chunks. A chunk is one logical, reviewable change
(one commit) that one implementer can complete and verify on its own, tests and translation
keys included; later chunks may depend on earlier ones.

| Chunk | File | Change | Why |
|-------|------|--------|-----|
| 1 | `path/to/file` | <concrete change> | <reason> |

Chunk notes: dependencies between chunks, which (if any) can run in parallel, and which wait
on something outside this repo (a backend endpoint, translation texts).

### Chunk progress
Ticked by /wf-build after each chunk is reviewed and committed.
- [ ] Chunk 1: <one-line name>

## Verification
Unit or component tests to add or change, one per behaviour that matters:
1. <happy path>
2. <each UI state from the table above>
3. <the case an implementer would not have thought of>

Checks: the project's test, lint (including accessibility lint, if it has one) and production
build commands, as listed in `CLAUDE.md`.

Manual check in the browser: the route, the role to log in as, and what to click to see each
state.

What must not change: other apps, existing routes and deep links, <existing users of shared
components>.

## Open questions
- <question> (owner, if not the user)

## As-built
Filled in after implementation: deviations from the plan and why, and anything a future
reader would otherwise be misled by.
````
