# LBO & M&A Modeling -- Institutional Methodology

## Protocol

### LBO Modeling Sequence
1. **Transaction Assumptions**: Establish entry EBITDA, entry multiple, offer price per share, diluted shares outstanding, and premium. Determine tax structure (stock sale vs. asset sale/338(h)(10) election) and accounting treatment.
2. **Sources & Uses**: Build the capital stack. Uses = buyout of equity + refinancing of oldco debt + transaction fees (2.0% of offer value) + financing fees. Sources = debt tranches + excess balance sheet cash + sponsor equity + management rollover. Total sources must equal total uses within 0.1%.
3. **Purchase Price Allocation**: Write up assets to fair market value (FMV). PP&E typically marked up 20% over book, intangible assets up to 150%. Calculate goodwill as purchase price minus FMV of net assets. Record deferred tax liabilities (DTLs) on the write-up spread.
4. **Income Statement Forecast**: Project revenue growth, margins (gross, R&D, SG&A), depreciation (including incremental from write-ups), amortization, stock-based compensation, and interest expense. Tax rate held constant through projection period.
5. **Cash Flow Statement**: Net income + D&A + SBC + changes in working capital + PIK interest addback = cash from operations. Subtract capex and capitalized software development costs. Result is pre-revolver free cash flow.
6. **Debt Schedule (Waterfall)**: Apply mandatory amortization first, then cash sweeps in strict priority: Term Loan A -> Term Loan B -> Senior Notes -> Subordinated Notes -> Preferred Stock. Revolver draws or pays down based on cash available relative to minimum cash balance.
7. **Pro Forma Balance Sheet**: Roll forward assets and liabilities. Equity roll-forward: BOP equity + net income - dividends + SBC - financing fee amortization = EOP equity. Balance check must equal zero.
8. **Returns Analysis**: Enterprise value at exit (exit EBITDA x exit multiple) minus net debt = equity value. Apply ownership percentages. Calculate IRR via =IRR(cash flows) and cash-on-cash multiple (MoIC) as exit equity / initial equity.
9. **Sensitivity Analysis**: Two-way table varying entry multiple (rows) x exit multiple (columns) producing IRR/MoIC matrix.

### M&A Modeling Sequence
1. **Deal Assumptions**: Establish offer price, premium, consideration mix (% stock / % cash), tax structure, and financing terms.
2. **Sources & Uses**: Sources = new borrowing (80% of cash consideration via debt, 20% via excess cash) + stock issued + cash for fees. Uses = cash to target + stock to target + target debt refinanced + deal fees + financing fees.
3. **Purchase Price Allocation**: Write up PP&E and intangible assets to FMV; write off target's existing goodwill and deferred tax assets; create new DTLs on write-ups; calculate resulting goodwill. Post-deal incremental D&A flows into the accretion/dilution analysis.
4. **Pro Forma Balance Sheet**: Combine acquirer and target standalone balance sheets, apply transaction adjustments (debt issuance, cash usage, equity issuance, asset step-ups, DTL creation, goodwill).
5. **Accretion/Dilution Analysis**: Pro forma net income = acquirer NI + target NI +/- after-tax transaction adjustments (interest on new debt, interest income forgone, synergies, incremental D&A, financing fee amortization, tax effect). Pro forma EPS = pro forma NI / pro forma shares outstanding. A/D = pro forma EPS - acquirer standalone EPS.
6. **Contribution Analysis**: Compute each party's percentage of combined revenue, EBITDA, net income, and enterprise value. Derive implied target valuation: implied target EV = acquirer EV / acquirer contribution % - acquirer EV. Bridge to equity value and per-share price.
7. **Sensitivity Analysis**: Two-way table varying offer price x % stock consideration yielding A/D per share.

## Key Formulas

### LBO
- **Enterprise Value**: EV = Equity Value + Debt - Cash = (Offer price x Diluted shares) + Oldco debt - Excess cash
- **Entry Multiple**: EV / LTM EBITDA
- **Goodwill**: Purchase price - FMV of net identifiable assets. Where FMV = Book value of equity + PP&E write-up + Intangible write-up - DTLs created.
- **DTLs Created**: Total asset write-ups x tax rate (for stock sales where book basis steps up but tax basis does not)
- **Incremental D&A**: Write-up amount / useful life. PP&E typically 10-20 years; intangible assets 15 years.
- **After-tax Cost of Debt**: Nominal rate x (1 - tax rate). At 25% tax rate, 5% nominal = 3.75% effective.
- **Mandatory Amortization**: Term Loan A: 10% of original principal in year 1, 5% thereafter. Term Loan B: 5% annually. Senior Notes: 0% (bullet). Sub Notes: 0% (PIK option).
- **Cash Sweep**: Excess cash flow after mandatory amortization applied at 100% to next tranche in waterfall.
- **PIK Interest**: PIK rate (typically 4-9%) x beginning balance. Added to principal; no cash outflow.
- **Revolver Availability**: Minimum of (80% x AR + 65% x Other Assets) and commitment size.
- **Sponsor IRR**: =IRR(initial equity outflow, interim dividends, terminal equity value). Target: 20%+ gross, 38-48% in base-through-upside cases.
- **MoIC (Cash-on-Cash)**: Terminal equity value / initial equity investment. 5.0-7.0x at institutional target.
- **Equity Roll-Forward**: Equity EOP = Equity BOP + Net Income - Dividends + SBC - Financing Fee Amortization

### M&A
- **Exchange Ratio**: Offer price per share / Acquirer share price
- **Nominal Exchange Ratio**: Offer price / Acquirer share price
- **Actual Exchange Ratio**: % Stock consideration x (Offer price / Acquirer share price)
- **Acquirer Shares Issued**: Exchange ratio x Target diluted shares outstanding x % stock consideration
- **Pro Forma Net Income**: Acquirer NI + Target NI - Interest on new debt (after-tax) - Interest income forgone (after-tax) + Synergies (after-tax) - Incremental D&A (after-tax) - Financing fee amortization (after-tax)
- **Pro Forma EPS**: Pro forma NI / Pro forma diluted shares
- **A/D per Share**: Pro forma EPS - Acquirer standalone EPS
- **A/D %**: (Pro forma EPS / Acquirer standalone EPS) - 1
- **Breakeven Synergy**: (|Dilution per share| x Pro forma shares) / (1 - tax rate)
- **Implied Target EV (Contribution)**: Acquirer EV / Acquirer contribution % - Acquirer EV
- **Implied Target Share Price**: (Implied Target EV - Target net debt) / Target diluted shares

## Practitioner Standards

### Capital Structure Norms
- Modern LBO equity contribution: 38-42% (vs. 20% in 1980s). Debt/EBITDA: ~6x at entry. Debt as % of EV: ~40%.
- Management rollover: 2-5% of total equity. Management option pool: 3-20% of total equity.
- Financing fees: Revolver 1.0% of commitment, Term Loans 1.5% of principal, Senior Notes 1.0% of principal. Capitalized and amortized straight-line over instrument term. Post-2015 rules require straight-line amortization of all financing fees.
- Revolver: Priced at LIBOR + 400bps with 1.0% LIBOR floor. Maximum availability calculated via borrowing base (80% of AR + 65% of Other Assets).
- Senior secured (Term Loans): Floating rate, secured (1st/2nd lien), shorter maturity, covenant-heavy, no SEC registration.
- Senior unsecured (Notes): Fixed coupon (~8.125%), bullet maturity, covenant-lite.
- Subordinated/Mezzanine: PIK toggle feature (4-9% PIK rate, 8% cash rate), equity kickers (warrants).

### IRR Targets
- Sponsor gross IRR target: 20%+ (institutional minimum), 38-48% in base-through-upside cases at 7.3-9.3x exit multiples.
- MoIC target: 5.0-7.0x over a 5-year hold period.
- Senior debt IRR: 4.5-5.1% (TLA/TLB), reflecting near-risk-free returns.
- Subordinated/Mezzanine IRR: 8-17% depending on equity kicker participation.
- Preferred stock IRR: 18-20%.
- Management equity IRR: 38-48% (aligned with sponsor, levered by option pool).

### Valuation Conventions
- Entry and exit multiples typically assumed equal in base case (no multiple expansion assumed).
- Exit assumed at year 5 post-close.
- Minimum cash balance: 180 (or roughly 2% of revenue) maintained throughout projection.
- Interest rate on cash: ~0.52% in low-rate environment.
- DCF can supplement LBO analysis to cross-check implied valuation.

### Tax and Accounting
- **Stock sale**: Book basis stepped up to FMV (creates DTL on write-up spread); tax basis unchanged. Goodwill not tax-deductible. DTL amortized over asset lives as book/tax depreciation difference reverses.
- **Asset sale / 338(h)(10)**: Both book AND tax basis stepped up to FMV. No DTL created. Goodwill IS tax-deductible, amortized over 15 years under IRC Section 197. Generates significant future tax savings.
- **DTL Rule of Thumb**: DTL = sum of asset write-ups x applicable tax rate. Annual DTL reversal = incremental book depreciation - incremental tax depreciation.
- **Pre-deal DTA/DTL**: Existing target DTAs are written off in PPA. Existing target DTLs may be retained or restated.
- **Permanent differences**: Land write-ups and goodwill in stock sales create no deferred taxes (no depreciation/amortization to reverse the difference).
- GAAP tax rate used for book purposes; statutory tax rate used for cash tax calculations. Common practice: assume pre-deal book basis equals tax basis when actual tax basis is unknown.

### Accretion/Dilution Drivers
- Stock deals: accretive when high P/E acquirer buys low P/E target (and vice versa). Core mechanic: the incremental earnings acquired must exceed the earnings-per-share dilution from new shares issued.
- Cash deals: generally more accretive (no share dilution), but interest expense on acquisition debt and forgone interest income partially offset.
- One-time charges are excluded from both cash and GAAP EPS in A/D analysis.
- Calendarization is required when acquirer and target have different fiscal year ends; align to acquirer's FYE.

## Data Integration

- **XBRL fact retrieval**: All historical financial statement data sourced via `search_xbrl_facts`. Use `list_xbrl_concepts` before querying unfamiliar concepts.
- **Fiscal calendar alignment**: Call `get_company_fiscal_calendar` before any period-specific retrieval.
- **Consensus estimates**: Forward EPS, revenue, and EBITDA sourced from `search_earnings_calendar` or FactSet-equivalent provider for projection inputs.
- **Debt and cash**: Gross debt and cash balances from latest SEC filing (10-K/10-Q) via `search_xbrl_facts` or `get_statement`.
- **Share count**: Diluted shares outstanding from the latest filing; treasury stock method applied to in-the-money options.
- **Transaction comps**: Precedent transaction data for entry/exit multiple calibration from `search_documents` (fairness opinions, merger proxies).
- **Credit statistics**: Target debt ratings (Moody's, S&P) from offering memoranda and credit rating reports accessible via `search_documents`.

## Output Structure

1. **Transaction Summary**: Entry EBITDA, offer price/share, premium, diluted shares, enterprise value, entry multiple
2. **Sources & Uses Table**: Each debt tranche with EBITDA turns and dollar amount; fees detail with % and annual amortization
3. **Purchase Price Allocation**: Book value, write-ups by asset class, DTLs created, FMV, goodwill
4. **Income Statement Projection**: 5-year forecast with revenue through net income, including incremental D&A from write-ups
5. **Cash Flow & Debt Paydown**: Operating CF -> investing CF -> pre-revolver FCF -> mandatory amortization -> cash sweep -> net change in cash
6. **Debt Schedule**: Opening balance, mandatory paydown, cash sweep, PIK accrual, closing balance for each tranche per period
7. **Pro Forma Balance Sheet**: Annual snapshots with equity roll-forward reconciliation
8. **Returns Waterfall**: Exit EV -> net debt -> equity value -> sponsor share -> IRR and MoIC at multiple exit scenarios
9. **Sensitivity Tables**: Entry multiple x Exit multiple -> IRR/MoIC matrix; Offer price x % Stock -> A/D matrix
10. **Contribution Analysis** (M&A): % contribution by metric, implied target EV, implied share price vs. offer price

## Purchase Price Allocation Supplement

### Protocol

#### PPA Mechanics Under ASC 805
The acquisition method prescribed by ASC 805 (Business Combinations) requires the acquirer to recognize and measure identifiable assets acquired, liabilities assumed, and any noncontrolling interest in the acquiree at their acquisition-date fair values. The mechanical process follows a strict sequence:

1. **Eliminate pre-existing goodwill**: The target's legacy goodwill from prior acquisitions is written off against equity before any fair value adjustments are applied. This ensures no legacy intangible overhang contaminates the post-acquisition balance sheet.

2. **Adjust to fair value**: Each asset and liability is measured against the fair value hierarchy (ASC 820): Level 1 inputs (quoted prices in active markets for identical assets), Level 2 inputs (observable inputs other than quoted prices), and Level 3 inputs (unobservable inputs requiring significant judgment). Tangible assets written up typically include PP&E (real property, personal property such as machinery and equipment) and inventory (raw materials, work-in-process, finished goods). Intangible assets requiring fair value recognition fall into four categories: technology-based (developed technology amortized over useful life; in-process R&D carried as indefinite-lived until completion, then reclassified and amortized), customer-based (contracts and relationships where regular customer contact exists), contract-based (licenses, royalties, franchise agreements, non-competition agreements), and artistic-based (works of art, literature, copyrights). Deferred revenue liabilities are typically written down to the cost-to-fulfill obligation, not face value.

3. **Calculate goodwill**: New goodwill is the residual after allocating purchase consideration to the fair value of net identifiable assets. The fundamental PPA equation: Total Consideration (cash + stock + debt assumed + contingent consideration + other) = Net Working Capital + Tangible Assets (FMV) + Intangible Assets (FMV) + Residual Goodwill. Transaction costs are excluded from total purchase consideration.

#### Deferred Tax Liability Creation
When assets are stepped up to fair value for book purposes but tax basis remains unchanged (typical in stock acquisitions), a deferred tax liability is created on the full step-up spread: DTL = SUM(asset write-ups - liability write-downs) x applicable tax rate. The DTL reverses over the useful life of the underlying assets as the incremental book depreciation/amortization exceeds tax depreciation, creating a future tax obligation. Land write-ups do not create DTLs because land is not depreciated; goodwill in a stock acquisition similarly creates no DTL because it is not amortized for tax purposes.

#### Step-Up Depreciation Impact
Write-ups to PP&E increase future depreciation expense, directly reducing post-acquisition EBIT and net income. Write-ups to finite-lived intangible assets increase amortization expense. Inventory step-up to fair value (typically finished goods at selling price less costs to sell, work-in-process and raw materials at replacement cost) increases cost of goods sold in the first post-acquisition period as the stepped-up inventory is sold through. These incremental non-cash charges create a structural earnings headwind that persists until the written-up assets are fully depreciated or amortized. Land is explicitly excluded from depreciation due to its assumed unlimited useful life.

#### Bargain Purchase Gain
When the fair value of net identifiable assets acquired exceeds total purchase consideration, negative goodwill results and is recognized as a bargain purchase gain. Under ASC 805, the acquirer must first reassess whether all assets acquired and liabilities assumed have been correctly identified and measured before recognizing any gain. Once validated, the gain is recorded as an immediate credit to the income statement (taxable) in the period of acquisition. For tax reporting purposes, however, no goodwill is recognized; instead, the fair values of acquired assets are sequentially reduced to fit within the total purchase consideration, eliminating the gain at the tax level.

#### Contingent Consideration
Contingent consideration (earn-outs, milestone payments, royalty arrangements) represents an obligation of the acquirer to transfer additional assets or equity to the seller if specified future events occur. Under ASC 805, contingent consideration must be fair valued at the acquisition date and recorded as a liability on the acquirer's books. Valuation employs scenario-based probability-weighted expected payment modeling, discounted at risk-adjusted rates appropriate to the contingent outcome. Subsequently, the liability is remeasured to fair value at each reporting date (quarterly), with changes flowing through earnings. This creates ongoing P&L volatility until the contingency period expires or the liability is settled.

### Practitioner Standards

#### Intangible Asset Valuation Methodology
Identifiable intangible assets are valued using income-approach DCF variants applied to each asset individually. Two primary methods are employed: the bifurcation method (separating cash flows attributable to existing assets vs. assets to be created in the future) and the relief-from-royalty method (measuring cost savings from owning rather than licensing an asset, applied to trademarks, trade names, and patented technologies). Cash flows are projected over each asset's expected economic life only; no terminal value is assumed. The cost approach (replacement or reconstruction cost) is reserved for cases where reliable cash flow projections cannot be established.

#### Allocation Benchmarks by Industry
Pre-deal accretion/dilution models apply industry-allocation percentages as proxies before formal appraisals are conducted. Across all industries (median): intangible assets represent 31% of purchase consideration, goodwill represents 35%. Technology sector: 33% intangibles / 55% goodwill (median). Healthcare: 43% intangibles / 36% goodwill. Financial institutions: 2% intangibles / 5% goodwill (median). Total purchase consideration allocated to intangibles plus goodwill across all industries: approximately 69% (median).

#### PPA Timing and Earnings Management Risk
Public companies must disclose PPA in the first 10-Q or 10-K following the acquisition date. Acquirers retain the right to adjust allocations for up to 12 months post-close, retroactively. This measurement-period window creates opportunities for earnings management: understating inventory values boosts subsequent gross margins when inventory is sold; understating receivables boosts income upon collection; understating PP&E and intangible assets reduces future D&A charges, mechanically lifting operating income. Audit scrutiny focuses on the reasonableness of fair value assignments due to these conflicting motivations.

#### Conflicting Stakeholder Incentives
Buyers seek to minimize future depreciation and amortization by allocating as much purchase consideration as possible to non-amortizable assets (goodwill, land, indefinite-lived intangibles) or assets with long useful lives. Auditors are required to ensure the reasonableness of fair value assignments under PCAOB standards. Valuation assumptions are inherently hypothetical and subjective; multiple stakeholders may advocate for assumptions that produce desired allocation outcomes, requiring the analyst to independently assess the credibility of disclosed allocations.

## Asset vs Stock Sale Supplement

### Tax Basis Step-Up Architecture
The structural distinction in M&A is whether the acquirer purchases stock or assets. An asset acquisition provides an inside basis step-up: assets revalue to fair market value, with the Aggregate Deemed Sale Price (ADSP = stock purchase price + target liabilities assumed) establishing total allocable basis. Gain equals ADSP minus the inside basis of total assets. A stock acquisition yields only carryover basis -- tax books remain at historical cost, with the purchase premium captured solely in an outside basis step-up in the acquired stock. The step-up's economic value is quantified as the PV of future tax savings: total write-up allocated across depreciable/amortizable classes, annual incremental D&A computed per class, multiplied by the corporate tax rate, discounted at cost of capital. Tax goodwill is amortized straight-line over 15 years under IRC Section 197 -- a shield structurally unavailable in stock acquisitions where goodwill carries no tax basis.

### Section 338(h)(10) Election Mechanics
The 338(h)(10) election resolves the structural tension: buyers demand step-up benefits while sellers seek to avoid conveying individual assets. The election treats a legal stock sale as an asset purchase for tax purposes. Stock exchanges legally; the IRS computes gains and basis as if every asset were individually sold. Eligibility requires: target is an S-corporation or 80%-plus-owned subsidiary; joint buyer-seller election filed before consummation (no retroactive filing); buyer is a C-corporation (PE sponsors insert blocker C-corps); more than 80% of target stock acquired within 12 months; domestic target only; unavailable in Section 368 reorganizations. Section 338(g) permits unilateral buyer election but triggers gross-up treatment punitive for C-corp targets. Section 336(e) provides analogous treatment for 80%-owned subsidiary stock dispositions where 338(h)(10) is unavailable, though narrower scope limits institutional deployment.

### Double Taxation and Entity-Specific Optimization
C-corporation asset sales trigger two-tier taxation: corporate-level gain at ordinary income rates (~40% top bracket), followed by shareholder-level capital gains (20%) on liquidation proceeds. Stock sales tax only the shareholder level. This double-tax penalty creates a structural C-corp bias toward stock sales; the buyer's PV of step-up benefits must exceed the seller's incremental tax cost for an asset deal to clear. Entity structure transforms this calculus. S-corporations are pass-through entities with single-level shareholder taxation; a 338(h)(10) election allows NOLs to offset the deemed asset gain while eliminating shareholder capital gains on the step-up portion, making the 338(h)(10) jointly optimal when NOLs exist. For 80%-plus-owned subsidiaries, Section 332 enables tax-free liquidation distributions to the parent. Both target and parent NOLs deploy against the corporate-level gain in an asset sale, providing dual coverage that can eliminate the first-level tax entirely. Parent NOLs also offset shareholder-level capital gain in a stock sale, but without step-up benefits.

### NOL Utilization and Section 382 Limits
NOLs function as a structural lever that can invert deal-structuring preferences. Asset sales permit unlimited NOL offset against corporate-level gain; any excess is extinguished. Stock sales carry NOLs to the acquirer but impose the IRC Section 382 annual limitation: usable NOLs capped at purchase price times the long-term tax-exempt rate (~2.3% currently), converting large NOL pools into slow-release assets with diminished PV. For subsidiary transactions, parent NOLs provide additional coverage -- corporate-level offset in asset sales, shareholder-level offset in stock sales. The corporate-level offset is more valuable per dollar consumed since it shields income taxed at 40% rather than the 20% capital gains rate.

### Deal Structure Optimization Framework
The institutional total-value framework computes seller after-tax proceeds plus PV of acquirer tax benefits. The structure maximizing this sum is theoretically optimal. When the acquirer's PV step-up benefit exceeds the seller's incremental tax cost, the acquirer raises the purchase price to compensate while retaining net surplus. The taxable-sale decision matrix (NOL-rich scenario, ranked by total value): 80%-plus subsidiary 338(h)(10) highest (full proceeds with zero capital gains leakage, full step-up PV), followed by S-corp 338(h)(10), subsidiary stock sale, C-corp asset sale, with C-corp and S-corp stock sales producing the lowest combined value. In non-taxable Section 368 reorganizations (at least 50% acquirer stock consideration), tax is deferred not eliminated: shareholders receive carryover basis in acquirer shares; the acquirer obtains no inside or outside basis step-up; NOLs transfer subject to Section 382 limits. Continuity of business and valid non-tax purpose are required. Type A (statutory merger), Type B (stock-for-stock), and Type C (stock-for-assets) forms predominate, with triangular merger variants dominant in large-cap transactions.

## Divestiture Methodology Supplement

### Spin-off Architecture and Section 355 Qualification

The tax-free spin-off under IRC Section 355 requires Distributing to hold at least 80% of both total combined voting power and each class of non-voting stock of Controlled immediately before distribution. Five additional requirements complete the qualification test: (1) the transaction must not be principally a device for distributing earnings and profits -- substantially pro-rata distribution with no shareholder exceeding 5% ownership is presumptively non-device; (2) each entity must have conducted an active trade or business for the preceding five years, with no acquisition of that business in a taxable transaction within the five-year window; (3) Distributing must distribute all stock and securities held in Controlled; (4) the separation must be motivated substantially by a corporate business purpose, not merely shareholder tax avoidance; and (5) continuity of interest and business enterprise must be maintained post-distribution. Qualified treatment eliminates both corporate-level gain on the asset transfer and shareholder-level ordinary income on the distribution, with shareholders receiving carryover basis allocated between Distributing and Controlled proportionally by fair market value. Boot (assets other than qualifying stock or securities) triggers taxable gain at both levels. The private letter ruling risk is material: the IRS can and does refuse rulings where a small operating business is folded into a larger entity for spin-off qualification, as demonstrated by Yahoo's failed 2015 Alibaba spin-off attempt. When qualification is uncertain, the reverse spin alternative -- spinning out the smaller core business while retaining the larger asset in the legacy entity -- minimizes potential tax exposure since taxable gain is proportional to the FMV of the entity being spun out.

### Equity Carve-out Architecture

The carve-out (partial IPO of a subsidiary) is conventionally limited to 20% of the parent's voting interest. Exceeding this threshold risks tax deconsolidation, triggering liability on any negative basis in the subsidiary and potentially compromising future spin-off qualification. Dual-class stock structures circumvent this constraint: the parent divests more than 20% of economic ownership via low-vote Class A shares while retaining at least 80% of voting interest through high-vote Class B shares, preserving both tax consolidation and dividends-received deduction eligibility (80%-owned subsidiary dividends are tax-free). Safeway's 2013 carve-out of Blackhawk Network demonstrates the pattern: post-IPO, Safeway held 75.7% of total outstanding shares but 91.6% of combined voting power. Primary share issuances are structured as non-taxable capital raises (APIC credit), while secondary share sales by the parent generate taxable capital gain or loss based on outside tax basis in the subsidiary stock.

### Split-off and Reverse Morris Trust Mechanics

Split-offs distribute subsidiary ownership through a tender offer: existing shareholders elect to exchange parent shares for subsidiary shares. The exchange ratio requires a premium sufficient to incentivize tendering but not so large as to invite IRS recharacterization as taxable compensation or a dividend. Under-subscription risk is mitigated by a pro-rata spin-off fallback for unexchanged shares. Pre-split-off carve-outs establish public market valuation benchmarks, providing objective defense of the exchange ratio against shareholder litigation.

Reverse Morris Trust transactions enable tax-free divestiture to a third-party acquirer through a two-step sequence: the parent spins the divested business into an independent company distributed to shareholders tax-free, then the acquirer immediately merges with that company in a tax-free stock-for-stock exchange. The binding structural constraint: parent shareholders must receive more than 50% of the vote and value of the surviving entity. Equity issuances by the acquirer within two years that dilute selling shareholders below this threshold retroactively negate tax-free treatment. A two-year lookback applies to pre-transaction M&A discussions between seller and acquirer; if significant dialogue occurred, a post-closing waiting period is imposed before the combined entity can engage in further M&A activity targeting the same assets. The acquirer can retain effective board and management control despite the technical majority held by seller shareholders.

### Divestiture Valuation Framework

Spin-off valuation employs when-issued (grey market) pricing as a pre-distribution signal, cross-validated against sum-of-the-parts analysis. The core diagnostic compares the subsidiary's percentage of combined enterprise value against its percentage of combined revenue or EBITDA -- a material positive spread signals the subsidiary is undervalued within the conglomerate (PayPal: 60% of combined EV vs. 40% of combined revenue). Dual peer-group benchmarking is required for hybrid businesses spanning multiple industry classifications; PayPal was framed against both internet companies (Google, Amazon, Apple) and payment networks (Visa, Mastercard). Institutional price target derivation uses a blended methodology: a 75%/25% P/E-to-DCF blend where P/E is derived by applying incumbent peer PEG ratios to the subsidiary's EPS growth rate, then discounted for competitive threat exposure (Morgan Stanley applied a 15% discount to Visa/Mastercard's PEG when valuing PayPal). Excess cash per share is added separately to P/E-based valuation. Bull/base/bear scenario analysis is parameterized by TPV growth rates, margin trajectory, and competitive intensity assumptions.

### Divestiture Accounting Protocol

Upon spin-off announcement, the parent reclassifies the subsidiary's net assets to "Net Assets of Discontinued Operations" on the balance sheet. Prior-period financials are retrospectively restated to present the subsidiary's results as discontinued operations. At close, the distribution is recorded at book value -- debit Retained Earnings, credit Net Assets of Discontinued Operations -- as a non-reciprocal transfer to owners. All accumulated other comprehensive income attributable to the spun entity is derecognized (eBay removed $12M AOCI upon PayPal distribution). On the SpinCo side, pre-distribution equity -- typically a single "Net parent investment" line representing the parent's intercompany investment account -- converts to standard equity structure (APIC plus retained earnings plus common stock) upon standalone establishment. Intercompany balances (notes receivable/payable between parent and subsidiary) are eliminated at separation. The subsidiary's deferred tax liabilities are remeasured for standalone status, frequently producing material step-changes (PayPal: DTL increased from $386M at year-end 2014 to $1,505M at year-end 2015 following the July 2015 separation).

### Divestiture Decision Framework

The institutional motivation typology for identifying divestiture candidates: (1) sum-of-the-parts discount where combined separated-entity values exceed the current conglomerate market capitalization; (2) pure-play valuation where different business lines command different multiples from distinct investor bases; (3) management attention and capital allocation efficiency degradation across diverse businesses; (4) earnings/capital drag where low-ROE, high-capital-intensity businesses suppress consolidated return metrics; (5) regulatory divestiture for SIFI de-designation or antitrust remediation; (6) financial leverage management via asset sale proceeds deployed against debt or to pre-fund acquisitions; (7) activist pressure with the institutional playbook of forced separation, governance stripping from SpinCo (no poison pill), and stake rotation from RemainCo to SpinCo; (8) merge-to-spin pattern (DowDuPont) combining complementary entities to extract synergies then separating into tax-free pure-plays; (9) competitive unlocking where independence enables commercial relationships with the parent's competitors; and (10) acquisition precursor where isolating a business unit facilitates its sale to a strategic buyer.
