#!/usr/bin/env python3
"""agentii_cmd.py — the implementation core of the `agentii.*` kit commands (S4).

Subcommands: specify / tasks / constitution / plan. The SKILL.md bodies document
the rules; this script is the deterministic machinery. `challenge` arrives with
S5; `converge` lives in converge.py; `implement` wraps dispatch.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import alloc_thesis_id  # noqa: E402
import g1_gate  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"

L1_FILES = {
    "constitution.md": "constitution-template.md",
    "constitution.yaml": "constitution-template.yaml",
    "assumptions.yaml": "assumptions-template.yaml",
    "value-checks.yaml": "value-checks-template.yaml",
    "taxonomy.yaml": "taxonomy-workspace-template.yaml",
}
VALID_BUMPS = {"major", "minor", "patch"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --- specify (Q23/Q27/Q30/Q32/Q83) -------------------------------------------

def constitution_ratified(workspace: Path) -> bool:
    """Q83: a constitution whose placeholders remain unreplaced is unratified —
    thesis creation is forbidden until the human fills the real values."""
    constitution = workspace / "constitution.md"
    if not constitution.is_file():
        return False
    text = constitution.read_text(encoding="utf-8")
    return "[WORKSPACE_NAME]" not in text


def specify(workspace: Path, slug: str) -> Path:
    if not constitution_ratified(workspace):
        raise SystemExit("SPECIFY REFUSED: constitution unratified (Q83 A+) — "
                         "run `agentii.constitution` and ratify L1 first")
    thesis = alloc_thesis_id.allocate(workspace / "theses", slug)
    _write(thesis / "spec.md", "# Research Thesis: " + slug + "\n\n"
           + "## 1. Research Question\n[TBD]\n\n## 1b. Pillars\n"
           + "### Pillar 1 — (Priority: P1) 🎯 Minimum Defensible View\n"
           + "**wrong_if**: `metric=<…> threshold=<…> source=<…>`\n\n"
           + "## 2. Universe Definition\n| Ticker | Company | Sector | Weight | Rationale |\n"
           + "|---|---|---|:---:|---|\n\n"
           + "## 3. Skill Deployment Matrix\n| Skill | Vertical | Depth | Tickers | Market Data Stage | Purpose |\n"
           + "|---|---|:---:|---|---|---|\n")
    _write(thesis / "thesis.md", "# Thesis: " + slug + "\n\n"
           + "```yaml\nclaim: [TBD]\npillars: []\nknown-open: []\n"
           + "budget: {max_tasks: 40, max_retries_per_task: 2}\n```\n")
    checklist = (TEMPLATES / "checklist-template.md")
    _write(thesis / "checklists" / "thesis-quality.md",
           checklist.read_text(encoding="utf-8") if checklist.is_file()
           else "# Thesis Quality Checklist\n")
    return thesis


# --- tasks (Q30/Q79) ----------------------------------------------------------

def expand_tasks(matrix: list[dict]) -> list[str]:
    """`mode: all` expands to N tasks at generation (Q79); each row = one task.
    `[P]` = different files AND no incomplete deps — same (ticker, skill) pairs
    are serialized across modes; distinct files are parallel."""
    rows: list[str] = []
    seen_files: set[str] = set()
    idx = 1
    for entry in matrix:
        modes = entry.get("modes") or [entry.get("mode") or "default"]
        if "all" in modes:
            modes = entry.get("all_modes") or ["default"]  # caller supplies expansion
        for mode in modes:
            file_key = f"{entry['ticker']}/{entry['skill']}"
            parallel = file_key not in seen_files
            seen_files.add(file_key)
            src = entry.get("src") or entry.get("pillar") or "spec"
            p_mark = "[P] " if parallel else ""
            rows.append(f"- [ ] T{idx:03d} {p_mark}[{entry.get('pillar', 'P1')}] "
                        f"{entry['ticker']} × {entry['skill']} × {mode} — "
                        f"{entry.get('purpose', 'analysis')} (src: {src})")
            idx += 1
    return rows


# --- constitution (Q33/Q83) ---------------------------------------------------

def constitution_scaffold(workspace: Path) -> list[Path]:
    written = []
    for out_name, template_name in L1_FILES.items():
        template = TEMPLATES / template_name
        if not template.is_file():
            continue
        _write(workspace / out_name, template.read_text(encoding="utf-8"))
        written.append(workspace / out_name)
    # Q77/Q82: the two rebuildable cache layers never enter git; evidence does.
    _write(workspace / ".gitignore",
           "# spec 046 Q77/Q82 — rebuildable caches, per-machine\n"
           "market-data/\nraw-data/\n"
           "# evidence quote snapshots inside each thesis ARE committed\n")
    written.append(workspace / ".gitignore")
    return written


def constitution_amend(workspace: Path, bump: str, note: str) -> None:
    if bump not in VALID_BUMPS:
        raise SystemExit(f"AMEND REFUSED: bump must be one of {sorted(VALID_BUMPS)} "
                         f"(Q33 — MAJOR/MINOR/PATCH definitions are written in)")
    constitution = workspace / "constitution.md"
    if not constitution.is_file():
        raise SystemExit("AMEND REFUSED: constitution.md not found — scaffold first")
    text = constitution.read_text(encoding="utf-8")
    entry = (f"<!--\nSync Impact Report entry\n  bump: {bump}\n  note: {note}\n"
             f"  old → new: [record changed principles here]\n  deferred: [none]\n-->\n")
    constitution.write_text(text + "\n" + entry, encoding="utf-8")
    print(f"AMENDED ({bump}) — MINOR/MAJOR marks constitution_pin-older theses "
          f"`stale` and dispatches re-examination after the gate-5 budget confirm.")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="agentii.* command core (S4)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("specify")
    sp.add_argument("--workspace", required=True)
    sp.add_argument("--slug", required=True)

    tp = sub.add_parser("tasks")
    tp.add_argument("--matrix", required=True, help="JSON list of {pillar, ticker, skill, mode(s), purpose}")

    cp = sub.add_parser("constitution")
    cp.add_argument("action", choices=["scaffold", "amend"])
    cp.add_argument("--workspace", required=True)
    cp.add_argument("--bump", default=None)
    cp.add_argument("--note", default="")

    args = p.parse_args(argv)

    if args.cmd == "specify":
        print(specify(Path(args.workspace), args.slug))
    elif args.cmd == "tasks":
        for row in expand_tasks(json.loads(args.matrix)):
            print(row)
    elif args.cmd == "constitution":
        if args.action == "scaffold":
            for f in constitution_scaffold(Path(args.workspace)):
                print("scaffolded", f)
        else:
            constitution_amend(Path(args.workspace), args.bump, args.note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
