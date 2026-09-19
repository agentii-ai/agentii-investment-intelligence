# competitive-positioning — Output Structure

1. **Executive Summary** (≤200 words) — headline competitive positioning conclusions
2. **Strategic Group Map** — peer positioning along 2–3 key dimensions (e.g., price vs quality, breadth vs specialization)
3. **Five Forces Assessment** — each force rated HIGH/MEDIUM/LOW with XBRL and filing evidence
4. **Competitive Advantage Analysis** — moat sources (brand, switching costs, network effects, scale, regulatory)
5. **Key Metrics** — market share estimates, margin comparisons vs peers, pricing power indicators
6. **Coverage Gaps & Citations** — data not retrievable + citation index

**Multi-ticker output**: write to `_cross/{descriptive-slug}_{YYYY-MM-DD_HHMM}_competitive-positioning_{affix}.md`
(frontmatter `tickers: [...]`). Pure industry/thematic analyses use
`_sector/{sector_name}/{YYYY-MM-DD_HHMM}_competitive-positioning_{affix}.md`.
