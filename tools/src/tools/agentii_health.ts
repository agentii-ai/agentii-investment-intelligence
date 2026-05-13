import { agentiiFetch } from '../client.js';

export const agentiiHealthTool = {
  name: 'agentii_health',
  description: 'Verify connection to agentii.ai. Returns API status, credit balance, and plan tier.',
  inputSchema: {
    type: 'object',
    properties: {},
  },
  handler: async (_args: any, env: { apiKey: string; baseUrl: string }) => {
    return agentiiFetch('/v1/health', env.apiKey, env.baseUrl);
  },
};
