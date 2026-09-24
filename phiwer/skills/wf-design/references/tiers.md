# Tiers

Size by risk and blast radius, not by lines of code. A two-line change to an auth check can
be large; a new 500-line self-contained module can be medium. Propose a tier with a one-line
reason; the user confirms or overrides.

## Small

Typical: a bug fix with a clear cause, a config change, a local refactor, anything touching a
couple of files where the right approach is obvious and easy to revert.

Requires: no doc. State which files you will change and why, then proceed. The always-on rules
in CLAUDE.md still apply.

Escalate to medium if you discover the change touches more than expected, involves a decision
the user would want a say in, or the "obvious" approach turns out to have alternatives.

## Medium

Typical: a feature within one module or service, a change to an internal interface, anything
where there are real design choices but limited impact outside the team's own code.

Requires: design doc; gates 1, 3, 4 and 5; a goldfish pass with an empty or trivial
guess-list (at most 2 goldfish rounds). Gates 2 and 6 in light form (a short assumptions list;
one goldfish, a second only if the first found real gaps). Critic is optional; suggest it if
the goldfish surfaced several gaps.

## Large

Typical: changes to public or cross-team APIs, data models or migrations, security or
privacy-sensitive paths, new services, anything hard to revert or with other teams depending
on it.

Requires: all six gates in full; goldfish loop until clean (at most 3 rounds); critic loop until
no blocker or major findings (at most 2 rounds). Suggest human review of the doc by a colleague
before approval where one is available.

## Round caps

The caps exist because uncapped review loops were the largest avoidable cost in this plugin's
history. When a cap is hit and the doc still isn't clean, stop looping and hand the residual
guesses or findings to the user: they decide whether to accept them as known risks, fix them
by hand, or split the work. A doc that can't converge in the cap is usually two designs.

## Signals

Push toward larger when: the change is hard to roll back; other teams or external clients
consume the interface; data is migrated or deleted; there is a security, privacy or money
path; you had to read many files to understand the area; the user is unsure what they want.

Push toward smaller when: the change is local, reversible and well-tested; there is an
established pattern in the codebase to follow; the user has already made the design decisions.
