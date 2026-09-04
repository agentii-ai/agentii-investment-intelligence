# comps — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts. **Before querying XBRL facts for peer comparability, call `get_statement_structure(accession_number)` for each peer ticker to verify concept availability — prevents cross-company line-item incomparability where one peer uses a non-standard concept name .**
- Branch (b) for multi-period unstructured queries via `search_cross_period`.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

## Protocol

1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.
2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.
3. Retrieval: follow the three-layer protocol —
 - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.
 - Layer 2: `read_source_outline` to scan page-level metadata.
 - Layer 2.5 (optional): `search_keyword_in_source` to filter large documents.
 - Layer 3: `read_source_pages` to deep-read only selected pages.
4. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per the evidence-pack output contract.
5. **xlsx-financials output**: invoke `xlsx-financials` as sub-skill to produce formatted `.xlsx` comps table workbook. For multi-ticker comps, output to `_cross/{slug}_{date}_statement-income.xlsx` . For single-ticker, output to `{ticker}/{date}_{time}_statement-income.xlsx`.
