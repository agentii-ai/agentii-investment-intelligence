# peer-bench — Output Structure

1. **Executive Summary** (≤200 words) — peer group overview, outliers, key takeaways
2. **Peer Group** — table of tickers, names, sectors, market caps
3. **Growth Comparison** — revenue/EPS growth table with YoY and CAGR
4. **Profitability Comparison** — margin and return metrics across peers
5. **Valuation Comparison** — trading multiples with mean/median/high/low
6. **Financial Health** — leverage and liquidity comparison
7. **Composite Ranking** — z-score matrix, growth/value quadrant positioning
8. **Coverage Gaps & Citations** — data not retrievable + citation index

**Multi-ticker output**: write to `_cross/{descriptive-slug}_{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md`
(frontmatter `tickers: [...]`). Pure sector/thematic analyses use
`_sector/{sector_name}/{YYYY-MM-DD_HHMM}_peer-bench_{affix}.md`.
