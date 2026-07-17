#!/usr/bin/env bash
# export.sh — multi-platform skill export wrapper (spec 039 US7, T083).
# Thin wrapper over packaging/export.py. Example:
#   bash packaging/export.sh --target codex,cowork,generic-cli
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${HERE}/export.py" "$@"
