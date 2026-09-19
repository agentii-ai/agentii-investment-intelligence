# valuation-methods — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill was upgraded from `structured_only` to `unstructured_document_search` scope (2026-06-03) to pull MD&A and risk-factor narrative context alongside XBRL multiples. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries spanning 10-K Item 1A risk factors (discount rate justification, beta/delta assumptions), MD&A forward-looking statements (growth rate validation, margin trajectory), and 8-K earnings press releases (valuation catalysts, guidance revisions).
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_label=financial_results_2_02` to anchor valuation against the most recent reported financials before Layer 2. For risk-factor analysis, also query `?secondary_label=other_events_8_01` to surface going-concern and impairment 8-Ks that may affect valuation assumptions.

## Protocol

This skill delivers analyst-grade output via 3 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter. **Sub-skill integrations**: for growth-adjusted valuation, invoke `peg-valuation` as sub-skill . For probability-weighted analysis, use `--mode=scenario` which constructs Bear/Base/Bull cases across all modes .
