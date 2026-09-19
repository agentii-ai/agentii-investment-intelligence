# turnaround — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: performance-stagnation-detection-and-classification

**Display name**: performance-stagnation-detection-and-classification

<!-- ported_from: references/prompts/5/5_1.yaml -->

**Focus**: Identify and extract indicators of performance stagnation across four key dimensions using comprehensive financial and operational analysis.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

### Mode: growth-catalyst-identification-and-assessment

**Display name**: growth-catalyst-identification-and-assessment

<!-- ported_from: references/prompts/5/5_2_1.yaml -->

**Focus**: Identify and extract announcements related to new products, services, or business initiatives that could serve as major catalysts to reaccelerate grow.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: growth-catalyst-execution-monitoring-and-progress-assessment

**Display name**: growth-catalyst-execution-monitoring-and-progress-assessment

<!-- ported_from: references/prompts/5/5_2_1_1.yaml -->

**Focus**: Monitor and assess the execution progress of identified growth catalyst initiatives through trackable metrics, market sentiment analysis, and mileston.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: leadership-change-impact-analysis

**Display name**: leadership-change-impact-analysis

<!-- ported_from: references/prompts/5/5_2_2.yaml -->

**Focus**: Identify and analyze senior leadership or key personnel changes that could materially shift company strategy, investor sentiment, or growth trajectory.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: strategic-leadership-impact-assessment-and-financial-projection

**Display name**: strategic-leadership-impact-assessment-and-financial-projection

<!-- ported_from: references/prompts/5/5_2_3.yaml -->

**Focus**: Analyze the speculated strategy or strategic shift tied to new executive appointments and assess the expected financial statement impacts based on the.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: strategic-initiative-execution-status-and-effectiveness-assessment

**Display name**: strategic-initiative-execution-status-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_2_3_1.yaml -->

**Focus**: Monitor and assess the execution status and effectiveness of strategic initiatives announced or underway, focusing on transformation levers that could.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: operational-execution-progress-and-effectiveness-assessment

**Display name**: operational-execution-progress-and-effectiveness-assessment

<!-- ported_from: references/prompts/5/5_3.yaml -->

**Focus**: Identify and extract trackable metrics and qualitative signals that reflect the execution progress and early results of the company's turnaround strat.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: new-product-performance-evaluation-and-turnaround-contribution-assessment

**Display name**: new-product-performance-evaluation-and-turnaround-contribution-assessment

<!-- ported_from: references/prompts/5/5_4_1.yaml -->

**Focus**: Identify and extract trackable metrics and indicators that evaluate the execution, market feedback, and impact of new products/services launched as gr.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`

### Mode: financial-turnaround-metrics-and-performance-validation

**Display name**: financial-turnaround-metrics-and-performance-validation

<!-- ported_from: references/prompts/5/5_4_2.yaml -->

**Focus**: Identify and extract quantitative financial metrics and supporting commentary that assess the financial outcomes of strategic turnaround initiatives.
 (rewritten via tool-name-map.json:system_v2_7)

- `get_company_profile`
- `search_keyword_in_source`
- `search_xbrl_facts`

<!-- END port-dimension-prompts methodology + modes -->
