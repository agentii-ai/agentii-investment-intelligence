# FX Options — Institutional Methodology

## FX-Specific Put/Call Mechanics

Every FX option involves two currencies simultaneously. A EUR call is also a USD put; the two descriptions reference one contract. The standard formulation states the option in terms of the first currency: "EUR call / USD put" means the holder has the right to buy EUR and sell USD at the strike. This duality is not semantic — the payout currency and premium currency flow from which side you denominate the trade.

## Market Structure: OTC Conventions

FX options trade over-the-counter (~98-99% of volume), not on exchange. This means every contract term is negotiable bilaterally between counterparties: any currency pair, any strike, any expiry date (any weekday), any notional size, any cutoff time, any premium currency, American or European exercise, deliverable or cash-settled. Despite full flexibility, institutional participants adhere to market conventions to streamline daily flow:

- **Notional size**: quoted in the first currency of the pair (e.g., 100m EUR in EURUSD, not 100m USD).
- **Premium currency**: USD if USD is one of the pair; otherwise the first currency (e.g., EUR in EURCHF).
- **Premium quoting**: as a percentage of notional. A 100m EURCHF option at 0.34% premium costs 340,000 EUR.
- **Currency hierarchy**: EUR > GBP > AUD > NZD > USD > CAD > CHF > others. The senior currency always appears first. GBPUSD is standard; USDGBP is effectively never quoted.
- **Exercise style**: European (exercise at expiry only) is the universal standard. American (exercise any day) is available on request but rarely traded.
- **Cutoff times**: NY cut (10am NY time) dominates North American and European trading. Tokyo cut (3pm Tokyo) prevails in Asia. Emerging market currencies (MXN, INR, RUB, KRW, BRL) often have bespoke cutoff times.
- **Tenor classification**: Short-dated = less than 1 month (minimum practical tenor: 1 day). Long-dated = over 1 year (out to 30 years observed for certain pairs).

## Moneyness: Forward-Referenced

In FX, at-the-money is defined relative to the **forward rate**, not the spot rate. An option is ATM when its strike approximates the outright forward for that tenor. ITM/OTM classification follows the >50%/<50% probability-of-exercise heuristic, assessed against the forward.

## Directional Strategies: Vanilla vs. Call Spread

**Long vanilla** provides full upside participation with downside capped at premium. Example: USDJPY spot at 102.50, buy 1-month USD call/JPY put strike 104. Notional $100m, premium $400,000 (0.4%). At expiry with spot at 106: exercise at 104, sell spot at 106, gross $1.88m, net $1.49m after premium. Maximum loss: $400,000.

**Call spread** reduces premium cost in exchange for capped profit. Buy $100m 103.00 call (pay $600K), sell $100m 104.25 call (receive $350K). Net premium: $250K. Maximum profit is bounded between the two strikes. At spot 106: buy at 103, forced delivery at 104.25 from short leg, gross $1.18m, net $929K after premium. The strategy suits a "slow and steady" directional view where a large blowout move is not anticipated and the trader is unwilling to pay the full vanilla premium.

## Institutional Use Cases

Six primary applications drive institutional FX option flow:

1. **Corporate hedging**: Exporters buying puts on their revenue currency to protect against adverse FX moves eroding home-currency profits.
2. **Investor hedging**: Cross-border portfolio holders buying options to isolate equity/asset exposure from currency translation risk (e.g., a US investor long Canadian equities buying USD call/CAD put).
3. **FX spot directional trading**: Levered directional bets with defined downside — hedge funds prioritize capital efficiency and asymmetric payoff.
4. **Volatility trading**: Pure vol exposure via straddles, strangles, and delta-hedged positions.
5. **Yield enhancement**: Selling options against existing exposures to harvest premium.
6. **Correlation trading**: Multi-currency structures exploiting cross-pair relationships.

## CME Exchange-Traded Conventions

Exchange-traded FX options (primarily CME) follow exchange-defined conventions that differ materially from OTC standards: fixed expiry dates, standardized strikes, and exchange-mandated contract specifications. CME screens display bid/offer, implied volatility on both sides, and Greeks (delta prominently). Exchange volume is a small fraction of the total market but offers transparency and central clearing.
