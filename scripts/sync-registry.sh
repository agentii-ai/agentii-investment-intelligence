#!/usr/bin/env bash
# Bootstrap / refresh skill-registry.yaml from on-disk skills (spec 039 A1, FR-008/FR-009).
# Thin wrapper over scripts/sync_registry.py. Preserves quality scores + enrichment
# history across re-syncs; refreshes structural fields from disk.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${HERE}/sync_registry.py" "$@"
