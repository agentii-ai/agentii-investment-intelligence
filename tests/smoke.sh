#!/bin/bash
# REQUIRED smoke test (T065): verify agentii API health endpoint
set -euo pipefail

BASE_URL="${AGENTII_BASE_URL:-https://api.agentii.ai}"
API_KEY="${AGENTII_API_KEY:-}"

if [ -z "$API_KEY" ]; then
  echo "SKIP: AGENTII_API_KEY not set"
  exit 0
fi

echo "Testing health endpoint at $BASE_URL/v1/health ..."
HEALTH=$(curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/v1/health")

if echo "$HEALTH" | grep -q '"status":"ok"'; then
  echo "✓ Health check passed: $HEALTH"
else
  echo "✗ Health check failed: $HEALTH"
  exit 1
fi

echo "✓ Smoke test passed"
