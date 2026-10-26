# earnings-preview — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (d) for simple lookups via `search_earnings_calendar` / `get_company_profile` / `search_companies`.

## Protocol

1. **Resolve the target first**: call `resolve_period(ticker, "next quarter" or the user's period, as_of?)`; bind guidance/estimates to `target_period_id`. `get_company_fiscal_calendar` supplies declared periods/gaps, never a month-derived quarter.
2. **Earnings calendar lookup**: call `search_earnings_calendar(ticker, upcoming=true)` for the next earnings date and consensus estimates; read `date_basis`/`fiscal_source` and never treat an estimate as a fiscal boundary.
3. **Financial highlights**: call `search_xbrl_facts(ticker, concept=["Revenues","NetIncomeLoss","OperatingIncomeLoss","EarningsPerShareDiluted"], period_id=<resolved trailing period_id>)` for each trailing quarter; batch the period_ids, do not derive quarters from months.
4. **Company context**: call `get_company_profile(ticker)` for company name, sector, industry.
5. **Peer discovery**: call `get_peer_comparison(ticker, metric)` (note: `search_companies` has no `sector`/`limit` params — pagination is `page`/`page_size`) for peer comparison slide.
6. **Slide-spec construction**: structure a 4–6 slide `.md` slide-deck specification (one section per slide, with title, bullets, and a source footer).
7. **Build**: write the polished `.md` slide-deck specification per `## Output Structure`.
8. **Review**: self-review the slide spec against the `## Validation Gates` below.
9. **Output**: write the artifact path per `## Output File`.
