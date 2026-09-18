#!/usr/bin/env python3
"""agentii_cmd.py — the implementation core of the `agentii.*` kit commands (S4).

Subcommands, in two kinds:

  Own implementation  — specify / clarify / tasks / constitution. The SKILL.md
                        bodies document the rules; this script is the machinery.

  Delegating          — converge / challenge / implement / status. Each already
                        had a complete `main(argv)` in its own script; this file
                        supplies only the dispatch entry (see DELEGATING below).

`plan` is intentionally NOT registered. It is an authoring step with a SKILL.md
and no script, so a verb here would return success and do nothing — the exact
anti-pattern spec 046 spent 63 decisions hunting. A command that cannot do its
work must not be invocable, or its absence stops being visible.
"""
from __future__ import annotations

import argparse
import importlib
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


# --- spec-matrix parsing (F1 remediation — the SKILL.md-documented path) -------

def parse_spec_matrix(spec_text: str) -> list[dict]:
    """Parse the spec-template's '## 3. Skill Deployment Matrix' markdown table
    (Skill | Vertical | Depth | Tickers | Market Data Stage | Purpose) into
    [{skill, tickers: [...], depth, purpose}].

    The Purpose cell (column 6) is carried through — it is the only place the
    spec states what a deployment is *for*, and discarding it left every task
    with the same placeholder text.
    """
    rows: list[dict] = []
    in_matrix = False
    for line in spec_text.splitlines():
        if "Skill Deployment Matrix" in line and line.lstrip().startswith("#"):
            in_matrix = True
            continue
        if in_matrix and line.startswith("## "):
            break
        if not in_matrix or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5 or cells[0] in ("Skill", "---", ":"):
            continue
        skill = cells[0].strip("`")
        depth = cells[2]
        tickers = [t.strip() for t in cells[3].replace("，", ",").split(",")
                   if t.strip()]
        purpose = cells[5] if len(cells) > 5 and cells[5] else "analysis"
        rows.append({"skill": skill, "tickers": tickers, "depth": depth.lower(),
                     "purpose": purpose})
    return rows


def parse_subs_to_pillars(spec_text: str) -> dict[str, list[str]]:
    """Map skill -> [pillar ids] from each pillar block's `Subscribed:` list.

    Q9 makes the subscription the binding consistency statement between a
    pillar and its deployment, so it is the authoritative source for a task's
    `src:`. Without this every task inherited the literal string "P1", which
    made the src: ref (Q26 traceability) vacuous.
    """
    import re as _re

    mapping: dict[str, list[str]] = {}
    for m in _re.finditer(
            r"###\s+Pillar\s+(\d+)\s+—.*?\*\*Subscribed\*\*:\s*([^\n]+)",
            spec_text, _re.S):
        pid = f"PIL-{m.group(1)}"
        for tok in _re.findall(r"`([^`]+)`", m.group(2)):
            if " × " in tok:
                _ticker, skill = tok.split(" × ", 1)
                skill = skill.strip()
                mapping.setdefault(skill, [])
                if pid not in mapping[skill]:
                    mapping[skill].append(pid)
    return mapping


def depth_to_modes(depth: str, registry: dict, skill: str) -> list[str]:
    """Q79 Depth-Tier merge: Deep/Full → all (expanded from the registry's mode
    slugs); Standard/Light → the skill's essentials_modes (fallback default)."""
    entry = next((s for s in registry.get("skills", [])
                  if s.get("skill_name") == skill), {})
    if depth in ("deep", "full"):
        return [m["slug"] for m in entry.get("modes", [])] or ["default"]
    return list(entry.get("essentials_modes") or ["default"])


def tasks_from_spec(spec_path: Path, registry: dict) -> list[str]:
    """The documented path: decompose the thesis spec's deployment matrix into
    ticker × skill × mode rows (Q30/Q79), routing through expand_tasks."""
    import yaml as _yaml

    if registry is None:
        registry = _yaml.safe_load(
            (ROOT / "skill-registry.yaml").read_text(encoding="utf-8")) or {}
    spec_text = spec_path.read_text(encoding="utf-8")
    skill_pillars = parse_subs_to_pillars(spec_text)
    entries: list[dict] = []
    for row in parse_spec_matrix(spec_text):
        modes = depth_to_modes(row["depth"], registry, row["skill"])
        # src: = the pillar(s) this skill is subscribed to (Q9/Q26). Falls back
        # to "P1" only when the spec declares no subscription for the skill.
        pillars = skill_pillars.get(row["skill"]) or ["P1"]
        pillar_field = "/".join(pillars)
        src_field = pillars[0] if len(pillars) == 1 else f"spec-{row['skill']}"
        for ticker in row["tickers"]:
            entry = {"pillar": pillar_field, "ticker": ticker, "skill": row["skill"],
                     "purpose": row["purpose"], "src": src_field}
            if row["depth"] in ("deep", "full"):
                entry["modes"] = ["all"]
                entry["all_modes"] = modes
            else:
                entry["modes"] = modes
            entries.append(entry)
    return expand_tasks(entries)


# --- clarify (the 8th kit command — D75 #4) -----------------------------------

MAX_CLARIFY_QUESTIONS = 5  # upstream v1.0.4's tightened per-round limit


def clarify_questions(spec_path: Path) -> list[dict]:
    """Phase 1 — a DETERMINISTIC scanner, never vibes. Candidate questions for
    underspecified spec items, each naming the field it unblocks."""
    text = spec_path.read_text(encoding="utf-8")
    questions: list[dict] = []
    # 1. prose wrong_if (Q8 contract 4: must be machine-checkable)
    for m in __import__("re").finditer(r"\*\*wrong_if\*\*:\s*(.+)$", text,
                                       flags=__import__("re").MULTILINE):
        w = m.group(1).strip()
        if not ("metric=" in w and "threshold=" in w and "source=" in w):
            questions.append({
                "id": f"wrongif-{len(questions)}",
                "target": "pillar wrong_if",
                "question": "Convert this prose wrong_if into machine-checkable form "
                            "— metric=<…> threshold=<…> source=<…> [op=<</>/<=/>=/==>] "
                            "(Q8 contract 4 rejects prose).",
                "options": None})
    # 2. universe rows without inclusion rationale
    for m in __import__("re").finditer(
            r"^\|\s*([A-Z0-9]{1,5})\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\|",
            text, flags=__import__("re").MULTILINE):
        questions.append({
            "id": f"rationale-{m.group(1)}",
            "target": f"universe row {m.group(1)}",
            "question": f"Write the inclusion rationale for {m.group(1)} — every "
                        f"ticker's membership must be justified (spec-template §2).",
            "options": None})
    # 3. budget undeclared (Q58)
    if "max_tasks" not in text:
        questions.append({"id": "budget", "target": "thesis budget",
                          "question": "Declare the thesis budget — "
                                      "{max_tasks, max_retries_per_task} (Q58).",
                          "options": ["{max_tasks: 80, max_retries_per_task: 2}",
                                      "{max_tasks: 40, max_retries_per_task: 2}",
                                      "{max_tasks: 160, max_retries_per_task: 3}"]})
    # 4. expiry_triggers undeclared (Q59)
    if "expiry_triggers" not in text:
        questions.append({"id": "expiry", "target": "expiry triggers",
                          "question": "Declare expiry_triggers — which events should "
                                      "auto-flag claims for re-review (Q59).",
                          "options": ["[earnings_release, fda_decision]",
                                      "[earnings_release]",
                                      "[earnings_release, constitution_bump, skill_version_mix]"]})
    # 5. subscriptions not in TICKER × skill form (Q9/Q79)
    # NOTE (2026-09-10): two defects fixed here.
    #   (a) `[^$]+` — inside a character class `$` is a LITERAL dollar, not an
    #       end-of-string anchor — and it matches newlines. With no '$' in the
    #       file the capture ran to EOF, so every spec reported one bogus
    #       "malformed subscription" made of fragments from unrelated lines.
    #   (b) the test was `" × " not in s`, which accepts `skill × mode`. A
    #       ticker-less token contains ' × ' too, so the real Q79 violation was
    #       never caught. The ticker must be anchored on the left.
    for m in __import__("re").finditer(r"Subscribed\*\*:\s*([^\n]+)", text):
        subs = [s.strip() for s in m.group(1).split(",") if s.strip()]
        malformed = [s for s in subs
                     if not __import__("re").match(r"^`?[A-Z0-9.]{1,6} × ", s)]
        if malformed:
            questions.append({
                "id": "subscriptions", "target": "pillar subscriptions",
                "question": "Subscription tokens must be 'TICKER × skill' pairs "
                            f"(got: {', '.join(malformed[:3])}) — they are the "
                            f"consistency statement (Q9) and the task identity (Q79). "
                            f"dispatch.py matches `ticker in subs` for earnings-trigger "
                            f"flips and thesis_status.py regex-extracts tickers from "
                            f"these, so a ticker-less token silently breaks both.",
                "options": None})
    return questions[:MAX_CLARIFY_QUESTIONS]


def clarify_encode(spec_path: Path, answers: list[dict]) -> str:
    """Phase 2 — append answers to the spec's `## Clarifications` section, then
    re-evaluate checklists/thesis-quality.md (Q32 bidirectional maintenance)."""
    import datetime

    today = datetime.date.today().isoformat()
    block = "\n".join(f"- [{today}] Q: {a.get('question', '')} → A: {a.get('answer', '')}"
                      for a in answers)
    text = spec_path.read_text(encoding="utf-8")
    if "## Clarifications" in text:
        text = text.replace("## Clarifications", f"## Clarifications\n\n{block}", 1)
    else:
        text = text.rstrip() + f"\n\n## Clarifications\n\n{block}\n"
    spec_path.write_text(text, encoding="utf-8")

    # Q32: the machine-maintained checklist is bidirectional — report the pass
    # count + regressions after the write.
    try:
        import converge  # same-directory module

        regressions = converge.re_evaluate_checklist(spec_path.parent)
        checklist_note = f"; checklist regressions: {len(regressions)}"
    except (ImportError, OSError):
        checklist_note = "; checklist re-evaluation skipped (no checklist)"
    return f"encoded {len(answers)} answer(s) into {spec_path.name}{checklist_note}"


# --- constitution (Q33/Q83) ---------------------------------------------------

def constitution_scaffold(workspace: Path, *, force: bool = False) -> list[Path]:
    """Scaffold is for EMPTY workspaces only (Q83). A ratified constitution —
    one whose [WORKSPACE_NAME] placeholder has been replaced — must never be
    silently overwritten: the doctrine in it is the single source of truth for
    every thesis. Amend it instead; --force overrides (deliberate reset)."""
    existing = workspace / "constitution.md"
    if existing.is_file() and "[WORKSPACE_NAME]" not in existing.read_text(encoding="utf-8"):
        if not force:
            raise SystemExit(
                "SCAFFOLD REFUSED: constitution.md is already ratified — use "
                "`agentii.constitution amend` (or pass --force to deliberately "
                "reset the workspace's doctrine)")
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


# ── The delegating commands (Phase 11 / Q22 · Q24 · Q26) ─────────────────────
#
# Each of these already had a complete implementation — a `main(argv)` with a
# `__main__` guard in its own script, plus a SKILL.md. What was missing was the
# dispatch entry. Measured 2026-09-18: four of the five unregistered commands were
# WIRING-ONLY, not unbuilt; this table is the whole of the work.
#
# `plan` is deliberately ABSENT. It is an authoring step with a SKILL.md and no
# script, so registering it here would create a verb that returns success and does
# nothing — the exact anti-pattern this spec spent 63 decisions hunting. A command
# that cannot do its work must not be invocable, or the absence stops being visible.
DELEGATING = {
    "converge": ("converge.py", "append `## Phase N: Convergence` to tasks.md (Q26)"),
    "challenge": ("challenge.py", "findings with content-derived stable IDs (Q9/Q40)"),
    "implement": ("dispatch.py", "dispatch tasks through the G1 preflight (Q22)"),
    "status": ("thesis_status.py", "workspace status board (Q24)"),
}


def _delegate(script: str, argv: list[str]) -> int:
    """Run a backing script's main(argv) in-process and return its exit code.

    In-process rather than subprocess, so the tool's own stdout and status are the
    command's — a wrapper that swallowed either would be a worse answer than no
    wrapper. `here` is re-inserted into sys.path because this module is also
    importable, in which case __file__'s directory is not sys.path[0]."""
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    return importlib.import_module(script[:-3]).main(argv)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="agentii.* command core (S4)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("specify")
    sp.add_argument("--workspace", required=True)
    sp.add_argument("--slug", required=True)

    cl = sub.add_parser("clarify")
    cl.add_argument("--thesis", required=True)
    cl.add_argument("--questions", action="store_true",
                    help="phase 1: emit candidate clarification questions (JSON)")
    cl.add_argument("--answers", default=None,
                    help="phase 2: JSON list of {question, answer} to encode")

    tp = sub.add_parser("tasks")
    tp.add_argument("--matrix", default=None,
                    help="JSON list of {pillar, ticker, skill, mode(s), purpose} "
                         "(scripting/tests; alternatively pass --thesis + --spec)")
    tp.add_argument("--thesis", default=None)
    tp.add_argument("--spec", default=None,
                    help="thesis spec.md — decomposes its Skill Deployment Matrix")

    cp = sub.add_parser("constitution")
    cp.add_argument("action", choices=["scaffold", "amend"])
    cp.add_argument("--workspace", required=True)
    cp.add_argument("--force", action="store_true",
                    help="deliberately reset a ratified constitution (Q83 guard override)")
    cp.add_argument("--bump", default=None)
    cp.add_argument("--note", default="")

    # Delegating commands carry no arguments of their own: everything after the verb
    # is forwarded verbatim (see the parse_known_args call below). add_help=False so
    # the TOOL's --help wins rather than this wrapper's — a wrapper advertising its
    # own shallow help over a richer tool is a small lie.
    #
    # nargs=REMAINDER was the first attempt and it does NOT work: it fails to capture
    # a leading optional, so `agentii.converge --help` died on the parent parser's
    # "unrecognized arguments". Registration is not function; only running it showed.
    for _name, (_script, _help) in DELEGATING.items():
        sub.add_parser(_name, help=_help, add_help=False)

    args, extra = p.parse_known_args(argv)

    if args.cmd in DELEGATING:
        return _delegate(DELEGATING[args.cmd][0], extra)
    if extra:
        # Strict everywhere else: silently accepting a mistyped flag on the
        # non-delegating commands is the failure this codebase keeps finding.
        p.error("unrecognized arguments: " + " ".join(extra))
    if args.cmd == "specify":
        print(specify(Path(args.workspace), args.slug))
    elif args.cmd == "clarify":
        thesis = Path(args.thesis)
        spec_path = thesis / "spec.md"
        if args.answers is not None:
            print(clarify_encode(spec_path, json.loads(args.answers)))
        elif args.questions:
            print(json.dumps(clarify_questions(spec_path), indent=2))
        else:
            raise SystemExit("clarify: pass --questions or --answers")
    elif args.cmd == "tasks":
        if args.matrix:
            rows = expand_tasks(json.loads(args.matrix))
        elif args.thesis and args.spec:
            rows = tasks_from_spec(Path(args.spec), None)
        else:
            raise SystemExit("tasks: provide --matrix OR both --thesis and --spec")
        for row in rows:
            print(row)
    elif args.cmd == "constitution":
        if args.action == "scaffold":
            for f in constitution_scaffold(Path(args.workspace), force=args.force):
                print("scaffolded", f)
        else:
            constitution_amend(Path(args.workspace), args.bump, args.note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
