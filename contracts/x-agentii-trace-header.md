# X-Agentii-Trace Header Contract (v1.1)

Agent call lineage tracing header for correlating API calls to specific agents and sub-agents within a user conversation.

**v1.1 (spec 060, 2026-09-21)** — reconciled with the deployed code. v1.0 described a mechanism that was never running: a Redis-minted run_id, a `depth` and `user_id` the caller sends, and a durable table that received no rows. Read this section before implementing from anything else. See "What changed in v1.1" at the end for the specific diff.

## Header Name

`X-Agentii-Trace`

## Format

Semicolon-separated key=value pairs. **Four fields are carried on the wire; two are not.**

```
X-Agentii-Trace: run_id={id}; agent={name}; parent={name}; instance={label}
```

`depth` and `user_id` do not appear in the header. They are platform values, derived or looked up server-side (below). A header that carries either is not rejected — the platform ignores them, which is why a caller cannot influence its own audit record.

## Fields

Six fields make up a trace record. Two of them are never sent by a caller.

| Field | On the wire? | Source | Format | Description |
|-------|--------------|--------|--------|-------------|
| `run_id` | Yes | MCP, **minted once per conversation** at `initialize` | `run-{36-stamp}{36-counter}{4-random}` | Per-conversation identifier. NEVER a UUID — a short id saves LLM context tokens. |
| `agent` | Yes | LLM agent (skill Preflight instruction) — or the MCP proxy, where the caller declared none | kebab-case skill name (e.g. `ratio-analysis`, `dcf-model`, `retrieval-subagent`); or `mcp:{tool_name}` when proxy-supplied | Which agent/skill made this call. A call the proxy executes supplies `mcp:{tool_name}` **only** when the caller's header carries no `agent`, and never overwrites one that does (2026-09-23; see `x-agentii-trace-delivery.md` § Step 3 for why the actor and not only the run). |
| `parent` | Yes | LLM agent | kebab-case parent agent name | Parent agent that spawned this agent. Omitted by root agents. |
| `instance` | Yes | LLM agent (orchestrator), optional | `{agent}-{n}` (e.g. `ratio-analysis-3`) | Disambiguates parallel siblings of the same agent type. Omitted when single instance; the platform **completes** it when it can see siblings the caller did not label. **Depth 0 counts**: a root agent's repeated calls in one run are siblings of one another, and are labelled `{agent}-2`, `{agent}-3`, … (measured 2026-09-23 — one composition tool made 38 root calls under one agent and the completion never ran for them, because the derivation returned early for a root). Best-effort by design: the count comes from the run's records as they exist when the call arrives, so two calls that are genuinely simultaneous can receive the same label — treat a label as a disambiguator, never as a unique key. |
| `depth` | **No** | **Platform-derived** | integer, 0-based | Nesting level, walked from the run's own recorded structure. NOT read from the header, and NOT stored as a caller claim — FR-131 is explicit that it is derived, because a trusted depth produces a tree that looks right. |
| `user_id` | **No** | **Server-side, from the API key** | internal user ID | NEVER on the wire, NEVER in LLM context. Accepting an identity from a caller would let a client attribute its calls to another account. |

## Examples

**Root agent (no parent):**
```
X-Agentii-Trace: run_id=run-lx8f2a9k4q; agent=equity-research
```

**Sub-agent with parent:**
```
X-Agentii-Trace: run_id=run-lx8f2a9k4q; agent=ratio-analysis; parent=equity-research
```

**Parallel sub-agents with instance disambiguation:**
```
X-Agentii-Trace: run_id=run-lx8f2a9k4q; agent=ratio-analysis; parent=equity-research; instance=ratio-analysis-1
X-Agentii-Trace: run_id=run-lx8f2a9k4q; agent=ratio-analysis; parent=equity-research; instance=ratio-analysis-2
```

**Untraced (header absent, or present without a `run_id`):**
```
X-Agentii-Trace: agent=untraced
```

A call arriving with no usable `run_id` is recorded as untraced. It is **never** handed a fresh run id to fill the gap: an invented id would silently start a second, orphaned run for a conversation that already has one, which is precisely the fragmentation this contract exists to prevent.

## Storage Architecture

### Hot tier: Redis (Upstash)

One sorted set per run, 7-day TTL. The member is a **five-field** tuple, canonically `agent|parent|instance|endpoint|status`; it deliberately does not carry `depth`, because depth is a property of the whole run and is written onto the record once, at the end of the request that produced it:

```
ZADD trace:{run_id} {timestamp_ms} "{agent}|{parent}|{instance}|{endpoint}|{status}"
EXPIRE trace:{run_id} 604800
```

Query: `ZRANGE trace:run-lx8f2a9k4q 0 -1 WITHSCORES` → all spans, real-time, ~1ms.

This set is also the input the depth derivation reads (see below): it already holds the parent links the walk needs, so no second read path exists.

### Durable store: Supabase `usage_logs`

The trace record is a column set on the **usage row** — `run_id`, `agent_name`, `parent_agent`, `depth` (the derived value), `instance`, `derived_at`. There is one row per API call and it carries both the metering and the lineage, so the archive and the billing view can never disagree about how many calls a run made.

Written by `apps/web/app/api/cron/flush-usage/route.ts`, which drains the Redis buffer that the API appends to after each authenticated `/v1/` call. Additive columns land via `apps/web/supabase/migrations/20260921_0035_trajectory_record.sql` (`ingested_at`, `instance`, `derived_at`, `params`).

### Fallback: Vercel function logs

The raw `X-Agentii-Trace` header is captured in every Vercel function invocation log. Survives Redis and Supabase failures, and is the last resort for reconstructing a run whose hot entry has expired before its rows were read.

Neon is explicitly NOT used for tracing data — tracing is operational/user data, not product data.

## Derivation

Depth and the sibling label are computed once per request by the API's `derive.ts`, between the trace and usage middleware:

1. Read this run's spans from the hot tier.
2. Walk the parent chain to find the depth of the calling agent. A root is depth 0 by definition.
3. If a declared parent appears in **no** record, the depth is left at the derivable minimum (a declared parent implies at least one level) and `derived_at` is left unset. The anomaly stays visible; a plausible-looking guessed depth does not.
4. A record sharing an agent **and** a parent with an earlier record is a parallel sibling. The caller's label is kept when supplied, since it may be more meaningful than a positional one; a label the platform supplies completes the caller's omission but is never the reason two siblings are distinguishable.

`derived_at` records that the depth on that row is a platform value rather than a caller-declared one.

## Tree Reconstruction

Real-time: group hot-tier members by `instance` to find parallel siblings; match `parent` → `agent` to rebuild the tree, exactly as the derivation walk does.

Long-term: `SELECT * FROM usage_logs WHERE run_id = $1 ORDER BY timestamp` → recursive traversal on `parent_agent`.

Parallelism detection: `SELECT instance, COUNT(*) FROM usage_logs WHERE run_id = $1 AND parent_agent = $2 GROUP BY instance HAVING COUNT(*) > 1`.

## Credit Attribution

Post-hoc calculation. The record stores endpoint, status, timestamp and the lineage — sufficient for workflow reconstruction. Credits computed by query:

```sql
SELECT run_id, agent_name, COUNT(*) AS call_count, SUM(response_time_ms) AS total_ms
FROM usage_logs
WHERE user_id = $1 AND timestamp > NOW() - INTERVAL '30 days' AND status_code = 200
GROUP BY run_id, agent_name
ORDER BY run_id, agent_name;
```

Multiply `call_count` by per-endpoint credit pricing for billing.

## What Changed in v1.1

| v1.0 said | v1.1 says | Why |
|-----------|-----------|-----|
| `depth` and `user_id` sent by the caller | Neither is on the wire | FR-131 forbids trusting a depth; accepting an identity from a caller would let a client attribute calls to another account. The deployed middleware never read either. |
| `run_id` minted by a Redis counter (`run-42`) | Minted once per conversation by the MCP, no Redis | The deployed MCP (mcp-agentii) has **no environment variables** by design, so a Redis-backed counter could not run there at all. |
| Durable store: a dedicated traces table | `usage_logs` — lineage is a column set on the usage row | The dedicated table received no rows. One row per call carrying both metering and lineage means the archive and the billing view can never disagree about how many calls a run made. |
| Depth "auto-derived by middleware" (stated once, in prose) | Derivation specified: read path, walk, and the unresolvable-parent outcome | The prose was right and unimplemented. An unspecified fallback is where a wrong depth gets invented. |

## Cross-Spec Dependencies

- **spec 019**: Hono `trace.ts` + `derive.ts` middleware, Redis hot tier
- **spec 022**: No changes (Neon not used for tracing)
- **spec 023**: Skill Preflight instruction in all SKILL.md files, CI validation (Checks 18 and 19)
- **spec 060**: depth derivation, archive, `usage_logs` record shape, this reconciliation
