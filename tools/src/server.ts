/**
 * MCP server — stdio transport. Registers all agentii data tools.
 * Agents invoke: npx -y @agentii/investment-intelligence
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { getEnv } from './env.js';
import { searchDocumentsTool } from './tools/search_documents.js';
import { getCompanyProfileTool } from './tools/get_company_profile.js';
import { listCoverageTool } from './tools/list_coverage.js';
import { agentiiHealthTool } from './tools/agentii_health.js';

const env = getEnv();

const server = new McpServer({
  name: 'agentii-investment-intelligence',
  version: '1.0.0',
});

// Register tools
const tools = [searchDocumentsTool, getCompanyProfileTool, listCoverageTool, agentiiHealthTool];

for (const tool of tools) {
  server.tool(tool.name, tool.description, tool.inputSchema, async (args: any) => {
    const result = await tool.handler(args, env);
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  });
}

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
