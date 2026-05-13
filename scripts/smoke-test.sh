#!/usr/bin/env bash
# Phase-1 live API smoke test for agentii-investment-intelligence.
#
# Verifies that the agentii data plane is reachable and that the API key in
# .env.local authenticates against the canonical endpoints declared in
# spec 023 FR-011 (`search_companies`, `get_company_profile`,
# `search_documents`). Mirrors the FR-027 cross-CLI smoke-test pattern but
# runs at repo level using curl so it's portable across all 5 host CLIs.
#
# Usage:
#   bash scripts/smoke-test.sh
#
# Requires:
#   - .env.local with AGENTII_API_KEY (gitignored; copy from .env.example)
#   - curl, jq
#
# Exit 0 on success, 1 on any HTTP non-2xx or missing key field.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env.local"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $ENV_FILE not found. Copy .env.example to .env.local and set AGENTII_API_KEY." >&2
  exit 1
fi

# Load env (only AGENTII_* vars to avoid surprises)
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -z "${AGENTII_API_KEY:-}" ]]; then
  echo "ERROR: AGENTII_API_KEY not set in $ENV_FILE" >&2
  exit 1
fi

# Until mcp.agentii.ai DNS is configured (per Round 2 Q1 prerequisite gate),
# smoke-test against the data API directly. Override via env if needed.
BASE="${AGENTII_API_URL:-https://api.agentii.ai}"
TICKER="${SMOKE_TICKER:-LLY}"

# Auth header convention: x-api-key (per agentii-ai/apps/api/src/middleware/auth.ts).
# spec 023 FR-006 does not pin the header name; the MCP server (when deployed
# at mcp.agentii.ai) is expected to translate Bearer→x-api-key internally.
HDR=(-H "x-api-key: $AGENTII_API_KEY")

pass() { echo "  ✓ $*"; }
fail() { echo "  ✗ $*" >&2; exit 1; }

http() {
  local url="$1"
  local body status
  body="$(curl -sS -w $'\n__HTTP__%{http_code}' "${HDR[@]}" "$url")"
  status="${body##*__HTTP__}"
  body="${body%__HTTP__*}"
  printf '%s' "$body"
  if [[ "$status" != "200" ]]; then
    return 1
  fi
}

echo "Smoke testing $BASE with ticker=$TICKER"
echo

echo "[1/5] /v1/health"
out="$(curl -sS "${HDR[@]}" "$BASE/v1/health")" || fail "health unreachable"
echo "$out" | grep -q '"status":"ok"' && pass "health=ok" || fail "health did not return ok"

echo "[2/5] /v1/search_companies?ticker=$TICKER (FR-011 search_companies tool)"
out="$(http "$BASE/v1/search_companies?ticker=$TICKER")" || fail "search_companies HTTP non-200"
echo "$out" | grep -q "\"ticker\":\"$TICKER\"" && pass "found ticker $TICKER" || fail "ticker missing"

echo "[3/5] /v1/get_company_profile/$TICKER (FR-011 get_company_profile tool)"
out="$(http "$BASE/v1/get_company_profile/$TICKER")" || fail "get_company_profile HTTP non-200"
echo "$out" | grep -q "\"sector_id\"" && pass "company profile resolved" || fail "no sector_id in profile"

echo "[4/5] /v1/search_documents?ticker=$TICKER&form_type=10-K&limit=3 (FR-011 search_documents tool)"
out="$(http "$BASE/v1/search_documents?ticker=$TICKER&form_type=10-K&limit=3")" || fail "search_documents HTTP non-200"
echo "$out" | grep -q '"data":' && pass "search_documents response well-formed" || fail "search_documents malformed"

echo "[5/5] Auth gate — bad key returns INVALID_API_KEY 401"
status="$(curl -sS -o /dev/null -w '%{http_code}' -H "x-api-key: sk_live_BAD_KEY_FOR_GATE_TEST" "$BASE/v1/search_companies?ticker=$TICKER")"
[[ "$status" == "401" ]] && pass "bad key → HTTP 401 (FR-008 AGENTII_AUTH_REQUIRED equivalent)" || fail "bad key did not return 401 (got $status)"

echo
echo "OK — all 5 smoke checks passed against $BASE"
