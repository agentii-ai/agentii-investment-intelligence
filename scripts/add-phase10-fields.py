#!/usr/bin/env python3
"""
Batch-apply Phase 10 frontmatter fields (temporal_scope, allowed_tools,
retrieval_scope) and methodology template to non-dimension SKILL.md files.

Non-dimension skills (BI, industry, models-and-pitches) are authored manually,
not via port-dimension-prompts.py. This script ensures CI-validatable frontmatter
consistency per spec 023 FR-058, FR-060, FR-056, FR-064.

Determinism: re-running this script against already-updated files produces no
changes (idempotent — yaml round-trip preserves ordering).

Usage:
    python3 scripts/add-phase10-fields.py           # apply to all non-dim skills
    python3 scripts/add-phase10-fields.py --check    # report skills needing update
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins" / "vertical-plugins"

# Per-vertical defaults
CONFIGS = {
    "business-intelligence": {
        "temporal_scope": {
            "default_quarters": 8, "max_quarters": 12,
            "description": "BI analysis: trailing 8 quarters for trend decomposition and scenario modeling",
        },
        "allowed_tools": [
            "search_xbrl_facts", "list_xbrl_concepts", "get_company_financials",
            "get_company_profile", "search_earnings_calendar",
            "search_documents", "read_source_outline", "read_source_pages",
            "get_entity_knowledge", "search_companies",
        ],
    },
    "industry-analysis": {
        "temporal_scope": {
            "default_quarters": 8, "max_quarters": 12,
            "description": "Industry analysis: trailing 8 quarters for peer trajectory and competitive dynamics",
        },
        "allowed_tools": [
            "search_xbrl_facts", "list_xbrl_concepts", "get_company_financials",
            "get_company_profile", "search_earnings_calendar",
            "search_documents", "read_source_outline", "read_source_pages",
            "get_entity_knowledge", "search_companies", "search_sec_filings",
        ],
    },
    "models-and-pitches": {
        "temporal_scope": {
            "default_quarters": 12, "max_quarters": 20,
            "description": "Financial modeling: trailing 12 quarters (3 fiscal years) for long-range projection inputs",
        },
        "allowed_tools": [
            "search_xbrl_facts", "list_xbrl_concepts", "get_company_financials",
            "get_company_profile", "search_earnings_calendar",
            "search_documents", "read_source_outline", "read_source_pages",
            "xlsx.build", "xlsx.recalc", "xlsx.evaluate", "xlsx.audit",
        ],
    },
}


def make_methodology(config):
    ts = config["temporal_scope"]
    at = config["allowed_tools"]
    return (
        "\n## Methodology\n\n"
        "### Retrieval Scope\n\n"
        "This skill performs unstructured document search at scale across SEC filings "
        "(10-K, 10-Q, 8-K). The three-layer agent-use-ready retrieval protocol "
        "(Document Discovery → Page Map → Deep Read) applies per spec 023 FR-056.\n\n"
        "### Retrieval Strategy\n\n"
        "Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:\n"
        "- Branch (a) for structured financial metrics via `search_xbrl_facts` with "
        "`list_xbrl_concepts` pre-condition for unfamiliar concepts.\n"
        "- Branch (b) for multi-period unstructured queries via `search_cross_period`.\n"
        "- Branch (c) for single-period document queries via direct `read_source_outline` "
        "→ `read_source_pages`.\n"
        "- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.\n\n"
        "### Temporal Scope\n\n"
        f"Default: {ts['default_quarters']} fiscal quarters (max {ts['max_quarters']}). "
        f"{ts['description']}.\n\n"
        "### Tool Allowlist\n\n"
        f"See frontmatter `allowed_tools` — {len(at)} tools declared for this vertical.\n\n"
        "### Protocol\n\n"
        "1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.\n"
        "2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.\n"
        "3. Retrieval: follow the three-layer protocol —\n"
        "   - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.\n"
        "   - Layer 2: `read_source_outline` to scan page-level metadata.\n"
        "   - Layer 2.5 (optional): `search_keyword_in_source` to filter large documents.\n"
        "   - Layer 3: `read_source_pages` to deep-read only selected pages.\n"
        "4. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per FR-046b.\n\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Report skills needing update without writing")
    ap.add_argument("--output-dir", type=Path, default=PLUGINS)
    args = ap.parse_args()

    needs_update = []
    updated = 0

    for vertical, config in CONFIGS.items():
        skills_dir = args.output_dir / vertical / "skills"
        if not skills_dir.is_dir():
            continue

        for skill_dir in sorted(skills_dir.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            text = skill_md.read_text()

            # Skip port-generated files (equity-research-core)
            if "dim-recent-quarter-performance" in str(skill_dir) or \
               any(d in str(skill_dir) for d in ["dim-competitive", "dim-growth",
                    "dim-secular", "dim-turnaround", "dim-risk",
                    "dim-earnings", "dim-valuation"]):
                continue

            # Parse frontmatter
            m = re.match(r'---\n(.*?)\n---\n', text, re.DOTALL)
            if not m:
                needs_update.append(f"{vertical}/{skill_dir.name}: no frontmatter")
                continue

            try:
                fm_data = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                needs_update.append(f"{vertical}/{skill_dir.name}: YAML parse error")
                continue

            body = text[m.end():]

            # Check if fields already present and correct
            missing = []
            if not fm_data.get("temporal_scope"):
                missing.append("temporal_scope")
            if not fm_data.get("allowed_tools"):
                missing.append("allowed_tools")
            if "### Retrieval Scope" not in text or "### Retrieval Strategy" not in text:
                missing.append("methodology template")

            if not missing:
                continue

            if args.check:
                needs_update.append(f"{vertical}/{skill_dir.name}: missing {missing}")
                continue

            # Apply fields
            fm_data["temporal_scope"] = {
                "default_quarters": config["temporal_scope"]["default_quarters"],
                "max_quarters": config["temporal_scope"]["max_quarters"],
                "description": config["temporal_scope"]["description"],
            }
            fm_data["allowed_tools"] = config["allowed_tools"]

            fm_yaml = yaml.dump(fm_data, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip('\n')
            new_fm = f"---\n{fm_yaml}\n---\n"

            # Replace old methodology if present
            if "## Methodology" in body:
                body = re.sub(r'## Methodology.*?(?=\n## Output Structure|\n## Error Handling|\Z)', '', body, flags=re.DOTALL)

            method_text = make_methodology(config)
            if "## Output Structure" in body:
                body = body.replace("## Output Structure", method_text + "## Output Structure")
            elif "## Error Handling" in body:
                body = body.replace("## Error Handling", method_text + "## Error Handling")

            new_text = new_fm + body
            if new_text != text:
                skill_md.write_text(new_text)
                updated += 1

    if args.check:
        if needs_update:
            print(f"{len(needs_update)} skill(s) need Phase 10 field update:", file=sys.stderr)
            for item in needs_update:
                print(f"  ✗ {item}", file=sys.stderr)
            return 1
        print("OK — all non-dimension skills have Phase 10 fields.")
        return 0

    print(f"Updated {updated} skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
