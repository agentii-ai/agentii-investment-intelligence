# secular-trends — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: evaluate-company-s-exposure-to-major-secular-technology-trends

**Display name**: Evaluate company's exposure to major secular technology trends

<!-- ported_from: references/prompts/4/4_1_optimized.yaml -->

**Focus**: Evaluate the company's exposure to and alignment with major secular technology trends.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

 - relevance_assessment
 - summary_findings
 - trend_exposure_matrix
- **validation_requirements**:
 - quantitative_support
 - source_diversity
 - temporal_coverage

### Mode: deep-dive-ai-trend-assessment-for-companies-with-identified-ai-exposure

**Display name**: Deep dive AI trend assessment for companies with identified AI exposure

<!-- ported_from: references/prompts/4/4_2_1_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-data-value-trend-assessment-for-companies-with-identified-data-exposure

**Display name**: Deep dive data value trend assessment for companies with identified data exposure

<!-- ported_from: references/prompts/4/4_2_2_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-ev-trend-assessment-for-companies-with-identified-ev-exposure

**Display name**: Deep dive EV trend assessment for companies with identified EV exposure

<!-- ported_from: references/prompts/4/4_2_3_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: deep-dive-analysis-for-quantum-computing-renewable-energy-and-other-emerging-tech-trends

**Display name**: Deep dive analysis for quantum computing, renewable energy, and other emerging tech trends

<!-- ported_from: references/prompts/4/4_2_4_optimized.yaml -->

**Focus**: _(no objective field in source YAML)_.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: evaluate-company-s-strategic-position-within-identified-technology-trends

**Display name**: Evaluate company's strategic position within identified technology trends

<!-- ported_from: references/prompts/4/4_2_optimized.yaml -->

**Focus**: Build on the Key Trend Exposure assessment to evaluate the company's strategic position.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

 - supporting_evidence
 - trend_header
- **validation_framework**:
 - competitive_benchmarking
 - consistency_check
 - financial_validation

### Mode: evaluate-company-s-capacity-and-readiness-to-invest-in-technology-transformation

**Display name**: Evaluate company's capacity and readiness to invest in technology transformation

<!-- ported_from: references/prompts/4/4_3_optimized.yaml -->

**Focus**: Evaluate the company's readiness and capacity to invest in technology as a strategic lever.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_outline`
- `read_source_pages`
- `search_keyword_in_source`
- `search_xbrl_facts`

 - citation_format
 - citation_requirements
- **tabular_assessment**:
 - dimension_specifications
 - required_fields

### Mode: assess-the-significance-of-technology-trends-in-current-investment-debate-and-market-perception

**Display name**: Assess the significance of technology trends in current investment debate and market perception

<!-- ported_from: references/prompts/4/4_4_optimized.yaml -->

**Focus**: Determine to what extent AI or any other major technology trend (data, automation, EV,.
 (rewritten via tool-name-map.json:system_v2_7)

- `list_sources`
- `read_source_pages`
- `search_keyword_in_source`

 - management_commentary
 - price_action_sentiment
 - sell_side_commentary
- **overall_summary_template**: [Technology Trend] is [Significant/Moderate/Insignificant] in the current investment
debate on [Company]. [2-3 sentences synthesizing evidence across sell-side commentary,
management emphasis, and market reaction. Explain why the technology trend matters or
doesn't matter to investors.]

- **structured_assessment**:
 - required_fields

<!-- END port-dimension-prompts methodology + modes -->
