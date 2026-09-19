# business-model — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: business-model-classification (1_1 — anchor)

**Display name**: Business Model & Offerings Classification

<!-- ported_from: references/prompts/1/1_1.md -->

**Objective**: Determine business-model type (product / service / platform), core offering, and market positioning (low-end / mid-tier / high-end) using the most recent 10-K (annual) and trailing 10-Q/20-F disclosures, supplemented by web search only where XBRL/filing data is insufficient.

**Output structure**:

- **Business Model**: [Product / Service / Platform]
- **Core Offering**: [e.g., Connected Wearable, Diagnostic Consumables, SaaS Subscription, Drug Pipeline, Cloud Platform]
- **Positioning**: [Low-end / Mid-tier / High-end] + brief rationale (e.g., "High-end based on >70% gross margin and premium ARPU vs. peers")
- **Citation density**: ≥1 citation per 200 words, format `{ticker} {citation_id} page<N>`.

### Mode: distribution-channel-analysis (1_2)

**Display name**: Distribution Channels & Go-to-Market Analysis

<!-- ported_from: references/prompts/1/1_2.md -->

**Objective**: Assess primary distribution model (direct sales / channel partners / hybrid), channel mix evolution (3-year trailing), and strategic implications for pricing power and customer intimacy.

**Output structure**:

- **Distribution Model**: [Direct Sales / Channel Partners / Hybrid]
- **Distribution Partners**: [list disclosed channel types and representative partners]
- **Current Channel Mix**: Direct : Indirect = 1 : XX (latest available data)
- **Historical Channel Mix Trend (Trailing 3 Years)**:
 - Year -2: [Direct : Indirect = 1 : XX]
 - Year -1: [Direct : Indirect = 1 : XX]
 - Current: [Direct : Indirect = 1 : XX]
- **Strategic Implication**: e.g., "Shift toward direct sales has enhanced pricing control and customer intimacy but increased SG&A".

### Mode: revenue-composition-and-concentration (1_3)

**Display name**: Revenue Composition & Concentration Risk Analysis

<!-- ported_from: references/prompts/1/1_3.md -->

**Objective**: Decompose revenue by product line / customer type / geography / end market, identify concentration risk (any single product or client >20% of total revenue), and trace temporal mix evolution.

**Output structure**:

- **Latest annual + trailing-quarter revenue breakdown (XBRL segment data)**:
 - By Product Line: top 3 contributors with %
 - By User Type (B2B vs. B2C): mix with %
 - By Geography (NA / EMEA / APAC): top 3 regions with %
 - By End Market: top 3 markets with %
- **Concentration Risk Matrix**: any product/client >20% flagged.
- **Temporal Comparison**: vs. prior quarter and YoY same-period.

### Mode: market-sizing-and-relative-growth (1_4)

**Display name**: Market Sizing (TAM/SAM/SOM) & Relative Growth

<!-- ported_from: references/prompts/1/1_4.md -->

**Objective**: Quantify TAM, SAM, SOM for key verticals, project 3-5 year CAGR, assess relative growth (company vs. addressable market) and historical SOM evolution.

**Output structure**:

- **Market Sizing & Growth**:
 - TAM (Current Year): USD XXX bn
 - SAM (Current Year): USD XXX bn
 - SOM (Current Year): XX%
 - TAM CAGR (Past 3 Years): XX%
 - TAM CAGR (Forward 3-5 Years): XX%
- **Relative Growth Table**: Company Revenue Growth vs. TAM CAGR for past 3Y and next 3Y.
- **Historical SOM Trajectory**: 3-year evolution with execution-strength assessment.

### Mode: management-and-leadership (1_5)

**Display name**: Management Team & Leadership Analysis

<!-- ported_from: references/prompts/1/1_5.md -->

**Objective**: Assess executive team backgrounds, track records, and recent leadership changes (CEO/CFO/COO/CMO) for strategic-execution implications.

**Output structure**:

- **Key Executives & Track Record**: [Name, Role, Tenure, Notable Prior Experience, Industry Expertise, Capital Allocation Record]
- **Recent Management Changes (Trailing 1-2 Quarters)**: [Name, Role, Effective Date, Reason, Successor Background]
- **Strategic Implications of Changes**: e.g., "New CFO brings strong M&A background, suggesting a shift toward inorganic growth".
