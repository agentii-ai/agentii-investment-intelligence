# Prose Safety Constraints

This document codifies mandatory prose-safety constraints for every SKILL.md
and command file in the package. `scripts/validate-prose-safety.py` enforces
these at CI time.

## Mandatory constraints

Skill bodies (prose outside `!command` preflight blocks and fenced code blocks)
MUST NOT contain:

### 1. Shell-variable forms

- `$VAR`, `${VAR}`, `$(cmd)` forms are forbidden in prose.
- **Rationale**: Claude Code and similar hosts do not expand shell variables
 in Markdown prose; users seeing `$API_KEY` in documentation may attempt to
 copy-paste it as-is into their shell.

### 2. Absolute filesystem paths

- No `/usr/`, `/home/`, `/var/`, `/etc/`, `/tmp/` prefixes in prose.
- **Rationale**: Paths are user-environment-specific. Use symbolic references
 (e.g., "your Claude config directory") or relative paths.

### 3. Backtick-wrapped shell tokens in prose body

- `` `npm install` ``, `` `pip install` ``, `` `brew install` `` as inline
 runnable commands in prose are forbidden.
- **Rationale**: Users may copy the backtick content and run it blindly. Use
 fenced code blocks with explicit language tags for commands.

### 4. Dependency-folder names

- `node_modules`, `__pycache__`, `.venv`, `dist/`, `build/`, `target/` in prose
 are forbidden outside of `.gitignore` examples or troubleshooting sections.
- **Rationale**: These are implementation-detail artifacts; they should not
 appear in user-facing methodology documentation.

## Exemptions

The following contexts are exempt from the above constraints:

1. **`!command` preflight blocks** — the `## Preflight` section may contain
 literal shell snippets for health probing.
2. **Fenced code blocks** with language tags (` ```bash `, ` ```python `, etc.)
 — any content, since users will clearly see it as executable code.
3. **HTML comments** (`<!-- ... -->`) — not rendered to users.
4. **Frontmatter** — YAML frontmatter is parsed as metadata, not prose.

## Enforcement

- `scripts/validate-prose-safety.py` runs against every `SKILL.md`, command
 `.md`, and cookbook prompt file in CI.
- Violations fail the build.
- Developers can run the script locally before committing:
 `python3 scripts/validate-prose-safety.py`
