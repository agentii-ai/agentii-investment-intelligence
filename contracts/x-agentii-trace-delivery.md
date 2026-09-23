# X-Agentii-Trace run_id Delivery Contract (v1.1)

How the LLM agent learns its `run_id`. The fundamental constraint: Claude Code does NOT inject MCP `serverInfo` or `tools/list` metadata into the LLM system prompt.

**v1.1 (spec 060, 2026-09-21)** — reconciled with the deployed MCP. v1.0 specified a Redis-counter mint and, in its degradation path, a fresh id generated whenever one was missing. Neither exists in the deployed code and neither could: `mcp-agentii` runs with **no environment variables**, so no server-side store can hold a counter across requests. The id is minted once, in memory, and from then on the **caller** is what carries it. See "What changed in v1.1" at the end.

## The Constraint

Claude Code's MCP client:
- Reads `serverInfo` (name, version) at `initialize` — uses it for display, NOT system prompt injection
- Reads `tools[]` from `tools/list` — extracts `name`, `description`, `inputSchema` for function calling; skips extra metadata
- Delivers `tools/call` results to the LLM — this is the ONLY channel the LLM reads

Therefore: `run_id` must arrive through a `tools/call` result to be visible to the LLM.

## Delivery Mechanism

### Step 1: Generation

At MCP `initialize`, the server mints this conversation's `run_id` **once per conversation**:

```
run_id = "run-" + base36(now % 1e6) + base36(local_counter) + 4 random chars
```

No Redis, no environment variable, no network call — the stamp, a per-instance counter and four random characters are enough to keep ids distinct without a shared store, and minting is not on any request's critical path. The value is held in module scope for the lifetime of the serverless instance (`sessionRunId` in `apps/mcp/api/mcp.js`).

Minted **once per run**, not per call. A conversation that calls twenty tools has one `run_id`, which is what makes the set of calls a run.

**Honest caveat**: module scope on Vercel means the id lives as long as the instance, and a conversation that is served by a second instance would see a second id. The caller-carried header (Step 3) is the mitigation: an agent that carries its own `run_id` forward pins one id for the whole conversation regardless of which instance serves which call. This is why the header, not the session variable, is the authority.

### Step 2: Delivery

Three surfaces, in descending order of what the LLM can actually see:

1. **`initialize` result** — `serverInfo.run_id` carries it: `{"name": "agentii", "version": "1.1.0", "run_id": "run-lx8f2a9k4q"}`. For clients, display and diagnostics. The LLM does not see it (see The Constraint).
2. **`tools/list` and `tools/call` `_meta`** — documents the header for a client that reads metadata:
   ```json
   { "_meta": { "x_agentii_trace": {
       "header": "X-Agentii-Trace",
       "format": "run_id={id}; agent={name}; parent={name}; instance={label}",
       "required": false,
       "description": "run_id is returned at initialize; depth and user identity are derived server-side and must not be sent"
   } } }
   ```
3. **`tools/call` result** — `_run_id` is appended to the payload the LLM reads:
   ```json
   { "content": [ { "type": "text", "text": "{\"_run_id\": \"run-lx8f2a9k4q\", \"ticker\": \"LLY\", ...}" } ] }
   ```

The `_run_id` is present in **every** tool result, not only the first, so a sub-agent — whose context does not include the parent's calls — learns the id on its own first call.

### Step 3: Propagation

On every subsequent call the agent carries the id back:

> Include the HTTP header `X-Agentii-Trace: run_id={id}; agent={skill_name}; parent={caller_name}; instance={instance_label}` — where `{id}` is the `_run_id` from the tool result. If you did not receive one, omit the header entirely.

The caller's header is the authority. The proxy forwards a caller-supplied header **verbatim, with one exception**: where the caller declared no `agent`, the proxy appends the tool it is executing, namespaced — `agent=mcp:{tool_name}`. A caller-declared `agent` is never overwritten, and `mcp:` cannot collide with a skill name (kebab-case, `ratio-analysis`). Elsewhere: only when the caller sends **no header at all** does the proxy substitute this conversation's session id, carrying the same agent label with it. `depth` and `user_id` are never added by the proxy: the API derives the depth from the run's recorded structure, and reads the identity from the API key.

**Why the proxy supplies the actor at all** (2026-09-23, spec 060 D-16). The question the archive exists to answer is *which data users reach for, and in what kind of workflow* — and that question is answered by the `agent`, not by the run: a run id groups calls, but it names nobody. This hop serves essentially every agent call, and the proxy is the one party that knows first-hand which tool it was asked to execute. Until the first real archive was read (15 segments, 31 records, one endpoint) the proxy sent a run with no actor, so the platform stored `agent_name = 'untraced'` for calls it could have named exactly — one of them measured, on this path. `untraced` keeps its meaning and its scope: it is what a call with no trace identifier is, and a caller who sends no header still gets no run (D-22) and no label.

### Step 4: All Subsequent Calls

The agent includes the header on every call. The merged header reaches `api.agentii.ai`, which records the lineage on the usage row, logs the span to the Redis hot tier, and derives depth and sibling label (`x-agentii-trace-header.md`).

## Why Other Approaches Were Rejected

### serverInfo.run_id as the delivery channel

The MCP spec allows `serverInfo` to carry the `run_id`, and the deployed server does populate it. **Rejected as the channel**: Claude Code reads `serverInfo` for display only and does NOT inject it into the LLM's system prompt. The value is there; the LLM never sees it. It is kept for clients and diagnostics, and must not be relied on for propagation.

### tools/list metadata alone

The `tools/list` response carries `_meta.x_agentii_trace`. **Rejected as the only channel**: Claude Code extracts `tools[]` for function definitions and skips the `meta` field. The LLM sees tool descriptions, not metadata. Retained because a client that does read metadata should be able to discover the header without reading source.

### Embedding run_id in tool descriptions

Every tool description could include the run_id: `"description": "run_id=run-lx8f2a9k4q. Search for companies by ticker..."`

**Rejected**: Pollutes all 25+ tool descriptions with session-specific data, so every `tools/list` call would have to regenerate all descriptions. Ugly and fragile.

## Degradation

A call must be traceable or honestly untraced — never quietly re-run.

| Situation | What happens |
|-----------|--------------|
| Header absent (agent never learned the id, direct REST call, context reset) | Recorded with `run_id = NULL` and `agent_name = 'untraced'`. The call is still metered and still logged. |
| Header present but malformed | Same: nothing parseable is extracted, so the call is untraced. |
| `run_id` present, `agent` absent | The run is intact; the span has no agent name. |
| `run_id` present but unknown to the platform (hot entry expired, or an id from another environment) | The row is recorded with what the header carried. Depth stays at the derivable minimum and `derived_at` stays unset, so the record shows the anomaly rather than a plausible value. |
| Caller sends `depth` or `user_id` | Ignored. Neither is read from the header. |

In no case is a missing `run_id` filled in with a new one. An invented id starts a second, orphaned run for a conversation that already has one — the exact fragmentation the trace exists to prevent — and it would look like a successful trace while doing it.

## What Changed in v1.1

| v1.0 said | v1.1 says | Why |
|-----------|-----------|-----|
| Generated via a Redis counter | Minted once, in memory, at `initialize` | `mcp-agentii` has no env vars by design; a shared counter cannot exist there. |
| Regenerated whenever a call arrived without one | Never regenerated; the call is recorded untraced | The old rule fragmented runs silently and presented itself as resilience. |
| "Minted **once per conversation**" as a *requirement* on the MCP | Stated as the shipped behaviour, with the caller-carried header as the authority | The requirement was unmet for months without any gate noticing; the caller-carried header is what actually holds a run together across instances. |
| "The MCP middleware injects `run_id`, `depth`, and `user_id`" | The proxy injects `run_id` **only**, and `agent=mcp:{tool}` where the caller declared no agent; depth is derived by the API, identity read from the API key | Depth must not be trusted from any caller (FR-131), and identity must never travel from a client (FR-204). |
| "The proxy forwards the caller's header verbatim" as an absolute | Verbatim **except** for the actor the caller did not declare | The absolute reading left the archive with runs and no actors on the hop that carries nearly every call; the exception is narrow (never overwrites, namespaced, recorded as the proxy's own) and the alternative — an unnamed call the proxy could name — is the defect (D-16). |
