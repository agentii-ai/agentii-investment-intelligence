# ratio-analysis — Methodology Detail

Extracted from SKILL.md for progressive disclosure (US5).

## Retrieval Strategy

Follow the retrieval strategy decision tree in `contracts/retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (d) for simple lookups via `get_realtime_quote` / `search_companies` / `search_earnings_calendar`.

## Protocol

1. **Pre-retrieval**: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format, then `get_ticker_coverage/{ticker}` .
2. **XBRL retrieval**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss","Assets","Liabilities","Equity","OperatingCashFlow","InventoryNet","ReceivablesNet","CurrentAssets","CurrentLiabilities","InterestExpense","LongTermDebt"], fiscal_year=[latest, latest-1, latest-2, latest-3])` — batch all concepts × 4 years.
3. **Price data**: `get_realtime_quote(ticker)` for current stock price, market cap, PE (TTM).
4. **Peer identification**: `get_peer_comparison(ticker, metric)` (or `search_companies(search=<industry>)` — note there is no `sector` param) to identify peer tickers for cross-company comparison.
5. **Compute ratios** into 6 categories per the Ratio Definitions below.
6. **Cross-company comparison**: for each peer, fetch key ratios and present comparison table with mean/median/high/low.
7. **Output**: per file convention with YAML frontmatter .

## Ratio Definitions

#### Profitability
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| ROE | Net Income / Avg Total Equity | >15% = strong; measures return to shareholders |
| ROA | Net Income / Avg Total Assets | >5% = efficient; asset utilization |
| ROIC | (EBIT × (1 - Tax Rate) / (Total Debt + Equity - Cash) | > WACC = value-creating |
| Gross Margin | Gross Profit / Revenue | Industry-dependent; higher = pricing power |
| Operating Margin | Operating Income / Revenue | >15% = healthy operations |
| Net Margin | Net Income / Revenue | >10% = strong bottom-line efficiency |

#### Liquidity
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Current Ratio | Current Assets / Current Liabilities | >1.5 = healthy; <1.0 = liquidity risk |
| Quick Ratio | (Cash + Receivables) / Current Liabilities | >1.0 = strong; acid test |
| Cash Ratio | Cash / Current Liabilities | Most conservative; >0.5 = adequate |
| Operating CF Ratio | Operating Cash Flow / Current Liabilities | >1.0 = can cover obligations from ops |

#### Leverage
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Debt-to-Equity | Total Debt / Total Equity | <2.0 = conservative; >4.0 = aggressive |
| Interest Coverage | EBIT / Interest Expense | >3x = safe; <1.5x = distress risk |
| Debt-to-EBITDA | Total Debt / EBITDA | <3x = manageable; >5x = highly leveraged |

#### Efficiency
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Asset Turnover | Revenue / Avg Total Assets | Higher = more efficient |
| Inventory Turnover | COGS / Avg Inventory | Higher = faster sales; watch for stockouts |
| Days Sales Outstanding | (Receivables / Revenue) × 365 | Lower = faster collections |
| Days Inventory Outstanding | (Inventory / COGS) × 365 | Lower = leaner operations |

#### Valuation (requires current price from `get_realtime_quote`)
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| P/E (LTM) | Price / LTM EPS | Lower = cheaper; sector-dependent |
| P/E (NTM) | Price / NTM Consensus EPS | Forward-looking; from `search_earnings_calendar` |
| P/B | Price / Book Value Per Share | <1.0 = below book; financials focus |
| EV/EBITDA | Enterprise Value / EBITDA | Capital-structure neutral |
| P/S | Market Cap / Revenue | Growth check; <2.0 = reasonable |
| PEG | P/E / Earnings Growth Rate | <1.0 = undervalued per Peter Lynch |

#### Growth
| Ratio | Formula | Interpretation |
|-------|---------|---------------|
| Revenue CAGR (3yr) | (Revenue_t / Revenue_t-3)^(1/3) - 1 | Trend; >10% = strong growth |
| EPS CAGR (3yr) | (EPS_t / EPS_t-3)^(1/3) - 1 | >10% = strong earnings growth |
| Revenue CAGR (5yr) | (Revenue_t / Revenue_t-5)^(1/5) - 1 | Longer trend |
| EPS CAGR (5yr) | (EPS_t / EPS_t-5)^(1/5) - 1 | Longer earnings trend |
