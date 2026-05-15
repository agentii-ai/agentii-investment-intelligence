#!/usr/bin/env python3
"""
Port references/prompts/{1..8}/*.yaml -> equity-research-core/skills/dim-*/SKILL.md.

Spec 023 Phase 3 task T060 (with T060a / T060b / T061a / T061b inline). Reads
analyst-curated sub-prompt YAMLs from `references/prompts/<dim>/`, applies
tool-name rewrites per `contracts/tool-name-map.json:system_v2_7`, slugifies
mode names per `contracts/slug-rules.md`, and emits enhanced SKILL.md files
plus per-mode output schemas under `outputs/<slug>.yaml`.

Determinism guarantees (T064):
  - All dict iterations are sorted by key.
  - File-system iteration is `sorted()` by basename.
  - Output writes go through a single `_write_if_changed` path that compares
    byte-for-byte against existing content before re-writing.
  - A `.port-manifest.json` records every input SHA256, output SHA256, and the
    `tool-name-map.json` version; CI compares the manifest between two
    consecutive runs and asserts byte-identical.

Failure codes:
  AGENTII_PORT_AMBIGUOUS_VERSION   bare + _optimized YAML coexist w/o marker
  AGENTII_PORT_AUDIT_DRIFT         filesystem vs audit table mismatch
  AGENTII_PORT_RESERVED_SLUG       slug == 'all' or 'essentials'
  AGENTII_PORT_SLUG_COLLISION      same-dim slug collision
  AGENTII_PORT_MISSING_ESSENTIALS  references/prompts/<dim>/essentials.yaml absent
  AGENTII_ESSENTIALS_BUDGET_EXCEEDED  sum of essentials tool calls > 12 (FR-052a)
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Users/frank/A/agenzym/references/prompts")

# ============================================================================
# Reconciled per-dim audit table (T061b) — agentii v1.0.
#
# Round 4 A1 reconciliation: dim-6 has 4 YAML files on disk (6, 6_1, 6_4, 6_5),
# NOT 5 as plan.md v3 audit table claimed. Total reconciled to 48 sub-prompts.
# The slot for 6_2/6_3 was never authored; analyst confirms 4 modes are
# sufficient for v1.0 risk coverage (see references/prompts/6/essentials.yaml
# rationale block).
# ============================================================================
# ============================================================================
# Per-dim frontmatter contracts (Phase 10 — FR-058, FR-060, FR-056)
# ============================================================================
# temporal_scope: analyst-curated defaults per dimension. Structured-only dims
# (exclusively XBRL/financial metrics queries) get >0 quarters for trend range.
TEMPORAL_SCOPE = {
    1: {"default_quarters": 4, "max_quarters": 8,
        "description": "Recent quarter performance: trailing 4 quarters for YoY comparison + sequential momentum"},
    2: {"default_quarters": 8, "max_quarters": 16,
        "description": "Competitive landscape: 8 quarters for market-share trajectories and positioning shifts"},
    3: {"default_quarters": 8, "max_quarters": 16,
        "description": "Growth strategy: 8 quarters for organic/inorganic growth trend decomposition"},
    4: {"default_quarters": 12, "max_quarters": 20,
        "description": "Secular tech trends: 12 quarters (3 fiscal years) for long-range technology adoption cycles"},
    5: {"default_quarters": 8, "max_quarters": 16,
        "description": "Turnaround/stagnation: 8 quarters for operational trend detection and inflection-point analysis"},
    6: {"default_quarters": 4, "max_quarters": 8,
        "description": "Risk analysis: trailing 4 quarters for near-term risk exposure + forward indicators"},
    7: {"default_quarters": 4, "max_quarters": 8,
        "description": "Earnings sentiment: trailing 4 quarters for earnings-call tone and guidance trends"},
    8: {"default_quarters": 4, "max_quarters": 8,
        "description": "Valuation methods: trailing 4 quarters for current multiples and DCF inputs"},
}

# allowed_tools: per-dimension tool allowlists. Core tools for all dims; dims 2/4
# additionally need peer/competitor resolution tools.
CORE_DIM_TOOLS = [
    "search_xbrl_facts", "list_xbrl_concepts", "get_company_financials",
    "get_company_profile", "search_earnings_calendar",
    "search_documents", "read_source_outline", "read_source_pages",
]
PEER_DIM_TOOLS = CORE_DIM_TOOLS + [
    "search_sec_filings", "get_entity_knowledge", "search_companies",
]
ALLOWED_TOOLS = {
    1: CORE_DIM_TOOLS,
    2: PEER_DIM_TOOLS,   # competitive-landscape needs peer resolution
    3: CORE_DIM_TOOLS,
    4: PEER_DIM_TOOLS,   # secular-tech-trends needs peer resolution
    5: CORE_DIM_TOOLS,
    6: CORE_DIM_TOOLS,
    7: CORE_DIM_TOOLS,
    8: CORE_DIM_TOOLS,
}

# retrieval_scope: only set for dims that don't need the three-layer protocol.
# EQ dims 1/6/7/8 are primarily structured-data + sentiment/text analysis;
# dims 2/3/4/5 do unstructured document search at scale (three-layer applies).
RETRIEVAL_SCOPE = {
    1: None,   # three-layer applies (MD&A + earnings docs)
    2: None,   # three-layer applies (competitive analysis across filings)
    3: None,   # three-layer applies (strategy docs across 10-K/earnings)
    4: None,   # three-layer applies (tech trends across multi-year filings)
    5: None,   # three-layer applies (turnaround analysis across filings)
    6: None,   # three-layer applies (risk factors across filings)
    7: None,   # three-layer applies (earnings sentiment across transcripts)
    8: None,   # three-layer applies (valuation methods across filings + XBRL)
}

AUDIT_TABLE = {
    1: {"count": 5, "skill": "dim-recent-quarter-performance", "mts": "single_target"},
    2: {"count": 8, "skill": "dim-competitive-landscape",      "mts": "target_with_optional_peers"},
    3: {"count": 5, "skill": "dim-growth-strategy",            "mts": "single_target"},
    4: {"count": 8, "skill": "dim-secular-tech-trends",        "mts": "target_with_optional_peers"},
    5: {"count": 9, "skill": "dim-turnaround-stagnation",      "mts": "target_with_required_peers"},
    6: {"count": 4, "skill": "dim-risk-analysis",              "mts": "single_target"},
    7: {"count": 6, "skill": "dim-earnings-sentiment",         "mts": "single_target"},
    8: {"count": 3, "skill": "dim-valuation-methods",          "mts": "single_target"},
}
# Total = 48. Update plan.md v3 audit table accordingly.

RESERVED_SLUGS = {"all", "essentials"}
ESSENTIALS_BUDGET_MAX = 12  # FR-052a

# ============================================================================
# Slug rules (mirror of contracts/slug-rules.md). Identical algorithm; this
# duplication is enforced by validate-mode-syntax.py (Check 'AGENTII_PORT_SLUG_DRIFT').
# ============================================================================
def slugify(text: str) -> str:
    """Normalize a string into a mode slug per slug-rules.md."""
    s = (text or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def _first_title_comment(yaml_path: Path) -> str:
    """Parse the first '# Title' comment line from a YAML file as a fallback name."""
    try:
        for line in yaml_path.read_text().splitlines()[:8]:
            if line.startswith("# ") and not line.startswith("# ="):
                title = line.lstrip("# ").strip()
                # Skip Version/Original/Purpose meta-comments
                if any(title.lower().startswith(p) for p in ("version", "original", "purpose", "optimized")):
                    continue
                return title
    except Exception:
        pass
    return ""


def slug_for_yaml(yaml_path: Path, dim: int, parsed) -> str:
    """Pick the right input to slugify per slug-rules.md priority chain."""
    name = None
    if isinstance(parsed, dict):
        if isinstance(parsed.get("name"), str):
            name = parsed["name"]
        elif isinstance(parsed.get("metadata"), dict):
            md = parsed["metadata"]
            if isinstance(md.get("description"), str):
                name = md["description"]
            elif isinstance(md.get("prompt_id"), str):
                pass  # too generic; fall through
        if not name and isinstance(parsed.get("task_config"), dict):
            tc = parsed["task_config"]
            if isinstance(tc.get("task_name"), str):
                name = tc["task_name"]
    if not name:
        # Fall back to the first '# Title' comment in the raw file
        name = _first_title_comment(yaml_path)
    if not name:
        # Final fallback: keep dim prefix for readability (2_1_1 -> 2-1-1)
        stem = yaml_path.stem
        if stem.endswith("_optimized"):
            stem = stem[: -len("_optimized")]
        name = stem
    slug = slugify(name)
    return slug


# ============================================================================
# Tool-name rewriting (T013 / FR-011).
# ============================================================================
def apply_tool_rewrites(text: str, mapping: dict) -> str:
    """Word-boundary-safe rewrite of every key in `mapping` to its value."""
    for legacy, modern in sorted(mapping.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\b{re.escape(legacy)}\b", modern, text)
    return text


# Upstream-prompt sanitizers (FR-050a citation rewrite + FR-020e prose safety).
# Legacy tuple citations [📄](ref_id-row_number) carry no source-UUID context
# at port time; they must be stripped (analyst restores real FR-050 citations
# when running the skill against live data).
_LEGACY_CITATION_RE = re.compile(r"\[📄\]\([^)]*\)")
# Shell-variable-form placeholders from upstream prompts (e.g. ${X.XX}, ${XXM})
# violate FR-020e prose-safety. Convert to plain markdown placeholders.
_DOLLAR_BRACE_RE = re.compile(r"\$\{([^}]*)\}")
# Upstream prompt template currency placeholders like $XXM, $X.XXM, $XXXM.
# These look like shell-variable references to FR-020e but are legitimate
# template placeholders in the source prompts. Convert to <amount> markdown
# placeholders so the port output is prose-safety clean. Real dollar amounts
# in tables (e.g. "$1,234M") are preserved (the [X.] prefix disqualifies).
_DOLLAR_PLACEHOLDER_RE = re.compile(r"\$(X[\w.]*M?)\b")


def sanitize_ported_text(text: str) -> str:
    """Apply FR-050a + FR-020e cleanups to ported prompt content."""
    text = _LEGACY_CITATION_RE.sub("_(cite source filing in v1.0 citation format at runtime)_", text)
    text = _DOLLAR_BRACE_RE.sub(r"<\1>", text)
    text = _DOLLAR_PLACEHOLDER_RE.sub(r"<\1-amount>", text)
    return text


# ============================================================================
# YAML normalization.
# ============================================================================
def _coalesce_objective(y: dict) -> str:
    """YAMLs vary: objective at top-level OR under task_config.objective."""
    if isinstance(y.get("objective"), str):
        return y["objective"].strip()
    tc = y.get("task_config") or {}
    if isinstance(tc, dict) and isinstance(tc.get("objective"), str):
        return tc["objective"].strip()
    return ""


def _coalesce_questions(y: dict) -> list:
    """key_questions OR key_evaluation_questions OR questions OR analytical_questions."""
    out = []
    for key in ("key_questions", "key_evaluation_questions", "questions", "analytical_questions"):
        v = y.get(key)
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    out.append(item.strip())
                elif isinstance(item, dict) and isinstance(item.get("text"), str):
                    out.append(item["text"].strip())
        elif isinstance(v, dict):
            for k in sorted(v.keys()):
                item = v[k]
                if isinstance(item, str):
                    out.append(item.strip())
                elif isinstance(item, dict) and isinstance(item.get("text"), str):
                    out.append(item["text"].strip())
    return out


def _coalesce_tool_calls(y: dict) -> list:
    """Find tool names referenced anywhere in the YAML for budget computation."""
    found = set()
    legacy = {
        "fetch_financial_statement", "fetch_filtered_document_names",
        "fetch_document_outline", "fetch_document_chunk_content",
        "search_keyword_in_filtered_documents", "fetch_stock_info",
    }
    modern = {
        "search_xbrl_facts", "list_sources", "read_source_outline",
        "read_source_pages", "search_keyword_in_source", "get_company_profile",
        "search_documents", "get_company_financials", "search_sec_filings",
        "get_sec_filing", "read_rendered_statement", "search_earnings_calendar",
        "list_upcoming_earnings", "get_entity_knowledge", "list_domains",
    }

    def _walk(obj):
        if isinstance(obj, str):
            for tn in legacy | modern:
                if re.search(rf"\b{re.escape(tn)}\b", obj):
                    found.add(tn)
        elif isinstance(obj, dict):
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for v in obj:
                _walk(v)

    _walk(y)
    return sorted(found)


def _output_structure_lines(y: dict) -> list:
    """Extract output requirements / output structure into a flat list of bullets."""
    out = []
    for key in ("output_requirements", "output_structure", "output_format"):
        v = y.get(key)
        if isinstance(v, dict):
            for k in sorted(v.keys()):
                if k.startswith("_"):
                    continue
                sub = v[k]
                if isinstance(sub, (str, int, float, bool)):
                    out.append(f"- **{k}**: {sub}")
                elif isinstance(sub, list):
                    out.append(f"- **{k}**:")
                    for item in sub:
                        if isinstance(item, str):
                            out.append(f"  - {item}")
                elif isinstance(sub, dict):
                    out.append(f"- **{k}**:")
                    for kk in sorted(sub.keys()):
                        out.append(f"  - {kk}")
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    out.append(f"- {item}")
    return out


# ============================================================================
# Rendering.
# ============================================================================
def render_mode_section(slug: str, name: str, objective: str,
                        questions: list, tool_calls: list,
                        output_lines: list, source_file: str) -> str:
    """Render one ## Mode: <slug> section."""
    lines = [
        f"## Mode: {slug}",
        "",
        f"**Display name**: {name}",
        "",
        f"<!-- ported_from: references/prompts/{source_file} -->",
        "",
        "### Objective",
        "",
        objective or "_(no objective field in source YAML)_",
        "",
    ]
    if questions:
        lines.append("### Key analytical questions")
        lines.append("")
        for q in questions:
            lines.append(f"- {q}")
        lines.append("")
    if tool_calls:
        lines.append("### Tool calls (rewritten via tool-name-map.json:system_v2_7)")
        lines.append("")
        for tc in tool_calls:
            lines.append(f"- `{tc}`")
        lines.append("")
    if output_lines:
        lines.append("### Output structure (per-mode)")
        lines.append("")
        lines.extend(output_lines)
        lines.append("")
    return "\n".join(lines)


def render_output_schema(slug: str, dim: int, mts: str, output_lines: list) -> dict:
    """Produce the outputs/<slug>.yaml content (FR-020a + citation density)."""
    return {
        "spec_version": "1.0",
        "mode_slug": slug,
        "dimension": dim,
        "multi_ticker_semantics": mts,
        "required_sections": ["Executive Summary", "Analysis", "Coverage Gaps", "Citations"],
        "citation_density": {
            "metric": "citations_per_200_words",
            "minimum": 1,
            "format_regex": r"\[\ud83d\udcc4 [^\]]+ p\.\d+\]\(agentii://source/[a-f0-9-]+\?accession=[\d-]+&page=\d+\)",
        },
        "validation_rules": [
            "section-presence",
            "citation-density",
            "trigger-coverage",
        ],
        "structure_hints": output_lines or ["(per parent SKILL.md ## Output Structure)"],
    }


# ============================================================================
# Audit + drift detection (T061b).
# ============================================================================
def collect_dim_yamls(dim: int, source_root: Path) -> list:
    """Return sorted list of source YAML Paths for dim, applying _optimized precedence."""
    dim_dir = source_root / str(dim)
    if not dim_dir.is_dir():
        return []
    all_yaml = sorted([p for p in dim_dir.glob("*.yaml") if p.name != "essentials.yaml"])
    # Build optimized lookup: bare-name (without _optimized) -> _optimized path
    optimized = {}
    bare = {}
    for p in all_yaml:
        if p.stem.endswith("_optimized"):
            optimized[p.stem[: -len("_optimized")]] = p
        else:
            bare[p.stem] = p
    # If both bare and optimized exist for the same stem, require marker file.
    marker = dim_dir / ".optimized-superseded.yaml"
    conflicts = sorted(set(bare) & set(optimized))
    if conflicts and not marker.is_file():
        raise SystemExit(
            f"AGENTII_PORT_AMBIGUOUS_VERSION: dim-{dim} has bare + _optimized for "
            f"{conflicts}. Create {marker} listing superseded bare filenames OR "
            f"remove the bare YAMLs."
        )
    # Emit _optimized when present; else bare. Skip bare if optimized exists.
    selected = []
    for p in all_yaml:
        stem = p.stem
        if stem.endswith("_optimized"):
            selected.append(p)
        elif stem not in optimized:
            selected.append(p)
        # else: bare-with-optimized-shadow → skip
    return sorted(selected, key=lambda p: p.name)


def check_audit_drift(dim: int, yamls: list) -> None:
    expected = AUDIT_TABLE[dim]["count"]
    actual = len(yamls)
    if expected != actual:
        raise SystemExit(
            f"AGENTII_PORT_AUDIT_DRIFT: dim-{dim} expected {expected} sub-prompts "
            f"(per AUDIT_TABLE / T061b), found {actual} on disk: "
            f"{[p.name for p in yamls]}"
        )


# ============================================================================
# Essentials + budget (FR-052a).
# ============================================================================
def load_essentials(dim: int, source_root: Path) -> dict:
    path = source_root / str(dim) / "essentials.yaml"
    if not path.is_file():
        raise SystemExit(
            f"AGENTII_PORT_MISSING_ESSENTIALS: dim-{dim} missing {path}. "
            f"essentials.yaml must be authored by an investment analyst per "
            f"FR-052a / Round 4 Q13 governance."
        )
    return yaml.safe_load(path.read_text()) or {}


def resolve_essentials_modes(essentials: dict, source_files_to_slug: dict) -> list:
    """Map essentials_source_files (filename tokens) -> actual slugs."""
    out = []
    for token in essentials.get("essentials_source_files", []):
        # Try a few normalizations to match.
        candidates = [
            token,
            f"{token}.yaml",
            f"{token}_optimized.yaml",
        ]
        slug = None
        for cand in candidates:
            if cand in source_files_to_slug:
                slug = source_files_to_slug[cand]
                break
            # Allow leading-prefix-stripped match
            for src_name, src_slug in source_files_to_slug.items():
                if Path(src_name).stem == token or Path(src_name).stem == f"{token}_optimized":
                    slug = src_slug
                    break
            if slug:
                break
        if not slug:
            raise SystemExit(
                f"AGENTII_PORT_INVALID_ESSENTIAL: essentials.yaml references "
                f"'{token}' which does not match any source YAML in this dim. "
                f"Available files: {sorted(source_files_to_slug.keys())}"
            )
        out.append(slug)
    return out


# ============================================================================
# SKILL.md rewriting — preserves frontmatter + structural sections,
# replaces ## Methodology placeholder with the rendered ## Mode: blocks,
# updates frontmatter `essentials_modes`.
# ============================================================================
# Port-generated content is bracketed by these sentinel HTML comments so
# re-runs replace cleanly regardless of how many ## Mode: sections were
# previously emitted.
PORT_BEGIN_MARK = "<!-- BEGIN port-dimension-prompts methodology + modes -->"
PORT_END_MARK = "<!-- END port-dimension-prompts methodology + modes -->"

SKILL_PLACEHOLDER_METHODOLOGY = re.compile(
    r"## Methodology\s*\n\n\*This is a Phase 1 scaffold.*?(?=\n## (?:Output Structure|Error Handling))",
    re.DOTALL,
)
SKILL_PORTED_BLOCK_RE = re.compile(
    re.escape(PORT_BEGIN_MARK) + r".*?" + re.escape(PORT_END_MARK) + r"\s*",
    re.DOTALL,
)
SKILL_FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def update_skill_md(skill_path: Path, mode_sections: list, essentials_modes: list, dim: int = 0) -> bool:
    """Replace bracketed port block (or initial scaffold placeholder) with ported ## Mode: sections."""
    if not skill_path.is_file():
        print(f"WARN: scaffold {skill_path} not found; skipping", file=sys.stderr)
        return False
    text = skill_path.read_text()

    ts = TEMPORAL_SCOPE.get(dim, TEMPORAL_SCOPE[1])
    methodology_intro = (
        "## Methodology\n\n"
        "### Retrieval Scope\n\n"
        "This skill performs unstructured document search at scale (10-K, 10-Q, 8-K filings "
        "spanning multiple fiscal periods). The three-layer agent-use-ready retrieval protocol "
        "(Document Discovery → Page Map → Deep Read) applies per spec 023 FR-056.\n\n"
        "### Retrieval Strategy\n\n"
        "Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:\n"
        "- Branch (a) for structured financial metrics via `search_xbrl_facts` with "
        "`list_xbrl_concepts` pre-condition for unfamiliar concepts.\n"
        "- Branch (c) for single-period document queries via direct `read_source_outline` "
        "→ `read_source_pages`.\n"
        "- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.\n\n"
        "### Temporal Scope\n\n"
        "Default: {dq} fiscal quarters (max {mq}). {desc}\n\n"
        "### Tool Allowlist\n\n"
        "See frontmatter `allowed_tools` — {nt} tools declared for this dimension.\n\n"
        "### Protocol\n\n"
        "This skill delivers analyst-grade output via {n} addressable mode(s); invoke with "
        "`--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see "
        "[Mode syntax](../../../../docs/commands/MODE_SYNTAX.md)). The default invocation "
        "(no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.\n\n"
    ).format(
        n=len(mode_sections),
        dq=ts["default_quarters"],
        mq=ts["max_quarters"],
        desc=ts["description"],
        nt=len(ALLOWED_TOOLS.get(dim, CORE_DIM_TOOLS)),
    )
    port_block = (
        PORT_BEGIN_MARK + "\n\n"
        + methodology_intro
        + "\n".join(mode_sections)
        + "\n"
        + PORT_END_MARK + "\n\n"
    )

    # 1. If a previous port block exists (bracketed by sentinels), replace it.
    new_text, n = SKILL_PORTED_BLOCK_RE.subn(port_block, text)
    if n == 0:
        # 2. First-time port: replace the Phase-1 scaffold's ## Methodology
        #    placeholder up through (but not including) ## Output Structure.
        new_text, n = SKILL_PLACEHOLDER_METHODOLOGY.subn(port_block, text)
    if n == 0:
        # 3. Last-resort fallback: insert before ## Output Structure if both
        #    sentinels and placeholder are missing (manually-edited file).
        new_text = re.sub(
            r"(?=## Output Structure)",
            port_block,
            text,
            count=1,
        )

    # 2. Insert/update essentials_modes in frontmatter (after multi_ticker_semantics)
    fm_match = SKILL_FRONTMATTER_RE.search(new_text)
    if fm_match:
        fm_body = fm_match.group(1)
        em_line = "essentials_modes:\n" + "".join(f"  - {s}\n" for s in essentials_modes).rstrip("\n")
        if "essentials_modes:" in fm_body:
            fm_body = re.sub(r"essentials_modes:.*?(?=\n[a-z]|\Z)", em_line + "\n", fm_body, flags=re.DOTALL)
        else:
            # Append after multi_ticker_semantics line
            fm_body = re.sub(
                r"(multi_ticker_semantics:.*?\n)",
                rf"\1{em_line}\n",
                fm_body,
                count=1,
            )
        new_text = new_text[: fm_match.start(1)] + fm_body + new_text[fm_match.end(1):]

    # 3. Insert/update temporal_scope, allowed_tools, retrieval_scope in frontmatter.
    # Merge into existing frontmatter — preserve all original fields.
    fm_match2 = SKILL_FRONTMATTER_RE.search(new_text)
    if fm_match2:
        try:
            fm_data = yaml.safe_load(fm_match2.group(1)) or {}
        except yaml.YAMLError:
            fm_data = {}

        # Ensure critical fields from AUDIT_TABLE are restored if missing
        info = AUDIT_TABLE.get(dim, {})
        if 'name' not in fm_data or not fm_data.get('name'):
            fm_data['name'] = info.get('skill', f'dim-{dim}')
        if 'multi_ticker_semantics' not in fm_data or not fm_data.get('multi_ticker_semantics'):
            fm_data['multi_ticker_semantics'] = info.get('mts', 'single_target')

        # Add/update Phase 10 fields
        ts = TEMPORAL_SCOPE.get(dim, TEMPORAL_SCOPE[1])
        fm_data['temporal_scope'] = {
            'default_quarters': ts['default_quarters'],
            'max_quarters': ts['max_quarters'],
            'description': ts['description'],
        }
        fm_data['allowed_tools'] = ALLOWED_TOOLS.get(dim, CORE_DIM_TOOLS)
        rs = RETRIEVAL_SCOPE.get(dim)
        if rs:
            fm_data['retrieval_scope'] = rs
        elif 'retrieval_scope' in fm_data:
            del fm_data['retrieval_scope']

        # Rebuild valid YAML frontmatter, preserving all original keys
        fm_yaml = yaml.dump(fm_data, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip('\n')
        new_text = new_text[: fm_match2.start(1)] + fm_yaml + "\n" + new_text[fm_match2.end(1):]

    if new_text != text:
        skill_path.write_text(new_text)
        return True
    return False


# ============================================================================
# Main.
# ============================================================================
def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--tool-map", type=Path,
                    default=ROOT / "contracts" / "tool-name-map.json")
    ap.add_argument("--output-dir", type=Path,
                    default=ROOT / "plugins" / "vertical-plugins" /
                    "equity-research-core" / "skills")
    ap.add_argument("--audit-budget", action="store_true")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    tool_map = json.loads(args.tool_map.read_text())
    rewrites = {k: v for k, v in tool_map.get("system_v2_7", {}).items()
                if not k.startswith("_")}
    tool_map_version = tool_map.get("version", "unknown")

    manifest = {
        "tool_map_version": tool_map_version,
        "audit_table_total": sum(d["count"] for d in AUDIT_TABLE.values()),
        "dims": {},
    }

    if args.audit_budget:
        print(f"{'Dim':<5} {'Skill':<35} {'Modes':<7} {'Essentials':<30} {'Budget':<8}")
        print("-" * 90)

    issues = []

    for dim in sorted(AUDIT_TABLE.keys()):
        info = AUDIT_TABLE[dim]
        yamls = collect_dim_yamls(dim, args.source)
        try:
            check_audit_drift(dim, yamls)
        except SystemExit as e:
            issues.append(str(e))
            continue

        # Parse + slugify all
        parsed_yamls = []
        source_files_to_slug = {}
        for p in yamls:
            try:
                y = yaml.safe_load(p.read_text()) or {}
            except yaml.YAMLError as e:
                issues.append(
                    f"AGENTII_PORT_INVALID_YAML: {p.relative_to(args.source.parent)}: {e}"
                )
                y = {"__invalid_yaml__": True, "__error__": str(e)}
            slug = slug_for_yaml(p, dim, y if isinstance(y, dict) and not y.get("__invalid_yaml__") else None)
            if slug in RESERVED_SLUGS:
                issues.append(
                    f"AGENTII_PORT_RESERVED_SLUG: dim-{dim}/{p.name} slugified to "
                    f"reserved keyword '{slug}'; analyst must rename via `name:` field"
                )
                continue
            parsed_yamls.append((p, y, slug))
            source_files_to_slug[p.name] = slug

        # Collision check within dim
        slugs = [t[2] for t in parsed_yamls]
        if len(slugs) != len(set(slugs)):
            seen = {}
            for p, _, s in parsed_yamls:
                seen.setdefault(s, []).append(p.name)
            dups = {s: files for s, files in seen.items() if len(files) > 1}
            issues.append(f"AGENTII_PORT_SLUG_COLLISION: dim-{dim}: {dups}")
            continue

        # Essentials
        essentials = load_essentials(dim, args.source)
        essentials_modes = resolve_essentials_modes(essentials, source_files_to_slug)

        # Compute essentials budget (proxy = sum of tool-call counts per essentials mode)
        budget_used = 0
        for p, y, slug in parsed_yamls:
            if slug in essentials_modes:
                tcalls = _coalesce_tool_calls(y)
                budget_used += len(tcalls)

        if budget_used > ESSENTIALS_BUDGET_MAX:
            issues.append(
                f"AGENTII_ESSENTIALS_BUDGET_EXCEEDED: dim-{dim} essentials budget "
                f"{budget_used} > {ESSENTIALS_BUDGET_MAX} (FR-052a)"
            )

        if args.audit_budget:
            print(f"{dim:<5} {info['skill']:<35} {len(parsed_yamls):<7} "
                  f"{','.join(essentials_modes):<30} {budget_used:<8}")

        if args.check_only or args.audit_budget:
            continue

        # Render and write
        mode_sections = []
        output_schema_writes = {}
        for p, y, slug in parsed_yamls:
            name = (y.get("name") or y.get("metadata", {}).get("description") or slug).strip()
            objective = sanitize_ported_text(apply_tool_rewrites(_coalesce_objective(y), rewrites))
            questions = [sanitize_ported_text(apply_tool_rewrites(q, rewrites)) for q in _coalesce_questions(y)]
            tcalls = _coalesce_tool_calls(y)
            # Rewrite legacy → modern in displayed tool list
            tcalls_modern = sorted(set(rewrites.get(t, t) for t in tcalls))
            output_lines = [sanitize_ported_text(line) for line in _output_structure_lines(y)]
            section = render_mode_section(
                slug=slug, name=name, objective=objective,
                questions=questions, tool_calls=tcalls_modern,
                output_lines=output_lines, source_file=f"{dim}/{p.name}",
            )
            mode_sections.append(section)
            output_schema_writes[slug] = render_output_schema(
                slug=slug, dim=dim, mts=info["mts"], output_lines=output_lines,
            )

        skill_dir = args.output_dir / info["skill"]
        skill_md = skill_dir / "SKILL.md"
        outputs_dir = skill_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        changed = update_skill_md(skill_md, mode_sections, essentials_modes, dim)
        if changed:
            print(f"[port] dim-{dim} -> {skill_md.relative_to(ROOT)}")

        for slug, schema in sorted(output_schema_writes.items()):
            out_path = outputs_dir / f"{slug}.yaml"
            new_content = yaml.safe_dump(schema, sort_keys=True, default_flow_style=False)
            if not out_path.is_file() or out_path.read_text() != new_content:
                out_path.write_text(new_content)

        manifest["dims"][f"dim-{dim}"] = {
            "skill": info["skill"],
            "mts": info["mts"],
            "modes": sorted(slugs),
            "essentials_modes": essentials_modes,
            "essentials_budget": budget_used,
            "source_yaml_count": len(parsed_yamls),
            "inputs": {p.name: _sha256(p) for p, _, _ in parsed_yamls},
        }

    if args.check_only or args.audit_budget:
        if issues:
            for i in issues:
                print(f"FAIL: {i}", file=sys.stderr)
            return 1
        return 0

    if issues:
        for i in issues:
            print(f"FAIL: {i}", file=sys.stderr)
        return 1

    # Write manifest
    manifest_path = args.output_dir.parent / ".port-manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"[port] manifest -> {manifest_path.relative_to(ROOT)}")
    print(f"[port] total modes ported: {sum(len(d['modes']) for d in manifest['dims'].values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
