#!/usr/bin/env python3
"""Report whether CLAUDE.md rules that cite a ticket are ever cited again.

Every CLAUDE.md rule added via a retrospective carries a ticket tag, e.g. "(TRA-1475)" or
"(Precedent: TRA-1475 -- OrderSnapshotService...)" -- a claim that the rule earned its place
because of that ticket. This script checks whether that ticket is referenced again in any
LATER, DIFFERENT ticket's design doc (--design-dir), or in the older pipeline's archived
phase artifacts (*_PHASE*.md under --archive-dir) -- a signal the
rule is still actively relevant to how work gets reviewed and implemented.

A rule whose origin ticket is never cited again is not necessarily wrong -- it may just not
have come up -- but it is a legitimate candidate for a human to reconsider during the next
/wf-close rule-update pass, rather than assuming every rule earns permanent shelf
space by default.

Usage:
    python3 check-rule-citations.py --rules CLAUDE.md [--rules .claude/rules/*.md ...] \
        --archive-dir docs/specs/archive [--design-dir docs/design] [--stale-days 90]

Best-effort: a missing/unreadable file is skipped, never aborts.
"""
import argparse
import glob
import os
import re
import sys

TAG_PATTERN = re.compile(r"\(([^)]*?\b([A-Z][A-Z0-9]+-\d+)\b[^)]*)\)")
TICKET_IN_TEXT = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
FRONTMATTER_TICKET = re.compile(r"^ticket:\s*([A-Za-z][A-Za-z0-9]+-\d+)\s*$", re.MULTILINE)

# Rule-numbering schemes (this project's own ORD-NN convention) are cross-references to
# other rules, not ticket citations -- excluded by default so "(see ORD-05)" isn't mistaken
# for a ticket tag. Extend with --exclude-prefix for other projects' internal rule IDs.
DEFAULT_EXCLUDED_PREFIXES = {"ORD"}


def _read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
        return ""


def _expand(patterns):
    paths = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        paths.extend(matches if matches else ([pattern] if os.path.isfile(pattern) else []))
    return paths


def _label_for(content, tag_start):
    """Label a tag with the start of its enclosing bullet/paragraph, not an arbitrary
    fixed-width slice -- avoids cutting into the middle of a sentence."""
    para_start = 0
    for marker in ("\n\n", "\n- ", "\n1. ", "\n#"):
        idx = content.rfind(marker, 0, tag_start)
        if idx > para_start:
            para_start = idx
    label = re.sub(r"\s+", " ", content[para_start:tag_start]).strip()
    label = re.sub(r"^[-*#\d.\s]+", "", label)
    return label[:100] if label else "(rule text not found)"


def _extract_tags(rule_files, excluded_prefixes):
    """Find every rule paragraph carrying a ticket tag. Returns {ticket: [label, ...]}
    where label is a short excerpt identifying which rule the tag belongs to."""
    tags = {}
    for path in rule_files:
        content = _read(path)
        if not content:
            continue
        for match in TAG_PATTERN.finditer(content):
            ticket = match.group(2)
            prefix = ticket.split("-", 1)[0].upper()
            if prefix in excluded_prefixes:
                continue
            label = _label_for(content, match.start())
            tags.setdefault(ticket, []).append(f"{os.path.basename(path)}: {label}")
    return tags


def _ticket_from_path(path):
    match = re.search(r"([A-Z][A-Z0-9]+-\d+)", os.path.basename(os.path.dirname(path))) \
        or re.search(r"([A-Z][A-Z0-9]+-\d+)", os.path.basename(path))
    return match.group(1).upper() if match else None


def _ticket_from_design_doc(path, content):
    """Design docs (wf-design) carry their ticket in frontmatter; fall back to the path."""
    match = FRONTMATTER_TICKET.search(content.split("\n---", 1)[0]) if content.startswith("---") else None
    return match.group(1).upper() if match else _ticket_from_path(path)


def _find_citations(archive_dir, design_dir=None):
    """{ticket: {citing_ticket: [file, ...]}} -- every OTHER ticket's phase artifact (or
    design doc) that mentions this ticket's tag."""
    citations = {}
    paths = [(p, False) for p in glob.glob(os.path.join(archive_dir, "**", "*_PHASE*.md"), recursive=True)]
    if design_dir:
        paths += [(p, True) for p in glob.glob(os.path.join(design_dir, "**", "*.md"), recursive=True)]
    for path, is_design_doc in paths:
        content = _read(path)
        if not content:
            continue
        owning_ticket = _ticket_from_design_doc(path, content) if is_design_doc else _ticket_from_path(path)
        for mentioned in set(TICKET_IN_TEXT.findall(content)):
            if owning_ticket and mentioned.upper() == owning_ticket.upper():
                continue  # a ticket's own artifacts always mention itself; not a citation
            citations.setdefault(mentioned.upper(), {}).setdefault(
                owning_ticket or os.path.basename(path), []).append(path)
    return citations


def main():
    parser = argparse.ArgumentParser(description="Report citation counts for tagged CLAUDE.md rules.")
    parser.add_argument("--rules", nargs="+", default=["CLAUDE.md"],
                         help="rule file path(s) or globs to scan for (TICKET) tags")
    parser.add_argument("--archive-dir", default="docs/specs/archive",
                         help="directory to scan for phase artifacts citing those tags")
    parser.add_argument("--design-dir", default="",
                         help="directory of wf-design docs to scan as well (ticket from frontmatter)")
    parser.add_argument("--exclude-prefix", nargs="*", default=[],
                         help="additional non-ticket prefixes to exclude (ORD is always excluded)")
    args = parser.parse_args()

    rule_files = _expand(args.rules)
    if not rule_files:
        print("check-rule-citations: no rule files found, skipping", file=sys.stderr)
        return

    excluded = DEFAULT_EXCLUDED_PREFIXES | {p.upper() for p in args.exclude_prefix}
    tags = _extract_tags(rule_files, excluded)
    if not tags:
        print("check-rule-citations: no ticket-tagged rules found in the given files", file=sys.stderr)
        return

    citations = _find_citations(args.archive_dir, args.design_dir or None)

    print(f"# Rule citation report ({len(tags)} tagged rules)\n")
    print("| Origin ticket | Rule | Cited by | Times |")
    print("|---|---|---|---:|")
    stale = []
    for ticket, labels in sorted(tags.items()):
        citing = citations.get(ticket, {})
        count = sum(len(v) for v in citing.values())
        cited_by = ", ".join(sorted(citing.keys())) or "-- none --"
        for label in labels:
            print(f"| {ticket} | {label} | {cited_by} | {count} |")
        if count == 0:
            stale.append(ticket)

    if stale:
        print(f"\n**{len(stale)} rule(s) never cited again — candidates for the next /wf-close "
              f"rule-update pass to reconsider (not necessarily wrong, just unconfirmed "
              f"since origin):** {', '.join(stale)}")
    else:
        print("\nEvery tagged rule has been cited again by at least one later ticket.")


if __name__ == "__main__":
    main()
