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
    # Q113's own rule, derived. The first version of this row did not exist and
    # the Status line therefore asserted `Implemented` against 179 open items.
    (re.compile(r"^\*\*Status\*\*:.*$", re.M),
     "**Status**: **{status}**（按 **Q113**，状态**由落地项派生**，不得由头部声明）"
     "。T-编号任务：**{done}/{total}** [X] · {open_t} 未决 · {partial} 部分"
     "（另有 {d75} 条 `D75#N` 缺陷记录，不计入任务数）。"),
]

TASKS_MD = "tasks.md"

# Q113's rule, mechanised: **存在未落地项时，不得为 `Implemented`**. The spec's own
# Status line asserted exactly that while 179 items were open — a hand-declared
# status that contradicted the rule written three lines below it, which is also
# the defect Q134 exists to eliminate. So the status is DERIVED here too.
#
# The task counts come from tasks.md. The test count does NOT appear: this script
# cannot measure it, and a status line asserting a number nothing verifies is the
# same defect one layer down. It is reported by the suite instead.
_STATUS_OPEN = "落地项未决"
_STATUS_DONE = "Implemented"


def _task_counts(spec: Path) -> tuple[int, int, int, int]:
    f = spec.parent / TASKS_MD
    if not f.is_file():
        return (0, 0, 0, 0)
    text = f.read_text(encoding="utf-8")
    done = len(re.findall(r"^- \[X\] T\d", text, re.M))
    open_ = len(re.findall(r"^- \[ \] T\d", text, re.M))
    partial = len(re.findall(r"^- \[~\] T\d", text, re.M))
    # `D75#N` entries are Part I's defect ledger — real checklist items, but not
    # T-numbered tasks. Counted separately so the Status line's "tasks" number is
    # unambiguous; the first version silently excluded them and read as 6 short.
    d75 = len(re.findall(r"^- \[X\] D75#", text, re.M))
    return (done, open_, partial, d75)


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
    done, open_t, partial, d75 = _task_counts(index_path)
    total_t = done + open_t + partial
    return {
        "rows": len(items),
        # Q113: unresolved landing items forbid `Implemented`.
        "status": _STATUS_DONE if len(items) - resolved == 0 else _STATUS_OPEN,
        "done": done, "open_t": open_t, "partial": partial, "total": total_t,
        "d75": d75,
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


# plan.md carries two hand-maintained blocks that the same index can derive.
# Both were stale when this was written: the Part II Status said "Not started"
# against 55 clarifications (there are 147 and 185 tasks are done), and the
# "Measured scope" table — whose own caption says "extracted from the spec, NOT
# ESTIMATED" — asserted 168 items / 22 resolved / 146 open against ≥218 / 39 / 179,
# understating every row of its by-type breakdown.
PLAN_ROWS = [
    (re.compile(r"^\*\*Part II Status\*\*:.*$", re.M),
     "**Part II Status**: **{plan_status}** — **{questions}** clarifications total "
     "(Q1–Q{maxq}), {done}/{total} T-tasks complete. See §II.1."),
    (re.compile(r"^\| Landing items \(do-once granularity\) \|.*\|$", re.M),
     "| Landing items (do-once granularity) | **{ge}{rows}**{floor_short} |"),
    (re.compile(r"^\| …already resolved.*\|$", re.M),
     "| …already resolved | {resolved} |"),
    (re.compile(r"^\| …\*\*open\*\* \|.*\|$", re.M),
     "| …**open** | **{open}** |"),
    (re.compile(r"^\| By type \|.*\|$", re.M),
     "| By type | {by_type} |"),
]


def render_plan(plan_text: str, vals: dict) -> tuple[str, list[str]]:
    stale: list[str] = []
    for rx, tmpl in PLAN_ROWS:
        m = rx.search(plan_text)
        if not m:
            stale.append(f"plan row not found: {tmpl[:44]}")
            continue
        want = tmpl.format(**vals)
        if m.group(0) != want:
            stale.append(m.group(0)[:60])
            plan_text = plan_text[:m.start()] + want + plan_text[m.end():]
    return plan_text, stale


def main() -> int:
    ap = argparse.ArgumentParser(prog="landing_status.py")
    ap.add_argument("--spec", required=True, help="path to spec.md")
    ap.add_argument("--plan", default=None,
                    help="path to plan.md; derives its Part II Status and "
                         "measured-scope table from the same index")
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit 1 instead of rewriting")
    a = ap.parse_args()

    spec = Path(a.spec).resolve()
    index = spec.parent / "landing-items.yaml"
    if not index.is_file():
        print(f"missing index: {index}", file=sys.stderr)
        return 2

    vals = derive(index)
    # values only the plan rows need
    # COUNT BOTH Q-BLOCK FORMS. Part I mixes them: 62 numbered and 21 written as
    # `- **Q: ...**` with no number. The first version counted only the numbered
    # ones and added 83 for Part I, which double-counted those 62 and reported
    # **209 clarifications for a real 147** — the third time this session that a
    # count of mine was the broken instrument, not the claim it measured.
    stext = spec.read_text(encoding="utf-8")
    qs = [int(m.group(1)) for m in re.finditer(r"^- \*\*Q(\d+):", stext, re.M)]
    vals["questions"] = len(qs) + len(re.findall(r"^- \*\*Q:", stext, re.M))
    vals["maxq"] = max(qs) if qs else 0
    vals["plan_status"] = ("落地项未决 — 未落地项存在时不得标 Implemented（Q113）"
                           if vals["open"] else "complete")
    vals["floor_short"] = ("" if vals["complete"] else
                           "  ← **下限，不是总数**（见 landing-items.yaml 头部 INCIDENT）")
    text = spec.read_text(encoding="utf-8")
    new, stale = render(text, vals)

    print(f"derived from {index.name}: rows={vals['ge']}{vals['rows']} "
          f"resolved={vals['resolved']} open={vals['open']} "
          f"meta_rules={vals['meta_rules']}"
          + ("" if vals["complete"] else "  [items_complete: false — the count is a FLOOR]"))
    if not stale:
        print("header is current — nothing to do.")
        # NOT an early return: plan.md's rows are a separate surface and must be
        # derived even when the spec header is already current. The first version
        # returned here, so `--plan` silently did nothing whenever the header was
        # clean — a flag that reports success while examining nothing.
        if not a.plan:
            return 0
    if a.check and stale:
        print(f"\nSTALE ({len(stale)} header value(s) disagree with the index):", file=sys.stderr)
        for s in stale:
            print(f"  - {s}", file=sys.stderr)
        print("\n  Run without --check to rewrite, then re-read the diff.", file=sys.stderr)
        return 1
    if stale:
        spec.write_text(new, encoding="utf-8")
        print(f"rewrote {len(stale)} header value(s) in {spec.name}")
        for s in stale:
            print(f"  was: {s}")

    if a.plan:
        plan = Path(a.plan).resolve()
        ptext, pstale = render_plan(plan.read_text(encoding="utf-8"), vals)
        if not pstale:
            print(f"{plan.name}: derived rows current — nothing to do.")
        elif a.check:
            print(f"\nSTALE in {plan.name} ({len(pstale)} row(s)):", file=sys.stderr)
            for s in pstale:
                print(f"  - {s}", file=sys.stderr)
            return 1
        else:
            plan.write_text(ptext, encoding="utf-8")
            print(f"rewrote {len(pstale)} derived row(s) in {plan.name}")
            for s in pstale:
                print(f"  was: {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
