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
2. **Bottom "Citations" section (OPTIONAL) = roll-up index** — a non-duplicative
   index of the sources already linked inline, not the primary citation surface.
   Optional because item 1 is the whole standard: an artifact whose every fact
   carries its link needs no second hop, and a roll-up that repeats a link the
   prose already gives is duplication rather than an index. Changed 2026-09-25
   (spec 062 `T084`) — the `equity-research-core` nine dropped it as a required
   element, and the owner's rule is the link *beside* the fact.
3. **Final Summary (TUI)** — after writing the deliverable, the closing chat message
   MUST be a summary a reader can use **without opening the file**, in this order:
   the **title** (`{ticker} · {skill} · {as_of}`); the **key conclusions** (3–5
   one-liners, each carrying its `[FACT]`/`[DEDUCTED]`/`[VIEW]` tag); the **key
   metrics** (3–6 numbers a reader would repeat to someone else); the deliverable's
   own **Executive Summary**; and a compact **Key Citations** list — the headline
   **5–10** facts, each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}`
   link, so the user can cmd+click straight to the exact SEC page. Keep it terse.
   **It is a summary, not a copy**: every headline in the chat must already appear in
   the file, beside its link, and nothing may appear in the chat that the file does
   not carry.

   **The five parts and the 5–10 bound are the `equity-research-core` nine's shape, and
   they are the standard** (recorded 2026-09-25, spec 062 `T084`). The nine previously
   declared only the Key Citations part; the other four existed in the owner's
   requirement and in the artifacts, not in any skill. **Known divergence, not repaired
   here**: 40 skills in the other vertical plugins declare `### Key Citations` with a
   **0–10** bound (canonical wording in `CHANGELOG.md`'s FR-081 entry), and 0–10 admits
   an empty list where 5–10 does not. Aligning them is the kit's work, not this spec's.

Never emit a vague `{Citations}` / `{Source(s)}` placeholder or a
`_(cite source filing in standard agentii citation format at runtime)_` hint:
write the explicit `/v/` link adjacent to the fact.

## agentii.md append

After writing the output file, append a YAML block to `agentii.md` at the
workspace root with `ticker`, `date`, `skill`, `output_file`, and
`key_conclusions` (plus `snapshot_ref` if a snapshot was synthesized). Create the
file with a `# Project Memory Index` heading if it does not exist. Append-only —
never modify existing entries. See `contracts/agentii-md-schema.md`.
