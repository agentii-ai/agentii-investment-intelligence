# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a vulnerability

**Do not open a public issue.** Contact the Agentii security owner through the private channel provided by
the publisher account. A public security contact is TBD and must be filled before marketplace submission.

Include:

- affected plugin/skill and version;
- reproduction steps;
- impact assessment;
- any suggested fix.

## Secrets

- This bundle contains **no API keys, tokens, passwords, or customer data**.
- Authentication uses `AGENTII_API_KEY` or OAuth at runtime.
- Do not commit a local `.env` or key file.

## Data access

- The bundle calls the Agentii MCP server; it does not bundle the data itself.
- Telemetry is limited to install/auth/skill-run events; no query text or ticker by default.

## Marketplace review

Before submission, the bundle must pass the marketplace safety scan and a secret scan.
