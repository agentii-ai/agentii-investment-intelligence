#!/usr/bin/env node
/** ESM shim — invokes the MCP server entry point */
import('../dist/server.js').catch((err) => {
  console.error('Failed to start agentii MCP server:', err.message);
  process.exit(1);
});
