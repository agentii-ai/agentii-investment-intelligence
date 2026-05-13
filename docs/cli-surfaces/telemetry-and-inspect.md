# CLI: `agentii plugin telemetry` + `agentii plugin inspect`

Documents the two CLI subcommands that expose local telemetry state and recent
plugin activity per FR-053a and FR-035.

## `agentii plugin telemetry`

Controls and inspects the local telemetry subsystem.

### Flags

| Flag | Description |
|---|---|
| `--show-config` | Print current `~/.agentii/config.json` `telemetry` block |
| `--show-recent N` | Show the most recent N telemetry events from `~/.agentii/logs/telemetry.jsonl` (default N=50) |
| `--purge` | Truncate `telemetry.jsonl` and all rotated logs; re-initialize with a new install_uuid |
| `--enable-server-export <off\|anonymous\|identified>` | Set `telemetry.tier` and `telemetry.server_export` |
| `--disable-server-export` | Set `telemetry.server_export: false` (alias for `--enable-server-export off`) |

### Examples

```sh
agentii plugin telemetry --show-config
agentii plugin telemetry --show-recent 100
agentii plugin telemetry --enable-server-export anonymous
agentii plugin telemetry --disable-server-export
```

## `agentii plugin inspect --recent`

Shows the most recent skill/MCP activity at a user-friendly granularity
(FR-035).

### Flags

| Flag | Description |
|---|---|
| `--recent [N]` | Show the most recent N plugin invocations (default N=50) with: skill name, MCP tool used, latency, resolved binding source for office calls (plugin-mcp / cowork-office-js / user-mcp per FR-043) |
| `--capabilities` | Print detected auth_modes + agentii_api_version from the MCP server (FR-006a) |

### Examples

```sh
agentii plugin inspect --recent 20
agentii plugin inspect --capabilities
```

## Storage

- Telemetry log: `~/.agentii/logs/telemetry.jsonl`
- Config: `~/.agentii/config.json`
- Event schema: `~/.agentii/logs/telemetry.schema.json` (installed at first run from this package's `contracts/telemetry.schema.json`)

### Rotation rules

- Rotate when `telemetry.jsonl` reaches 100 MB **OR** age exceeds 30 days (whichever first).
- Retain up to 5 rotated files: `telemetry.jsonl.1` … `telemetry.jsonl.5`.
- Rotated files are gzipped after age 7 days.

### Permissions

- Directory `~/.agentii/logs/` is `0700`.
- File `~/.agentii/logs/telemetry.jsonl` is `0600`.
- Violations of these permissions cause the CLI to refuse to read/write telemetry until corrected (defense against shared-filesystem leakage).

## Redaction guarantees (FR-053b)

The following field names are forbidden in any telemetry event:

- `ticker`, `symbol`, `tickers`, `symbols`
- `prompt`, `user_prompt`, `system_prompt`
- `model_response`, `llm_response`, `completion`
- `evidence_pack`
- `xlsx_spec`, `pptx_spec`
- `file_path`, `absolute_path`
- `citation_uri`, `citation`
- `document_chunk_id`, `chunk_id`, `page_content`
- `email`, `user_id`, `username`
- `api_key`, `apiKey`, `x-api-key`

`scripts/validate-telemetry-redaction.py` scans all emission points in CI and fails the build on any forbidden field reference.
