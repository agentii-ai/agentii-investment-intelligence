# Multi-Platform Export (Codex / Cowork / Generic-CLI)

**spec 039 US7 / Part IV.** Claude Code is the canonical host and needs no export —
install it via `scripts/copy-skills-local.sh` or the meta-plugin. Use export only to run
the same skills on other hosts.

## Generate variants

```bash
# all skills, selected targets → packaging/targets/<platform>/<skill>/
bash packaging/export.sh --target codex,cowork,generic-cli

# one skill
bash packaging/export.sh --skill plugins/vertical-plugins/macro-strategy/skills/agentii/rate-cycle
```

`packaging/targets/` is build output (gitignored) — regenerate any time; re-runs are diff-clean.

## Per-target output

| Target | Files produced | Install |
|--------|----------------|---------|
| `codex` | `SKILL.md` + `plugin.json` | Point your Codex plugin loader at `packaging/targets/codex/<skill>/`. |
| `cowork` | `SKILL.md` + `metadata.json` | Import the skill dir into your Cowork workspace. |
| `generic-cli` | `SKILL.md` | Any Agent-Skills-compatible CLI reads the markdown directly. |

## What is preserved

- **`~~category` placeholders** (`~~macro_data` / `~~market_data` / `~~earnings_data`) — connector-agnostic; your host's `.mcp.json` maps them to concrete tools.
- **AGENT_CONTRACT envelope semantics** — data-tool responses are identical across hosts.
- **Citations** — the `agentii.ai/v/{ticker}/{citation_id}/{page}` links are host-independent.

## No regression

Export only *reads* canonical SKILL.md and writes under `packaging/targets/`. The Claude
Code install path (`plugins/agentii-plugin/`) is never touched, so the 6 already-supported
hosts continue to work unchanged. See `packaging/README.md` for the full decision matrix.
