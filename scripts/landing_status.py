#!/usr/bin/env python3
"""landing_status.py — compute spec 046's header from `landing-items.yaml` (Q113/Q134).

The spec's `Status:` block is a **declaration** unless something recomputes it. It
said "COMPLETE" while 181 items were open, and its counts sat at 212 rows while the
file held 216 — because they were maintained by hand across several rounds and
several edits silently no-op'd. Q134's rule is that the header is *derived*; this
is the thing that derives it.

`landing-items.yaml`'s own line 12 has documented this command since the file was
written. Until now it did not exist.

Usage:
    python3 scripts/landing_status.py --spec <spec.md>          # rewrite the header
    python3 scripts/landing_status.py --spec <spec.md> --check  # exit 1 if stale
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

# The header rows this script owns. Each is (regex, template) where the template
# takes the derived value. Anything else in the header is prose and is left alone.
ROWS = [
    (re.compile(r"^\| 落地项（本索引，do-once 粒度） \|.*\|$", re.M),
     "| 落地项（本索引，do-once 粒度） | **{ge}{rows}**{floor_note} |"),
    # `.*` not `[^）]*`: the note itself contains a parenthesised clause, and the
    # first version of this pattern therefore could not re-match its own output.
    (re.compile(r"^\| 其中已解决 \|.*\|$", re.M),
     "| 其中已解决 | **{resolved}**（{resolved_note}） |"),
    (re.compile(r"^\| 其中未解决 \| \*\*\d+\*\* \|", re.M),
     "| 其中未解决 | **{open}** |"),
    (re.compile(r"^按类型：.*$", re.M),
     "按类型：{by_type}。"),
]

RESOLVED_NOTE = ("spec 侧自更正 + 免责声明装配 + Phase 11 接线 + taxonomy v2 扩展 + 具名工件/数量审计")


def derive(index_path: Path) -> dict:
    d = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    items = d["items"]
    bt = collections.Counter(i["type"] for i in items)
    resolved = sum(1 for i in items if i.get("resolved"))
    # The index may be a FLOOR rather than a total. `landing-items.yaml` declares
    # this about itself when its own construction is known to be incomplete — it
    # does today, after a `git checkout` destroyed the working file and the
    # reconstruction recovered 217 of ~230 items from the session transcript.
    #
    # A derived header that reports a floor as a total is the defect Q113 exists
    # to prevent, one layer down: the number would be computed (so it passes the
    # derivation test) and still wrong (so it fails the point). `items_complete:
    # false` makes the header say `≥N` instead.
    complete = bool(d.get("totals", {}).get("items_complete", True))
    return {
        "rows": len(items),
        "ge": "" if complete else "≥",
        "complete": complete,
        "resolved": resolved,
        "open": len(items) - resolved,
        "by_type": " · ".join(f"`{k}` {v}" for k, v in sorted(bt.items(), key=lambda x: -x[1])),
        "resolved_note": RESOLVED_NOTE,
        "floor_note": ("" if complete else
                       "（**本索引是下限，不是总数** —— 见文件头部的 INCIDENT 记录："
                       "一次 `git checkout` 毁掉了工作副本，从会话记录重建得 217 条，"
                       "**约 13 条已确认不可恢复**）"),
        "meta_rules": len(d.get("meta_rules") or []),
    }


def render(spec_text: str, vals: dict) -> tuple[str, list[str]]:
    """Return (new_text, stale_row_labels). Idempotent: a second run changes nothing."""
    stale: list[str] = []
    for rx, tmpl in ROWS:
        m = rx.search(spec_text)
        if not m:
            stale.append(f"header row not found: {tmpl[:40]}")
            continue
        want = tmpl.format(**vals)
        if m.group(0) != want:
            stale.append(m.group(0)[:60])
            spec_text = spec_text[:m.start()] + want + spec_text[m.end():]
    return spec_text, stale


def main() -> int:
    ap = argparse.ArgumentParser(prog="landing_status.py")
    ap.add_argument("--spec", required=True, help="path to spec.md")
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 instead of rewriting")
    a = ap.parse_args()

    spec = Path(a.spec).resolve()
    index = spec.parent / "landing-items.yaml"
    if not index.is_file():
        print(f"missing index: {index}", file=sys.stderr)
        return 2

    vals = derive(index)
    text = spec.read_text(encoding="utf-8")
    new, stale = render(text, vals)

    print(f"derived from {index.name}: rows={vals['ge']}{vals['rows']} "
          f"resolved={vals['resolved']} open={vals['open']} "
          f"meta_rules={vals['meta_rules']}"
          + ("" if vals["complete"] else "  [items_complete: false — the count is a FLOOR]"))
    if not stale:
        print("header is current — nothing to do.")
        return 0
    if a.check:
        print(f"\nSTALE ({len(stale)} header value(s) disagree with the index):", file=sys.stderr)
        for s in stale:
            print(f"  - {s}", file=sys.stderr)
        print("\n  Run without --check to rewrite, then re-read the diff.", file=sys.stderr)
        return 1
    spec.write_text(new, encoding="utf-8")
    print(f"rewrote {len(stale)} header value(s) in {spec.name}")
    for s in stale:
        print(f"  was: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
