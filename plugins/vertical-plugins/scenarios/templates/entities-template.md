# Entities — [Thesis Name]

> Q20/Q36: the entity_claims schema and the entity/metric map for this thesis.
> For `market_data_stage: early` theses this file MUST additionally define the
> bars schema of `get_price_history` (Q42) — no bars schema, no implement.

## entity_claims schema

```yaml
entity_claims:
  - entity: NVDA
    metric: gross_margin
    value: 73.0
    unit: pct
    period: 2026Q2
    source: xbrl:us-gaap:GrossProfit/Revenues
    retrieved_at: 2026-09-08T09:12:00-04:00
    observed_at: 2026-09-08T16:00:00-04:00   # market-derived claims only (Q71)
```

## Entity / metric map

| entity | metric | unit | source |
|---|---|---|---|

## (early theses only — Q42) `get_price_history` bars schema

- Fields: date (ISO, exchange-local NY), open/high/low/close (float, **no None** —
  missing rows dropped, never zero-filled), volume (int)
- Minimum bars for SMA(20): 20 — fewer ⇒ `INSUFFICIENT_HISTORY`
- Python consumption: `Bash: python3 script.py` reads the JSON envelope
