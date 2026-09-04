# WSP Healthcare Sector Methodology

## Industry Segmentation (Banking & PE Lens)

The healthcare industry is segmented by investment banks and private equity firms into three primary verticals, each with distinct valuation drivers and risk profiles:

**Life Sciences**: Biotech, Large Pharma, Specialty Pharma, Generics. Differentiated by R&D intensity, pipeline maturity, and patent exposure. Generics compete on volume contracts and manufacturing cost; branded pharma competes on formulary positioning and clinical differentiation.

**Med Tech**: Devices and Equipment. Capital equipment cycles, regulatory clearance pathways (510k vs PMA), and hospital capital budgeting cycles drive revenue visibility.

**Healthcare Services**: The most structurally complex vertical, subdivided into Other Services (CROs, PBMs, pharmacies, distributors, HCIT), Payers (Managed Care Organizations, CMS), and Providers (hospitals, ASCs, SNFs, home health). Providers are further classified by acuity (acute vs. post-acute) and setting (inpatient vs. outpatient).

## PBM Ecosystem and Drug Pricing Mechanics

Pharmacy Benefit Managers (PBMs) sit at the center of pharmaceutical economics, functioning as the intermediary that dictates which drug is dispensed (brand vs. generic) and at what net price. The PBM value chain operates through three levers:

1. **Formulary Rebates**: Branded manufacturers pay rebates to PBMs for inclusion on the formulary (covered drugs list). This is not a discount to the consumer -- it is a payment for market access that flows manufacturer-to-PBM, creating a spread between list price and net realized price that drives manufacturer gross-to-net calculations.

2. **Generic Utilization and Mail Order Penetration**: PBMs reduce system costs by converting prescriptions to generics and routing volume through captive mail-order facilities, capturing margin on both the spread and the distribution channel.

3. **Vertical Integration**: The industry has consolidated along the PBM axis. Cigna owns Express Scripts; CVS owns both Caremark (PBM) and Aetna (payer). These mergers and alliances create closed-loop ecosystems where the same entity controls the formulary, the pharmacy network, and the insurance risk pool.

The summary statement from the WSP modeling framework: "PBMs reduce costs by negotiating drug prices with drug manufacturers and retail pharmacies and by driving generic utilization and mail order penetration."

## Generics Revenue Build Methodology

The generics revenue build follows a structured, multi-stage projection framework:

### Stage 1: Market Sizing
- Source branded revenue from the innovator's 10-K product disclosures or third-party prescription data.
- Derive market volume: Branded Revenue / Estimated Brand Price (sourced from GoodRx or wholesale acquisition cost databases).
- Assume 2% annual market volume growth as a baseline.

### Stage 2: Generic Penetration Curve
- Model branded-to-generic conversion as a gradual process: 95% generic share in Year 1, stepping to 99% by Year 5.
- Branded drugs retain a small residual share initially, fading as PBMs systematically drive conversions to therapeutically equivalent generics.

### Stage 3: Competitor Entry Dynamics
- Model sequential new entrant arrivals (4 competitors in Year 1, adding one per year until the market becomes unprofitable for an additional entrant -- typically plateauing at 6-7 competitors).
- Each new entrant erodes incumbent share: starting at 25% market share for the first mover, declining to approximately 14% at steady state.

### Stage 4: Price Erosion
- Generic prices launch at roughly 50-55% of the branded price and decline approximately 10% per year with each new competitor entry.
- Price erosion stabilizes once the competitor count plateaus (no further 10% annual decline when no new entrants).
- At steady state, generic prices typically settle at 15-20% of the original branded price.

### Stage 5: Risk-Weighting for Pipeline Products
- For products still in development, apply a probability weight to projected revenue based on the estimated likelihood of successful FDA bioequivalence approval.
- Paragraph IV patent challenges (Hatch-Waxman framework): when a generic company challenges a branded patent before expiry and wins, it gains 180 days of marketing exclusivity -- a critical asymmetric upside scenario in generics modeling.

## Hospital Revenue Build Methodology

### Volume Derivation
The hospital revenue model is built from physical capacity, not market share:
- Beds per hospital (from 10-K operating data) x occupancy rate = average daily census.
- Average daily census x 365 = total annual patient-days (inpatient volume proxy).
- Outpatient volume split from total (typically ~13% of total volume for large hospital systems).
- Equivalent Admissions = (Inpatient Admissions x total revenue per case ratio) + Outpatient Volume. This metric serves as the combined volume KPI, analogous to a retail company's transaction count.

### Revenue per Equivalent Admission
- Revenue per equivalent admission functions as the "price" variable, driven by two factors: payer mix shifts and reimbursement rate changes.
- Medicare reimbursement is based on Diagnosis Related Groups (DRGs) at contracted rates; Managed Medicare (Medicare Advantage) carries 300-400 bps higher reimbursement.
- Medicaid rates are structurally the lowest among all payer types.

### Same-Facility Growth
The hospital industry equivalent of same-store sales: revenue, admissions, and revenue per equivalent admission measured on a same-facility basis, excluding acquisitions. HCA 2018 baseline: 6.5% same-facility revenue growth, 2.5% admission growth, 3.9% revenue per equivalent admission growth.

### Acquisition Modeling
- Newly acquired hospitals are modeled as smaller facilities (lower bed count) with lower Year-1 occupancy (~52% vs. ~57% for mature facilities).
- Revenue contribution is multiplied by 0.5 in the acquisition year, reflecting a mid-year closing assumption.
- Post-acquisition, new facilities inherit the same operational metrics (outpatient mix, length of stay, revenue per admission) as the existing portfolio.

## Payer and Provider Financial Metrics

### Medical Loss Ratio (MLR)
The central KPI for managed care organizations: MLR = Medical Costs / Premium Revenue. This ratio governs both profitability and regulatory compliance (ACA minimum MLR requirements).

### Payer Mix Analysis
For providers, revenue is decomposed by payer source, each with distinct reimbursement characteristics:
- Medicare (Traditional FFS): ~21% of revenue, DRG-based reimbursement.
- Managed Medicare (Medicare Advantage): ~11% of revenue, contracted rates on DRG basis, growing faster (+13.4% CAGR) as enrollment shifts to private plans.
- Managed Care / Commercial: ~52% of revenue, 1-3 year contracts with volume steering through Preferred Provider Organizations.
- Medicaid: structurally lowest reimbursement, increasingly incorporating outcomes-based payments or penalties.

### Uncompensated Care
Modeled as: Gross Uncompensated Care Charges x Cost-to-Charges Ratio. This captures charity care, uninsured discounts, and price concessions. The cost-to-charges ratio (patient care costs / gross patient charges) serves as the conversion factor from list prices to economic cost.

### Payment Integrity Revenue Model
A distinct sub-industry within HCIT: payment integrity companies audit claims for errors and over-billing, earning a percentage of what they "catch" (typically 20-30% contingency). The revenue model is directly tied to claims volume and payer adjudication inefficiency.

## Industry Structural Trends

**Vertical Consolidation**: Payers acquiring PBMs, pharmacies acquiring payers, pharmacies merging with distributors -- creating integrated delivery and financing ecosystems that compress margins for independent players.

**Value-Based Care Migration**: The fundamental reimbursement model shift from fee-for-service (volume-driven) to value-based care (outcome-driven), with pay-for-performance components increasingly embedded in provider contracts.

**Integrated Delivery Networks (IDNs)**: Provider-payer systems operating within a defined geographic area, negotiating as a single entity against suppliers and leveraging combined data across the care continuum.
