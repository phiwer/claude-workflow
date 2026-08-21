---
name: wf-phase5-verify
description: Run Phase 5 verification after implementation - verify spec was implemented correctly, check tests pass, document any deviations. Produces PHASE5_VERIFICATION.md.
argument-hint: [spec-file-path]
allowed-tools: Read, Glob, Grep, Write, Bash, Task, AskUserQuestion
model: sonnet
---

# Phase 5: Implementation Verification

Verify the implementation matches the specification, all tests pass, and document any deviations.

## Spec to Verify

$ARGUMENTS

## Instructions

### Step 0: Read Project Config

1. Try to read `.claude/workflow/project-config.json`
2. Extract values (defaults if absent):
   - `specDir` = `docs/specs`
   - `archiveDir` = `docs/specs/archive`
3. Find the main worktree root:
   ```
   Run: git worktree list 2>/dev/null | head -1 | awk '{print $1}'
   Use the result as GIT_MAIN_ROOT. All context files live at:
     {GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json
   Falls back to .claude/workflow/ if git command fails.
   ```

### Step 1: Handle Missing Arguments / Auto-Detect Spec

If no spec path was provided:

1. Glob `{GIT_MAIN_ROOT}/.claude/workflow/*-context.json`. If multiple found, ask the user which feature to continue (AskUserQuestion). If one found, check it for a recent `specPath` to use.
   - **Reconcile before trusting it.** The on-disk artifacts are the source of truth; the context file is only a cache a prior phase may have failed to update (interrupted, errored, or you took over manually). Before relying on `lastPhase`, check it against reality — the spec `Status`, which `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE*.md` documents exist, and whether the implementation and tests are present. If they disagree, **trust the artifacts**, tell the user about the drift, and rewrite the context to match before continuing.
2. Use Glob to find active specs: `{specDir}/*/*.md`
2. Filter for `*_SPEC.md` files with Status: "READY FOR IMPLEMENTATION" or similar
3. Check which of those have no PHASE5_VERIFICATION.md yet. A Phase 3 consolidation doc is not
   required — a `/wf-plan`-originated spec reaches `READY FOR IMPLEMENTATION` via live
   consolidation and never produces one.
4. If multiple found, use AskUserQuestion to ask which to verify
5. If a spec's Status is still DRAFT (consolidation never happened at all), warn and suggest
   running `/wf-phase3-consolidate` (full pipeline) or `/wf-plan` (if no spec exists yet)

### Step 2: Read Required Documents

Read:
1. The main spec file
2. The Phase 3 consolidation document, if it exists — otherwise the spec's own "Decisions
   Requiring Your Judgment" section (a `/wf-plan`-originated spec never produces a separate
   Phase 3 document)
3. The Phase 4 implementation record (`{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE4_IMPLEMENTATION.md`), if present — use its deviations list as the handoff rather than reconstructing it
4. CLAUDE.md for implementation context

### Step 3: Delegate the FULL Test Suite Run to a Subagent

Test output — especially failures, with full stack traces — is verbose, and running it inline
would put all of that directly into this session's context for no benefit once you have the
result. Spawn a subagent (via Task) to run the suite and report back only a structured summary.

**Always run the full suite; never let the Phase 5 verdict rest on a targeted run** (`-Dtest=`,
`pytest …::…`, `.only`, a single spec file). A targeted run only proves the tests you *thought
to name* still pass — it cannot catch regressions in classes you didn't think to run, which is
exactly where they hide. The risk is highest for the changes Phase 5 is least suspicious of: a
**constraint removal** or any behaviour change has a regression surface of "every test that
exercised the old behaviour," and that set is precisely the one you won't hand-pick. This
constraint must survive delegation — put it directly in the subagent's brief, not just in your
own instructions, since the subagent is a fresh context with no memory of why it matters.

> Precedent — why this rule exists: TRA-1466 removed an override that forced pipeline reports to
> `DATA` content. A targeted Phase 5 run of two hand-picked classes passed and the feature was
> declared verified, but a stale test in an *unrun* class still asserted the old "forced to
> DATA" contract. Only CI (full suite) caught it, after Phase 5 had signed off.

Spawn a general-purpose subagent with this brief:

> Run the project's **entire** test suite — every test, not a hand-picked subset. Check
> CLAUDE.md for the project-specific command (e.g. `mvn test`, `npm test`, `pytest`). **Never**
> scope to specific classes/files (`-Dtest=`, `pytest …::…`, `.only`, a single spec file) — a
> targeted run only proves the tests you thought to name still pass and cannot catch regressions
> in classes you didn't think to run. [Precedent: TRA-1466 — a targeted 2-class run passed while
> a stale test in an unrun class still asserted a removed contract; only the full suite caught
> it.] A targeted run is fine while you're iterating to get fast feedback, but your final report
> must be backed by one clean full-suite run.
>
> Report back concisely, not the raw log:
> - The test runner's own summary line verbatim (e.g. "Tests run: 340, Failures: 0, Errors: 0")
> - Total tests run, passed, failed
> - Any new test classes added (names only)
> - For each failure: test name + the assertion/error message (not the full stack trace unless
>   it's needed to explain what broke)

Use the subagent's structured summary for the rest of this phase — do not re-run the suite
inline in the main session, and do not ask the subagent to paste its raw output back to you.

Capture (from the subagent's summary):
- Total tests run
- Tests passed/failed
- Any new test classes added

### Step 4: Verify Implementation Checklist

Check each item from the spec:

1. **Files Added**: Verify all specified files exist
2. **Files Modified**: Verify changes were made to specified files
3. **Configuration/Constants Added**: Check relevant config files
4. **HTTP Endpoints**: Verify endpoints work (if applicable)
5. **Integration Points**: Check pipeline/factory integration
6. **Test Coverage**: Verify test files exist and pass

### Step 5: Document Deviations

If the implementation differs from the spec:
1. Document what changed
2. Explain why the deviation was necessary
3. Determine if the spec should be updated

### Step 6: Create Verification Document

Create `{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE5_VERIFICATION.md`:

```markdown
# {FEATURE-ID} Phase 5: Verification

**Date**: {today's date}
**Feature**: {Feature Name}
**Phase**: 5 of 6 (Verification)

---

## Executive Summary

{Brief summary of implementation status}

**Status**: {✅ VERIFIED - Ready for Retrospective / ⚠️ ISSUES FOUND / ❌ FAILED}

---

## Verification Checklist

### 1. Files Added

**Status**: {PASS ✅ / FAIL ❌}

| Expected File | Status | Notes |
|---------------|--------|-------|
| {File} | ✅ | {location} |

### 2. Files Modified

**Status**: {PASS ✅ / FAIL ❌}

| File | Expected Change | Status |
|------|-----------------|--------|
| {File} | {change} | ✅ |

### 3. HTTP Endpoints (if applicable)

**Status**: {PASS ✅ / FAIL ❌ / N/A}

{Endpoint verification details}

---

## Test Coverage Analysis

### Test Count Summary

**Target**: {from spec}
**Delivered**: {actual count}

### Test Classes

| Test | Focus | Tests | Status |
|------|-------|-------|--------|
| {TestClass} | {focus} | {count} | ✅ |

### Test Run Results

```
{paste test output summary}
```

---

## Deviations from Specification

### Deviation 1: {Title}

**Spec Said**: {what spec specified}
**Implementation**: {what was actually done}
**Reason**: {why the change}
**Spec Update Needed**: {Yes/No}

---

## Phase 5 Verdict

**Status**: ✅ **VERIFIED - Ready for Retrospective**

**Test Summary**: {X} tests, all passing

**Deviations**: {count} documented

---

**Verification Completed**: {date}
**Next Phase**: Phase 6 - Retrospective (`/wf-phase6-retrospective`)
```

### Step 7: Update Main Spec Status

Edit the main spec to update Status to "IMPLEMENTED".

### Step 8: Output Summary

1. Confirm the verification document was created
2. Report overall status
3. Summarize test results
4. List any deviations

### Step 9: Record token usage

Append this phase's token usage to the verification document and context:

```bash
TU=$(ls "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/phiwer/phiwer/*/scripts/record-token-usage.py 2>/dev/null | head -1)
[ -n "$TU" ] && python3 "$TU" --phase wf-phase5-verify \
  --context "{GIT_MAIN_ROOT}/.claude/workflow/{FEATURE-ID}-context.json" \
  --artifact "{archiveDir}/{feature-dir}/{FEATURE-ID}_PHASE5_VERIFICATION.md" \
  --ledger "{specDir}/TOKEN_LEDGER.csv" --ticket "{FEATURE-ID}" \
  || echo "token-usage: script not found, skipping (best-effort)"
```

### Step 10: Phase Complete — Next Steps

**If VERIFIED** — display:
> Phase 5 complete. Implementation verified. ✅
>
> **Next**: Start a new session and run `/wf-phase6-retrospective` — context will auto-load.
> (Every retrospective checked across this project's history was either a verified, durable
> CLAUDE.md addition or a reasoned "nothing generalizable here" — never filler, even for small
> features. Consider `/wf-phase5-6-complete` next time to avoid a second context reload — this
> standalone path is for when you deliberately want to pause here first.)

**If ISSUES FOUND** — use AskUserQuestion for the within-phase decision only:
- header: "Issues found"
- question: "Verification found issues. How do you want to proceed?"
- option1: label="Fix and re-verify", description="Address issues, then re-run /wf-phase5-verify in a new session"
- option2: label="Proceed to retrospective", description="Continue despite issues — document them in the retrospective"

Then display: "After deciding, start a new session to continue."

Do NOT offer AskUserQuestion for the VERIFIED path. The user must manually start a new session.
