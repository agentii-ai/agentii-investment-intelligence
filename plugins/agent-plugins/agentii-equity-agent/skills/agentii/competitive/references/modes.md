# competitive — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: direct-competitor-identification-and-analysis

**Display name**: direct-competitor-identification-and-analysis

<!-- ported_from: references/prompts/2/2_1_1.yaml -->

**Focus**: Leverage multiple sources to identify and evaluate the company's major competitors across products, geographies, and development stages, providing a c.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `search_keyword_in_source`

### Mode: market-share-dynamics-analysis

**Display name**: market-share-dynamics-analysis

<!-- ported_from: references/prompts/2/2_1_2.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share dynamics over the past 2 years, using trackable operating metrics d.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `read_source_outline`
- `search_xbrl_facts`

### Mode: market-share-evolution-and-competitive-benchmarking

**Display name**: market-share-evolution-and-competitive-benchmarking

<!-- ported_from: references/prompts/2/2_1_3.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share trends over the past 12 quarters, using trackable operating metrics.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: forward-looking-market-share-outlook-and-strategic-assessment

**Display name**: forward-looking-market-share-outlook-and-strategic-assessment

<!-- ported_from: references/prompts/2/2_1_4.yaml -->

**Focus**: Leverage multiple data sources to evaluate the company's forward-looking market share outlook over the next 1-2 years, using operating metrics and qua.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `search_keyword_in_source`

### Mode: market-concentration-and-competitive-positioning-analysis

**Display name**: market-concentration-and-competitive-positioning-analysis

<!-- ported_from: references/prompts/2/2_1_5.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share dynamics and competitive positioning over the past 12 quarters, usi.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: market-share-growth-drivers-and-retention-risk-analysis

**Display name**: market-share-growth-drivers-and-retention-risk-analysis

<!-- ported_from: references/prompts/2/2_1_6.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the company's market share growth drivers and retention risks over the most recent 12 quarters.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: market-share-capture-efficiency-and-execution-analysis

**Display name**: market-share-capture-efficiency-and-execution-analysis

<!-- ported_from: references/prompts/2/2_1_7.yaml -->

**Focus**: Leverage multiple data sources to evaluate the company's capability to capture market share and execute against market opportunities, using operating .
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: indirect-competition-and-substitution-threat-analysis

**Display name**: indirect-competition-and-substitution-threat-analysis

<!-- ported_from: references/prompts/2/2_2.yaml -->

**Focus**: Leverage multiple data sources to identify and evaluate the indirect competitive landscape facing the company, including substitutes, adjacent market .
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `read_source_outline`
- `search_keyword_in_source`

<!-- END port-dimension-prompts methodology + modes -->
