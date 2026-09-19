# earnings-preview — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (d) for simple lookups via `search_earnings_calendar` / `get_company_profile` / `search_companies`.

## Protocol

1. **Earnings calendar lookup**: call `search_earnings_calendar(ticker, fiscal_year=current)` to get the most recent reported quarter, next earnings date, and consensus estimates.
2. **Financial highlights**: call `search_xbrl_facts(ticker, concept=["Revenues","NetIncomeLoss","OperatingIncomeLoss","EarningsPerShareDiluted"], fiscal_period=["Q1","Q2","Q3","Q4","FY"], fiscal_year=[current, current-1])` for trailing data.
3. **Company context**: call `get_company_profile(ticker)` for company name, sector, industry.
4. **Peer discovery**: call `get_peer_comparison(ticker, metric)` (note: `search_companies` has no `sector`/`limit` params — pagination is `page`/`page_size`) for peer comparison slide.
5. **Slide-spec construction**: structure a 4–6 slide `.md` slide-deck specification (one section per slide, with title, bullets, and a source footer).
6. **Build**: write the polished `.md` slide-deck specification per `## Output Structure`.
7. **Review**: self-review the slide spec against the `## Validation Gates` below.
8. **Output**: write the artifact path per `## Output File`.
