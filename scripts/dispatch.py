#!/usr/bin/env python3
"""dispatch.py — the thin dispatch loop (spec 046 Q37). S1 scope.

Load-bearing rule: `thesis_dir` is passed EXPLICITLY to every subagent (no singleton
activity pointer — upstream's .specify/feature.json pattern is a data race at
cardinality N). A subagent not told its thesis is a DISPATCH DEFECT, not a lookup
failure. The cwd-upward fallback exists only for human invocation and, when used,
is journaled as `thesis_resolution: cwd_fallback` (never silent).

The full implement command (budget, skill_pin, checklist soft-gate) wraps this loop
later (tasks T053); S1 only proves the dispatch contract.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1_gate  # noqa: E402 — frontmatter parsing for the resume verdict
import journal  # noqa: E402


def resume_verdict(thesis_dir: Path, ticker: str, skill: str, mode: str,
                   current_pins: dict | None = None) -> str:
    """Q56 artifact-driven resume: the filesystem IS the checkpoint (no checkpoint
    file exists). Verdicts: run (absent) / skip (valid FR-090 + fresh pins) /
    resume (corrupted — re-run with --resume) / stale (leave for converge).

    T032: `[x]` in tasks.md is display-only and never read here — the verdict
    derives exclusively from artifact state.
    """
    root = thesis_dir / "artifacts" / ticker
    if not root.is_dir():
        return "run"
    suffix = f"_{skill}_{mode}.md"
    hits = sorted(p for p in root.glob("*.md") if p.name.endswith(suffix))
    if not hits:
        return "run"
    art = hits[-1]
    fm = g1_gate.parse_frontmatter(art.read_text(encoding="utf-8"))
    if not fm or any(not fm.get(pin) for pin in g1_gate.FIVE_PINS):
        return "resume"  # frontmatter missing/corrupted → partial write class
    if current_pins:
        for pin, current in current_pins.items():
            if current is not None and str(fm.get(pin)) != str(current):
                return "stale"  # leave for converge — the pins say so
    return "skip"


def preflight(plan: list[dict], registry: dict) -> list[str]:
    """Q13 compile-time preflight: every node's data-side `requires:` checked
    BEFORE the first node is dispatched — fast-fail naming the offending node
    (the "compiler problem" framing at scenario granularity). Registry entries
    are keyed by skill_name with their own `requires` lists."""
    problems: list[str] = []
    for node in plan:
        skill = node.get("skill")
        if skill not in registry:
            problems.append(f"preflight: node '{skill}' has no registry entry")
            continue
        for req in node.get("requires") or []:
            if req not in registry:
                problems.append(f"preflight: node '{skill}' requires '{req}' — "
                                f"not resolvable in the registry (fast-fail)")
    return problems


def retry_policy(error_code: str) -> tuple[int, bool]:
    """Q14 retry policy by failure class: deterministic failures fast-fail (retry
    cannot change the result); VALIDATOR_FAIL retries N≈2 WITH the failure report
    injected (without it, same input yields same output — pure token burn)."""
    deterministic = {"DATA_STALE", "CALC_UNVALIDATED", "ASSUMPTION_UNPINNED",
                     "LOOKAHEAD_VIOLATION", "VALUE_IMPLAUSIBLE", "DEP_MISSING",
                     "SCHEMA_MISMATCH", "PIN_MISMATCH", "UNFRAMED_REFERENCE",
                     "CONSTITUTION_BREACH", "PRICE_ACCESS_PREMATURE",
                     "INSUFFICIENT_HISTORY"}
    if error_code in deterministic:
        return 0, False
    if error_code == "VALIDATOR_FAIL":
        return 2, True
    return 1, True  # unknown judgment-class: bounded, with report


def reuse_verdict(artifact: Path, freshness_window_days: int,
                  current_pins: dict | None, now: str) -> str:
    """Q60 time-window reuse: validate a declared source_artifact (frontmatter
    validity + as_of within the skill-type freshness window) → reuse (skip) or
    force_rerun."""
    fm = g1_gate.parse_frontmatter(artifact.read_text(encoding="utf-8"))
    if not fm or any(not fm.get(p) for p in g1_gate.FIVE_PINS):
        return "force_rerun"
    if current_pins:
        for pin, current in current_pins.items():
            if current is not None and str(fm.get(pin)) != str(current):
                return "force_rerun"
    as_of = str(fm.get("as_of") or "")
    try:
        import datetime
        as_of_date = datetime.date.fromisoformat(as_of)
        now_date = datetime.date.fromisoformat(now)
        if (now_date - as_of_date).days > freshness_window_days:
            return "force_rerun"
    except ValueError:
        return "force_rerun"
    return "reuse"


class RateLimiter:
    """Q82: max_in_flight per data source. Dispatcher-internal counter ONLY —
    the Q37 rule prohibits subagents contending over shared state, but a single
    dispatcher's private counter is not shared state. Recorded limitation: under
    multiple dispatchers this yields per-machine quotas, not global accuracy."""

    def __init__(self, ceilings: dict[str, int]):
        self.ceilings = ceilings
        self._in_flight: dict[str, int] = {}

    def acquire(self, source: str) -> bool:
        ceiling = self.ceilings.get(source)
        if ceiling is None:
            return True
        if self._in_flight.get(source, 0) >= ceiling:
            return False
        self._in_flight[source] = self._in_flight.get(source, 0) + 1
        return True

    def release(self, source: str) -> None:
        self._in_flight[source] = max(0, self._in_flight.get(source, 0) - 1)


def skill_version_hash(skill_dir: Path) -> str:
    """Q57: version_hash = content hash of the skill directory (SKILL.md +
    references/). Marketplace version labels are human-readable only — the hash
    is the machine truth."""
    import hashlib

    h = hashlib.sha256()
    for p in sorted(skill_dir.rglob("*")):
        if p.is_file() and p.name != "__pycache__" and "__pycache__" not in p.parts:
            h.update(p.name.encode("utf-8"))
            h.update(p.read_bytes())
    return h.hexdigest()[:12]


def enforce_budget(executed_tasks: int, budget: dict | None) -> tuple[bool, str]:
    """Q58: task-count budget — a deterministic economic limit. Exceeding halts
    with an approval-card message (never a silent overrun)."""
    if not budget:
        return False, ""
    max_tasks = budget.get("max_tasks")
    if max_tasks is None:
        return False, ""
    if executed_tasks > int(max_tasks):
        return True, ("BUDGET_HALT: executed tasks exceed budget max_tasks="
                      f"{max_tasks} — Q39 approval card required to continue")
    return False, ""


def record_skill_pin(thesis_dir: Path, skill: str, version_hash: str) -> None:
    """Q57: record skill_pin {name: version_hash} before the first task; a version
    change mid-thesis APPENDS the new hash (never overwrites history)."""
    pins_file = thesis_dir / "skill_pins.jsonl"
    import json

    with open(pins_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"skill": skill, "version_hash": version_hash,
                            "recorded": __import__("datetime").datetime.now().astimezone().isoformat()}) + "\n")


def daily_sweep(theses: list[Path], *, earnings_calendar: dict,
                constitution: Path | None, theses_by_id: dict) -> list[str]:
    """Q59+Q67+Q70: one deterministic poll loop, three jobs. Returns the field-flip
    records — the dispatcher flips FIELDS only; judgment stays with converge.
    (a) expiry triggers vs the earnings/FDA calendar → pending_review;
    (b) constitution drift vs regime declarations → constitution_drift;
    (c) dependency propagation — upstream claim state change → consumer pending_review."""
    import json

    flips: list[str] = []
    states: dict[tuple[str, str], str] = {}
    for t in theses:
        try:
            doc = json.loads((t / "thesis.md").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for claim in (doc.get("judgment") or {}).get("claims") or []:
            if isinstance(claim, dict):
                states[(t.name, claim.get("id"))] = claim.get("state")
    for t in theses:
        try:
            doc = json.loads((t / "thesis.md").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        claims = (doc.get("judgment") or {}).get("claims") or []
        # (c) dependency propagation — upstream claim state changed. The mapping
        # lives in the THESIS-level depends_on: [{thesis_id, claims: [...]}].
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            for dep_entry in doc.get("depends_on") or []:
                if not isinstance(dep_entry, dict):
                    continue
                owner = theses_by_id.get(dep_entry.get("thesis_id"))
                if owner is None:
                    continue
                for dep in dep_entry.get("claims") or []:
                    upstream_state = states.get((owner.name, dep), "pinned")
                    if upstream_state in ("superseded", "retired", "retired_by_ic"):
                        if claim.get("state") != "pending_review":
                            flips.append(f"pending_review: {claim.get('id')} "
                                         f"(upstream {dep} {upstream_state})")
        # (a) expiry triggers vs the calendar
        triggers = doc.get("expiry_triggers") or []
        subs = doc.get("subscriptions") or []
        if "earnings_release" in triggers:
            for day, tickers in (earnings_calendar or {}).items():
                for ticker in tickers:
                    if ticker in subs:
                        for claim in claims:
                            if (isinstance(claim, dict)
                                    and claim.get("entity") == ticker
                                    and claim.get("state") == "pinned"):
                                flips.append(f"pending_review: {claim.get('id')} "
                                             f"(earnings {day})")
    return flips


def check_constitution_drift(constitution: Path, indicators: dict) -> list[str]:
    """Q67: deterministic comparison of leading indicators vs the declared regime.
    Detection is deterministic; correction is human — drift findings go to
    converge + the IC agenda."""
    import re as _re
    import yaml as _yaml

    try:
        doc = _yaml.safe_load(constitution.read_text(encoding="utf-8")) or {}
    except (OSError, _yaml.YAMLError):
        return []
    findings: list[str] = []
    regime = doc.get("regime") or {}
    for trigger in regime.get("drift_triggers") or []:
        cond = trigger.get("condition", "")
        m = _re.match(r"([\w ]+) ([<>]=?) ([\d.]+) for (\d+) consecutive months", cond)
        if not m:
            continue
        # Prefer the trigger's declared `indicator` field; the condition may use a
        # shorthand ("ISM" vs "ISM Manufacturing PMI").
        indicator = trigger.get("indicator") or m.group(1)
        op, val, n = m.group(2), float(m.group(3)), int(m.group(4))
        series = indicators.get(indicator) or []
        if len(series) < n:
            continue
        window = series[-n:]
        breached = {"<": all(v < val for v in window),
                    ">": all(v > val for v in window),
                    "<=": all(v <= val for v in window),
                    ">=": all(v >= val for v in window)}.get(op, False)
        if breached:
            findings.append(f"constitution_drift: {indicator} {op} {val} for {n} "
                            f"consecutive months vs declared regime "
                            f"'{regime.get('declared')}' (Q67)")
    return findings


def resolve_thesis_dir(explicit: str | None, cwd: Path) -> tuple[Path, str | None]:
    """Returns (thesis_dir, fallback_note). Refuses when neither path resolves —
    ambiguity must hard-fail (a silent wrong-ticker write is unrecoverable)."""
    if explicit:
        return Path(explicit), None
    # Human-only fallback: walk upward looking for theses/{nnn}-{slug}/.
    cur = cwd
    while cur != cur.parent:
        candidate = cur / "theses"
        if candidate.is_dir():
            hits = sorted(candidate.glob("[0-9][0-9][0-9]-*"))
            if len(hits) == 1:
                return hits[0], "cwd_fallback"
            if len(hits) > 1:
                raise SystemExit(
                    f"DISPATCH_ERROR: {len(hits)} theses under {candidate} — pass "
                    f"--thesis-dir explicitly (ambiguity must hard-fail, Q37)"
                )
        cur = cur.parent
    raise SystemExit(
        "DISPATCH_ERROR: thesis_dir missing — explicit --thesis-dir required (Q37); "
        "no unique theses/{nnn}-{slug}/ found upward from cwd"
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Thin dispatch loop (S1, Q37)")
    p.add_argument("--thesis-dir", default=None,
                   help="explicit thesis directory (REQUIRED on the dispatch path)")
    p.add_argument("--task", required=True,
                   help="task triple 'TICKER SKILL MODE', e.g. 'NVDA recent-quarter default'")
    p.add_argument("--journal", default=None,
                   help="journal shard path for the dispatch record")
    args = p.parse_args(argv)

    thesis_dir, fallback = resolve_thesis_dir(args.thesis_dir, Path.cwd())
    parts = args.task.split()
    if len(parts) != 3:
        raise SystemExit("DISPATCH_ERROR: --task must be 'TICKER SKILL MODE'")
    ticker, skill, mode = parts

    # D75 #5 (T-001 first-run feedback): journal EVERY dispatch — the S1 scope
    # journaled only the cwd-fallback path, leaving the mandatory explicit-path
    # dispatches silent and the reducer with an empty journal. thesis_resolution
    # records the path taken: explicit | cwd_fallback.
    if not args.journal:
        raise SystemExit(
            "DISPATCH_ERROR: --journal required — every dispatch must be journaled "
            "(Q37; the reducer reads these records)"
        )
    journal.append_entry(Path(args.journal),
                         journal.make_entry(skill, ticker, mode,
                                            thesis_dir.name, [],
                                            thesis_resolution=(
                                                fallback or "explicit")))
    print(f"DISPATCH {ticker} × {skill} × {mode} → thesis_dir={thesis_dir} "
          f"(journaled: {fallback or 'explicit'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
