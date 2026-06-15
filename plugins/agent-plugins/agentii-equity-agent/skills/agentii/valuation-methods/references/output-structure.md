# valuation-methods — Output Structure (full template)

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a compact summary under `## Output Structure`.

The final deliverable MUST be written as a markdown file to the workspace using the convention :

```
{ticker}/{YYYY-MM-DD_HHMM}_valuation-methods_{affix}.md
```

Where `affix` is a short descriptive slug (e.g., `multiples-and-models`, `dcf-walk`, `comps-table`, `sotp-summary`). Examples:

- `LLY/2026-05-25_1430_valuation-methods_multiples-and-models.md`
- `NVDA/2026-05-25_1545_valuation-methods_dcf-walk.md`

The path is RELATIVE to the agent's invocation cwd. Skills MUST NOT write under absolute paths.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.
