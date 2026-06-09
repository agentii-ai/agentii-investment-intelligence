# Trace Tree Reconstruction Guide

How to reconstruct the full agent→sub-agent call hierarchy from `X-Agentii-Trace` data stored in Redis (hot, 7d TTL) and Supabase PostgreSQL (cold, long-term audit).

## Data Model

Each API call produces one trace record with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | VARCHAR(32) | Per-conversation identifier (`run-42`) |
| `agent_name` | VARCHAR(128) | Which agent/skill made this call |
| `parent_agent` | VARCHAR(128) | Parent agent (NULL for root) |
| `instance` | VARCHAR(64) | Parallel sibling label (NULL if single) |
| `depth` | INTEGER | Nesting level (0 = root) |
| `endpoint` | VARCHAR(256) | API endpoint called |
| `timestamp` | TIMESTAMPTZ | When the call occurred |
| `status` | INTEGER | HTTP status code |
| `duration_ms` | INTEGER | Call duration |
| `user_id` | VARCHAR(64) | API key owner |

## Real-Time Reconstruction (Redis)

### Get all spans for a run

```redis
ZRANGE trace:run-42 0 -1 WITHSCORES
```

Returns all spans as `{timestamp_ms}|{agent}|{parent}|{instance}|{endpoint}|{status}` sorted by time.

### Find parallel siblings

Group by `(parent_agent, agent_name)` and look for multiple entries with different `instance` values:

```redis
# All entries for ratio-analysis sub-agents
ZRANGEBYLEX trace:run-42 [1719000000000|ratio-analysis [1719000000000|ratio-analysis\xFF
```

### Build the tree

1. Fetch all spans for `run_id` via `ZRANGE`
2. Parse each span into `(agent, parent, instance, endpoint, timestamp)`
3. Roots: spans where `parent` is empty
4. Children: spans where `parent` matches another span's `agent`
5. Parallel: children with same `(parent, agent)` but different `instance`

## Long-Term Reconstruction (Supabase)

### Full trace for one run

```sql
SELECT * FROM agent_traces
WHERE run_id = 'run-42'
ORDER BY timestamp;
```

### Recursive tree

```sql
WITH RECURSIVE agent_tree AS (
  SELECT *, 0 AS level
  FROM agent_traces
  WHERE run_id = 'run-42' AND parent_agent IS NULL
  UNION ALL
  SELECT ul.*, at.level + 1
  FROM agent_traces ul
  JOIN agent_tree at ON ul.parent_agent = at.agent_name
    AND ul.run_id = at.run_id
)
SELECT * FROM agent_tree ORDER BY level, timestamp;
```

### Parallelism detection

```sql
SELECT parent_agent, agent_name, instance, COUNT(*) AS call_count
FROM agent_traces
WHERE run_id = 'run-42'
  AND parent_agent IS NOT NULL
GROUP BY parent_agent, agent_name, instance
HAVING COUNT(*) > 1
ORDER BY parent_agent, agent_name;
```

### User workflow reproduction

Reconstruct all activity for a user in a time window:

```sql
SELECT run_id, agent_name, parent_agent, instance, depth, endpoint, timestamp, status
FROM agent_traces
WHERE user_id = 'usr_x1'
  AND timestamp BETWEEN '2026-06-09T10:00:00Z' AND '2026-06-09T11:00:00Z'
ORDER BY run_id, timestamp;
```

## Credit Attribution (Post-Hoc per FR-106e)

Credits are NOT stored in trace records — they are computed from trace data:

```sql
SELECT run_id, agent_name,
       COUNT(*) AS call_count,
       SUM(duration_ms) AS total_ms
FROM agent_traces
WHERE user_id = $1
  AND timestamp > NOW() - INTERVAL '30 days'
  AND status = 200
GROUP BY run_id, agent_name
ORDER BY run_id, agent_name;
```

Multiply `call_count` by per-endpoint credit pricing from the pricing table. Use `endpoint` instead of `agent_name` for endpoint-level granularity:

```sql
SELECT run_id, agent_name, endpoint,
       COUNT(*) AS call_count
FROM agent_traces
WHERE user_id = $1
  AND timestamp > NOW() - INTERVAL '30 days'
  AND status = 200
GROUP BY run_id, agent_name, endpoint
ORDER BY run_id, agent_name, endpoint;
```

## Fallback: Vercel Function Logs

When Redis and Supabase are unavailable, the raw `X-Agentii-Trace` header is captured in every Vercel function log. Parse via Log Drains (Datadog, Grafana Loki):

```
grep "X-Agentii-Trace" vercel-logs.jsonl | jq '.headers["x-agentii-trace"]'
```
