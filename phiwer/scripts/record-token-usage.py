#!/usr/bin/env python3
"""Record Claude Code token usage for a workflow phase.

Locates the current session's transcript via $CLAUDE_CODE_SESSION_ID (searched
under $CLAUDE_CONFIG_DIR/projects), sums its `usage` plus the usage of any
subagents it spawned (`<session>/subagents/agent-*.jsonl`), then:

  --mode record : writes a "## Token Usage" section into the phase artifact (if
                  given) and a tokenUsage entry into the workflow context JSON.
  --mode total  : reads the context's recorded per-phase usage and writes a
                  "## Token Usage (all phases)" grand-total table into the
                  artifact (used by /wf-close). The table surfaces non-cached
                  output (generated) tokens per phase alongside the gross total.

If --ledger is given, every --mode record call also appends one row to a git-committed CSV
ledger (ticket, phase, who ran it, model, tokens) -- unlike the context JSON (gitignored,
deleted by /wf-close) and the per-doc markdown tables (scattered across many files), the
ledger is a single durable, structured record of what every feature/phase actually cost, and
who ran it. --mode total appends one further row per feature with phase="ALL_PHASES_TOTAL",
attributed to whoever ran the completing phase -- i.e. who completed the feature.

Best-effort: any missing file is treated as zero and never aborts the phase.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import re
import subprocess
import sys

USAGE_KEYS = ("input_tokens", "output_tokens",
              "cache_read_input_tokens", "cache_creation_input_tokens")
LEDGER_HEADER = ("timestamp", "ticket", "phase", "user", "model",
                  "main_total", "subagent_total", "subagent_count", "phase_total")


def _find_main_transcript(cfg, sid):
    base = os.path.join(cfg, "projects")
    target = f"{sid}.jsonl"
    for root, _dirs, files in os.walk(base):
        if target in files:
            return root, os.path.join(root, target)
    return None, None


def _sum_file(path):
    totals = dict.fromkeys(USAGE_KEYS, 0)
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                usage = (obj.get("message") or {}).get("usage") or {}
                for key in USAGE_KEYS:
                    value = usage.get(key)
                    if isinstance(value, int):
                        totals[key] += value
    except (FileNotFoundError, IsADirectoryError):
        pass
    totals["total"] = sum(totals[k] for k in USAGE_KEYS)
    return totals


def _sum_files(paths):
    agg = dict.fromkeys(USAGE_KEYS, 0)
    for path in paths:
        one = _sum_file(path)
        for key in USAGE_KEYS:
            agg[key] += one[key]
    agg["total"] = sum(agg[k] for k in USAGE_KEYS)
    return agg, len(paths)


def _fmt(number):
    return f"{number:,}"


def _row(label, data, bold_total=False):
    total = f"**{_fmt(data['total'])}**" if bold_total else _fmt(data["total"])
    return (f"| {label} | {_fmt(data['input_tokens'])} | {_fmt(data['output_tokens'])} "
            f"| {_fmt(data['cache_read_input_tokens'])} "
            f"| {_fmt(data['cache_creation_input_tokens'])} | {total} |")


def _phase_section(main, sub, subcount):
    combined = {k: main[k] + sub[k] for k in USAGE_KEYS}
    combined["total"] = main["total"] + sub["total"]
    lines = [
        "## Token Usage",
        "",
        "| scope | input | output | cache-read | cache-create | total |",
        "|-------|------:|-------:|-----------:|-------------:|------:|",
        _row("main session", main),
    ]
    if subcount:
        lines.append(_row(f"subagents (×{subcount})", sub))
    lines.append(_row("**phase total**", combined, bold_total=True))
    lines.append("")
    lines.append("_As of phase completion; main session + spawned subagents. "
                 "Excludes this recording step and the phase's final summary._")
    lines.append("")
    return "\n".join(lines), combined


def _upsert(artifact, heading, body):
    """Insert or replace a section that begins with an exact heading line."""
    try:
        with open(artifact, encoding="utf-8") as handle:
            content = handle.read()
    except FileNotFoundError:
        return False
    pattern = re.compile(r"(?m)^" + re.escape(heading) + r"\n.*?(?=\n## |\Z)", re.S)
    if pattern.search(content):
        content = pattern.sub(body.rstrip() + "\n", content, count=1)
    else:
        content = content.rstrip() + "\n\n" + body.rstrip() + "\n"
    with open(artifact, "w", encoding="utf-8") as handle:
        handle.write(content)
    return True


def _current_user():
    """Best-effort identity of whoever is running this phase. git identity is preferred over
    the OS login since it reflects the actual developer on a shared machine, and matches how
    the rest of this project already attributes work (commit authorship)."""
    for cmd in (("git", "config", "user.name"), ("git", "config", "user.email")):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        except (OSError, subprocess.SubprocessError):
            continue
        value = result.stdout.strip()
        if result.returncode == 0 and value:
            return value
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"


def _extract_primary_model(path):
    """Best-effort: the most common `message.model` value in a transcript. Not load-bearing
    for anything else this script does -- if the field is absent (older transcript formats,
    subagent files that don't carry it) this just returns "" and the ledger row leaves the
    column blank rather than failing."""
    counts = {}
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    continue
                model = (obj.get("message") or {}).get("model")
                if model:
                    counts[model] = counts.get(model, 0) + 1
    except (FileNotFoundError, IsADirectoryError):
        pass
    return max(counts, key=counts.get) if counts else ""


def _append_ledger(ledger_path, row):
    """Append one row to the git-committed token ledger, writing the header first if the
    file is new. Best-effort: a failure here must never abort the phase."""
    if not ledger_path:
        return
    try:
        os.makedirs(os.path.dirname(ledger_path) or ".", exist_ok=True)
        is_new = not os.path.exists(ledger_path)
        with open(ledger_path, "a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            if is_new:
                writer.writerow(LEDGER_HEADER)
            writer.writerow(row)
    except OSError as exc:
        print(f"token-usage: could not write ledger {ledger_path}: {exc}", file=sys.stderr)


def _load_context(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except (ValueError, OSError):
            return {}
    return {}


def _worktree_roots():
    """Every checkout of the current repository (main first), or [] outside git."""
    try:
        result = subprocess.run(("git", "worktree", "list", "--porcelain"), capture_output=True,
                                text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return []
    if result.returncode != 0:
        return []
    return [line[len("worktree "):] for line in result.stdout.splitlines()
            if line.startswith("worktree ")]


def _merge_stray_contexts(context_path, data):
    """Best-effort recovery for a context file written into a worktree instead of the main
    checkout. Confirmed on TRA-1531: /wf-design wrote its context (and its token usage) under
    the worktree after EnterWorktree, while /wf-build and /wf-close used the main checkout's
    file, so the design phase was missing from the grand total. Copies in phases and keys the
    main file lacks; never overwrites, so a phase is never counted twice. Returns the list of
    stray files merged."""
    target = os.path.realpath(context_path)
    name = os.path.basename(context_path)
    usage = data.setdefault("tokenUsage", {})
    merged = []
    for root in _worktree_roots():
        candidate = os.path.join(root, ".claude", "workflow", name)
        if not os.path.isfile(candidate) or os.path.realpath(candidate) == target:
            continue
        stray = _load_context(candidate)
        for phase, value in (stray.get("tokenUsage") or {}).items():
            if phase not in usage:
                usage[phase] = value
            elif usage[phase] != value:
                print(f"token-usage: {candidate} has a different '{phase}' entry; "
                      f"keeping the one in {context_path}", file=sys.stderr)
        for key, value in stray.items():
            if key not in ("tokenUsage", "tokenUsageTotal", "lastPhase"):
                data.setdefault(key, value)
        merged.append(candidate)
        print(f"token-usage: merged stray context {candidate} into {context_path}",
              file=sys.stderr)
    if merged:
        data["tokenUsageTotal"] = sum(v.get("total", 0) for v in usage.values())
    return merged


def _record(args, cfg, sid):
    if not sid:
        print("token-usage: no CLAUDE_CODE_SESSION_ID; skipping", file=sys.stderr)
        return
    session_dir, main_tx = _find_main_transcript(cfg, sid)
    if not main_tx:
        print("token-usage: session transcript not found; skipping", file=sys.stderr)
        return
    main = _sum_file(main_tx)
    sub_glob = os.path.join(session_dir, sid, "subagents", "**", "agent-*.jsonl")
    sub, subcount = _sum_files(glob.glob(sub_glob, recursive=True))
    section, combined = _phase_section(main, sub, subcount)

    if args.artifact:
        _upsert(args.artifact, "## Token Usage", section)

    data = _load_context(args.context)
    _merge_stray_contexts(args.context, data)
    usage = data.setdefault("tokenUsage", {})
    usage[args.phase] = {
        "main": main, "subagents": sub,
        "subagentCount": subcount, "total": combined["total"],
    }
    data["tokenUsageTotal"] = sum(v.get("total", 0) for v in usage.values())
    os.makedirs(os.path.dirname(args.context) or ".", exist_ok=True)
    with open(args.context, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    print(section)

    if args.ledger:
        ticket = args.ticket or data.get("featureId") or "unknown"
        model = _extract_primary_model(main_tx)
        _append_ledger(args.ledger, (
            datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            ticket, args.phase, _current_user(), model,
            main["total"], sub["total"], subcount, combined["total"],
        ))


def _total(args):
    data = _load_context(args.context)
    if _merge_stray_contexts(args.context, data):
        with open(args.context, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    usage = data.get("tokenUsage", {})
    if not usage:
        print("token-usage: no per-phase usage recorded yet", file=sys.stderr)
        return
    lines = [
        "## Token Usage (all phases)",
        "",
        "| phase | subagents | output (non-cached) | total tokens |",
        "|-------|----------:|--------------------:|-------------:|",
    ]
    grand = 0
    grand_output = 0
    for phase, value in usage.items():
        grand += value.get("total", 0)
        output = ((value.get("main") or {}).get("output_tokens", 0)
                  + (value.get("subagents") or {}).get("output_tokens", 0))
        grand_output += output
        lines.append(f"| {phase} | {value.get('subagentCount', 0)} "
                     f"| {_fmt(output)} | {_fmt(value.get('total', 0))} |")

    lines.append(f"| **grand total** |  | **{_fmt(grand_output)}** | **{_fmt(grand)}** |")

    lines.append("")
    lines.append("_\"output (non-cached)\" is generated tokens, which are never served "
                 "from cache; the remainder of each phase's total is input, the bulk of "
                 "it cache reads._")
    body = "\n".join(lines)
    if args.artifact:
        _upsert(args.artifact, "## Token Usage (all phases)", body)
    print(body)

    if args.ledger:
        ticket = args.ticket or data.get("featureId") or "unknown"
        _append_ledger(args.ledger, (
            datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            ticket, "ALL_PHASES_TOTAL", _current_user(), "",
            "", "", "", grand,
        ))


def main():
    parser = argparse.ArgumentParser(description="Record workflow phase token usage.")
    parser.add_argument("--phase", default="", help="phase key, e.g. wf-build")
    parser.add_argument("--context", required=True, help="path to {FEATURE-ID}-context.json")
    parser.add_argument("--artifact", default="", help="phase artifact markdown file")
    parser.add_argument("--mode", choices=["record", "total"], default="record")
    parser.add_argument("--ledger", default="",
                         help="path to a git-committed CSV ledger to append this row to "
                              "(e.g. {specDir}/TOKEN_LEDGER.csv); omit to skip ledger writing")
    parser.add_argument("--ticket", default="",
                         help="ticket id for the ledger row; defaults to the context file's "
                              "featureId if omitted")
    args = parser.parse_args()

    cfg = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")

    if args.mode == "total":
        _total(args)
    else:
        if not args.phase:
            print("token-usage: --phase required for record mode", file=sys.stderr)
            return
        _record(args, cfg, sid)


if __name__ == "__main__":
    main()
