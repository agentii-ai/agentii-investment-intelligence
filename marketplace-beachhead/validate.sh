#!/usr/bin/env bash
# Validate the 24-skill beachhead for Claude and prepare the Codex check.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Claude strict validation =="
claude plugin validate "$HERE" --strict

echo "== Secret scan (manifests/config only) =="
if grep -RInE '(\bsk-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9]{20,})' \
  "$HERE/.claude-plugin" "$HERE/.agents" "$HERE/plugins" 2>/dev/null; then
  echo "Potential secret found — stop." >&2
  exit 1
else
  echo "No embedded secret pattern found."
fi

echo "== Codex install check (isolated HOME) =="
TMP="/tmp/codex-beachhead-check"
rm -rf "$TMP"; mkdir -p "$TMP"
HOME="$TMP" codex plugin marketplace add "$HERE"
HOME="$TMP" codex plugin add equity-research-core@agentii-research-beachhead
HOME="$TMP" codex plugin add bio-pharm@agentii-research-beachhead
HOME="$TMP" codex plugin list

echo "== Done =="
echo "Claude:  claude plugin marketplace add $HERE"
echo "Codex:   codex plugin marketplace add $HERE"
