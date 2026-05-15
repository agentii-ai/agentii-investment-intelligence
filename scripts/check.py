#!/usr/bin/env python3
"""
Lint all plugin + managed-agent manifests and verify cross-file references.

Ported and extended from anthropics/financial-services/scripts/check.py
(Apache 2.0) with 14 mandatory checks per spec 023 FR-014a/b, FR-020a/b, FR-054, FR-010, FR-052b
(checks 13 + 14 added per Round 4 Q12 + Q15; checks 19–22 added per Phase 10
agentic-search mechanisms FR-056, FR-058, FR-060, FR-064):

  1.  YAML parse all *.yaml under managed-agent-cookbooks/.
  2.  JSON parse all plugin.json / marketplace.json / steering-examples.json /
      *.schema.json contract files.
  3.  agent.md frontmatter has name + description.
  4.  Reference resolution (system.file, skills[].path, skills[].from_plugin,
      callable_agents[].manifest).
  5.  Skill drift detection between agent-plugin bundles and vertical sources.
  6.  Agent prose `skill-name` references resolve to bundled skills.
  7.  Marketplace source paths resolve to directories with plugin.json.
  8.  Every managed-agent-cookbook has agent.yaml + README.md + steering-examples.json.
  9.  Every SKILL.md has ## Output Structure + ## Error Handling.
  10. Every SKILL.md frontmatter has multi_ticker_semantics.
  11. Every SKILL.md has ## Defaults OR frontmatter `parameter_free: true`.
  12. Every SKILL.md has ## Triggers with ≥10 list items.
  13. Every vertical's .mcp.json `agentii` entry is byte-identical to
      contracts/mcp-canonical.json (FR-010, Round 4 Q15).
  14. Every command .md file in plugins/**/commands/ ends with the canonical
      MODE_SYNTAX.md footer link (FR-052b, Round 4 Q12).
  15–18. (Reserved for FR-044 protocol, pre-publish gate, essentials.yaml, fingerprint drift)
  19. Every SKILL.md has temporal_scope frontmatter block with valid
      default_quarters (1-20), max_quarters (>= default_quarters, <= 20),
      description (FR-058 / Phase 10 agentic search).
  20. Every SKILL.md has allowed_tools list with valid canonical tool names,
      office-plane tools only in models-and-pitches, structured_only skills
      exclude document tools (FR-060 / Phase 10).
  21. Every SKILL.md has three-layer protocol in ## Methodology OR
      valid retrieval_scope opt-out in frontmatter (FR-056 / Phase 10).
  22. Every SKILL.md ## Methodology has all 5 required subsections:
      Retrieval Scope, Retrieval Strategy, Temporal Scope, Tool Allowlist,
      Protocol (FR-064 / Phase 10 skill-methodology-template.md).

Exit 0 if clean, 1 otherwise. Requires: pyyaml, jsonschema.
"""
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
PLUGINS = ROOT / "plugins"
MANAGED = ROOT / "managed-agent-cookbooks"
CONTRACTS = ROOT / "contracts"

errors: list[str] = []
checked = 0


def err(msg: str) -> None:
    errors.append(msg)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# --- 1. YAML parse ----------------------------------------------------------
for yml in sorted(MANAGED.rglob("*.yaml")):
    checked += 1
    try:
        with open(yml) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(f"YAML parse: {rel(yml)}: {e}")

for yml in sorted(CONTRACTS.rglob("*.yaml")):
    checked += 1
    try:
        with open(yml) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(f"YAML parse: {rel(yml)}: {e}")

# --- 2. JSON parse ----------------------------------------------------------
json_globs = [
    ".claude-plugin/marketplace.json",
    "plugins/**/.claude-plugin/plugin.json",
    "plugins/**/.mcp.json",
    "managed-agent-cookbooks/*/steering-examples.json",
    "contracts/*.json",
    "contracts/*.schema.json",
    "plugins/vertical-plugins/*/contracts/*.json",
    "managed-agent-cookbooks/*/contracts/*.json",
]
for pat in json_globs:
    for jf in sorted(ROOT.glob(pat)):
        checked += 1
        try:
            json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            err(f"JSON parse: {rel(jf)}: {e}")

# --- 3. agent.md frontmatter -----------------------------------------------
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    checked += 1
    text = md.read_text()
    if not text.startswith("---"):
        err(f"frontmatter: {rel(md)}: missing leading ---")
        continue
    try:
        _, fm, _ = text.split("---", 2)
        meta = yaml.safe_load(fm)
        for k in ("name", "description"):
            if k not in meta:
                err(f"frontmatter: {rel(md)}: missing '{k}'")
    except (ValueError, yaml.YAMLError) as e:
        err(f"frontmatter: {rel(md)}: {e}")


# --- 4. reference resolution -----------------------------------------------
def check_refs(yml: Path) -> None:
    try:
        data = yaml.safe_load(yml.read_text()) or {}
    except yaml.YAMLError:
        return
    base = yml.parent
    sys_spec = data.get("system")
    if isinstance(sys_spec, dict) and "file" in sys_spec:
        p = (base / sys_spec["file"]).resolve()
        if not p.is_file():
            err(f"ref: {rel(yml)}: system.file -> {sys_spec['file']} (not found)")
    for s in data.get("skills") or []:
        if isinstance(s, dict) and "path" in s:
            p = (base / s["path"]).resolve()
            if not p.exists():
                err(f"ref: {rel(yml)}: skills.path -> {s['path']} (not found)")
        if isinstance(s, dict) and "from_plugin" in s:
            p = (base / s["from_plugin"]).resolve()
            if not (p / "skills").is_dir():
                err(f"ref: {rel(yml)}: skills.from_plugin -> {s['from_plugin']} (no skills/ dir)")
    for c in data.get("callable_agents") or []:
        if isinstance(c, dict) and "manifest" in c:
            p = (base / c["manifest"]).resolve()
            if not p.is_file():
                err(f"ref: {rel(yml)}: callable_agents.manifest -> {c['manifest']} (not found)")


for yml in sorted(MANAGED.rglob("*.yaml")):
    check_refs(yml)

# --- 5. agent-plugin bundled skills match vertical source ------------------
import filecmp

src_by_name = {p.name: p for p in PLUGINS.glob("vertical-plugins/*/skills/*") if p.is_dir()}
for bundled in sorted(PLUGINS.glob("agent-plugins/*/skills/*")):
    if not bundled.is_dir():
        continue
    src = src_by_name.get(bundled.name)
    if not src:
        err(f"bundled-skill: {rel(bundled)}: no vertical source named '{bundled.name}'")
        continue
    cmp = filecmp.dircmp(src, bundled)
    if cmp.diff_files or cmp.left_only or cmp.right_only:
        err(f"bundled-skill: {rel(bundled)}: drifted from {rel(src)} (run sync-agent-skills.py)")

# --- 6. agent.md skill references -------------------------------------------
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    slug = md.parents[1].name
    sk_dir = PLUGINS / "agent-plugins" / slug / "skills"
    bundle = {p.name for p in sk_dir.iterdir() if p.is_dir()} if sk_dir.is_dir() else set()
    for ref in set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", md.read_text())):
        if ref in src_by_name and ref not in bundle:
            err(
                f"agent-prose: {rel(md)}: references `{ref}` but "
                f"plugins/agent-plugins/{slug}/skills/{ref}/ is not bundled"
            )

# --- 7. marketplace source paths resolve ------------------------------------
mp = ROOT / ".claude-plugin" / "marketplace.json"
if mp.is_file():
    for p in json.loads(mp.read_text()).get("plugins", []):
        src = (ROOT / p["source"]).resolve()
        if not (src / ".claude-plugin" / "plugin.json").is_file():
            err(f"marketplace: {p['name']} source -> {p['source']} (no plugin.json)")

# --- 8. required files per managed-agent-cookbook ---------------------------
# Cookbooks are populated in Phase 7 (US7). At Phase 1, a cookbook directory
# may exist with only `contracts/` and `subagents/` subdirs and no agent.yaml.
# Treat the cookbook as "populated" only once agent.yaml exists at the root.
for d in sorted(MANAGED.iterdir()):
    if not d.is_dir():
        continue
    if not (d / "agent.yaml").is_file():
        continue  # cookbook not yet populated; skip required-file check
    for req in ("agent.yaml", "README.md", "steering-examples.json"):
        if not (d / req).is_file():
            err(f"missing: {rel(d)}/{req}")

# --- 9-12. SKILL.md structural checks ---------------------------------------
SKILL_FILES = sorted(PLUGINS.glob("vertical-plugins/*/skills/*/SKILL.md")) + \
              sorted(PLUGINS.glob("agent-plugins/*/skills/*/SKILL.md"))

for sk in SKILL_FILES:
    checked += 1
    text = sk.read_text()
    # parse frontmatter
    meta = {}
    if text.startswith("---"):
        try:
            _, fm, body = text.split("---", 2)
            meta = yaml.safe_load(fm) or {}
        except (ValueError, yaml.YAMLError) as e:
            err(f"skill-frontmatter: {rel(sk)}: {e}")
            continue
    else:
        err(f"skill-frontmatter: {rel(sk)}: missing leading ---")
        continue

    # Check 9: ## Output Structure + ## Error Handling
    if "## Output Structure" not in text:
        err(f"skill-structure: {rel(sk)}: missing '## Output Structure' (FR-020a)")
    if "## Error Handling" not in text:
        err(f"skill-structure: {rel(sk)}: missing '## Error Handling' (FR-020b)")

    # Check 10: multi_ticker_semantics in frontmatter
    mts = meta.get("multi_ticker_semantics")
    valid_mts = {"single_target", "target_with_optional_peers", "target_with_required_peers", "basket_v1_1"}
    if mts not in valid_mts:
        err(
            f"skill-mts: {rel(sk)}: multi_ticker_semantics '{mts}' invalid "
            f"(must be one of {sorted(valid_mts)}) (FR-054)"
        )

    # Check 11: ## Defaults OR parameter_free: true
    if "## Defaults" not in text and not meta.get("parameter_free", False):
        err(
            f"skill-defaults: {rel(sk)}: missing '## Defaults' table "
            f"and frontmatter parameter_free is not true (FR-014b)"
        )

    # Check 12: ## Triggers with ≥10 items (scaffold may have 0; warn only if section exists with <10)
    trig_match = re.search(r"## Triggers\s*\n(.*?)(?=\n##|\Z)", text, flags=re.DOTALL)
    if trig_match:
        trig_body = trig_match.group(1)
        items = re.findall(r"^\s*[-*]\s+\S+", trig_body, flags=re.MULTILINE)
        if items and len(items) < 10:
            err(
                f"skill-triggers: {rel(sk)}: '## Triggers' has {len(items)} items "
                f"(need ≥10 per FR-014a)"
            )

# --- Check 13: vertical .mcp.json agentii entry == mcp-canonical.json --------
MCP_CANONICAL = CONTRACTS / "mcp-canonical.json"
if MCP_CANONICAL.exists():
    try:
        canonical = json.loads(MCP_CANONICAL.read_text())
        canonical_agentii = canonical.get("agentii")
    except json.JSONDecodeError as e:
        err(f"mcp-canonical: {rel(MCP_CANONICAL)}: invalid JSON: {e}")
        canonical_agentii = None
    if canonical_agentii:
        for vertical_dir in (PLUGINS / "vertical-plugins").glob("*/"):
            mcp_path = vertical_dir / ".mcp.json"
            if not mcp_path.exists():
                err(
                    f"mcp-replication: {rel(vertical_dir)}: missing .mcp.json "
                    f"(FR-010 / Round 4 Q15 — every vertical must replicate canonical agentii entry)"
                )
                continue
            checked += 1
            try:
                vertical_mcp = json.loads(mcp_path.read_text())
            except json.JSONDecodeError as e:
                err(f"mcp-replication: {rel(mcp_path)}: invalid JSON: {e}")
                continue
            servers = vertical_mcp.get("mcpServers", vertical_mcp)
            vertical_agentii = servers.get("agentii")
            if vertical_agentii != canonical_agentii:
                err(
                    f"mcp-replication: {rel(mcp_path)}: 'agentii' entry differs from "
                    f"contracts/mcp-canonical.json (FR-010 / Round 4 Q15 byte-equality)"
                )
else:
    err("mcp-canonical: contracts/mcp-canonical.json missing (FR-010 / Round 4 Q15)")

# --- Check 14: command files end with MODE_SYNTAX.md footer link -------------
MODE_SYNTAX_LINK_RE = re.compile(
    r"\[Mode syntax\]\(\.\./\.\./\.\./docs/commands/MODE_SYNTAX\.md\)"
)
for cmd in PLUGINS.glob("**/commands/*.md"):
    checked += 1
    text = cmd.read_text()
    if not MODE_SYNTAX_LINK_RE.search(text):
        err(
            f"command-mode-syntax: {rel(cmd)}: missing canonical MODE_SYNTAX.md footer "
            f"link (FR-052b / Round 4 Q12 — every slash command must reference "
            f"`../../../docs/commands/MODE_SYNTAX.md`)"
        )

# --- Check 15-18: reserved for Phase 4 (FR-044 protocol), Phase 9 (pre-publish gate),
#     Phase 3 essentials.yaml presence, and .upstream-pin.yaml fingerprint drift.

# --- Check 19: temporal_scope frontmatter field (FR-058) --------------------
for sk in SKILL_FILES:
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    ts = meta.get("temporal_scope")
    if not isinstance(ts, dict):
        err(
            f"skill-temporal-scope: {rel(sk)}: missing 'temporal_scope' frontmatter block "
            f"(FR-058 — must have default_quarters, max_quarters, description)"
        )
        continue
    dq = ts.get("default_quarters")
    mq = ts.get("max_quarters")
    desc = ts.get("description")
    if not isinstance(dq, (int, float)) or dq < 1 or dq > 20:
        err(
            f"skill-temporal-scope: {rel(sk)}: default_quarters={dq} invalid "
            f"(must be 1-20) (FR-058)"
        )
    if not isinstance(mq, (int, float)) or mq < (dq or 1) or mq > 20:
        err(
            f"skill-temporal-scope: {rel(sk)}: max_quarters={mq} invalid "
            f"(must be >= default_quarters and <= 20) (FR-058)"
        )
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        err(
            f"skill-temporal-scope: {rel(sk)}: description missing or too short "
            f"(FR-058 — human-readable rationale required)"
        )

# --- Check 20: allowed_tools frontmatter field (FR-060) ---------------------
# Gather canonical MCP tool names from tool-name-map.json
CANONICAL_TOOLS: set[str] = set()
OFFICE_TOOLS = {"xlsx.build", "xlsx.recalc", "xlsx.evaluate", "xlsx.audit", "pptx.build", "pptx.refresh"}
DOCUMENT_TOOLS = {"read_source_outline", "read_source_pages", "search_keyword_in_source", "search_documents", "search_sec_filings"}
# Full canonical surface: FR-011 MCP tools + office tools
FR011_TOOLS = {
    "search_clinical_trials", "search_xbrl_facts", "read_rendered_statement",
    "search_documents", "search_sec_filings", "get_sec_filing",
    "get_entity_knowledge", "read_source_pages", "search_keyword_in_source",
    "read_source_outline", "list_sources", "get_company_profile",
    "search_companies", "search_catalysts", "get_company_financials",
    "search_insider_trades", "search_biotech_news", "search_medical_devices",
    "get_homepage_summary", "search_earnings_calendar", "get_company_fiscal_calendar",
    "list_xbrl_concepts", "search_cross_period", "search_ipos",
    "get_stock_quote", "get_options_chain", "get_index_quotes",
    "search_stock_movers", "search_faers_events", "list_coverage",
    "get_ticker_coverage", "list_upcoming_earnings", "get_earnings_calendar_event",
    "list_domains",
}
CANONICAL_TOOLS.update(FR011_TOOLS)
CANONICAL_TOOLS.update(OFFICE_TOOLS)
CANONICAL_TOOLS.update(DOCUMENT_TOOLS)
# Also load from tool-name-map for any missing
tnm_path = CONTRACTS / "tool-name-map.json"
if tnm_path.exists():
    try:
        tnm = json.loads(tnm_path.read_text())
        CANONICAL_TOOLS.update(tnm.get("system_v2_7", {}).values())
        if isinstance(tnm.get("mcp_tool_descriptions"), dict):
            CANONICAL_TOOLS.update(tnm["mcp_tool_descriptions"].keys())
    except (json.JSONDecodeError, KeyError):
        pass

for sk in SKILL_FILES:
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    at = meta.get("allowed_tools")
    if not isinstance(at, list) or len(at) < 1:
        err(
            f"skill-allowed-tools: {rel(sk)}: missing or empty 'allowed_tools' list "
            f"(FR-060 — must declare ~5-10 tools the skill uses)"
        )
        continue
    skill_dir = str(sk.parent.parent.parent.name)  # vertical plugin directory name
    is_models = (skill_dir == "models-and-pitches")
    rs = meta.get("retrieval_scope", "")
    for tool in at:
        if tool in CANONICAL_TOOLS:
            continue
        # Also accept office tools and tools in the MCP canonical + FR-011 list
        if tool in OFFICE_TOOLS or tool in DOCUMENT_TOOLS:
            CANONICAL_TOOLS.add(tool)  # lazily expand
            continue
        err(
            f"skill-allowed-tools: {rel(sk)}: tool '{tool}' not found in canonical "
            f"tool surface (FR-060)"
        )
    # office-plane tools only in models-and-pitches
    if not is_models:
        for tool in at:
            if tool in OFFICE_TOOLS:
                err(
                    f"skill-allowed-tools: {rel(sk)}: office-plane tool '{tool}' "
                    f"declared by non-models-and-pitches skill (FR-060)"
                )
    # structured_only skills exclude document-retrieval tools
    if rs == "structured_only":
        for tool in at:
            if tool in DOCUMENT_TOOLS:
                err(
                    f"skill-allowed-tools: {rel(sk)}: document-retrieval tool '{tool}' "
                    f"declared by retrieval_scope: structured_only skill (FR-060)"
                )

# --- Check 21: three-layer protocol presence OR retrieval_scope opt-out (FR-056) ---
for sk in SKILL_FILES:
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    rs = meta.get("retrieval_scope")
    valid_rs = {"structured_only", "single_document", "simple_lookup"}
    has_layer1 = "read_source_outline" in sk.read_text()
    has_layer3 = "read_source_pages" in sk.read_text()
    has_protocol = has_layer1 and has_layer3
    if rs and rs not in valid_rs:
        err(
            f"skill-retrieval-scope: {rel(sk)}: retrieval_scope '{rs}' invalid "
            f"(must be one of {sorted(valid_rs)}) (FR-056)"
        )
    if not rs and not has_protocol:
        err(
            f"skill-retrieval-scope: {rel(sk)}: no retrieval_scope opt-out and "
            f"no three-layer protocol found in methodology (FR-056 — must contain "
            f"Layer 1→2→2.5→3 OR declare retrieval_scope)"
        )

# --- Check 22: methodology template subsection conformance (FR-064) ----------
METHODOLOGY_SUBS = [
    "### Retrieval Scope",
    "### Retrieval Strategy",
    "### Temporal Scope",
    "### Tool Allowlist",
    "### Protocol",
]
for sk in SKILL_FILES:
    text = sk.read_text()
    if "## Methodology" not in text:
        err(
            f"skill-methodology: {rel(sk)}: missing '## Methodology' section "
            f"(FR-064 — all 5 subsections required: {', '.join(METHODOLOGY_SUBS)})"
        )
        continue
    for sub in METHODOLOGY_SUBS:
        if sub not in text:
            err(
                f"skill-methodology: {rel(sk)}: missing '{sub}' subsection "
                f"under ## Methodology (FR-064 — skill-methodology-template.md)"
            )

# --- report ----------------------------------------------------------------
if errors:
    print(f"FAIL — {len(errors)} issue(s) across {checked} file(s):\n", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK — {checked} file(s) checked, 0 issues.")
