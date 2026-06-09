# Session Archival Format

Session transcripts are stored as archival records in `sessions/{YYYY-MM-DD}/`. They contain the full agent conversation transcript and are accessed only via explicit `read_session` tool call. Sessions are NOT auto-loaded into agent context (transcripts can exceed 50K tokens).

## Directory Structure

```
sessions/
├── INDEX.md # Auto-loaded session index (~1KB)
├── 2026-06-03/
│ ├── 0930_ses_a1b2c3d4.jsonl # Morning LLY analysis session
│ ├── 1430_ses_e5f6g7h8.jsonl # Afternoon comps session
│ └── 1700_ses_i9j0k1l2.jsonl # End-of-day synthesis session
└── 2026-06-02/
 └── 1100_ses_m3n4o5p6.jsonl
```

## Session File Format

Each session file is JSONL (one JSON object per line = one agent turn):

```jsonl
{"role":"user","content":"/agentii:recent-quarter LLY","ts":"2026-06-03T09:30:00Z"}
{"role":"agent","content":"Running recent-quarter analysis for LLY...","tool_calls":[{"tool":"search_xbrl_facts","params":{"ticker":"LLY","concept":["Revenues","NetIncomeLoss"],"fiscal_year":[2026]}}],"ts":"2026-06-03T09:30:05Z"}
{"role":"tool","tool":"search_xbrl_facts","result":{"facts":[{"concept":"us-gaap:Revenues","value":18500000000,"period":"2026Q1"}]},"ts":"2026-06-03T09:30:08Z"}
```

## sessions/INDEX.md Format

The INDEX.md file provides a lightweight catalog of all sessions. It IS auto-loaded on startup (negligible token cost, typically <1KB):

```markdown
# Session Index

| Date | Session ID | Tickers | Skills | Summary |
|------|-----------|---------|--------|---------|
| 2026-06-03 | ses_a1b2c3d4 | LLY | recent-quarter, dcf | Q1 revenue $18.5B, DCF suggests 15% upside |
| 2026-06-03 | ses_e5f6g7h8 | LLY, NVO, PFE | comps | LLY trades at 22x EV/EBITDA vs peer median 18x |
| 2026-06-02 | ses_m3n4o5p6 | NVDA | recent-quarter, competitive | Data center revenue +40% QoQ, CUDA moat intact |
```

## Memory System Integration

| Layer | File | Auto-Load? | Purpose |
|-------|------|------------|---------|
| Index | `agentii.md` | Yes  | Project memory index — what analyses exist, key conclusions |
| Snapshots | `snapshots/{ticker}/{date}_thesis.md` | Yes  | Point-in-time investment thesis — auto-loaded for context restoration |
| Session Index | `sessions/INDEX.md` | Yes  | What sessions exist — lightweight catalog |
| Raw Sessions | `sessions/{date}/{time}_{id}.jsonl` | No | Full transcripts — accessed via `read_session` tool on demand |

## read_session Tool

Agents access session history via the `read_session` tool:

```
read_session(session_id: string, date?: string, range?: {start: int, end: int}) → SessionTranscript
```

- `session_id`: The session ID from INDEX.md
- `date`: Optional date filter (defaults to searching all dates)
- `range`: Optional line range for partial reads (avoids loading 50K+ token transcripts)

## Cross-Reference

- ****: agentii.md memory index
- ****: Two-tier output model with snapshots
- ****: This contract
