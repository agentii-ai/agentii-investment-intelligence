import { agentiiFetch } from '../client.js';

export const getCompanyProfileTool = {
  name: 'get_company_profile',
  description: 'Get company overview with pipeline summary, catalyst count, and recent activity.',
  inputSchema: {
    type: 'object',
    properties: {
      ticker: { type: 'string', description: 'Stock ticker symbol' },
    },
    required: ['ticker'],
  },
  handler: async (args: any, env: { apiKey: string; baseUrl: string }) => {
    return agentiiFetch(`/v1/get_company_profile/${args.ticker}`, env.apiKey, env.baseUrl);
  },
};
