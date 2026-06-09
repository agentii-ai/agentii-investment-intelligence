# Partner-Built Plugins (Reserved — v1.0 empty)

This directory reserves the namespace for partner-contributed plugins that
extend `agentii-investment-intelligence` with proprietary data sources,
domain-specific analytics, or specialized modeling tools .

**Status at v1.0**: The partner-built directory is empty. No partner plugins
ship with the v1.0 release. `scripts/validate-partner-plugin.py` enforces this
invariant: `marketplace.json` MUST NOT contain any entry with
`partner_built: true` at v1.0 .

## Submission process

1. Read [partner-plugin-spec.md](./partner-plugin-spec.md) for mandatory
 technical requirements.
2. Fork `agentii-ai/agentii-investment-intelligence`, add your plugin under
 `plugins/partner-built/<your-slug>/`.
3. Include a `partner-plugin-license-attestation.md` with your plugin's
 license, data-source attribution, and a declaration that your MCP server
 honors independent authentication (i.e., your API keys, not
 `AGENTII_API_KEY`).
4. Open a pull request. Label it `partner-plugin-review`.

## Review SLA

- First acknowledgment within 5 business days.
- Technical review (MCP reachability, license check, tool-name collision check)
 within 10 business days.
- Editorial review (methodology soundness, citation discipline, /b
 compliance) within 15 business days.
- v1.x merge if approved; v1.0 accepts no partner plugins.

## Curation criteria

- MCP server independently deployed by partner and reachable over HTTPS.
- Partner holds valid license for any upstream data source the plugin exposes.
- Zero tool-name collisions with first-party `agentii.*` namespace.
- Passes `scripts/validate-partner-plugin.py` lint.
- SKILL.md follows the four-verb taxonomy (`search_`, `get_`, `list_`, `read_`)
 and citation format.
- License-compatible with Apache 2.0 (this package's license).
