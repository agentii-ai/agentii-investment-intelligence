# Multi-Platform Packaging (spec 039 US7 / Part IV)

**C0 decision matrix** — augment, do not regress. Claude Code is the canonical host;
all other targets are *derived* from the same on-disk SKILL.md, so the currently-working
hosts never regress.

## Supported targets

| Target | Emits | Notes |
|--------|-------|-------|
| `claude-code` | `SKILL.md` | **Canonical** — the source of truth; no transform. Already shipped via `assemble-agentii-namespace.sh` + `docs/install/`. |
| `codex` | `SKILL.md` + `plugin.json` | Codex plugin manifest (name, description, entrypoint, tools). |
| `cowork` | `SKILL.md` + `metadata.json` | Lightweight metadata sidecar. |
| `generic-cli` | `SKILL.md` | Portable host — markdown alone. |

## Invariants (enforced by tests/test_packaging.py)

1. **Placeholders preserved** — `~~macro_data` / `~~market_data` / `~~earnings_data` copied verbatim (connector-agnostic, C1).
2. **Envelope semantics untouched** — bodies are copied, not rewritten.
3. **Reproducible** — sorted keys, no timestamps → re-runs are diff-clean.

## Usage

```bash
# all skills, all targets → packaging/targets/<platform>/<skill>/
bash packaging/export.sh

# selected targets
bash packaging/export.sh --target codex,cowork,generic-cli

# single skill
bash packaging/export.sh --skill plugins/vertical-plugins/macro-strategy/skills/agentii/rate-cycle
```

## Relationship to Skill Seekers

`skillseekers.config.yaml` mirrors the Skill Seekers target layout. The native
`export.py` is the default (self-contained, no external dep); an external Skill Seekers
run can substitute later by consuming the same config. `packaging/targets/` is
build output (gitignored).

## No-regression guarantee

The canonical Claude Code path (`plugins/agentii-plugin/` meta-plugin assembly) is
unchanged by export — export only *reads* SKILL.md and writes under `packaging/targets/`.
The 6 already-supported hosts continue to work exactly as before.
