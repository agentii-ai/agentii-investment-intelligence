#!/usr/bin/env bash
# Build the 24-skill beachhead from the canonical plugin directories.
# Copies (does not symlink) so marketplace validation can read plugin.json.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
for p in equity-research-core bio-pharm; do
  rm -rf "$HERE/plugins/$p"
  mkdir -p "$HERE/plugins/$p"
  rsync -a --exclude='.DS_Store' --exclude='__pycache__' \
    "$REPO/plugins/vertical-plugins/$p/" "$HERE/plugins/$p/"
  echo "copied $p"
done

# Normalize marketplace-facing metadata for a strict-clean validation.
python3 - "$HERE/plugins/equity-research-core/.claude-plugin/plugin.json" \
          "$HERE/plugins/bio-pharm/.claude-plugin/plugin.json" <<'PY'
import json, sys
erc, bio = sys.argv[1], sys.argv[2]
d = json.load(open(erc))
d.pop("agentii_api_version", None)  # canonical custom field; Claude ignores it
json.dump(d, open(erc, "w"), indent=2); open(erc, "a").write("\n")
d = json.load(open(bio))
d.setdefault("author", {"name": "agentii-ai", "url": "https://agentii.ai"})
json.dump(d, open(bio, "w"), indent=2); open(bio, "a").write("\n")
PY

echo "beachhead built: $HERE"
