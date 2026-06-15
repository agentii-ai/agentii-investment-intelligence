# Citation & Memory Contract (shared include)

Canonical citation-density rule, the deployed/tested clickable citation format,
the Citation Placement Policy, and the `agentii.md` append instruction. Skills
reference this file with a one-line pointer instead of inlining the prose.

## Citation density

≥1 citation per 200 words of body text. Bare `page_no` integers are forbidden —
every citation MUST carry both a human-readable label and a clickable link.

## Citation link format (deployed, tested — do NOT invent a new scheme)

The clickable markdown link MUST match the format in
`contracts/skill-methodology-template.md` verbatim:

```
[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
```

Example: `[📄 NVDA 10-K p.2](https://agentii.ai/v/NVDA/sec173/2)`.

### URL tiers (authoritative)

- **Tier 2 — browser redirect (THE format skills emit in markdown)**:
  `https://agentii.ai/v/{ticker}/{citation_id}/{N}` — path-based, ~7 tokens,
  browser-clickable (cmd+click in iTerm/Terminal), redirects to
  `api.agentii.ai/v1/view_document/...`.
- **Backup (accepted, compat)**: short query
  `https://agentii.ai/view?t=NVDA&c=sec173&p=2`. Legacy verbose
  `https://agentii.ai/view?ticker=...&citation_id=...&page_no=page2` is
  deprecated — do not emit.
- **Tier 1 — agent-to-agent (deferred)**: `agentii://view/{ticker}/{citation_id}/{N}`
  — NOT browser-clickable; reserved for evidence packs / MCP responses. Do NOT
  emit in skill markdown output.

Inline bare text `{ticker} {citation_id} page<N>` is acceptable as the citation
*label*, but every citation MUST also carry the clickable `/v/` link.

## Citation Placement Policy (FR-050)

1. **Inline-after-fact (primary surface)** — every material fact, table row, and
   metric is immediately followed by its clickable
   `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link. Do NOT defer all
   citations to a bottom section.
2. **Bottom "Citations" section = roll-up index** — a non-duplicative index of
   the sources already linked inline, not the primary citation surface.
3. **Final Summary (TUI)** — after writing the deliverable, the skill's closing
   chat message MUST include a compact **Key Citations** list (the headline 5–10
   facts) of clickable `/v/` URLs, so the user can cmd+click straight to the
   exact SEC page without opening the file. Keep it terse — headline facts only.

Never emit a vague `{Citations}` / `{Source(s)}` placeholder or a
`_(cite source filing in standard agentii citation format at runtime)_` hint:
write the explicit `/v/` link adjacent to the fact.

## agentii.md append

After writing the output file, append a YAML block to `agentii.md` at the
workspace root with `ticker`, `date`, `skill`, `output_file`, and
`key_conclusions` (plus `snapshot_ref` if a snapshot was synthesized). Create the
file with a `# Project Memory Index` heading if it does not exist. Append-only —
never modify existing entries. See `contracts/agentii-md-schema.md`.
