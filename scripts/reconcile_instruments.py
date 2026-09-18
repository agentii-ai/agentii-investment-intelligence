#!/usr/bin/env python3
"""reconcile_instruments.py — T162 (Q140/Q81). The migration reconciler.

WHY THIS EXISTS. Q81 rule 2 rotates `agentii.md` per period. In a workspace with
NO `constitution.md`, `agentii.md` **IS the constitution** — so rotating it
rotates away the project's principles, justified by a premise that is false
there. Q140 caught that as a *destructive* action, the seventh and most severe
instance of this spec's one recurring defect.

T160 gates the rotation on the instrument predicate, which stops the harm going
forward. **This script is for the workspaces it already happened to.** Rotation
is one-way: once a principles-bearing `agentii.md` is rotated, the principles are
gone from the live file, and nothing in the system would notice — the file still
exists, it is just no longer the thing it was.

So this compares what a workspace's `agentii.md` SAYS (in the archive, in git
history, or in whatever survived) against its `constitution.md`, and reports what
would be lost if the two were treated as interchangeable. It is the only item in
the spec that can catch a workspace already migrated onto the wrong path.

Usage:
    python3 scripts/reconcile_instruments.py --workspace <dir>
    python3 scripts/reconcile_instruments.py --workspace <dir> --json
    python3 scripts/reconcile_instruments.py --a old-agentii.md --b constitution.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# A "principle" is a normative statement. The heuristics below are deliberately
# mechanical: Q140's own rule is that the instrument's ROLE follows from
# `constitution.md`'s existence, not from a judgment about the prose. The same
# discipline applies here — this reports candidates for a human to check, and
# never claims a principle was lost on its own authority.
_PRINCIPLE_HEADING = re.compile(r"^#{1,4}\s+(.{3,120})$", re.M)
_NORMATIVE = re.compile(
    r"(?i)\b(MUST|MUST NOT|SHALL|NEVER|ALWAYS|REQUIRED|FORBIDDEN|PROHIBIT|"
    r"\bP\d+(\.\d+)?\b|principle|约束|必须|禁止|不得|原则)")


def extract_principles(text: str) -> list[str]:
    """Candidate principles: headings, plus lines carrying a normative marker.

    Returns normalised strings so the comparison is not defeated by whitespace or
    a markdown bullet that moved."""
    out: list[str] = []
    for m in _PRINCIPLE_HEADING.finditer(text):
        h = m.group(1).strip()
        if not re.match(r"^(table of contents|contents|fields|usage|changelog)\b", h, re.I):
            out.append(h)
    for line in text.splitlines():
        s = line.strip().lstrip("-*0123456789. ").strip()
        if len(s) < 12 or len(s) > 240:
            continue
        if _NORMATIVE.search(s) and not _PRINCIPLE_HEADING.match(line):
            out.append(s)
    seen, deduped = set(), []
    for p in out:
        k = re.sub(r"\W+", " ", p).lower()
        if k not in seen:
            seen.add(k)
            deduped.append(p)
    return deduped


def reconcile(a_text: str, b_text: str) -> dict:
    """What `a` (the old instrument) says that `b` (the new one) does not.

    `lost` is the finding. It is not "b is wrong" — a migration may legitimately
    drop a principle — but a drop that nobody decided is the failure Q140 is
    about, and only a diff makes it visible."""
    a, b = extract_principles(a_text), extract_principles(b_text)
    b_norm = {re.sub(r"\W+", " ", x).lower() for x in b}
    b_blob = re.sub(r"\W+", " ", b_text).lower()

    lost, kept = [], []
    for p in a:
        k = re.sub(r"\W+", " ", p).lower()
        # Present if the exact line survived, or if its distinctive terms do.
        terms = [w for w in k.split() if len(w) > 4]
        hit = k in b_norm or (terms and sum(t in b_blob for t in terms) / len(terms) >= 0.75)
        (kept if hit else lost).append(p)
    return {"principles_in_a": len(a), "principles_in_b": len(b),
            "kept": kept, "lost": lost}


def survey(workspace: Path) -> dict:
    """Workspace-level view: which instrument governs, and what a migration lost."""
    import agentii_cmd

    kind, why = agentii_cmd.detect_instrument(workspace)
    out = {"workspace": str(workspace), "instrument": kind, "why": why}
    c, a = workspace / "constitution.md", workspace / "agentii.md"
    out["files"] = {"constitution.md": c.is_file(), "agentii.md": a.is_file()}

    if kind == agentii_cmd.INSTRUMENT_AGENTII_MD:
        out["verdict"] = (
            "agentii.md IS the constitution here — Q81 rules 1-2 (rotation) must "
            "NOT run against it, and a rotation already performed is unrecoverable "
            "from the live file.")
        out["rotation_safe"] = False
    elif kind == agentii_cmd.INSTRUMENT_CONSTITUTION:
        out["verdict"] = ("constitution.md governs; agentii.md is a chronicle and "
                          "Q81's rotation applies normally.")
        out["rotation_safe"] = True
        if a.is_file():
            r = reconcile(a.read_text(encoding="utf-8"), c.read_text(encoding="utf-8"))
            # Only meaningful if agentii.md looks principles-bearing at all.
            if r["lost"]:
                out["reconcile"] = r
                out["verdict"] += (
                    f" ⚠️ {len(r['lost'])} principle(s) appear in agentii.md and not "
                    f"in constitution.md — check the migration did not silently "
                    f"drop them.")
    else:
        out["verdict"] = "no instrument — nothing to reconcile"
        out["rotation_safe"] = None
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="reconcile_instruments.py",
                                 description="instrument reconciler (T162, Q140)")
    ap.add_argument("--workspace", help="workspace directory to survey")
    ap.add_argument("--a", help="compare this file (the OLD instrument)")
    ap.add_argument("--b", help="…against this one (the NEW instrument)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.a and a.b:
        r = reconcile(Path(a.a).read_text(encoding="utf-8"),
                      Path(a.b).read_text(encoding="utf-8"))
        if a.json:
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(f"{r['principles_in_a']} principle(s) in {a.a}, "
                  f"{r['principles_in_b']} in {a.b}")
            print(f"\nWOULD BE LOST ({len(r['lost'])}):")
            for p in r["lost"]:
                print(f"  - {p[:110]}")
        return 1 if r["lost"] else 0

    if not a.workspace:
        ap.print_help()
        return 2
    ws = Path(a.workspace).resolve()
    if not ws.is_dir():
        print(f"not a directory: {ws}", file=sys.stderr)
        return 2
    out = survey(ws)
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"workspace : {out['workspace']}")
        print(f"instrument: {out['instrument']}")
        print(f"  {out['why']}")
        print(f"  rotation_safe: {out['rotation_safe']}")
        print(f"\n{out['verdict']}")
        if "reconcile" in out:
            print(f"\nWOULD BE LOST ({len(out['reconcile']['lost'])}):")
            for p in out["reconcile"]["lost"]:
                print(f"  - {p[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
