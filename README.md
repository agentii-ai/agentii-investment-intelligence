# agentii-investment-intelligence

**Agent-use-ready financial data for AI agents.** SEC filings, clinical trials, FDA approvals, FAERS, earnings, and company profiles — optimized for LLM consumption with gold-label signal extraction.

[![Apache 2.0 License](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)

> This repository ships **two distribution surfaces** mirroring the [`anthropics/financial-services`](https://github.com/anthropics/financial-services) pattern:
> 1. **MCP server** (this README's Quick Install) — raw MCP for any LLM client / Claude API / custom agent harness, distributed via `tools/`.
> 2. **Marketplace plugin** — opinionated skills + slash commands + managed-agent cookbook, distributed via `plugins/` and `marketplace.json`. Primary target: **Claude Cowork**. Secondary: Claude Code / OpenCode / Goose / Codex / OpenClaw via the Agent Skills standard. See [Install as marketplace plugin](#install-as-marketplace-plugin-claude-cowork-primary) below.
>
> Both surfaces share the same `mcp.agentii.ai` data plane and `AGENTII_API_KEY` credential.

## Install as MCP server (any LLM client) — Quick Install by CLI agent

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

## Install as marketplace plugin (Claude Cowork primary)

For users running **Claude Cowork** (or Claude Code / OpenCode / Goose / Codex / OpenClaw) who want the full skills + slash-commands + managed-agent cookbook bundle:

```sh
claude plugin marketplace add agentii-ai/agentii-investment-intelligence
claude plugin install equity-research-core      # 8 dimension skills, 8 slash commands
claude plugin install business-intelligence     # 5 BI skills, 5 slash commands
claude plugin install industry-analysis         # 4 industry skills, 4 slash commands
claude plugin install models-and-pitches        # 7 modeling skills, 6 slash commands (Excel/PPT)
claude plugin install agentii-equity-agent      # one-shot bundle: all 24 skills + 23 commands + system prompt
```

Each vertical is **independently installable** (a sell-side analyst may install only `equity-research-core`; a corp-strategy team may install `business-intelligence + industry-analysis`). The `agentii` MCP entry is replicated byte-identically across each vertical's `.mcp.json` from `contracts/mcp-canonical.json`.

For **Claude Cowork managed-agent deployment** (headless / server-side / Claude-for-M365), see [`managed-agent-cookbooks/agentii-equity-agent/`](./managed-agent-cookbooks/agentii-equity-agent/).

For **slash-command invocation syntax** (`--mode=` / `--modes=` / `--peers=`), see [`docs/commands/MODE_SYNTAX.md`](./docs/commands/MODE_SYNTAX.md).

## Get an API Key

**[agentii.ai](https://agentii.ai)** — 7-day free trial, 1,000 credits, no credit card.

## License

Apache-2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE) for upstream attribution (the `models-and-pitches` vertical ports skills from `anthropics/financial-services` (Apache-2.0) per spec 023 FR-017a/b).
