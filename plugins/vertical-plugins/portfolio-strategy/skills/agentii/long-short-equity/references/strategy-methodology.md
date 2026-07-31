# Long/Short Equity Strategy — Methodology Reference

Institutional methodology for classifying, sourcing, and evidencing two-sided equity
positions. Fused from buy-side long/short and professional research frameworks; all text is
an original paraphrase. Companion to `SKILL.md`.

---

## 1. The Unifying Concept: Earnings Disconnect

Every strategy in this space reduces to one question: **what does the market believe, and
what do I believe differently?** Merger arbitrage, deep value, and growth investing look
unrelated on the surface, but each monetizes a gap between priced expectation and delivered
outcome. The disconnect *is* the position. An absolute valuation opinion — "this is cheap"
— is not a position, because it contains no statement about what the market has wrong.

This framing has a practical consequence: before any thesis work, state the consensus
numerically. If the consensus cannot be articulated, a variant view cannot exist.

---

## 2. Consensus Is Not the Published Number

The consensus figure carried on data terminals is a simple arithmetic average of sell-side
analyst estimates. It is a lagging artifact, and it is not what the marginal buyer is
actually underwriting.

**Buy-side consensus typically moves ahead of sell-side consensus.** Capital repositions
before published estimates are revised. Trading against the printed figure while real
positioning has already shifted is a routine and expensive error — the "beat" arrives, and
the stock falls, because the effective bar was higher than the published one.

Triangulating the effective expectation is qualitative work with no clean data source:

- Compare notes with other holders of the position
- Deliberately seek out the view on the other side of the trade
- Weight recent revisions and their direction more heavily than the stale average
- Treat unusually wide estimate dispersion as evidence that no consensus exists

Record the result as an explicit range with a direction, not a point estimate. Where the
buy-side expectation cannot be triangulated, mark the disconnect **unquantified** rather
than defaulting to the published figure.

---

## 3. Strategy Spectrum

Strategies arrange along a continuum from spread-focused (return driven by a mechanical
price gap closing) to fundamentals-focused (return driven by business outcomes).

| Strategy | Position on spectrum | Return driver | Typical horizon |
|---|---|---|---|
| **Merger arbitrage** | Spread-focused | Gap between market price and announced acquisition price | 0–18 months |
| **General event-driven** | Spread, leaning fundamental | A specific event: regulatory change through full operational turnaround | 0–24 months |
| **Activist** | Intermediate | Taking a stake and agitating for improvement, sale, or breakup | 0–24 months |
| **Value / deep value** | Fundamentals-focused | Discount to net present value, on a **price** basis | 0–5 years+ |
| **Growth / growth at a reasonable price** | Fundamentals-focused | Discount on an **earnings** basis | 0–5 years+ |

Three qualifications matter and are routinely ignored:

1. **The list is not exhaustive.** Real books contain hybrids.
2. **Categories are not mutually exclusive.** An activist position in a cheap asset is both
   activist and deep value.
3. **Every fund has a unique style.** These are guidelines for reasoning, not taxonomy to
   be enforced.

The practical use of the classification is calibration: it sets the expected holding period
and therefore the evidence bar. A spread-focused position needs deal-mechanics certainty
within months. A fundamentals-focused position needs a multi-year business judgment. Applying
the wrong evidence standard to either is the most common process failure.

Note the distinction between the two fundamentals-focused styles: value seeks a discount on
a **price** basis (what the assets are worth), growth seeks a discount on an **earnings**
basis (what the future stream is worth). They are not interchangeable and require different
evidence.

---

## 4. Idea Sourcing

Five routes, each with a characteristic bias that determines what must be validated:

| Route | Characteristic strength | Must be validated for |
|---|---|---|
| Industry research and trade events | Early visibility on real demand shifts | Confirmation bias from vendor narratives |
| Tangential analysis of adjacent markets | Finds indirect exposure others miss | Weak causal link to the target's economics |
| Conversations with analysts and operators | Ground-level operating detail | Independent quantitative confirmation |
| Curated research communities | Detailed pre-existing theses | Crowding; the idea may already be consensus |
| Quantitative screens | Systematic, unbiased coverage | Qualitative validation; screens surface accounting artifacts |

Provenance is diagnostic, not decorative. A screen-sourced idea and a conversation-sourced
idea carry inverted risk profiles: the screen needs qualitative work, the conversation needs
numbers. Recording the route tells the analyst which test is still missing. Crowding risk
deserves particular attention for community-sourced ideas — a well-argued public thesis may
already be in the price, and on the short side it may also be hard to borrow.

---

## 5. Shorting: Two Distinct Activities

- **Alpha shorting** — individual short positions intended to earn a return on their own
  thesis. Analytically demanding, and the reason two-sided skill is valued.
- **Index shorting** — shorting a broad index to damp the long book's market exposure.
  Operationally simple, generates no selection alpha.

Funds use both. Alpha shorting is the more valued capability precisely because it is harder.
The two are not substitutes: a beta problem calls for index shorting, while a conviction
about a specific deteriorating business calls for an alpha short.

### Structural constraints unique to the short side

1. **Long bias of the market** — the unconditional drift works against the position
2. **Unbounded loss** — losses are theoretically unlimited; gains cap at 100%
3. **Time horizon** — an over-valuation can persist for years while carry accrues against you
4. **Availability** — the borrow must exist and remain available
5. **Short interest and days-to-cover** — crowded positions invite squeezes
6. **Volatility** — adverse moves enlarge the position automatically
7. **Sizing** — consequently shorts require smaller initial size than longs of equal conviction

A correct thesis in a crowded, hard-to-borrow name is **not an executable position**.
Executability is a gate, not a footnote.

---

## 6. Short Archetypes

Three recurring patterns. Each carries its own evidence requirement, and substituting a
generic valuation opinion for the archetype-specific test is the characteristic failure.

### Competition short

*Setup*: A complacent incumbent faces a credible, innovative new entrant.

*Evidence required*:
- Establish the entrant's true competitive capability through unit-economics analysis,
  product testing, and primary research — not press coverage
- Assess incumbent management's **willingness** to react and the **likelihood** they actually
  will

The second test is the one usually skipped. An incumbent with the resources and the
willingness to respond can absorb a new entrant; the short then fails despite a correct read
on the entrant's product. Capability to respond and willingness to respond are separate
questions.

### Consumer euphoria

*Setup*: Outsized enthusiasm for a consumer-facing product that will not sustain.

*Evidence required*:
- Assess the long-term potential of the product and company through market-sizing analysis
- Validate through direct product testing

The discipline here is separating a genuine durable adoption curve from a fad. Market sizing
provides the ceiling; product work provides the retention judgment. Absent both, this
archetype reduces to a bet against price momentum, which is not a thesis.

### Disappearing business

*Setup*: An incumbent operating in a market that will structurally cease to exist.

*Evidence required*:
- Determine the **rate** of decline, not merely its direction
- Assess cash-flow characteristics through the decline
- Determine the company's ability to **re-deploy** cash into something viable

Rate is decisive. A business declining slowly while generating strong cash flow can
out-return the market for years and is a poor short despite a correct terminal view.
Successful cash redeployment can invalidate the thesis entirely. This archetype fails most
often on timing and on underestimating management's reinvestment optionality.

---

## 7. Position Assembly Checklist

Before committing, confirm each of the following is documented:

1. Strategy classification with its implied holding period
2. Consensus stated numerically, with the buy-side estimate separated from the published one
3. The disconnect quantified, with direction
4. Idea provenance and the validation it implies
5. Long-side basis (price vs earnings discount) or short-side archetype with its specific test
6. Archetype-matched precedent, weighted by situation rather than sector
7. Falsification condition and a deadline
8. For shorts: borrow, short interest, days-to-cover — executability cleared

An item that cannot be completed is a coverage gap and must be reported as one, not
silently omitted.
