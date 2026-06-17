#!/usr/bin/env python3
"""Record Claude Code token usage for a workflow phase.

Locates the current session's transcript via $CLAUDE_CODE_SESSION_ID (searched
under $CLAUDE_CONFIG_DIR/projects), sums its `usage` plus the usage of any
subagents it spawned (`<session>/subagents/agent-*.jsonl`), then:

  --mode record : writes a "## Token Usage" section into the phase artifact (if
                  given) and a tokenUsage entry into the workflow context JSON.
  --mode total  : reads the context's recorded per-phase usage and writes a
                  "## Token Usage (all phases)" grand-total table into the
                  artifact (used by Phase 6).

Best-effort: any missing file is treated as zero and never aborts the phase.
"""
import argparse
import glob
import json
import os
import re
import sys

USAGE_KEYS = ("input_tokens", "output_tokens",
              "cache_read_input_tokens", "cache_creation_input_tokens")


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


def _load_context(path):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except (ValueError, OSError):
            return {}
    return {}


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


def _total(args):
    data = _load_context(args.context)
    usage = data.get("tokenUsage", {})
    if not usage:
        print("token-usage: no per-phase usage recorded yet", file=sys.stderr)
        return
    lines = [
        "## Token Usage (all phases)",
        "",
        "| phase | subagents | total tokens |",
        "|-------|----------:|-------------:|",
    ]
    grand = 0
    for phase, value in usage.items():
        grand += value.get("total", 0)
        lines.append(f"| {phase} | {value.get('subagentCount', 0)} | {_fmt(value.get('total', 0))} |")
    lines.append(f"| **grand total** |  | **{_fmt(grand)}** |")
    lines.append("")
    body = "\n".join(lines)
    if args.artifact:
        _upsert(args.artifact, "## Token Usage (all phases)", body)
    print(body)


def main():
    parser = argparse.ArgumentParser(description="Record workflow phase token usage.")
    parser.add_argument("--phase", default="", help="phase key, e.g. wf-phase4-implement")
    parser.add_argument("--context", required=True, help="path to {FEATURE-ID}-context.json")
    parser.add_argument("--artifact", default="", help="phase artifact markdown file")
    parser.add_argument("--mode", choices=["record", "total"], default="record")
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
