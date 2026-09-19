# Institutional Defaults

- Lookback: per skill `temporal_scope`.
- Currency: reporting currency from the first XBRL fact `unit` (no conversion at v1.0).
- XBRL: `is_primary = true` default; `?include_all_sources=true` only for audit/reconciliation.
- Dedup: API-side; do not re-implement client-side.
