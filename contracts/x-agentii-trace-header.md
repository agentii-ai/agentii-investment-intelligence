# X-Agentii-Trace Header Contract (v1.0, frozen per FR-106)

Agent call lineage tracing header for correlating API calls to specific agents and sub-agents within a user conversation.

## Header Name

`X-Agentii-Trace`

## Format

Semicolon-separated key=value pairs:

```
X-Agentii-Trace: run_id={id}; agent={name}; parent={parent_name}; instance={label}; depth={n}; user_id={uid}
```

## Fields

| Field | Required | Source | Format | Description |
|-------|----------|--------|--------|-------------|
| `run_id` | Yes | MCP middleware (Redis `INCR agentii:run_id_counter`) | `run-{counter}` (e.g., `run-42`) | Per-conversation identifier. NEVER UUID. Short ID saves LLM context tokens. |
| `agent` | Yes | LLM agent (skill Preflight instruction) | kebab-case skill name (e.g., `ratio-analysis`, `dcf-model`, `retrieval-subagent`) | Which agent/skill made this call. |
| `parent` | No | LLM agent | kebab-case parent agent name | Parent agent that spawned this agent. Omitted by root agents. |
| `instance` | No | LLM agent (orchestrator) | `{agent}-{n}` (e.g., `ratio-analysis-3`) | Disambiguates parallel siblings of the same agent type. Omitted when single instance. |
| `depth` | Yes | MCP middleware | integer, 0-based | Nesting level. Root agent = 0, first sub-agent = 1, etc. |
| `user_id` | Yes | MCP middleware (derived from API key) | internal user ID | NEVER exposed to LLM context. Derived server-side from API key. |

## Examples

**Root agent (no parent):**
```
X-Agentii-Trace: run_id=run-42; agent=equity-research; depth=0; user_id=usr_x1
```

**Sub-agent with parent:**
```
X-Agentii-Trace: run_id=run-42; agent=ratio-analysis; parent=equity-research; depth=1; user_id=usr_x1
```

**Parallel sub-agents with instance disambiguation:**
```
X-Agentii-Trace: run_id=run-42; agent=ratio-analysis; parent=equity-research; instance=ratio-analysis-1; depth=1; user_id=usr_x1
X-Agentii-Trace: run_id=run-42; agent=ratio-analysis; parent=equity-research; instance=ratio-analysis-2; depth=1; user_id=usr_x1
```

**Untraced fallback (header absent or unparseable):**
```
X-Agentii-Trace: run_id=run-43; agent=untraced; depth=0; user_id=usr_x1
```

## Storage Architecture

### Hot Tier: Redis (Upstash)

Sorted set per run_id, 7-day TTL:

```
ZADD trace:{run_id} {timestamp_ms} "{agent}|{parent}|{instance}|{endpoint}|{status}"
EXPIRE trace:{run_id} 604800
```

Query: `ZRANGE trace:run-42 0 -1 WITHSCORES` → all spans, real-time, ~1ms.

### Cold Tier: Supabase PostgreSQL

`agent_traces` table for long-term audit. Batch-written every 30s or 100 traces.

### Fallback: Vercel Function Logs

The raw `X-Agentii-Trace` header is automatically captured in every Vercel function invocation log. Survives Redis and Supabase failures.

Neon is explicitly NOT used for tracing data — tracing is operational/user data, not product data.

## Tree Reconstruction

Real-time: Group Redis ZSET results by `instance` to find parallel siblings. Build tree by matching `parent_agent` → `agent`.

Long-term: `SELECT * FROM agent_traces WHERE run_id = $1 ORDER BY timestamp` → recursive traversal on `parent_agent`.

Parallelism detection: `SELECT instance, COUNT(*) FROM agent_traces WHERE run_id = $1 AND parent_agent = $2 GROUP BY instance HAVING COUNT(*) > 1`.

## Credit Attribution

Post-hoc calculation (FR-106e). Trace stores endpoint, status, timestamp — sufficient for workflow reconstruction. Credits computed by query:

```sql
SELECT run_id, agent_name, COUNT(*) AS call_count, SUM(duration_ms) AS total_ms
FROM agent_traces
WHERE user_id = $1 AND timestamp > NOW() - INTERVAL '30 days' AND status = 200
GROUP BY run_id, agent_name
ORDER BY run_id, agent_name;
```

Multiply `call_count` by per-endpoint credit pricing for billing.

## Cross-Spec Dependencies

- **spec 019**: Hono middleware (`trace.ts`), Redis provisioning, Supabase `agent_traces` migration, batch writer
- **spec 022**: No changes (Neon not used for tracing)
- **spec 023**: Skill Preflight instruction in all SKILL.md files, CI validation (Check 18, Check 19)
