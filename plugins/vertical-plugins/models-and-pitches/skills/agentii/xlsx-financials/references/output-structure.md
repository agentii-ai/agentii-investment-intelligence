# xlsx-financials — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

The primary deliverable is an `.xlsx` workbook with proper number formatting, frozen headers, and calculation arc cross-validation. A companion `.md` summary captures validation results and key citations. Output conventions follow the Anthropic FSI xlsx-author standard (blue font = hardcoded inputs, black font = formulas).

### Single-Ticker
```
{ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx
```
Example: `LLY/2026-06-03_1430_statement-income.xlsx`

### Multi-Ticker
```
_cross/{slug}_{YYYY-MM-DD_HHMM}_statement-{type}.xlsx
```
Example: `_cross/LLY-vs-peers_2026-06-03_1430_statement-income.xlsx`

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
