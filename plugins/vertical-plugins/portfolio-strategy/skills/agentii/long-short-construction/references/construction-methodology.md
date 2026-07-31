# Long/Short Book Construction — Methodology Reference

Institutional methodology for sizing and balancing a two-sided equity book. Fused from
professional portfolio-construction and buy-side long/short frameworks; all text is an
original paraphrase. Companion to `SKILL.md`.

---

## 1. Exposure Algebra

Exposure is the share of capital committed on each side, expressed as a percentage of
net asset value. Two derived measures govern the book, and they answer different
questions:

| Measure | Formula | What it controls | Common name |
|---|---|---|---|
| **Gross exposure** | Long % + Short % | Total capital at work; the amount of idiosyncratic risk being harvested | "Leverage" |
| **Net exposure** | Long % − Short % | Residual directional sensitivity to the broad market | "Market risk" |

The critical discipline is treating these as **two independent dials**. Gross sets how
much stock-specific opportunity the book is exposed to. Net sets how much of the return
is simply the market. A book can raise gross (more alpha attempts) while holding net
constant (unchanged market risk) — that is the central move in long/short construction,
and it is what distinguishes the strategy from levered long-only.

### Beta-adjusted net exposure

Raw net exposure silently assumes both sides carry identical market sensitivity. They
rarely do. The decision-grade measure is:

```
Beta-adjusted net = (Long % x weighted long beta) - (Short % x weighted short beta)
```

A book at 100% long / 50% short shows a raw net of 50%. If the longs are high-beta
growth names at beta 1.4 and the shorts are defensive staples at beta 0.6, the
beta-adjusted net is (100 x 1.4) − (50 x 0.6) = 110% — **more** directional risk than
the raw figure implies, not less. Reporting raw net in this situation understates market
risk by more than half. Always compute both; when they diverge by more than ~15
percentage points, the hedge is mis-specified and the short side must be re-selected or
re-sized.

---

## 2. Risk Decomposition — Why Two Sides At All

Every equity position bundles two distinct risks:

1. **Market risk** — the portion of the move explained by the broad index
2. **Company/industry risk** — the idiosyncratic residual specific to the business

A long-only book accepts both. Pairing a long against a short causes the market-risk
components to offset, leaving a book whose return is driven by the *relative* outcome of
two idiosyncratic views:

```
Long (market + idiosyncratic) + Short (market + idiosyncratic)
    -> market components cancel
    -> residual = long idiosyncratic + short idiosyncratic
```

This is the structural justification for the strategy: it converts a directional bet
into a bet on analytical skill. It also explains the strategy's failure mode — with
market risk removed, there is nothing left to carry a book whose stock selection is
wrong. Hedging does not reduce the cost of bad research; it removes the beta tailwind
that previously masked it.

---

## 3. Exposure Configurations and Return Dilution

Hedging is not free. When shorts carry the same beta as longs, every unit of short
exposure cancels a unit of market return. Three canonical configurations on 100 units of
capital in a 10% market, with equal betas of 1.0 and zero alpha on both sides:

| Configuration | Long | Short | Net | Gross | Capital employed | Profit | Return |
|---|---|---|---|---|---|---|---|
| Long only | 100 | 0 | 100 | 100 | 100 | 10 | **10%** |
| Balanced hedge | 100 | 50 | 50 | 150 | 100 | 5 | **5%** |
| Directional tilt | 125 | 50 | 75 | 175 | 100 | 8 | **8%** |

The lesson is exact and often misunderstood: introducing 50 units of equal-beta short
exposure **halves** the return, from 10% to 5%. Return tracks net exposure, not gross.
Raising gross from 150 to 175 while lifting net from 50 to 75 restores return to 8% — but
that is a decision to take more market risk, not evidence of better hedging.

Therefore a short book that exists only to damp beta is a pure drag on return. Shorts
must be expected to generate their own alpha, or index-level hedging is the cheaper and
more honest instrument.

### Fund-return sensitivity grid

Publish the book's return across a market range before committing. For the three
configurations above:

| Market return | −20% | −10% | 0% | +10% | +20% |
|---|---|---|---|---|---|
| Long only | −20.0% | −10.0% | 0.0% | +10.0% | +20.0% |
| Balanced hedge (net 50) | −10.0% | −5.0% | 0.0% | +5.0% | +10.0% |
| Directional tilt (net 75) | −15.0% | −7.5% | 0.0% | +7.5% | +15.0% |

The slope of each row **is** net exposure. This grid is the clearest single artifact for
confirming that realized market sensitivity matches intent.

---

## 4. Alpha and Beta Attribution

Separate every period's profit into the part that came from market direction and the part
that came from selection. Attribute both sides independently:

```
Side profit = (exposure x beta x market return)  +  (exposure x alpha)
                      beta contribution                alpha contribution
```

Worked example — 125 long / 50 short, betas 1.0, market +10%, long alpha 5.0%, short
alpha 2.5% (a short alpha of +2.5% means the shorted names underperformed by 2.5%):

| Component | Opening | Beta contribution | Alpha contribution | Profit |
|---|---|---|---|---|
| Long book | 125 | +12.5 | +6.25 | +18.75 |
| Short book | (50) | −5.0 | +1.25 | −3.75 |
| **Total** | **75** | **+7.5** | **+7.5** | **+13** |

Return on 100 units of capital is 13%. With alpha added, the sensitivity grid shifts
upward across the whole range:

| Market return | −20% | −10% | 0% | +10% | +20% |
|---|---|---|---|---|---|
| Fund return (with alpha) | −10.0% | −2.5% | **+5.0%** | +12.5% | +20.0% |

Two properties matter. At a flat market the book still returns +5.0% — that is the alpha
showing through with no beta assistance, and it is the entire economic case for the
strategy. And in a −10% market the book loses 2.5% rather than 7.5%. Alpha shifts the
intercept; net exposure sets the slope. Diagnose the book on both parameters separately,
because a book can look fine on return while its intercept is zero and its slope is
simply large.

---

## 5. Constructing the Short Side

Distinguish two mechanically different activities:

- **Alpha shorting** — individual short positions taken to earn a profit in their own
  right. Analytically demanding and the source of genuine two-sided skill.
- **Index shorting** — shorting a broad index purely to damp the long book's beta.
  Operationally simple, contributes no selection alpha.

Both are legitimate; they are not interchangeable. Index shorting is the correct tool for
a beta problem. Alpha shorting is the correct tool for a conviction on a specific
business deteriorating. Using alpha shorts as a beta hedge incurs the analytical cost of
the former with the return profile of the latter.

### Structural constraints on the short side

The short side is not a mirror image of the long side. Seven constraints have no long-side
analogue and must be checked before sizing:

1. **Long bias of equity markets** — the unconditional drift is upward, so shorts fight a
   persistent headwind over time
2. **Unbounded loss** — losses are theoretically unlimited while gains cap at 100%
3. **Timing sensitivity** — a correct thesis on an over-valued business can take years,
   during which carry accrues against the position
4. **Borrow availability** — the shares must be locatable and stay locatable
5. **Short interest and days-to-cover** — crowded shorts invite squeezes; days-to-cover
   measures how long an unwind would take at normal volume
6. **Volatility asymmetry** — a losing short grows into the book as it moves against you,
   automatically increasing the exposure you least want
7. **Sizing** — because of (2) and (6), shorts require smaller initial sizes and firmer
   stops than longs of equal conviction

Constraint (6) deserves emphasis: position drift on shorts is adverse by construction.
A long that falls shrinks its own weight, self-limiting the damage; a short that rises
expands its weight, compounding it. Short books therefore need scheduled re-sizing, not
just stop levels.

---

## 6. Pair Construction

When expressing a relative view as an explicit pair:

1. **Same risk factor** — both legs should share the primary exposure being neutralized
   (sector, geography, or style). A pair spanning two sectors is two directional bets.
2. **Beta-match, do not dollar-match** — equalize `exposure x beta` on each leg, not
   dollar notional. Dollar-matching two legs of unequal beta leaves residual market risk.
3. **Independent theses** — each leg must clear the research bar alone. A weak short
   attached to a strong long is a tax on the long, not a hedge.
4. **Divergence catalyst** — identify the specific event expected to widen the spread and
   the date range in which it should occur.
5. **Correlation check** — historically correlated legs can decouple precisely under the
   stress the pair was built to survive; size for the decoupled case.

---

## 7. Book-Level Limits

Set these before entering positions, and treat breaches as mandatory review triggers:

| Limit | Typical institutional range | Rationale |
|---|---|---|
| Gross exposure | 130–200% | Above this, idiosyncratic risk dominates and a broad factor shock overwhelms selection |
| Net exposure band | −20% to +60% | Defines the strategy's identity; drifting outside it is style drift |
| Beta-adjusted net deviation from raw net | < 15pp | Larger gaps indicate a mis-specified hedge |
| Single long position | 3–5% | Standard conviction sizing |
| Single short position | 1.5–3% | Halved for unbounded loss and adverse drift |
| Days-to-cover on any short | < 5 days | Squeeze avoidance |
| Sector net exposure | ±15% | Prevents an unintended sector bet inside a "neutral" book |

Recompute gross, net, and beta-adjusted net after every position change. The two dials
only stay independent if they are measured continuously; otherwise a series of individually
reasonable trades silently converts a hedged book into a levered directional one.
