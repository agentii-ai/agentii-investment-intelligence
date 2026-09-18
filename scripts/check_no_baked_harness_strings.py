#!/usr/bin/env python3
"""check_no_baked_harness_strings.py — Q34 (spec 046). Two checks, not one.

Q34 came from an upstream failure that was OBSERVED rather than predicted: speckit
built an abstraction for harness invocation syntax, then bypassed it in three
places, producing five "shared" cores that differed only in decorative call
strings. Its rule 3 reads:

    CI 检查：core 树内 grep 字面量 `/agentii-` 或 `/agentii.` → fail

**That rule as literally written is unusable here, and measuring said so.** This
repo contains 307 occurrences of `//agentii.` — every one of them a citation URL
of the form `https://agentii.ai/v/...`. A literal grep would emit 307 findings and
catch nothing. The rule's INTENT is to catch harness-specific *command invocation*
strings (`/agentii-plan` for one harness vs `/agentii.plan` for another), so check
A anchors on the registered command verbs instead of on the raw literal.

Check B is the one that actually bites. Q34 rule 4 says
`packaging/targets/{harness}/` "仅决定文件放到哪里（.claude/skills/ vs
.agents/skills/ vs .opencode/commands/），**不重写文件内容**" — targets PLACE,
they do not rewrite. If that holds, every target file is byte-identical to its
source, and any difference is either staleness (a copy that outlived an edit) or an
undeclared rewrite (the Q34 violation itself). Both are failures; both are
mechanically decidable; neither is visible by reading — 330 files all "exist".

Exit codes: 0 = clean, 1 = findings, 2 = the tree could not be read.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
TARGETS = KIT / "packaging" / "targets"

# A command-invocation string is a separator plus a VERB, not the product domain.
# Deriving the verbs from agentii_cmd.py keeps this honest as commands are added.
_CMD = re.compile(r"[/$]agentii[-.]([a-z][a-z-]+)")
# URL citations are the 307 false positives the literal rule would produce.
_URL = re.compile(r"//agentii\.ai")

# Where the rule itself is discussed; a check that flags its own documentation
# teaches people to ignore it.
EXEMPT = {
    "scripts/check_no_baked_harness_strings.py",
    "scripts/audit_named_artifacts.py",
}


def _verbs() -> set[str]:
    src = KIT / "scripts" / "agentii_cmd.py"
    if not src.is_file():
        return set()
    text = src.read_text(encoding="utf-8")
    verbs = set(re.findall(r'add_parser\(\s*"([a-z-]+)"', text))
    m = re.search(r"^DELEGATING\s*=\s*\{(.*?)^\}", text, re.S | re.M)
    if m:
        verbs |= set(re.findall(r'"([a-z-]+)":\s*\(', m.group(1)))
    return verbs


def _sources() -> dict[str, Path]:
    """skill dir name -> its canonical SKILL.md, excluding the packaged copies."""
    out: dict[str, Path] = {}
    for p in KIT.glob("plugins/**/skills/**/SKILL.md"):
        out.setdefault(p.parent.name, p)
    return out


def check_a(verbs: set[str]) -> list[str]:
    """No harness-specific command invocation in the core tree."""
    problems: list[str] = []
    scanned = 0
    for p in sorted(KIT.rglob("*")):
        rel = p.relative_to(KIT).as_posix()
        if (not p.is_file() or rel in EXEMPT or p.suffix not in
                {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt"}):
            continue
        if any(seg in rel for seg in ("/.venv/", "/.git/", "node_modules/",
                                      "/packaging/targets/")):
            continue
        scanned += 1
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if _URL.search(line):
                continue                      # a citation URL, not an invocation
            for m in _CMD.finditer(line):
                if m.group(1) in verbs:
                    problems.append(f"{rel}:{i} baked command invocation {m.group(0)!r}")
    print(f"  A. baked harness strings — {scanned} files scanned, {len(problems)} findings")
    return problems


def check_b(sources: dict[str, Path]) -> tuple[list[str], dict[str, int]]:
    """Every package target file must be byte-identical to its source (Q34 rule 4)."""
    problems: list[str] = []
    per: dict[str, list[int]] = {}
    if not TARGETS.is_dir():
        return [f"{TARGETS} does not exist — Q34 has nothing to check"], {}
    for t in sorted(TARGETS.glob("*/*/SKILL.md")):
        harness, skill = t.parts[-3], t.parent.name
        src = sources.get(skill)
        per.setdefault(harness, [0, 0])
        per[harness][1] += 1
        if src is None:
            problems.append(f"{t.relative_to(KIT)} — no source skill named {skill!r}")
            continue
        a = hashlib.sha256(src.read_bytes()).hexdigest()
        b = hashlib.sha256(t.read_bytes()).hexdigest()
        if a != b:
            per[harness][0] += 1
            problems.append(f"{t.relative_to(KIT)} — stale or rewritten vs {src.relative_to(KIT)}")
    stale = sum(v[0] for v in per.values())
    tot = sum(v[1] for v in per.values())
    print(f"  B. target == source — {tot} packaged SKILL.md files, {stale} differ")
    for h in sorted(per):
        print(f"       {h:<14} {per[h][0]:>3} / {per[h][1]}")
    return problems, {h: v[0] for h, v in per.items()}


def main() -> int:
    ap = argparse.ArgumentParser(prog="check_no_baked_harness_strings.py")
    ap.add_argument("--max-report", type=int, default=10,
                    help="cap printed findings per check (a message nobody can read is not a message)")
    a = ap.parse_args()

    verbs, sources = _verbs(), _sources()
    if not verbs:
        print("could not read command verbs from agentii_cmd.py", file=sys.stderr)
        return 2
    print(f"Q34 — harness independence (spec 046)\n  command verbs: {sorted(verbs)}\n")

    pa = check_a(verbs)
    pb, _ = check_b(sources)
    problems = pa + pb

    if not problems:
        print("\nOK — no baked harness strings; every target matches its source.")
        return 0

    # stdout first: stderr is unbuffered, so without this the findings render ABOVE
    # the summary that explains them.
    sys.stdout.flush()
    print(f"\n{len(problems)} finding(s):", file=sys.stderr)
    for p in problems[:a.max_report]:
        print(f"  - {p}", file=sys.stderr)
    if len(problems) > a.max_report:
        print(f"  … +{len(problems) - a.max_report} more", file=sys.stderr)
    print("\n  A findings mean a harness separator reached the core tree (Q34 rule 1/2).\n"
          "  B findings mean packaging rewrote content OR the copies outlived an edit\n"
          "  (Q34 rule 4). Both are fixed the same way: regenerate targets from source.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
