# earnings-sentiment — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill was upgraded from `structured_only` to `unstructured_document_search` scope (2026-06-03) to pull 8-K earnings press releases, MD&A guidance, and Item 1A risk factors alongside XBRL EPS data. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries spanning 8-K earnings press releases (management tone, sentiment language, guidance language), MD&A guidance discussion (forward-looking sentiment, confidence signals), and Item 1A risk factors (uncertainty context, cautionary language).
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

**Layer 1 `secondary_label` allowlist **: prefer `?secondary_labels=financial_results_2_02,regulation_fd_disclosure_7_01` to capture earnings-related 8-Ks AND Reg-FD guidance disclosures before Layer 2. For uncertainty context, also query `?secondary_label=other_events_8_01` for material-event 8-Ks that may signal sentiment shifts.

## Protocol

This skill delivers analyst-grade output via 6 addressable mode(s); invoke with `--mode=<slug>` / `--modes=<slug1>,<slug2>` / `--mode=all` (see [Mode syntax](../../../../docs/commands/MODE_SYNTAX.md). The default invocation (no flag) runs the `essentials_modes` subset declared in this skill's frontmatter.
