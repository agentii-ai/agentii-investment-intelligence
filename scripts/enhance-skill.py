#!/usr/bin/env python3
"""enhance-skill.py — workflow-driven skill enrichment CLI (spec 039 Part I, US1/US2).

Loads a YAML workflow preset, validates ``applies_to`` against the skill registry,
and enriches the target skill's ``references/knowledge-frameworks.md`` idempotently
(dedupe by citation_id) and its ``## Methodology`` (analogue-retrieval step). Supports
chaining multiple presets (US2) with working-copy threading when ``uses_history: true``.

Design for testability (R10): enrichment stages accept injected citation records so
CI runs deterministically without LLM/MCP calls. When run for real, the records are
sourced from spec 037 MCP tools (wired in US4); absent those, the stage is a no-op that
still creates the template and reports coverage_gap.

Path note: lives in scripts/ alongside check.py; data scripts are under data-tools/.
"""
from __future__ import annotations

import argparse
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = REPO_ROOT / "contracts"
WORKFLOWS = REPO_ROOT / "workflows"
WORKFLOW_SCHEMA = CONTRACTS / "workflow.schema.json"
KF_TEMPLATE = CONTRACTS / "knowledge-frameworks-template.md"

# Table headers keyed by logical table name (matches the template).
_TABLE_HEADERS = {
    "strategies": "## Referenced Strategies",
    "cases": "## Referenced Cases",
    "setups": "## Referenced Setups",
}


class PresetError(Exception):
    """Raised on invalid workflow preset (parse or schema), with line info where possible."""


# --------------------------------------------------------------------------- presets
def load_preset(path: Path) -> dict[str, Any]:
    """Parse + schema-validate a workflow preset. Invalid YAML raises PresetError
    with a line number; schema violations raise PresetError with the failing field."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        preset = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        line = (mark.line + 1) if mark else "?"
        raise PresetError(f"{path}: invalid YAML at line {line}: {getattr(e, 'problem', e)}") from e
    if not isinstance(preset, dict):
        raise PresetError(f"{path}: preset must be a mapping")
    if WORKFLOW_SCHEMA.exists():
        try:
            import jsonschema

            jsonschema.validate(preset, json.loads(WORKFLOW_SCHEMA.read_text()))
        except ImportError:
            pass
        except Exception as e:  # noqa: BLE001
            raise PresetError(f"{path}: schema validation failed: {e}") from e
    return preset


def resolve_preset(name: str, extra_dir: Optional[Path] = None) -> Path:
    """Resolve a preset by name. A user preset dir (extra_dir) overrides bundled."""
    for base in [d for d in (extra_dir, WORKFLOWS) if d]:
        cand = Path(base) / f"{name}.yaml"
        if cand.is_file():
            return cand
    raise PresetError(f"workflow preset '{name}' not found in {extra_dir or ''} or {WORKFLOWS}")


def matches_applies_to(preset: dict, skill_entry: dict) -> tuple[bool, str]:
    """Return (ok, reason). Refuse when the skill does not satisfy applies_to (FR-006)."""
    rules = preset.get("applies_to") or {}
    want_v = rules.get("vertical")
    if want_v and skill_entry.get("vertical") != want_v:
        return False, f"vertical mismatch: preset wants '{want_v}', skill is '{skill_entry.get('vertical')}'"
    want_layers = rules.get("layer_tags")
    if want_layers:
        have = set(skill_entry.get("layer_tags") or [])
        if not have.intersection(want_layers):
            return False, f"layer mismatch: preset wants {want_layers}, skill has {sorted(have)}"
    min_score = rules.get("min_quality_score")
    if min_score is not None:
        score = skill_entry.get("quality_score")
        score = 0.0 if score is None else float(score)
        if score < float(min_score):
            return False, f"quality below min: {score} < {min_score}"
    return True, "ok"


# --------------------------------------------------------------- knowledge-frameworks
def _template_text(skill_name: str) -> str:
    if KF_TEMPLATE.exists():
        return KF_TEMPLATE.read_text(encoding="utf-8").replace("{skill_name}", skill_name)
    # Minimal fallback if template contract is absent.
    return (
        f"# Knowledge Frameworks — {skill_name}\n\n"
        "## Referenced Strategies\n\n| strategy_id | title | kind | one-line |\n|---|---|---|---|\n\n"
        "## Referenced Cases\n\n| case_id | title | time_horizon | domain | one-line |\n|---|---|---|---|---|\n\n"
        "## Referenced Setups\n\n| setup_id | title | pattern_type | timeframe |\n|---|---|---|---|\n"
    )


def count_citations(kf_path: Path) -> int:
    """Count unique citation ids already present (first column of any table row)."""
    if not Path(kf_path).is_file():
        return 0
    return len(_existing_ids(Path(kf_path).read_text(encoding="utf-8")))


def _existing_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        # skip header + separator rows
        if not first or set(first) <= set("-: ") or first in {"strategy_id", "case_id", "setup_id"}:
            continue
        ids.add(first)
    return ids


def insert_citations(kf_path: Path, table: str, rows: list[dict], skill_name: str) -> int:
    """Idempotently insert citation rows into the named table. Creates the file from
    template if missing. Returns the count of NEW rows inserted (dedupe by citation_id).
    """
    kf_path = Path(kf_path)
    if table not in _TABLE_HEADERS:
        raise ValueError(f"unknown table '{table}' (expected one of {sorted(_TABLE_HEADERS)})")
    if not kf_path.exists():
        kf_path.parent.mkdir(parents=True, exist_ok=True)
        kf_path.write_text(_template_text(skill_name), encoding="utf-8")

    text = kf_path.read_text(encoding="utf-8")
    existing = _existing_ids(text)
    new_rows = [r for r in rows if r.get("citation_id") not in existing]
    if not new_rows:
        return 0

    lines = text.splitlines()
    header = _TABLE_HEADERS[table]
    try:
        h_idx = next(i for i, l in enumerate(lines) if l.strip() == header)
    except StopIteration:
        # table header absent — append the section
        lines += ["", header, "", "| id | ... |", "|---|---|"]
        h_idx = len(lines) - 3
    # find the last table row after the header (skip blank + separator)
    insert_at = h_idx + 1
    i = h_idx + 1
    while i < len(lines) and (lines[i].strip().startswith("|") or lines[i].strip() == ""):
        if lines[i].strip().startswith("|"):
            insert_at = i + 1
        i += 1
    rendered = ["| " + " | ".join(str(c) for c in r["columns"]) + " |" for r in new_rows]
    lines[insert_at:insert_at] = rendered
    kf_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(new_rows)


# --------------------------------------------------------------------------- runner
def _skill_dir(skills_root: Path, skill_entry: dict, skill_name: str) -> Optional[Path]:
    vert = skill_entry.get("vertical", "*")
    cand = skills_root / "vertical-plugins" / vert / "skills" / "agentii" / skill_name
    if cand.exists():
        return cand
    hits = list(skills_root.glob(f"vertical-plugins/*/skills/agentii/{skill_name}"))
    return hits[0] if hits else None


def _score_skill_dir(skill_dir: Path) -> Optional[float]:
    """Reuse quality-scan.py's scorer for the rollback guard. Returns None if unavailable."""
    try:
        import importlib.util

        qpath = REPO_ROOT / "scripts" / "quality-scan.py"
        spec = importlib.util.spec_from_file_location("quality_scan", qpath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.score_skill(skill_dir)["score"]
    except Exception:  # noqa: BLE001
        return None


CONTRACT_CHECKS_NOTE = "Checks 13/19/20/21/22"


def run_contract_guard(skills_root: Path) -> tuple[bool, str]:
    """Run check.py after edits; halt on violation (FR-025). Best-effort: if check.py
    is absent (e.g., test sandbox), treat as pass."""
    check = REPO_ROOT / "scripts" / "check.py"
    if not check.exists():
        return True, "check.py absent — skipped"
    res = subprocess.run([sys.executable, str(check)], capture_output=True, text=True, cwd=str(REPO_ROOT))
    return res.returncode == 0, (res.stdout + res.stderr)


def enrich(
    skill_name: str,
    workflow_names: list[str],
    *,
    registry_path: Path,
    skills_root: Path,
    dry_run: bool = False,
    user_workflow_dir: Optional[Path] = None,
    injected_records: Optional[dict] = None,
    spec037_client: Optional[Any] = None,
) -> dict[str, Any]:
    """Execute one or more workflow presets against a skill.

    injected_records: optional {workflow_name: {table: [rows]}} for deterministic tests.
    spec037_client: optional duck-typed spec-037 MCP client; when supplied and no
      injected_records, reference_injection stages source rows via knowledge_bridge.
    Without either, reference_injection stages are no-ops (report citations_inserted: 0).
    """
    entry = _registry.get_skill(skill_name, path=registry_path)
    if entry is None:
        return {"skill": skill_name, "workflows": workflow_names, "dry_run": dry_run,
                "status": "error", "error": f"skill '{skill_name}' not in registry"}

    skill_dir = _skill_dir(skills_root, entry, skill_name)
    if skill_dir is None:
        return {"skill": skill_name, "workflows": workflow_names, "dry_run": dry_run,
                "status": "error", "error": f"on-disk skill dir for '{skill_name}' not found"}

    kf_path = skill_dir / "references" / "knowledge-frameworks.md"
    before = kf_path.read_text(encoding="utf-8") if kf_path.exists() else ""

    # Work on a temp copy so --dry-run writes nothing and chaining threads history.
    work = Path(tempfile.mkdtemp(prefix="enhance-")) / "knowledge-frameworks.md"
    if before:
        work.write_text(before, encoding="utf-8")

    total_inserted = 0
    applied: list[str] = []
    coverage_gaps: list[str] = []
    methodology_patched = False
    for wf_name in workflow_names:
        preset = load_preset(resolve_preset(wf_name, user_workflow_dir))
        ok, reason = matches_applies_to(preset, entry)
        if not ok:
            shutil.rmtree(work.parent, ignore_errors=True)
            return {"skill": skill_name, "workflows": workflow_names, "dry_run": dry_run,
                    "status": "refused", "error": f"{wf_name}: {reason}"}

        # Source records: injected (tests) > spec-037 bridge (real) > none.
        recs = (injected_records or {}).get(wf_name)
        if recs is None and spec037_client is not None:
            import knowledge_bridge  # local import keeps module optional

            fetched = knowledge_bridge.fetch_enrichment(spec037_client, wf_name, entry)
            recs = fetched.get("records", {})
            if fetched.get("status") == "coverage_gap":
                coverage_gaps.append(fetched.get("coverage_gap", wf_name))
        recs = recs or {}

        for stage in preset.get("stages", []):
            if stage["type"] == "reference_injection":
                for table, rows in recs.items():
                    total_inserted += insert_citations(work, table=table, rows=rows, skill_name=skill_name)
            elif stage["type"] == "methodology_patch" and not methodology_patched:
                # Injected into the on-disk SKILL.md ## Methodology at write time (below).
                methodology_patched = True
            # quality_audit handled by quality-scan.py post-write.
        applied.append(wf_name)

    after = work.read_text(encoding="utf-8") if work.exists() else ""
    diff = "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=f"a/{kf_path.name}", tofile=f"b/{kf_path.name}",
    ))

    result = {
        "skill": skill_name,
        "workflows": workflow_names,
        "dry_run": dry_run,
        "status": "ok",
        "citations_inserted": total_inserted,
        "diff": diff,
    }
    if coverage_gaps:
        result["coverage_gap"] = coverage_gaps

    # US4 rollback guard (R2): if any preset had a quality_audit stage, score before/after
    # and refuse to persist a regression.
    has_audit = any(
        s.get("type") == "quality_audit"
        for wf in applied
        for s in load_preset(resolve_preset(wf, user_workflow_dir)).get("stages", [])
    )
    if not dry_run and after != before and has_audit:
        score_before = _score_skill_dir(skill_dir)
        # tentatively write, score, restore on regression
        kf_path.parent.mkdir(parents=True, exist_ok=True)
        kf_path.write_text(after, encoding="utf-8")
        score_after = _score_skill_dir(skill_dir)
        if score_before is not None and score_after is not None and score_after < score_before:
            kf_path.write_text(before, encoding="utf-8")  # rollback
            shutil.rmtree(work.parent, ignore_errors=True)
            return {**result, "status": "rolled_back",
                    "error": f"score regressed {score_before}→{score_after}; reverted",
                    "score_before": score_before, "score_after": score_after}

    if not dry_run and after != before:
        kf_path.parent.mkdir(parents=True, exist_ok=True)
        kf_path.write_text(after, encoding="utf-8")
        # methodology_patch: inject runtime analogue block into SKILL.md if requested + absent
        if methodology_patched:
            import knowledge_bridge

            sk_md = skill_dir / "SKILL.md"
            if sk_md.is_file():
                md = sk_md.read_text(encoding="utf-8")
                if "### Runtime Analogue Discovery" not in md and "## Methodology" in md:
                    block = knowledge_bridge.methodology_analogue_block()
                    md = md.replace("## Methodology", "## Methodology" + block, 1)
                    sk_md.write_text(md, encoding="utf-8")
        # record enrichment history + refs count in registry
        entry["has_knowledge_frameworks"] = True
        entry["spec_037_references"] = count_citations(kf_path)
        entry["last_enriched"] = datetime.now(timezone.utc).isoformat()
        hist = entry.setdefault("enrichment_workflows_applied", [])
        stamp = datetime.now(timezone.utc).isoformat()
        for wf in applied:
            hist.append({"name": wf, "timestamp": stamp})
        _registry.upsert_skill(entry, path=registry_path)
        # contract-preservation guard (FR-025)
        guard_ok, guard_out = run_contract_guard(skills_root)
        result["contract_guard"] = "pass" if guard_ok else "fail"
        if not guard_ok:
            result["status"] = "contract_violation"
            result["error"] = guard_out[-800:]

    shutil.rmtree(work.parent, ignore_errors=True)
    return result


# --------------------------------------------------------------------------- CLI
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Workflow-driven skill enrichment (spec 039 Part I)")
    sub = p.add_subparsers(dest="cmd")

    wf = sub.add_parser("workflow", help="manage presets")
    wf.add_argument("action", choices=["list", "show", "validate"])
    wf.add_argument("name", nargs="?")
    wf.add_argument("--user-workflow-dir", type=Path, help="user preset dir (overrides bundled same-name)")
    wf.add_argument("--json", action="store_true")

    p.add_argument("--skill")
    p.add_argument("--workflow", action="append", default=[], help="preset name (repeatable → chain)")
    p.add_argument("--from-registry", action="store_true")
    p.add_argument("--vertical")
    p.add_argument("--layer")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--auto-approve", action="store_true")
    p.add_argument("--output-diff", type=Path)
    p.add_argument("--json", action="store_true")
    p.add_argument("--registry", type=Path, default=_registry.DEFAULT_REGISTRY_PATH)
    p.add_argument("--skills-root", type=Path, default=REPO_ROOT / "plugins")
    p.add_argument("--user-workflow-dir", type=Path)
    return p


def _cmd_workflow(args) -> int:
    if args.action == "list":
        names = sorted(f.stem for f in WORKFLOWS.glob("*.yaml"))
        print("\n".join(names) if not args.json else json.dumps(names))
        return 0
    if not args.name:
        print("workflow show|validate requires a name", file=sys.stderr)
        return 2
    try:
        preset = load_preset(resolve_preset(args.name, args.user_workflow_dir))
    except PresetError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    if args.action == "validate":
        print(f"OK — {args.name} valid ({len(preset.get('stages', []))} stage(s))")
    else:
        print(json.dumps(preset, indent=2) if args.json else yaml.safe_dump(preset, sort_keys=False))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "workflow":
        return _cmd_workflow(args)

    targets: list[str] = []
    if args.from_registry:
        cands = _registry.get_enrichment_candidates(
            path=args.registry, vertical=args.vertical, layer=args.layer)
        targets = [c["skill_name"] for c in cands]
    elif args.skill:
        targets = [args.skill]
    else:
        print("nothing to do: pass --skill <name> or --from-registry", file=sys.stderr)
        return 2
    if not args.workflow:
        print("pass at least one --workflow <preset>", file=sys.stderr)
        return 2

    results = []
    for skill in targets:
        try:
            r = enrich(skill, args.workflow, registry_path=args.registry,
                       skills_root=args.skills_root, dry_run=args.dry_run,
                       user_workflow_dir=args.user_workflow_dir)
        except PresetError as e:
            r = {"skill": skill, "status": "error", "error": str(e)}
        results.append(r)

    if args.output_diff and results and results[0].get("diff"):
        Path(args.output_diff).write_text(results[0]["diff"], encoding="utf-8")

    payload = results[0] if len(results) == 1 else {"batch": results}
    if args.json:
        print(json.dumps(payload))
    else:
        for r in results:
            print(f"{r['skill']}: {r['status']} ({r.get('citations_inserted', 0)} citations)")
    worst = {r.get("status") for r in results}
    return 0 if worst <= {"ok", "refused"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
