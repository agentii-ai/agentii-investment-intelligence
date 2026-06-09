# Slash-command Mode & Peer Syntax (v1.0 frozen)

Canonical reference for invoking `agentii-investment-intelligence` slash commands across Claude Code, OpenCode, Goose, Codex, OpenClaw, and Claude Cowork. Frozen at v1.0 per the mode-addressability syntax + Round 4 Q12.

## Invocation Forms

Every slash command of the form `/agentii:<command> <TICKER>` accepts the following four forms:

| Form | Behavior |
|---|---|
| `/agentii:<command> <TICKER>` | Runs the skill's `essentials_modes` curated default subset (declared per-skill in SKILL.md frontmatter; typically 2–3 highest-leverage sub-prompts). |
| `/agentii:<command> <TICKER> --mode=<slug>` | Runs a single named mode. `<slug>` is the slugified `## Mode: <name>` heading from SKILL.md (lowercase, hyphenated, mechanically derived). |
| `/agentii:<command> <TICKER> --modes=<slug1>,<slug2>,<slug3>` | Runs a comma-separated subset of modes. **No spaces** — commas only (survives host-CLI tokenization). |
| `/agentii:<command> <TICKER> --mode=all` | Runs every mode of the dimension. Reserved keyword `all` cannot be used as a real mode slug. |

## Peer-set Argument

Skills with `multi_ticker_semantics: target_with_optional_peers` or `target_with_required_peers` accept `--peers=`:

| Form | Behavior |
|---|---|
| `--peers=<T1>,<T2>,<T3>` | Explicit peer set (comma-separated, no spaces, max 10 peers per Round 3 Q11). |
| (omitted, `optional_peers`) | Auto-resolved top-5 peers from `gold.canonical_entities` ranked by sector + sub-industry + SIC overlap; included as `coverage_attestation.auto_peers[]` in the evidence pack. |
| (omitted, `required_peers`) | Raises `AGENTII_PEERS_REQUIRED` with auto-suggested top-5 peers so the user can re-run. |

## Multi-Ticker Basket (reserved at v1.0)

Basket-positional invocation `/agentii:<command> LLY,NVO,PFE` is parseable today but raises `AGENTII_BASKET_NOT_SUPPORTED` with a roadmap pointer to v1.1. No v1.0 skill declares `multi_ticker_semantics: basket_v1_1`.

## Error Codes

| Code | Trigger |
|---|---|
| `AGENTII_UNKNOWN_MODE` | Unknown mode name. Response includes the valid mode list for that command. |
| `AGENTII_PEERS_REQUIRED` | `target_with_required_peers` skill invoked without `--peers=`. Response auto-suggests top-5 peers. |
| `AGENTII_PEERS_TOO_MANY` | `--peers=` argument exceeds 10 entries (protects retrieval-subagent context budget). |
| `AGENTII_BASKET_NOT_SUPPORTED` | Basket-positional input at v1.0 (reserved for v1.1). |
| `AGENTII_UNKNOWN_TICKER` | Ticker not in launch coverage registry. |
| `AGENTII_AMBIGUOUS_TICKER_ARG` | Argument cannot be disambiguated as ticker vs. mode-slug. |

## Examples

### equity-research-core (`/agentii:dcf` is in `models-and-pitches`; `/agentii:competitive` lives here)

```
/agentii:competitive LLY # essentials_modes default
/agentii:competitive LLY --mode=peer-overview # single mode
/agentii:competitive LLY --modes=peer-overview,market-share # multi-mode
/agentii:competitive LLY --mode=all # full dimension
/agentii:competitive LLY --peers=NVO,PFE,MRK # explicit peer set
```

### business-intelligence

```
/agentii:business-model AAPL # essentials default
/agentii:revenue-decomp AAPL --mode=segment-by-product
/agentii:operational-kpi AAPL --modes=ndr,gross-margin,cac-payback
```

### industry-analysis

```
/agentii:peer-bench LLY --peers=NVO,PFE,MRK,ABBV # required_peers; --peers= mandatory
/agentii:competitive-positioning LLY # auto-resolved peers
/agentii:supply-chain TSLA --mode=tier-1-suppliers
```

### models-and-pitches

```
/agentii:dcf LLY # 5-year DCF, default assumptions
/agentii:dcf LLY --mode=10-year-extended # 10-year DCF per the models-and-pitches vertical optimization
/agentii:comps LLY --peers=NVO,PFE,MRK # comps-analysis: required_peers
/agentii:pitch-deck LLY --mode=ic-memo # specific deliverable kind
```

## Cross-host Compatibility

This syntax works identically across:

- **Claude Code** — slash commands resolved via `.claude-plugin/plugin.json` + `commands/*.md`
- **OpenCode** — skill discovery in `~/.config/opencode/skills/`
- **Goose** — extension install via `goose extension`
- **Codex** — skill-directory copy
- **OpenClaw** — `openclaw add @agentii/investment-intelligence`
- **Claude Cowork** — managed-agent cookbook + steering-examples (primary marketplace target)

Validated by `scripts/validate-mode-syntax.py` (the mode-addressability syntax CI gate).

## See Also

- [Multi-Ticker Semantics (the multi-ticker semantics contract)](../../specs/023-agentii-financial-analysis/spec.md#fr-054)
- [Mode Naming Convention (Round 3 Q12)](../../specs/023-agentii-financial-analysis/spec.md#clarifications)
- [Per-skill `essentials_modes` declaration](../../contracts/agentii-config.schema.json)
