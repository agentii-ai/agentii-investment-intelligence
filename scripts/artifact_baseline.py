#!/usr/bin/env python3
"""artifact_baseline.py — the corpus measurement FR-043 requires (spec 058 T039/T041/T042).

FR-043, in its own words: *"058 MUST measure the existing artifact corpus once, against the
criteria derived per FR-002, and publish a per-skill and per-thesis baseline: declared
elements present and missing, citation coverage, mode compliance, frontmatter completeness,
and length distribution. The measurement MUST be **read-only** — it MUST NOT modify any
workspace artifact. Every element that fails across the entire corpus MUST [be reported]."*

IT IMPORTS THE GATE'S CRITERIA rather than re-deriving them: `check_output_quality.criteria_for`
and `check_output_quality.check_text` are the single implementation of "which elements does
this skill declare, and are they present". A baseline that measured them independently would
drift from the gate that enforces them — the two-implementations-of-one-check defect this
kit keeps removing, and the reason T039's corrected text says "import, do not re-derive".

THE THREE FAILURES THAT LOOK ALIKE, which is what the publication exists to separate
(`SC-013`): a skill that **declared a contract its output does not meet** (declared-and-unmet),
a skill that **declared nothing** and cannot be held to it (declares-nothing), and a skill
that **produced no output at all** in this corpus (produced-nothing). Today all three read as
"the corpus has nothing".

READ-ONLY, and asserted rather than promised: the script opens files for reading and writes
nothing under `--workspaces`. `T040` verifies every artifact's hash and mtime are unchanged
after a run, and `tests/test_artifact_baseline.py` asserts it too.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_output_quality as gate  # noqa: E402 — the single criteria implementation (D1)
import check_artifact_citations as citations  # noqa: E402 — the same frontmatter walker, one copy

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "contracts" / "artifact-baseline.md"

_FILENAME = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})(?:_(?P<hhmm>\d{4}))?_(?P<rest>.+)$")
_VIEW = re.compile(r"https://agentii\.ai/v/[^\s)\"'\\>]+")
_LINK_DEST = re.compile(r"\]\(\s*(https://agentii\.ai/v/[^\s)]+)\s*\)")
_MODE_HEADING = re.compile(r"(?m)^### Mode: (.+)$")
# The FR-090 output-schema fields the contract declares and the corpus was measured to lack.
FR090 = ("affix", "conclusions", "date", "facts_count", "citation_count", "key_metrics")


def declared_modes(skill_dir: Path) -> list[str]:
    """The mode slugs the skill declares, from its own `references/modes.md`."""
    f = skill_dir / "references" / "modes.md"
    return _MODE_HEADING.findall(f.read_text(encoding="utf-8", errors="ignore")) if f.is_file() else []


def skill_name(artifact: Path) -> str | None:
    m = _FILENAME.match(artifact.stem)
    return m.group("rest").split("_")[0] if m else None


def measure(artifact: Path, skills_root: Path, criteria_cache: dict) -> dict:
    text = artifact.read_text(encoding="utf-8", errors="ignore")
    skill_dir = gate.skill_for(artifact, skills_root)
    key = str(skill_dir) if skill_dir else None
    if key and key not in criteria_cache:
        criteria_cache[key] = gate.criteria_for(skill_dir)
    crit = criteria_cache.get(key) if key else None

    _p, counts = gate.check_text(text, criteria=crit)
    fm = gate._frontmatter(text)
    body = gate._body(text)
    modes = declared_modes(skill_dir) if skill_dir else []
    mode = str(fm.get("mode") or "")
    m = _FILENAME.match(artifact.stem)

    return {
        "path": str(artifact),
        "thesis": artifact.parts[artifact.parts.index("theses") + 1] if "theses" in artifact.parts else "",
        "skill": skill_dir.name if skill_dir else None,
        "matched": skill_dir is not None,
        "words": counts.get("words", 0),
        "elements_declared": counts.get("elements_declared", 0),
        "elements_missing": counts.get("elements_missing", 0),
        "citation_urls": counts.get("citation_urls", 0),
        "citations_needed": counts.get("citations_needed", 0),
        "inline_links": len(_LINK_DEST.findall(body)),
        "frontmatter_urls": len(_VIEW.findall("\n".join(citations._strings(fm)))),
        "mode": mode,
        "modes_declared": modes,
        "mode_declared": bool(modes) and mode in modes,
        "pins_present": sum(1 for p in gate.FIVE_PINS if p in fm),
        "pins_placeholder": [p for p in gate.FIVE_PINS
                             if p in fm and str(fm.get(p) or "").strip().lower()
                             in gate.PLACEHOLDER_VALUES],
        "fr090_present": [f for f in FR090 if fm.get(f) is not None],
        "has_date_component": bool(m),
        "has_hhmm_component": bool(m and m.group("hhmm")),
    }


def scan(workspaces: list[Path], skills_root: Path = gate.ALL_SKILLS_ROOT) -> list[dict]:
    rows: list[dict] = []
    cache: dict = {}
    for ws in workspaces:
        for art in sorted(ws.rglob("*.md")):
            if "artifacts" not in art.parts and art.parent.name != "_cross":
                continue
            rows.append(measure(art, skills_root, cache))
    return rows


def rollup(rows: list[dict], skills_root: Path = gate.ALL_SKILLS_ROOT) -> dict:
    """Per-skill and per-thesis aggregates, plus the corpus-wide element failures."""
    per_skill: dict[str, dict] = defaultdict(
        lambda: {"artifacts": 0, "elements_declared": 0, "elements_missing": 0,
                 "mode_declared": 0, "mode_other": Counter(), "produced": True})
    element_failures: Counter = Counter()
    for r in rows:
        s = r["skill"] or "(no skill resolved)"
        a = per_skill[s]
        a["artifacts"] += 1
        a["elements_declared"] += r["elements_declared"]
        a["elements_missing"] += r["elements_missing"]
        a["mode_declared"] += int(r["mode_declared"])
        if r["mode"] and not r["mode_declared"]:
            a["mode_other"][r["mode"]] += 1
        if r["elements_missing"] and r["elements_declared"]:
            element_failures[s] += r["elements_missing"]

    # "produced nothing" = a skill in the registry with no artifact at all in this corpus.
    produced = {r["skill"] for r in rows if r["skill"]}
    all_skills = {p.parent.name for p in skills_root.glob("*/skills/agentii/*/SKILL.md")}
    declares_nothing = []
    for s in sorted(produced):
        hits = list(skills_root.glob(f"*/skills/agentii/{s}/SKILL.md"))
        if hits and not gate.criteria_for(hits[0].parent)["elements"]:
            declares_nothing.append(s)

    return {
        "per_skill": {k: {**v, "mode_other": dict(v["mode_other"])}
                      for k, v in sorted(per_skill.items())},
        "element_failures": dict(element_failures.most_common()),
        "declares_nothing": sorted(set(declares_nothing)),
        "produced_nothing": sorted(all_skills - produced),
        "artifacts": len(rows),
        "words": [r["words"] for r in rows],
        # Split by population, because the convention applies to ARTIFACTS: a `_cross/`
        # synthesis has no `{date}_{skill}_{affix}` name by design, so folding the two
        # together reports a defect in 15 files that are not supposed to comply.
        "hhmm_missing": sum(1 for r in rows if not r["has_hhmm_component"]),
        "hhmm_missing_artifacts": sum(1 for r in rows
                                      if "artifacts" in Path(r["path"]).parts
                                      and not r["has_hhmm_component"]),
        "artifacts_only": sum(1 for r in rows if "artifacts" in Path(r["path"]).parts),
        "cross_only": sum(1 for r in rows if "artifacts" not in Path(r["path"]).parts),
        "date_missing": sum(1 for r in rows if not r["has_date_component"]),
        "pin_placeholders": sum(1 for r in rows if r["pins_placeholder"]),
        "fr090_zero": {f: sum(1 for r in rows if f not in r["fr090_present"]) for f in FR090},
    }


def render(rows: list[dict], agg: dict, workspaces: list[Path]) -> str:
    """The published baseline (T041). Machine-derived: every number below comes from the
    run, and the run's date and corpus path are stated so a stale copy is visible."""
    ws = ", ".join(f"`{w}`" for w in workspaces)
    words = agg["words"] or [0]
    out = [
        "<!-- GENERATED by scripts/artifact_baseline.py — do not hand-edit. -->",
        f"# Artifact corpus baseline — {date.today().isoformat()}",
        "",
        f"**Corpus**: {ws} · **Artifacts measured**: {agg['artifacts']} · **Read-only**: yes",
        "",
        "Generated by `python3 scripts/artifact_baseline.py --workspaces <path>`. The",
        "criteria are imported from `scripts/check_output_quality.py`, so this baseline and",
        "the enforcement gate cannot disagree about what a declared element is (FR-043).",
        "",
        "## Corpus-wide findings about the CONTRACT",
        "",
        "FR-043's last sentence: an element that fails across the *entire* corpus is a finding",
        "about the contract, not 200+ per-artifact defects. Read these as one statement about",
        "what the corpus is (thesis-mode documents) versus what the skills declare",
        "(single-skill report structure).",
        "",
        "| measure | value |",
        "|---|---|",
        f"| artifacts with a declared skill | {sum(1 for r in rows if r['matched'])} of {agg['artifacts']} |",
        f"| declared elements absent, corpus-wide | {sum(r['elements_missing'] for r in rows)} of {sum(r['elements_declared'] for r in rows)} |",
        f"| artifacts missing the `HHMM` filename component | {agg['hhmm_missing_artifacts']} of {agg['artifacts_only']} under `artifacts/` + {agg['hhmm_missing'] - agg['hhmm_missing_artifacts']} of {agg['cross_only']} `_cross/` syntheses (no date prefix by design) |",
        f"| artifacts missing the `YYYY-MM-DD` filename component | {agg['date_missing']} |",
        f"| artifacts carrying a placeholder pin value | {agg['pin_placeholders']} |",
        f"| words per artifact (min / median / max) | {min(words)} / {sorted(words)[len(words)//2]} / {max(words)} |",
        "",
        "### FR-090 output-schema fields, absent count",
        "",
        "| field | artifacts lacking it |",
        "|---|---|",
    ]
    for f, n in agg["fr090_zero"].items():
        out.append(f"| `{f}` | {n} |")

    out += ["", "## The three failures that look alike (`SC-013`)", "",
            "*`declared-and-unmet`* — the skill declares a contract and the artifact",
            "does not meet it. *`declares-nothing`* — the skill enumerates no structure,",
            "so it cannot be held to one. *`produced-nothing`* — the skill has **no artifact",
            "in this corpus at all**, which is a statement about this corpus (it exercised a",
            "subset of the registry), not a defect in the skill.", "",
            "| skill | kind | artifacts | declared elements absent | mode mismatch |",
            "|---|---|---|---|---|"]
    for s, a in agg["per_skill"].items():
        # A group with no skill resolved cannot be "declared-and-unmet": no declaration
        # applies to it, which is a fourth state and must not be folded into the third.
        kind = "unmatched — no skill resolved" if s.startswith("(no skill") else "declared-and-unmet"
        out.append(f"| `{s}` | {kind} | {a['artifacts']} | "
                   f"{a['elements_missing']} of {a['elements_declared']} | "
                   f"{a['artifacts'] - a['mode_declared']} |")
    for s in agg["declares_nothing"]:
        out.append(f"| `{s}` | **declares-nothing** | — | — | — |")
    for s in agg["produced_nothing"]:
        out.append(f"| `{s}` | **produced-nothing** | 0 | — | — |")

    out += ["", "## Per-skill detail", ""]
    for s, a in agg["per_skill"].items():
        out.append(f"### `{s}`")
        out.append("")
        out.append(f"- artifacts: {a['artifacts']}")
        out.append(f"- declared elements absent: {a['elements_missing']} of {a['elements_declared']}")
        out.append(f"- artifacts using a declared mode slug: {a['mode_declared']} of {a['artifacts']}")
        if a["mode_other"]:
            others = ", ".join(f"`{k}` ×{v}" for k, v in
                               sorted(a["mode_other"].items(), key=lambda kv: -kv[1]))
            out.append(f"- **mode NOT declared by this skill**: {others}")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="artifact_baseline.py",
        description="FR-043 — measure the artifact corpus once, read-only, and publish it.")
    ap.add_argument("--workspaces", nargs="+", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"where to publish (default: {DEFAULT_OUT})")
    ap.add_argument("--skills-root", type=Path, default=gate.ALL_SKILLS_ROOT)
    ap.add_argument("--json", action="store_true", help="also print the raw rows")
    ap.add_argument("--no-publish", action="store_true",
                    help="measure and report, write no baseline file")
    a = ap.parse_args(argv)

    missing = [w for w in a.workspaces if not w.is_dir()]
    if missing:
        print(f"FAIL   workspace(s) not found: {missing}", file=sys.stderr)
        return 2

    rows = scan(a.workspaces, a.skills_root)
    if not rows:
        print("FAIL   no artifact examined — the corpus paths matched nothing, which is not "
              "a clean baseline (FR-006's zero-surface rule)", file=sys.stderr)
        return 1
    agg = rollup(rows, a.skills_root)
    doc = render(rows, agg, a.workspaces)

    if not a.no_publish:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(doc, encoding="utf-8")
    if a.json:
        print(json.dumps({"rows": rows, "aggregate": agg}, indent=2))
    else:
        print(f"OK — {agg['artifacts']} artifact(s) measured read-only"
              + ("" if a.no_publish else f"; baseline published to {a.out}"))
        print(f"     declared elements absent: {sum(r['elements_missing'] for r in rows)}"
              f" of {sum(r['elements_declared'] for r in rows)}")
        print(f"     artifacts without the HHMM filename component: {agg['hhmm_missing']}")
        print(f"     artifacts with a placeholder pin: {agg['pin_placeholders']}")
        print(f"     declares-nothing skill(s): {agg['declares_nothing'] or 'none'}")
        print(f"     produced-nothing skill(s): {len(agg['produced_nothing'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
