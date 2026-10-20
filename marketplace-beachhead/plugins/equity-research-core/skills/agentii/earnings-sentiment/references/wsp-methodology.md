# earnings-sentiment -- Consensus vs. Variant View and FEV Framework

Institutional buy-side methodology for earnings analysis, sentiment assessment, and valuation signal extraction. Applied to earnings call interpretation, sell-side report deconstruction, and investment thesis construction.

## Protocol

### Consensus vs. Variant View Framework

The buy-side analytical edge comes from systematically identifying where the consensus narrative is incomplete or incorrect.

**Phase 1 -- Map the Consensus**: Reconstruct what the market is pricing in: the structural tailwind, the company's stated competitive advantage, the growth algorithm, and the valuation support. Sources: sell-side initiation reports, earnings transcripts, management presentations.

**Phase 2 -- Interrogate Each Pillar**: Test each element independently. Does scale create a moat in a local business with a 5-mile catchment radius? Are wage pressures fully reflected in consensus margin estimates? Is supply in the company's largest markets adequately discounted?

**Phase 3 -- Identify the Variant Perception**: Where the consensus is weak is where alpha lives. The variant perception must be specific, falsifiable, and tied to a valuation consequence. Example: consolidated EV/EBITDA comps suggest fair value, but sum-of-the-parts decomposition reveals owned real estate assigned zero incremental value -- worth 50-100% of current equity when properly separated.

### FEV Framework

Apply this lens to every earnings event:

**Fundamentals**: Establish ground truth from the most recent quarter and trailing periods. Revenue drivers: occupancy by segment, pricing trajectory, payer mix shifts. Cost structure: largest expense categories, wage inflation sensitivity, merger synergy realization. Capital intensity: CFFO versus capex gap, discretionary versus mandatory capex decomposition. Balance sheet: debt trajectory, off-balance-sheet obligations via capitalized operating leases, goodwill impairment risk. Segment-level margin trends with black-box risks flagged where management provides insufficient disclosure.

**Expectations**: Back out what the current price embeds. Using consensus multiples, extract implied growth, margin, and return assumptions. When comps trade at 8.3x and 17.3x LTM EBITDA, the dispersion is informative -- the lower multiple reflects business mix and quality, not simply a discount. Blindly averaging comps destroys signal. Ask: what must be true for the current price to be correct? For the variant view to be correct?

**Valuation**: Apply multiple lenses. Never rely on a single methodology:

1. **DCF**: Baseline intrinsic value for businesses with visible cash flow trajectories.
2. **EV/EBITDA comps**: LTM and NTM. Select peers based on business model similarity, not just industry. Understand why each peer trades where it does before weighting it. Adjust EBITDA for non-recurring items. Include all debt-like items in net debt, including capitalized operating leases.
3. **Sum-of-the-parts**: When the company owns material assets that consolidated multiples obscure. Separate owned real estate (valued via cap rates on implied chargeable rent) from operations (valued via EBITDAR multiples). Value ancillary and management-service segments at their own multiples.
4. **Scenario analysis**: Vary coverage ratios, cap rates, and segment multiples across defensible ranges. The range -- not just the midpoint -- informs position sizing.

### Sell-Side Report Deconstruction

Sell-side research is an input, not an answer. Extract key assumptions driving the target price. Test each against independent data. Identify whether the conclusion follows from consensus thinking or contains a variant perception. Note omissions -- unaddressed material risks signal consensus blind spots.

### Earnings Call Protocol

**Pre-call**: Read the press release and 8-K. Build updated common-size statements. Identify the three to five questions the filing alone cannot resolve. Review the prior quarter's transcript for forward-looking statements to validate: `search_documents(ticker={T}, form_type="earnings_call_transcript")` → `read_source_outline` → `read_source_pages` on the guidance/forward_looking-labeled pages.

**During the call**: Listen for tone shifts, new emphasis or de-emphasis of segments, and guidance specificity. The Q&A session surfaces variant views: note which analysts ask which questions, whether management deflects or engages, and whether any question produces a pause or inconsistency.

**Post-call**: Update projections immediately. Cross-reference call claims against the filed 10-Q/10-K -- divergences in emphasis between spoken and written record are analytically significant. For unresolved questions, initiate IR contact.

### Position Building and Incentive Alignment

When an earnings event strengthens the variant view without full conviction, enter with a small position while continuing due diligence. The downside cushion (embedded asset value, hard catalyst) provides margin of safety to enter before certainty. Scale as evidence accumulates; exit if the thesis deteriorates.

Deconstruct management compensation from the proxy: stock options align with share price; time-based RSUs do not. Performance metrics must connect to the thesis catalyst. If the thesis requires real estate monetization but management is compensated on CFFO, incentives are misaligned -- a quiet thesis-killer.
