# Qualitative Filtering & Catalyst Methodology

Methodology fused from professional investment frameworks; all text is an original paraphrase.

---

## The Qualitative Process: MOP → KPI → Results

The qualitative process bridges the gap between quantitative screening signals and actionable investment conviction. It operates through a three-stage framework that mirrors how institutional portfolio managers structure their research.

### The Core Framework

**Management Operating Plan (MOP) → Key Performance Indicators (KPIs) → Financial Results**

The MOP is management's stated strategy — what they tell investors they will do. KPIs are the measurable operational metrics that track whether the strategy is working. Results are the financial outcomes that confirm or deny the strategy's effectiveness.

The critical insight: companies do not literally publish a document called "Management Operating Plan." The analyst must **infer** the MOP by identifying KPIs first, then reverse-engineering the strategic plan those KPIs are designed to measure.

The analyst's job is to verify that the MOP→KPI→Results chain is intact and credible. A broken chain — where KPIs don't align with the stated strategy, or results contradict KPI trends — is the highest-quality short signal in fundamental analysis.

### The Three-Stage Evolution (Full Framework)

This qualitative process is preceded by two quantitative stages:

1. **Quant Discovery** (Forward-Looking Valuation): Identification of positive and negative outliers in a sector using forward valuation metrics
2. **Quant Evidence** (Backward-Looking Financial Statements): Do the financial statements support the valuation outlier signal?
3. **Qual Drivers** (Backward and Forward-Looking KPIs and MOP): Identify KPIs → infer MOP → verify against results → identify catalysts

**Key analytical questions to ask continuously:**
- Why is earnings growth or revenue growth so strong (or weak)?
- Why does the market value this company the way it does?
- Does the stock deserve its premium or discount to the sector?
- Will the company continue to beat (or miss) expectations?
- Is this a high-probability outcome?

**Critical distinction**: A good company does not equal a good stock. "Buy and hold forever" is an investor's mindset, not a trader's. For the 20-60 day horizon, catalysts are required.

---

## Stage 1: KPI Identification

### What are KPIs?

Key Performance Indicators are the non-financial and semi-financial metrics that management uses to run the business. They are the operational drivers that **precede** financial results. KPIs are leading indicators; financial statements are lagging confirmations.

### KPI Source Hierarchy

Institutional practice follows a specific source hierarchy for KPI discovery:

1. **Investor Relations Websites** — Presentations, shareholder letters, quarterly and annual reports. IR pages are designed for investors and contain the metrics management wants you to track.
2. **Earnings Call Transcripts** — Management literally tells you what numbers to focus on. CEO/CFO communications are scripted and rehearsed. Retrieve via `search_documents(ticker={T}, form_type="earnings_call_transcript")` → `read_source_pages` (citation prefix `ect<N>`; prepared_remarks pages hold the scripted commentary, qa pages the unscripted answers). The technique: scan the transcript pages, let your eye zoom in on the numbers, pay less attention to narrative flourishes.
3. **Company Presentations** — Roadshow materials, conference presentations. Often contain updates between earnings calls.

### KPI Quality Assessment

KPI quality is assessed on three dimensions:

- **Consistency**: Does management report the same KPIs quarter after quarter? Changing KPIs every quarter is a major red flag — it suggests management has no consistent operational framework, or worse, is cycling through metrics to find flattering ones.
- **Lead vs. Lag**: Are the KPIs leading (predictive of future results) or lagging (confirmatory of past results)? Leading KPIs like order backlog and customer acquisition cost are more valuable for forward-looking analysis than lagging KPIs like revenue.
- **Auditability**: Are the KPIs independently verifiable or purely self-reported? Self-reported non-GAAP metrics require heightened scrutiny. Industry-level data from trade organizations provides cross-validation.

### Sector-Specific KPI Templates

Different business models have fundamentally different operational drivers. The analyst must identify which KPIs matter for the specific business model under analysis.

**SaaS / Subscription:**
- Annual Recurring Revenue (ARR), Monthly Recurring Revenue (MRR)
- Churn rate (monthly and annualized)
- Net Revenue Retention (> 110% indicates strong expansion within existing customers)
- Customer Acquisition Cost (CAC), CAC payback period (target: < 12 months)
- Lifetime Value to CAC ratio (LTV/CAC > 3x is the institutional benchmark)
- Magic Number (net new ARR / prior quarter Sales & Marketing spend)
- Number of customers above $100K ARR threshold

**Retail:**
- Same-store sales (the foundational retail KPI)
- Traffic trends and average ticket size
- Sales per square foot
- Average Unit Retail (AUR) — price per item sold
- Inventory turnover and sell-through rates
- Digital penetration percentage (e-commerce as % of total sales)
- Store count: openings, closures, total square footage (gross and net)
- Number of brands and store nameplate count
- New-to-file customer acquisition

**Manufacturing:**
- Capacity utilization rate
- Order backlog and book-to-bill ratio
- Production volume by facility
- Inventory levels: raw materials, work-in-progress, finished goods
- Supplier concentration and lead times

**Financial Services:**
- Assets Under Management (AUM) and net flows
- Net Interest Margin (NIM) and trajectory
- Loan loss provisions as percentage of loan book
- Efficiency ratio (operating expenses / revenue)
- Regulatory capital ratios

**Healthcare / Biotech:**
- Patient volume and procedure counts
- Clinical trial enrollment progress and milestones
- FDA submission and PDUFA dates
- Patent expiry calendar for branded pharmaceuticals
- Payer mix and reimbursement rate trends

### Building KPI Dashboards

Once KPIs are identified for a company, they form a reusable dashboard. Many KPIs apply across an entire sector (same-store sales, inventory turnover, sales per square foot for all retail). Some are idiosyncratic to a specific company.

The reason a stock is a positive or negative outlier often lies in a particular KPI divergence from sector norms. The quantitative screen identifies the outlier; the KPI analysis explains WHY it is an outlier.

No comprehensive KPI encyclopedia exists for every sector. Over time, KPIs evolve as business models change. The analyst must learn the **process** of discovering KPIs, not memorize a static list.

---

## Stage 2: Management Operating Plan (MOP) Analysis

### What is a Management Operating Plan?

The MOP is the strategic blueprint management communicates to investors. It encompasses: growth strategy, capital allocation priorities, margin targets, market positioning, product roadmap, and operational objectives. It is qualitative by nature but must be evaluated for credibility and consistency.

### MOP Inference Methodology

Since companies do not publish a document called "MOP," the analyst infers it from:
- CEO/CFO scripted remarks on earnings calls
- Investor day presentations and strategic updates
- MD&A section of 10-K/10-Q filings
- Shareholder letters
- Press releases announcing strategic initiatives

The inference process: collect all forward-looking statements from management → identify recurring themes and targets → synthesize into a coherent strategic narrative → test for internal consistency and external credibility.

### MOP Credibility Assessment: Five-Dimension Scorecard

Each dimension scored 0-10. Composite score < 25 = high risk.

1. **Track Record (weight: 30%)**
   - Has management delivered on prior stated plans? Check 3+ years of guidance vs. actuals
   - Pattern of meeting, beating, or missing targets
   - Consistency of narrative over time vs. frequent strategy pivots

2. **Consistency (weight: 20%)**
   - Does the current MOP align with the historical MOP?
   - Strategy pivots increase uncertainty and reduce credibility
   - Exception: a well-explained strategic shift by new management can be positive

3. **Realism (weight: 20%)**
   - Are the targets achievable given industry dynamics, competitive position, and macro environment?
   - Does the revenue growth target imply taking significant market share from established competitors? If yes, what is the mechanism?
   - Margin targets: do they assume unrealistic operating leverage?

4. **Alignment (weight: 15%)**
   - Insider ownership: do key executives hold meaningful stock positions?
   - Compensation structure: are performance hurdles tied to stated KPIs?
   - Insider transaction patterns: buying = alignment, consistent selling = red flag
   - Small insider sales relative to total holdings are normal (financing personal expenses); large systematic selling is not

5. **Disclosure Quality (weight: 15%)**
   - Transparency of communications vs. promotional language
   - Specificity of targets vs. vague aspirations
   - Willingness to discuss challenges vs. only highlighting positives

### MOP Red Flags

- "Transformational M&A" announced without clear integration plan → empire building, not value creation
- Guidance repeatedly missed with vague explanations → management lacks visibility or candor
- Management compensation heavily stock-based with minimal performance hurdles → optimizing for volatility, not long-term value
- CEO/CFO turnover within 18 months of guidance issuance → credibility destroyed
- Strategy pivot without acknowledgment that prior strategy failed → intellectual dishonesty

---

## The Management Team: Alpha/Beta/Delta Framework

Institutional portfolio managers evaluate management depth using a hierarchical framework that goes far beyond reading the executive bios on the company website.

### Alpha: The CEO

The single most important person in the organization. Assessment dimensions:
- **Tenure**: How long in role? New CEOs deserve a 2-4 quarter observation period before judgment
- **Prior public company experience**: Has this person led a public company before? Private company CEOs often struggle with quarterly earnings cadence and disclosure requirements
- **Capital allocation track record**: The CEO's most important long-term function. Look at M&A history, share buyback timing, dividend decisions
- **Communication style**: Candid and specific vs. promotional and vague. The best CEOs explain challenges clearly; the worst pretend challenges don't exist
- **Background**: Founder-CEO (often strong vision, sometimes weak operations) vs. hired-gun CEO (often strong operations, sometimes weak vision)

### Primary Betas: Key Lieutenants

These are the direct reports who execute the CEO's strategy. Typically: CFO, Chief Product Officer, Chief Technology Officer, Chief Architect, Head of Corporate Development, Chief Marketing Officer.

Assessment dimensions:
- Industry background: relevant experience or outsider?
- Tenure: long-serving team = stable execution; revolving door = chaos
- Prior success in role: what did they achieve at their previous company?

### Secondary Betas: Extended Leadership

Chief Customer Officer, Chief People Officer, General Counsel, EVP Revenue Operations, EVP Customer Success. These roles matter less for investment decisions individually but collectively indicate management depth.

### Red Flags in Management
- **Cluster departures** within 6 months — multiple key people leaving simultaneously signals internal crisis
- **"Personal reasons"** without succession plan — the vaguest and most concerning departure reason
- **CFO departure** within 18 months of guidance — accounting concerns
- **Insider selling cluster** — multiple executives selling simultaneously

### Compensation Alignment Check
- Are performance hurdles tied to stated KPIs, or are they generic (total shareholder return)?
- Do clawback provisions exist?
- Is insider ownership meaningful (> 1% of shares outstanding for CEO)?
- Is insider ownership growing (buying) or shrinking (selling)?

**Important nuance**: Internal transfers of stock (non-open market dispositions) are often transfers to new key hires or employee compensation pools — this is reassuring, not bearish. Open market sales require more scrutiny but small amounts relative to total holdings are normal.

---

## The Board of Directors: Governance Quality Assessment

The Board's four statutory tasks: (1) Establish vision, mission, and values; (2) Set strategy and structure; (3) Delegate to management; (4) Exercise accountability to shareholders. The analyst assesses whether the board actually performs these functions or is a rubber stamp for management.

### Board Quality Checklist

**Independence (minimum threshold):**
- ≥ 75% independent directors
- Independent lead director or chair (separation of CEO and Chairman roles)
- Audit, Compensation, and Nominating committees fully independent

**Expertise:**
- At least one director with deep industry experience
- At least one financial expert on audit committee (CPA, CFO experience, or investment background)
- Directors with prior public company board experience
- Diversity of background (functional, industry, demographic)

**The "Political Incest" Check:**
- How many current or former management members sit on the board?
- How many interlocking directorships exist (director A sits on director B's company board, and vice versa)?
- High overlap between management and board = governance risk. The board exists to oversee management, not to be management's social club.

### Board Red Flags
- Classified (staggered) board → management insulated from proxy contests
- Supermajority voting requirements for charter changes → entrenches management
- Director tenure > 15 years → loss of independence and fresh perspective
- CEO also serving as Chairman → concentration of power
- Related-party transactions disclosed in proxy → potential self-dealing
- Interlocking directorships among board members → compromised independence

### What the Board Is Not
The board does not manage the company. It hires, evaluates, and if necessary fires the CEO. It approves strategy but does not create it. A board that micromanages is as dysfunctional as a board that rubber-stamps. Look for the board's track record: have they made timely CEO changes? Have they rejected value-destructive acquisitions? Have they aligned compensation with performance?

---

## Stage 3: Industry Analysis & Competitive Position

### Beyond Porter's Five Forces: The Institutional Approach

University textbooks present Porter's Five Forces and SWOT analysis as analytical frameworks to be filled out systematically. Institutional practice is more nuanced: these are **thinking prompts**, not rigid analytical boxes.

The institutional approach asks different questions:
- What are the 3-5 factors that truly determine competitive outcomes in this industry?
- Where is the power concentrated: with suppliers, customers, or the companies themselves?
- What would need to happen for the industry structure to change?
- Who benefits and who loses from the current structure?

### Verifying Management's Competitive Claims

**Do not trust management pronouncements on competition.** Every management team claims competitive advantages. The institutional approach triangulates:
1. Read competitor 10-Ks — how do they describe the competitive landscape? Does it match?
2. Industry trade organizations and trade journals — unfiltered data from neutral sources
3. Customer and supplier disclosures — who has pricing power?
4. Market share data over 3-5 years — is the company gaining or losing?

If competitor filings describe fundamentally different competitive dynamics than management's narrative, that is a significant red flag — management is either unaware of competitive reality (incompetence) or deliberately misrepresenting it (dishonesty). Either way, avoid the stock.

### Demographic Demand Analysis

For industries with demographic-driven demand (healthcare, senior living, education, housing), the institutional approach models demand drivers quantitatively:
- Population cohort sizes by age group
- Penetration rates and capacity utilization
- Supply/demand balance at granular geographic level
- Regulatory and reimbursement trends

Example methodology for senior living: Total addressable population (75+ age cohort) × penetration rate × capacity utilization → demand forecast. Compare to supply pipeline (new construction starts, certificate of need approvals) → supply/demand imbalance → pricing power assessment.

---

## Stage 3b: Consensus Reconstruction and the Variant View

Qualitative work establishes what the business will do. It becomes a *position* only when
compared against what the market already expects. The gap between the two — the **earnings
disconnect** — is the tradeable object. An assessment that a business is well run is not an
idea; an assessment that it is better run than the market has priced is.

Sequence matters: complete the KPI, MOP, and industry work **first**, then reconstruct
consensus. Reading consensus early anchors the analysis to the very expectation the work is
supposed to test independently.

### Published Consensus Is Not the Real Bar

The consensus figure on a data terminal is a simple arithmetic average of sell-side analyst
estimates. Two properties make it a poor proxy for the market's actual expectation:

1. **It is stale.** Analysts revise after evidence accumulates, not before.
2. **Buy-side consensus moves ahead of sell-side consensus.** Capital repositions first;
   published estimates follow.

This is the mechanism behind the familiar and expensive pattern where a company beats the
published estimate and the stock falls: the effective bar held by the marginal buyer was
higher than the printed one. Underwriting against the published average while real
positioning has already shifted is not a conservative assumption — it is a wrong one.

### Triangulation Procedure

There is no clean data source for the buy-side expectation. It is assembled:

1. Establish the published sell-side average and, separately, the **dispersion** of estimates
2. Weight the most recent revisions and their direction far more heavily than the average
3. Compare notes with others holding the position
4. Deliberately seek the view of those on the other side of the trade — the strongest
   available test of a thesis is a well-argued opposing case
5. Combine into a best-estimate **range with a direction**, never a point estimate

Interpretation rules:

- **Wide dispersion** means no consensus exists. The disconnect framing does not apply;
  the opportunity is in resolving uncertainty, not in being contrarian.
- **Tight dispersion with stale revisions** is the highest-value configuration: an apparently
  settled expectation that the qualitative evidence contradicts.
- **Tight dispersion with rapid recent revisions** means the gap is already closing. Verify
  the idea is not simply late.

Where the buy-side expectation cannot be triangulated, record the disconnect as
**unquantified** and flag it as a coverage gap. Do not silently substitute the published
figure — that converts an unknown into a false precision.

### Stating the Variant View

Express the output in one structured sentence, with all four elements present:

> The market expects **[consensus, numerically]**. The evidence indicates
> **[variant view, numerically]**, because **[one or two specific KPI/MOP findings]**.
> The gap closes when **[catalyst]** occurs by **[date]**.

Failure modes to reject at review:

- A description of the company with no statement of what the market has wrong
- A variant view asserted without a numerical consensus to differ from
- A directional opinion with no catalyst — an investment, not a trade (see the hard gate below)
- A "variant" view that restates consensus in different words

---

## Stage 4: Catalyst Identification

### What Is a Catalyst?

A catalyst is a specific, identifiable event that is likely to cause a stock to reprice. It is the "timing" component of the trade idea formula. Without a catalyst, even a fundamentally correct thesis may not generate returns within the 20-60 day trading window.

The three types of catalysts:
1. **Operational**: Events that move KPIs, revenue, earnings, or forward valuation
2. **Technical**: Events related to capital structure, index changes, or short positioning
3. **Market/Economy**: Macro events outside company control

### Complete Catalyst Taxonomy

| Category | Examples | Typical Lead Time | Outcome Type |
|----------|---------|:---:|:---:|
| **Earnings** | Quarterly report, guidance update, pre-announcement | Scheduled | Spectrum (range of beat/miss magnitudes) |
| **Corporate Action** | M&A announcement, divestiture, spin-off, buyback authorization | Days-Weeks | Binary (deal happens or doesn't) |
| **Regulatory** | FDA decision, antitrust ruling, license approval | Weeks-Months | Binary |
| **Management Change** | CEO/CFO departure or appointment, activist 13-D filing, board refresh | Days-Weeks | Spectrum |
| **Industry Event** | Competitor earnings read-through, sector re-rating, commodity price shift | Variable | Spectrum |
| **Macro Event** | Central bank rate decision, election, trade policy announcement | Scheduled | Spectrum |

### Catalyst Quality Assessment (Four Dimensions)

1. **Specificity**: Can you put a date on it, or at least a narrow window? "Eventually the market will recognize the value" is NOT a catalyst — it is wishful thinking. A catalyst must be specific enough to create a timeline.

2. **Magnitude**: What is the expected price impact?
   - ≥ 15% expected impact: high conviction catalyst
   - 5-15%: standard trade catalyst
   - < 5%: the catalyst is unlikely to generate sufficient return to justify the risk

3. **Probability**: Based on historical frequency and current conditions, what is the likelihood the catalyst occurs as expected?
   - Earnings beat patterns: if management has beaten 10 of last 12 quarters, a continued beat has high probability
   - FDA approval: use historical approval rates by phase and therapeutic area
   - M&A completion: regulatory risk, financing risk, shareholder vote risk

4. **Binary vs. Spectrum**: The outcome distribution determines position sizing.
   - **Binary catalysts** (FDA yes/no, deal close/fail): discontinuous outcomes demand smaller position sizes
   - **Spectrum catalysts** (earnings beat/miss magnitude, multiple re-rating): continuous outcomes can support standard sizing

### The 20-60 Day Catalyst Constraint

For a trade idea to be actionable, at least one catalyst must be identifiable within the 20-60 day window. If the nearest catalyst is 90+ days away, the idea belongs on a watchlist, not in the active pipeline.

**Catalyst stacking** (multiple catalysts within the window) increases conviction. A stock with an earnings report, an industry conference, and a potential product announcement all within 60 days is catalyst-rich.

**The tumbleweed test**: Count the company's non-earnings press releases over the last 12 months. If the company averages fewer than one non-earnings press release per month between quarterly reports, it is a "tumbleweed stock" — the vast empty space between earnings creates no opportunities for expectation shifts. Avoid tumbleweed stocks entirely.

Companies that communicate actively between earnings — through product announcements, investor conference presentations, business updates, and industry event participation — provide the catalyst frequency that active trading requires.

### The Hard Gate: Trade Idea vs. Investment Idea

The institutional distinction:
- **Trade Idea**: Has a specific, dateable catalyst within 20-60 days. Presenting a trade idea means answering: "When does the stock move? When do I get paid?"
- **Investment Idea**: May be fundamentally correct but lacks near-term catalysts. Presenting an investment idea as a trade idea is a professional error.

If you cannot identify a catalyst within the trading window, you have found an investment, not a trade. Be intellectually honest with yourself about the distinction.

### The Gray Area: 60-120 Days

The 20-60 day horizon is a guide, not an exact science. Trades sometimes hit targets within 20 days; other times they drift past 60. The "gray area between 60 and 120 days" requires particular honesty — every day that passes without the catalyst materializing, the thesis transitions from trade to investment. Set a hard review date at 60 days and either the catalyst is in sight or the position is closed.

---

## Qualitative Evidence Triangulation

### The Mosaic Theory Approach

Conviction in qualitative analysis comes not from any single data source, but from the **convergence of multiple independent sources** all pointing to the same conclusion. The mosaic theory of investing holds that material non-public information is illegal to trade on, but the **synthesis** of disparate public information creates a legitimate analytical edge.

**Triangulation examples:**
- **Competitive position**: Management narrative (earnings calls) + competitor filings (10-K competition sections) + industry trade data + market share trends → triangulated conviction on competitive reality
- **Demand trajectory**: Company KPIs + supplier commentary + customer behavior data + macroeconomic indicators → triangulated conviction on demand trend
- **Execution quality**: MOP targets + KPI trends + financial results + management departures/arrivals → triangulated conviction on execution capability

When all independent data sources converge on the same conclusion, conviction is high. When they diverge, the divergence itself is the signal — something is being misrepresented, and the analyst must determine by whom and why.

### The "Explain It to a 10-Year-Old" Test

If you cannot describe what the company does in 1-2 sentences that a 10-year-old would understand, you do not understand the business well enough to trade it. This is not a simplification exercise — it is a comprehension test. Professional analysts use this test before committing capital.

Example: "This company runs retirement homes. Old people pay them monthly rent for a room, meals, and help with daily activities. As more Americans turn 75, more people need their services."

If the analyst cannot produce something this clear, the business is either too complex to analyze (conglomerates, multi-line financials) or the analyst has not done enough work.

### The "Three to Five Factors" Rule

Professional portfolio managers identify 3-5 factors that truly drive the investment outcome. Analyzing more than five things means the analyst is spread too thin and has failed to prioritize.

The process:
1. List everything that could affect the stock
2. Rank by potential impact on the thesis
3. Select the top 3-5
4. Focus ALL analytical energy on these factors
5. Monitor the rest for changes that would elevate their importance

## Qualitative Red Flag Catalog

The following patterns, identified through institutional trading experience, indicate elevated risk of management dishonesty, business deterioration, or governance failure. The presence of 3+ red flags from this catalog is a hard stop for long candidates and a potential short signal.

### Earnings Quality Red Flags
1. "Non-recurring" charges appearing in 3+ of the last 4 quarters → they are recurring by definition; management is masking structural cost issues
2. SBC exceeding 10% of revenue → significant dilution being excluded from non-GAAP earnings
3. Consistent GAAP losses with non-GAAP profits → the adjustments are hiding real economic costs
4. Frequent changes to non-GAAP definitions → management moves the goalposts to maintain the appearance of profitability
5. Aggressive revenue recognition policies (bill-and-hold, channel stuffing indicators: DSO rising + inventory building simultaneously)

### Governance Red Flags
6. Board dominated by management insiders → the board cannot oversee what it is part of
7. Classified board combined with supermajority voting → management is insulated from shareholder accountability
8. Director tenure exceeding 15 years → entrenchment and loss of independence
9. CEO also serving as Chairman → concentration of power without checks
10. Related-party transactions disclosed in proxy statements → potential self-dealing

### Management Credibility Red Flags
11. Changing KPIs every quarter → management lacks a consistent operational framework
12. "Transformational M&A" announced without a clear integration plan → empire building
13. Repeated guidance misses with vague explanations → management lacks visibility or candor
14. CEO/CFO departure within 18 months of significant guidance → the guidance was not credible
15. Compensation heavily stock-based with minimal performance hurdles → optimizing for volatility, not value creation

### Disclosure Red Flags
16. Auditor changes without clear explanation → accounting disagreement risk
17. Late filings or material weakness disclosures → internal control failure
18. Trade organization data contradicts management narrative → someone is misrepresenting reality
19. Competitor filings describe fundamentally different competitive dynamics → management is gaslighting investors
20. Segment reporting changes that reduce transparency → management is hiding deteriorating business units

---

## MCP Integration

When qualitative analysis identifies patterns, query the knowledge base for validation:

```
search_investment_strategies(domain=fundamental, kind=qualitative)
  → validate MOP assessment methodology against known frameworks

search_investment_cases(domain=catalyst_driven, sectors_focus=[derived])
  → find historical cases where similar catalysts played out

search_by_analogue(event_type=[catalyst type], company_situation=[derived])
  → cross-strategy discovery: what other situations produced similar catalyst patterns?

search_investment_strategies(domain=fundamental, sectors_focus=[derived])
  → sector-specific KPI frameworks and qualitative assessment methodologies
```

Matched strategies provide: qualitative assessment methodology validation, sector-specific KPI templates, known management red flag patterns.
Matched cases provide: historical examples of management turnaround successes/failures, catalyst-driven price moves with magnitude data, governance failure case studies.
