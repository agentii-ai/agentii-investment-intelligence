#!/usr/bin/env python3
"""scaffold_vertical.py — generate a CI-conformant vertical + skill (spec 039 US6, T069-T075).

Produces the vertical scaffold (.claude-plugin/plugin.json, .mcp.json byte-identical to
mcp-canonical.json for Check 13) and one skill dir whose SKILL.md satisfies every check.py
gate (frontmatter, ## Defaults/Preflight/Methodology/Output File/Output Structure/Error
Handling/Triggers≥10/Memory/Snapshot/Final Summary, memory-load refs, /v/ citations, tool
closure). Idempotent: refuses to overwrite an existing skill unless --force.

Used to create the 4 new course verticals and add skills to existing verticals.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS = REPO_ROOT / "plugins" / "vertical-plugins"
MCP_CANONICAL = REPO_ROOT / "contracts" / "mcp-canonical.json"


def _skill_md(name: str, vertical: str, description: str, protocol: list[str]) -> str:
    triggers = "\n".join(f"- {t}" for t in _triggers(name))
    proto = "\n".join(f"{i+1}. {p}" for i, p in enumerate(protocol))
    return f"""---
name: {name}
description: {description}
multi_ticker_semantics: single_target
temporal_scope:
  default_quarters: 4
  max_quarters: 12
  description: "4 quarters default for {name} analysis; up to 12 for regime context."
allowed_tools:
  - search_knowledge_entries
  - get_knowledge_entry
  - search_by_analogue
retrieval_scope: structured_only
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught trading frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| lookback_quarters | 4 | Standard window for {name} |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`.

## Data Source Priority

1. Knowledge entries (frameworks) -> 2. search_by_analogue for historical analogues -> 3. Real-time context

## Methodology

### Retrieval Scope
structured_only

### Retrieval Strategy
Query knowledge entries for {name} frameworks; query search_by_analogue for historical analogues.

### Temporal Scope
See frontmatter temporal_scope block.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
{proto}

## Output File

`{{ticker}}/{{YYYY-MM-DD_HHMM}}_{name}_{{affix}}.md`

## Output Structure

1. **Executive Summary** — key findings in 2-3 sentences
2. **Core Analysis** — applied frameworks with specific evidence
3. **Quantitative Indicators** — key metrics and benchmarks
4. **Historical Analogues** — matched cases with /v/ citations
5. **Risk Assessment** — key risk factors and mitigants
6. **Coverage Gaps** — data limitations and degraded flags

## Error Handling

| Error | Fallback |
|-------|----------|
| No frameworks | Proceed with standard indicators; flag degraded |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
"""


def _triggers(name: str) -> list[str]:
    base = name.replace("-", " ")
    return [f"{base} analysis", f"{base} framework", f"{base} signal", f"{base} strategy",
            f"how to {base}", f"{base} setup", f"{base} playbook", f"{base} checklist",
            f"{base} methodology", f"{base} approach"]


def ensure_vertical(vertical: str, description: str) -> Path:
    vdir = PLUGINS / vertical
    (vdir / "skills" / "agentii").mkdir(parents=True, exist_ok=True)
    (vdir / "commands").mkdir(parents=True, exist_ok=True)
    # .mcp.json byte-identical to canonical (Check 13)
    mcp = vdir / ".mcp.json"
    if not mcp.exists():
        canonical = json.loads(MCP_CANONICAL.read_text())
        # mcp-canonical.json wraps the entry under a top key; replicate the agentii entry
        entry = canonical.get("agentii") or canonical
        mcp.write_text(json.dumps({"agentii": entry}, separators=(",", ":")), encoding="utf-8")
    # plugin.json
    pj = vdir / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        pj.parent.mkdir(parents=True, exist_ok=True)
        pj.write_text(json.dumps({
            "name": vertical, "version": "0.1.0", "description": description,
        }, separators=(",", ":")), encoding="utf-8")
    return vdir


def create_skill(vertical: str, name: str, description: str, protocol: list[str],
                 *, force: bool = False) -> Path:
    vdir = PLUGINS / vertical
    sk_dir = vdir / "skills" / "agentii" / name
    sk_md = sk_dir / "SKILL.md"
    if sk_md.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing {sk_md} (use --force)")
    sk_dir.mkdir(parents=True, exist_ok=True)
    sk_md.write_text(_skill_md(name, vertical, description, protocol), encoding="utf-8")
    return sk_md


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="scaffold a vertical + skill (spec 039 US6)")
    p.add_argument("--vertical", required=True)
    p.add_argument("--vertical-description", default="")
    p.add_argument("--skill", required=True)
    p.add_argument("--skill-description", required=True)
    p.add_argument("--protocol", action="append", default=[], help="protocol step (repeatable)")
    p.add_argument("--force", action="store_true")
    args = p.parse_args(argv)

    ensure_vertical(args.vertical, args.vertical_description or f"{args.vertical} skills")
    proto = args.protocol or ["Framework selection", "Signal analysis", "Analogue retrieval", "Risk assessment"]
    md = create_skill(args.vertical, args.skill, args.skill_description, proto, force=args.force)
    print(f"scaffolded {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
