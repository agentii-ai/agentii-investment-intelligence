# X-Agentii-Trace run_id Delivery Contract (v1.0, per FR-106a(c)

How the LLM agent learns its `run_id` — the fundamental constraint is that Claude Code does NOT inject MCP `serverInfo` or `tools/list` metadata into the LLM system prompt.

## The Constraint

Claude Code's MCP client:
- Reads `serverInfo` (name, version) at `initialize` — uses it for display, NOT system prompt injection
- Reads `tools[]` from `tools/list` — extracts `name`, `description`, `inputSchema` for function calling; skips extra metadata
- Delivers `tools/call` results to the LLM — this is the ONLY channel the LLM reads

Therefore: `run_id` must arrive through a `tools/call` result to be visible to the LLM.

## Delivery Mechanism

### Step 1: Generation

At MCP `initialize` time, the server generates `run_id` via Redis:

```
run_id = "run-" + Redis.INCR("agentii:run_id_counter")
```

Result: `run-42`, `run-43`, etc. Globally unique across all Vercel instances, sub-millisecond.

### Step 2: First Tool Call Injection

On the **first** `tools/call` after `initialize`, the MCP server injects `run_id` into the result content:

```json
{
 "content": [
 {
 "type": "text",
 "text": "{\"_run_id\": \"run-42\", \"ticker\": \"LLY\", \"company_name\": \"Eli Lilly and Co\", ...}"
 }
 ]
}
```

The `_run_id` field is always present in the first response, and also included in subsequent responses (so sub-agents learn their run_id on their first call too).

### Step 3: Agent Propagation

The agent system prompt instructs:

> The first tool you call will return a `_run_id` in its result. On every subsequent tool call, include HTTP header `X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. The MCP server will inject run_id, depth, and user_id automatically.

### Step 4: All Subsequent Calls

The agent includes `agent`, `parent`, and `instance` in the `X-Agentii-Trace` header on every call. The MCP middleware injects `run_id`, `depth`, and `user_id`. The merged header is logged to Redis, Supabase, and Vercel logs.

## Why Other Approaches Were Rejected

### serverInfo.run_id

The MCP spec allows `serverInfo` to carry the `run_id`:

```json
{ "name": "agentii", "version": "2.1.0", "run_id": "run-42" }
```

**Rejected**: Claude Code reads `serverInfo` for display purposes only. It does NOT inject `serverInfo.run_id` into the LLM's system prompt. The LLM never sees it.

### tools/list Metadata

The `tools/list` response can carry metadata alongside `tools[]`:

```json
{ "tools": [...], "meta": { "run_id": "run-42" } }
```

**Rejected**: Claude Code extracts `tools[]` for function definitions. It skips the `meta` field entirely. The LLM sees tool descriptions, not metadata.

### Embedding run_id in Tool Descriptions

Every tool description could include the run_id: `"description": "run_id=run-42. Search for companies by ticker..."`

**Rejected**: Pollutes all 25+ tool descriptions with session-specific data. Every `tools/list` call would need to regenerate all descriptions. Ugly and fragile.

## Graceful Degradation

If the first tool call's `_run_id` is somehow lost (agent context window reset, direct REST call bypassing MCP):

1. The API middleware checks for `X-Agentii-Trace` header
2. If `run_id` is missing: auto-generates one, sets `agent=untraced`
3. The trace is incomplete (no agent hierarchy) but the call is still logged with a valid run_id
4. Vercel logs still capture the raw headers
