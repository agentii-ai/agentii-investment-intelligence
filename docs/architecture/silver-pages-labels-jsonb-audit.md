# Silver Pages Labels JSONB Audit

**Status**: PENDING — requires read-only Neon DB access  
**Task**: T264 (Phase 17)  
**Created**: 2026-06-03

## Audit Scope

Verify that `pipeline.src_silver_pages.labels` JSONB column correctly merges:
1. The `general` label set produced by Phase C LLM extraction
2. Every `labels_*` silver-layer folder set

## Expected JSONB Shape

```json
{
  "general": {
    "description": "<~100-char LLM-generated page summary>",
    "keywords": ["entity", "term", "..."],
    "category": "<page category>"
  },
  "financial_results": { "...": "..." },
  "guidance": { "...": "..." }
}
```

## Audit Checklist

- [ ] Read `seed_silver_pages.py` — verify JSONB merge logic
- [ ] Read `seed_labels_to_neon.py` — verify label extraction path
- [ ] Read `seed_sec_pipeline.py` — verify page insertion path
- [ ] Run audit SQL on live Neon: `SELECT jsonb_object_keys(labels) AS top_level_key, count(*) FROM pipeline.src_silver_pages GROUP BY top_level_key ORDER BY count(*) DESC LIMIT 20;`
- [ ] Confirm `general` appears in ~100% of rows (expected: 96%+ of 243K rows)
- [ ] Check for `labels_*`-derived keys appearing in subsets

## Deferred

This audit requires read-only access to the production Neon database (`DATABASE_URL_API_READONLY`). File a spec 022 ticket if drift is found.
