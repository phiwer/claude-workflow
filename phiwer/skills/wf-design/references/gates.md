# Planning gates

Exit criteria, not steps. Work on them in any order; keep the checklist in the doc current.
Each gate has a pass test and the most common way it is faked.

## 1. Problem stated

**Pass:** the Problem section explains, in 3–5 plain sentences, what is wrong or missing and
for whom, and the user has agreed to that wording. A non-engineer could understand it.

**Faked when:** the problem statement is really a solution statement ("we need a cache").
Ask what goes wrong today without it.

## 2. Assumptions challenged

**Pass:** the doc lists the assumptions the design rests on (about load, users, data,
callers, ownership, existing behaviour). Each has been either verified (with a file reference
or a researcher finding), accepted by the user as a known risk, or removed.

**Faked when:** assumptions are listed but none were checked. Anything about how the current
system behaves should be verified in code, not asserted.

## 3. First design proposed by Claude, argued to a choice

**Pass:** Claude proposed an initial design in prose before the user presented theirs; the
user and Claude argued it into the chosen approach; the Plan section describes it jargon-light
with a block diagram where that helps.

**Faked when:** the chosen design is the user's first idea with no real alternative
considered. If nothing was argued, ask what the design would look like if the main constraint
were different.

## 4. Alternatives recorded

**Pass:** every serious option considered and rejected is in Alternatives with the reason it
lost, including ones the critic or goldfish raised and the user rejected.

**Faked when:** the section contains strawmen nobody seriously considered. It should hold the
options someone would plausibly propose again later.

## 5. File-level plan and acceptance criteria

**Pass:** Implementation lists every file to create or change with what changes and why,
grouped into chunks that can each be implemented and verified on their own, with dependencies
between chunks stated. Verification states how we will know it works: tests to add, behaviour to
observe, what must not change.

**Faked when:** entries like "update service layer as needed". Every entry should name a file
and a concrete change. A chunk that cannot be verified without a later chunk is too small or
cut in the wrong place.

## 6. Goldfish clean

**Pass:** a fresh goldfish, given only the doc path, explains the goal and the relevant parts
of the current system correctly, and its guess-list is empty or trivial. For large tier, the
critic also returns no blocker or major findings. If a round cap (see `tiers.md`) is hit
first, the gate passes only when the user explicitly accepts the residual items; record them
under Open questions.

**Faked when:** the Elephant added context to the goldfish's brief, or the same subagent was
reused after the doc changed. Always a new subagent, always only the doc path.
