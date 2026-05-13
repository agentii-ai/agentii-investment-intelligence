# agentii-investment-intelligence

**Agent-use-ready financial data for AI agents.** SEC filings, clinical trials, FDA approvals, FAERS, earnings, and company profiles — optimized for LLM consumption with gold-label signal extraction.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

## Quick Install — Pick your CLI agent

### Claude Code
```sh
mkdir -p ~/.claude && curl -sSL https://raw.githubusercontent.com/agentii-ai/agentii-investment-intelligence/main/adapters/claude-code/.mcp.json | AGENTII_API_KEY="$AGENTII_API_KEY" envsubst > ~/.claude/mcp.json
```

### Codex (OpenAI)
```sh
mkdir -p ~/.codex && curl -sSL https://raw.githubusercontent.com/agentii-ai/agentii-investment-intelligence/main/adapters/codex/codex.json | envsubst > ~/.codex/config.toml
```

### Goose
```sh
mkdir -p ~/.config/goose && curl -sSL https://raw.githubusercontent.com/agentii-ai/agentii-investment-intelligence/main/adapters/goose/profiles.yaml | envsubst >> ~/.config/goose/profiles.yaml
```

### Claude Cowork
```sh
curl -sSL https://raw.githubusercontent.com/agentii-ai/agentii-investment-intelligence/main/adapters/claude-cowork/connector.json | envsubst > ~/.claude-cowork/connectors/agentii.json
```

### OpenClaw
```sh
curl -sSL https://raw.githubusercontent.com/agentii-ai/agentii-investment-intelligence/main/adapters/openclaw/openclaw.json | envsubst > ~/.openclaw/skills/agentii.json
```

## Verify

Restart your agent, then type: `/agentii-health`

Expected: `ok, plan=trial, 1000 credits`

## Tools

| Tool | Description | Credits |
|---|---|---|
| `search_documents` | Search SEC filings by ticker, form type | 1 |
| `get_company_profile` | Company overview + pipeline summary | 1 |
| `list_coverage` | Available data sources for a ticker | 1 |
| `read_source_outline` | Document table of contents | 1 |
| `read_source_pages` | Full page content by page numbers | 1/page |
| `search_keyword_in_source` | Full-text search within a document | 2 |
| `search_unified` | Cross-source search | 3 |

## Get an API Key

**[agentii.ai](https://agentii.ai)** — 7-day free trial, 1,000 credits, no credit card.

## License

MIT © agentii-ai
