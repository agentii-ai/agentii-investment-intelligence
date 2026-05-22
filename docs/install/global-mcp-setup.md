# Global MCP Setup — One-Time Configuration

The recommended setup loads agentii MCP tools on **every** Claude Code session, from **any** directory. No per-project `.mcp.json` files needed.

## Claude Code MCP Resolution Hierarchy

Claude Code checks MCP config in this order (highest to lowest priority):

| Priority | Config | Scope |
|----------|--------|-------|
| 1 | `--mcp-config <path>` CLI flag | Single invocation |
| 2 | `./.mcp.json` (project root) | Current project (team-shared) |
| 3 | `~/.claude.json` → `projects.<path>.mcpServers` | Per-project personal |
| **4** | **`~/.claude.json` → `mcpServers`** | **Global — all projects** ← use this |
| 5 | `~/.claude/mcp.json` | Legacy (deprecated) |

## One-Command Setup

```bash
# Set your API key (add to ~/.zshrc for persistence)
export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE

# Register agentii globally
claude mcp add-json --scope global agentii \
  '{"type":"http","url":"https://mcp.agentii.ai/mcp","headers":{"Authorization":"Bearer ${AGENTII_API_KEY}"}}'
```

This writes to `~/.claude.json` under the top-level `mcpServers` key. All Claude Code sessions automatically discover 20 agentii tools.

## Verify

```bash
# Check registration
claude mcp list | grep agentii

# Start Claude Code and verify tools
claude
> tools/list
# Expected: 20 tools including search_documents, search_xbrl_facts, get_company_financials, etc.
```

## How It Works

1. `claude mcp add-json` writes the MCP server config to `~/.claude.json`
2. `${AGENTII_API_KEY}` is expanded from your environment at Claude Code startup
3. The MCP server at `mcp.agentii.ai/mcp` speaks JSON-RPC 2.0 with SSE transport
4. Auth is forwarded as `Authorization: Bearer <key>` (also accepts `X-API-Key`)

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `✘ not authenticated` | Key not set or expired | `export AGENTII_API_KEY=sk_live_...` then restart Claude Code |
| `tools/list` shows 0 tools | MCP server unreachable | `curl https://mcp.agentii.ai/health` — should return `{"status":"ok","tools":20}` |
| `${AGENTII_API_KEY}` not expanded | Env var set after Claude Code started | Restart Claude Code after setting the env var |
| No tools in project directory | Using old `.mcp.json` instead of global config | Remove project `.mcp.json` — global `~/.claude.json` takes priority |

## Plugin Bug Workaround (Claude Code v2.1.143)

Claude Code v2.1.143 has a known bug ([GitHub issue #15178](https://github.com/anthropics/claude-code/issues/15178)) where `claude plugin install` does not inject skills/commands into the runtime. If `/agentii:recent-quarter` shows "no command" after installing the plugin marketplace:

```bash
# Copy skills into your project's .claude/ directory
bash /path/to/agentii-investment-intelligence/scripts/copy-skills-local.sh

# Restart Claude Code
```

This copies `skills/agentii/` into `.claude/skills/agentii/`, which Claude Code reads directly (bypassing the plugin system). The directory structure creates the `/agentii:<name>` namespace automatically.

## Removing

```bash
claude mcp remove agentii
```

## Alternative: Per-Project `.mcp.json`

If you prefer per-project configuration (e.g., for CI/CD or containerized environments), copy the snippet below into your project root as `.mcp.json`:

```json
{
  "mcpServers": {
    "agentii": {
      "type": "http",
      "url": "https://mcp.agentii.ai/mcp",
      "headers": { "Authorization": "Bearer ${AGENTII_API_KEY}" }
    }
  }
}
```

Tools load only when Claude Code starts in that directory. The global `~/.claude.json` approach is recommended for daily use.
