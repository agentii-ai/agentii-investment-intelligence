#!/usr/bin/env python3
"""converge.py — the cadence engine (spec 046 Q26). S2 scope.

Contract:
- Append-only: the ONLY write is a `## Phase N: Convergence` section appended to
  tasks.md. Never rewrite, renumber, reorder or delete — not even previous
  Convergence sections. A clean run leaves tasks.md BYTE-IDENTICAL (no empty
  section header).
- Evaluates artifact CURRENT state — never git history, never `[x]` (Q26 A+: the
  ledger may lie; the correction is deterministic and has a bounded expiry: the
  next converge).
- Deterministic gaps (`stale` pin drift, `invalidated` wrong_if triggers) are
  UNCAPPED — cheap and must be complete. Judgment-class gaps (missing/partial/
  contradicts/unrequested) honor the Q40 cap.
- Finding IDs are content-derived (Q40) — re-runs append nothing for identical
  findings already present in any Convergence section.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1_gate  # noqa: E402 — frontmatter parsing

MAX_JUDGMENT_FINDINGS = 50  # Q40 cap for the judgment class only
FIVE_PINS = g1_gate.FIVE_PINS

_TASK_RE = re.compile(r"^- \[[ xX]\] (T\d{3}) .*?(\b[A-Z0-9]{1,5})\s*×\s*([a-z0-9-]+)\s*×\s*([a-z0-9-]+)", re.MULTILINE)
_CONV_RE = re.compile(r"^## Phase (\d+): Convergence", flags=re.MULTILINE)
_FINDING_ID_RE = re.compile(r"id=([a-f0-9]{12})")
_WRONG_IF_DEFAULT_OP = "<"  # falsifier default: "I'm wrong if metric falls below threshold"


def finding_id(entity: str, metric: str, period: str, gap_type: str) -> str:
    """Content-derived stable ID (Q40): hash(entity+metric+period+gap_type).
    Unchanged state re-runs yield byte-identical IDs."""
    seed = "|".join([entity, metric, period, gap_type])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _artifact_path_for(thesis: Path, ticker: str, skill: str, mode: str) -> Optional[Path]:
    root = thesis / "artifacts" / ticker
    if not root.is_dir():
        return None
    suffix = f"_{skill}_{mode}.md"
    hits = sorted(p for p in root.glob("*.md") if p.name.endswith(suffix))
    return hits[-1] if hits else None  # latest dated artifact for this skill×mode


def _evaluate_stale(artifact: Path, current_pins: dict[str, Any]) -> list[tuple[str, str]]:
    """Deterministic, uncapped: pins absent or older than current → (pin, fid)."""
    fm = g1_gate.parse_frontmatter(artifact.read_text(encoding="utf-8"))
    gaps: list[tuple[str, str]] = []
    for pin, current in current_pins.items():
        value = fm.get(pin)
        if current is None:
            continue  # no current value = nothing to compare against
        if value is None or str(value) != str(current):
            period = str(fm.get("as_of") or "unknown")
            gaps.append((pin, finding_id(artifact.parent.parent.name, pin, period, "stale")))
    return gaps


def _evaluate_wrong_if(thesis: Path) -> list[tuple[str, str, str]]:
    """Deterministic, uncapped: wrong_if entries (metric+threshold+source) evaluated
    against entity_claims values across artifacts. Triggered → invalidated."""
    thesis_md = thesis / "thesis.md"
    if not thesis_md.is_file():
        return []
    try:
        doc = json.loads(thesis_md.read_text(encoding="utf-8"))
        wrong_if = (doc.get("judgment") or {}).get("wrong_if") or []
    except (ValueError, AttributeError):
        return []
    claims: dict[tuple[str, str], tuple[float, str]] = {}
    for art in (thesis / "artifacts").rglob("*.md"):
        fm = g1_gate.parse_frontmatter(art.read_text(encoding="utf-8"))
        for c in fm.get("entity_claims") or []:
            if isinstance(c, dict) and isinstance(c.get("value"), (int, float)):
                claims[(c.get("entity"), c.get("metric"))] = (float(c["value"]), str(c.get("period") or "unknown"))
    out: list[tuple[str, str, str]] = []
    for wf in wrong_if:
        if not isinstance(wf, dict):
            continue
        metric, threshold = wf.get("metric"), wf.get("threshold")
        if metric is None or not isinstance(threshold, (int, float)):
            continue  # Q8 contract 4: prose wrong_if is not mechanically evaluable
        entity = wf.get("entity") or "*"
        if entity == "*":
            hits = [(k, v) for k, v in claims.items() if k[1] == metric]
        else:
            hits = [(k, v) for k, v in claims.items() if k == (entity, metric)]
        for (ent, _m), (value, period) in hits:
            op = wf.get("op", _WRONG_IF_DEFAULT_OP)
            triggered = {"<": value < threshold, ">": value > threshold,
                         "<=": value <= threshold, ">=": value >= threshold,
                         "==": value == threshold}.get(op, value < threshold)
            if triggered:
                out.append((ent, metric, finding_id(ent, metric, period, "invalidated")))
    return out


def _evaluate_missing(thesis: Path, tasks_text: str, existing_ids: set[str]) -> tuple[list[str], int]:
    """Judgment-class, capped (Q40): task rows whose artifact does not exist.
    Returns (appended_rows, finding_count)."""
    rows: list[str] = []
    for m in _TASK_RE.finditer(tasks_text):
        ticker, skill, mode = m.group(2), m.group(3), m.group(4)
        art = _artifact_path_for(thesis, ticker, skill, mode)
        if art is None or not art.is_file():
            fid = finding_id(ticker, skill, mode, "missing")
            if fid in existing_ids:
                continue
            existing_ids.add(fid)
            rows.append(f"- [ ] {m.group(1)} [Convergence] Re-run {ticker} × {skill} × {mode}: "
                        f"artifact missing (src: converge:missing id={fid})")
            if len(rows) >= MAX_JUDGMENT_FINDINGS:
                break
    return rows, len(rows)


def check_skill_version_mix(thesis: Path, current_hashes: dict[str, str]) -> list[str]:
    """Q57: artifacts carrying a skill_pin hash that differs from the current skill
    hash are a methodology mix within one thesis — report, never silently accept."""
    findings: list[str] = []
    artifacts_root = thesis / "artifacts"
    if not artifacts_root.is_dir():
        return findings
    for art in sorted(artifacts_root.rglob("*.md")):
        fm = g1_gate.parse_frontmatter(art.read_text(encoding="utf-8"))
        pin = fm.get("skill_pin")
        if isinstance(pin, dict):
            for skill, recorded in pin.items():
                current = current_hashes.get(skill)
                if current and recorded != current:
                    findings.append(f"skill_version_mix: {art.name} used "
                                    f"{skill}={recorded}; current={current}")
        elif isinstance(pin, str) and ":" in pin:
            skill, recorded = pin.split(":", 1)
            current = current_hashes.get(skill)
            if current and recorded != current:
                findings.append(f"skill_version_mix: {art.name} used "
                                f"{skill}={recorded}; current={current}")
    return findings


def stage3_archive(thesis: Path, *, challenge_clean: set[str]) -> list[dict]:
    """Q64: converge generates the stage-3 archive ONLY for challenge-clean
    superseded/retired post-mortems — bad wins must not pollute the knowledge
    base (Q68 linkage). Case format: thesis background + claim + evidence +
    result + lessons; source=thesis_postmortem + thesis_id/claim_id tags."""
    import json as _json

    try:
        doc = _json.loads((thesis / "thesis.md").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    archives: list[dict] = []
    for claim in (doc.get("judgment") or {}).get("claims") or []:
        if not isinstance(claim, dict):
            continue
        if claim.get("state") not in ("superseded", "retired", "retired_by_ic"):
            continue
        if claim.get("id") not in challenge_clean:
            continue  # Q68: unchallenged claims never enter the knowledge base
        archives.append({
            "source": "thesis_postmortem",
            "thesis_id": thesis.name,
            "claim_id": claim.get("id"),
            "claim": claim.get("claim", ""),
            "outcome": claim.get("state"),
            "lessons": claim.get("lessons", ""),
        })
    return archives


def write_pending_queue(workspace: Path, archives: list[dict]) -> Path:
    """Q64: the pending queue — archives wait here for the human approval card.
    The card is the ONLY path into gold.investment_cases (no auto-write)."""
    import json as _json

    queue = workspace / "_eval" / "postmortem-pending.jsonl"
    queue.parent.mkdir(parents=True, exist_ok=True)
    for record in archives:
        with open(queue, "a", encoding="utf-8") as f:
            f.write(_json.dumps(record) + "\n")
    return queue


def approve_pending(workspace: Path, approver: str) -> list[dict]:
    """Q39 approval card: the human decision. Returns the approved records with
    the approver stamp — the consumer (gold.investment_cases writer) accepts only
    records that passed through here."""
    import json as _json

    queue = workspace / "_eval" / "postmortem-pending.jsonl"
    approved = workspace / "_eval" / "postmortem-approved.jsonl"
    if not queue.is_file():
        return []
    records = []
    for line in queue.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = _json.loads(line)
        rec["approved_by"] = approver
        records.append(rec)
        with open(approved, "a", encoding="utf-8") as f:
            f.write(_json.dumps(rec) + "\n")
    queue.unlink()  # the queue is drained only by an explicit approval action
    return records


def re_evaluate_checklist(thesis: Path) -> list[str]:
    """Q32: the machine-maintained checklist is BIDIRECTIONAL — converge
    re-evaluates the machine-checkable items and reports regressions (items that
    pass now can go back to unchecked — research requirements decay with time)."""
    regressions: list[str] = []
    checklist = thesis / "checklists" / "thesis-quality.md"
    if not checklist.is_file():
        return regressions
    spec_md = thesis / "spec.md"
    spec_text = spec_md.read_text(encoding="utf-8") if spec_md.is_file() else ""
    lines = checklist.read_text(encoding="utf-8").splitlines()
    out_lines: list[str] = []
    for line in lines:
        if not line.startswith("- [x]"):
            out_lines.append(line)
            continue
        # machine-checkable item: wrong_if must carry metric+threshold+source
        if "wrong_if" in line and "metric" in line:
            has_pillars = "### Pillar" in spec_text
            ok = has_pillars and "threshold=" in spec_text and "source=" in spec_text
            if not ok:
                regressions.append(line.strip())
                line = line.replace("- [x]", "- [ ]", 1)  # regression: uncheck
        out_lines.append(line)
    if regressions:
        checklist.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return regressions


def run(thesis: Path, current_pins: dict[str, Any]) -> dict[str, Any]:
    tasks_path = thesis / "tasks.md"
    tasks_text = tasks_path.read_text(encoding="utf-8") if tasks_path.is_file() else ""
    existing_ids = set(_FINDING_ID_RE.findall(tasks_text))

    appended: list[str] = []
    judgment_count = 0

    # Deterministic, uncapped: stale pins + invalidated wrong_if.
    artifacts_root = thesis / "artifacts"
    if artifacts_root.is_dir():
        for art in sorted(artifacts_root.rglob("*.md")):
            for pin, fid in _evaluate_stale(art, current_pins):
                if fid in existing_ids:
                    continue
                existing_ids.add(fid)
                ticker = art.parent.name
                appended.append(f"- [ ] T9xx [Convergence] Re-run {ticker} artifact "
                                f"{art.name}: pin {pin} older than current "
                                f"(src: converge:stale id={fid})")
    for ent, metric, fid in _evaluate_wrong_if(thesis):
        if fid in existing_ids:
            continue
        existing_ids.add(fid)
        appended.append(f"- [ ] T9xx [Convergence] Re-examine claim on {ent}.{metric}: "
                        f"wrong_if triggered (src: converge:invalidated id={fid})")

    # Judgment-class, capped: missing artifacts.
    missing_rows, judgment_count = _evaluate_missing(thesis, tasks_text, existing_ids)
    appended.extend(missing_rows)

    # Q58: a thesis paused on budget is a finding, not silence.
    try:
        doc = json.loads((thesis / "thesis.md").read_text(encoding="utf-8"))
        if (doc.get("judgment") or {}).get("budget_paused"):
            appended.append("- [ ] T9xx [Convergence] Thesis paused on budget — "
                            "Q39 approval card required to resume "
                            "(src: converge:budget_paused)")
    except (OSError, ValueError, AttributeError):
        pass

    if not appended:
        # Q26: a clean run reports `converged` and touches nothing — byte-identical.
        return {"status": "converged", "findings": 0, "judgment_findings": 0}

    # Number the new Convergence section after any existing ones (append-only).
    phase_n = len(_CONV_RE.findall(tasks_text)) + 1
    section = [f"## Phase {phase_n}: Convergence"] + [r.replace("T9xx", f"T{900+phase_n:03d}") for r in appended]
    new_text = (tasks_text.rstrip() + "\n\n" + "\n".join(section) + "\n")
    _atomic_append(tasks_path, new_text)
    return {"status": "gaps_found", "findings": len(appended),
            "judgment_findings": judgment_count}


def _atomic_append(path: Path, content: str) -> None:
    """Append-only write preserving the original bytes; atomic replace so a crash
    mid-write never leaves a truncated tasks.md."""
    import os
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Converge — append-only gap closure (Q26)")
    p.add_argument("--thesis", required=True, help="theses/{nnn}-{slug}/ directory")
    p.add_argument("--pins", required=True, help="JSON dict of current pin values")
    args = p.parse_args(argv)
    current = json.loads(args.pins)
    result = run(Path(args.thesis), current)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
