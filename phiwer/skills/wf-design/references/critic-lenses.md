# Critic lenses

For large tier, the general critic can be joined by up to two lens critics. A lens narrows
what a critic checks; it is not a persona. Pick lenses only for risks the design actually has
(the Signals in `tiers.md`), propose them to the user, and add them only on confirmation.

Dispatch each lens critic with the doc path, the lens name and its checklist copied verbatim
from below. Nothing else: no summary, no hints about what you suspect.

A project agent from `.claude/agents/` may replace a lens when it covers the same risk (e.g. a
security agent for the security lens); give it the same brief.

## security

Use when: authentication, authorization, secrets, personal data, money, or input from outside
the trust boundary.

- Every new entry point: who can call it, and where is that enforced?
- Every new read path: can it return data the caller must not see (other tenants, other users)?
- Untrusted input reaching queries, file paths, shell commands, templates or deserializers.
- Secrets or personal data in logs, errors, events, URLs or caches.
- Failure modes that fail open instead of closed.

## data

Use when: schema changes, migrations, deletes, backfills, or a change in what is persisted.

- Is the migration safe on the real data volume, and while old code is still running?
- Can it be rolled back, and what happens to data written after the migration?
- Every write: idempotent on retry? Inside which transaction boundary?
- Existing rows that don't match the new assumptions (nulls, duplicates, legacy values).
- Anything deleted or overwritten that cannot be recovered.

## api

Use when: a public, cross-team or externally consumed interface changes (HTTP, events,
messages, shared libraries).

- Is every change backward compatible for existing consumers? If not, what is the transition?
- Field semantics, not only shape: units, nullability, ordering, error codes.
- Versioning and deprecation: who has to change, and in what order are things deployed?
- Event or message consumers that replay old messages against new code.

## concurrency

Use when: shared mutable state, parallel workers, retries, scheduled jobs, or ordering
assumptions.

- Two instances running the same thing at once: what breaks?
- Race windows between read and write; lost updates; check-then-act.
- Retries and redelivery: duplicate effects, ordering changes.
- Timeouts and partial failure in the middle of a multi-step operation.
