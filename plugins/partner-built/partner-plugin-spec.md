# Partner Plugin Specification (v1.0)

Mandatory technical requirements for partner-contributed plugins in
`plugins/partner-built/`. Enforced by `scripts/validate-partner-plugin.py`.

## 1. Independent MCP server

- Partner MUST ship their own MCP server, deployed on partner-controlled
  infrastructure.
- MCP server MUST expose an HTTPS `/health` endpoint returning 200 in <2s.
- MCP server MUST authenticate with partner-owned credentials, NOT
  `AGENTII_API_KEY`. Partners MAY document their own API-key onboarding flow
  in the plugin README.
- MCP server URL MUST be declared in the plugin's `.mcp.json` as a standalone
  entry (not mixed into the agentii data-plane or office-plane declarations).

## 2. SKILL.md format compliance

- Every partner skill MUST be a `SKILL.md` file following the same structure
  as first-party skills:
  - YAML frontmatter with `name`, `description`, `multi_ticker_semantics`.
  - `## Preflight`, `## Triggers` (≥10 phrases), `## Defaults`,
    `## Methodology`, `## Output Structure`, `## Error Handling`.
- Skill names MUST follow the four-verb taxonomy (`search_`, `get_`, `list_`,
  `read_`).
- Citation format MUST match FR-050 regex if the skill emits citations.

## 3. Tool-name namespace

- Partner skill bodies and command files MAY invoke agentii-MCP tools, but
  MUST NOT declare conflicting tool names.
- Reserved namespace: `agentii.*` is first-party-only.
- Partners SHOULD namespace their own MCP tools as `<partner-slug>.<verb>_<noun>`
  (e.g., `lseg.get_yield_curve`).

## 4. License attestation

- `plugins/partner-built/<slug>/partner-plugin-license-attestation.md` is
  required and MUST contain:
  - Partner organization name and contact.
  - Plugin license (must be Apache 2.0 compatible).
  - Declaration of any upstream data sources and their licenses.
  - Explicit statement that partner holds all rights to distribute the plugin.

## 5. Validation

- `python3 scripts/validate-partner-plugin.py --slug <slug>` MUST exit 0.
- Checks include: MCP-server reachability, license attestation presence,
  tool-name collision scan, SKILL.md structural validity.

## 6. Dependency declarations

- Partner plugins declare agentii-MCP tool dependencies (if any) in
  `<slug>/.claude-plugin/plugin.json` under `dependencies.agentii_tools`.
- Example:
  ```json
  {
    "dependencies": {
      "agentii_tools": ["search_companies", "get_company_profile"]
    }
  }
  ```

## 7. v1.0 invariant

- At v1.0, `marketplace.json` MUST NOT include any partner plugin entries.
- `scripts/validate-partner-plugin.py` FAILs the build if it detects any
  plugin entry with `partner_built: true` in `marketplace.json`.

## 8. Update cadence

- Partners can submit v1.x plugins via PR once v1.0 ships.
- Partner plugins version independently from first-party verticals but must
  declare compatibility with a specific `agentii_api_version`.
