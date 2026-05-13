import { agentiiFetch } from '../client.js';

export const listCoverageTool = {
  name: 'list_coverage',
  description: 'List available data sources and freshness for tickers. Returns per-source record counts.',
  inputSchema: {
    type: 'object',
    properties: {
      ticker: { type: 'string', description: 'Stock ticker symbol (optional — lists all if omitted)' },
    },
  },
  handler: async (args: any, env: { apiKey: string; baseUrl: string }) => {
    return agentiiFetch('/v1/list_coverage', env.apiKey, env.baseUrl, {
      params: args.ticker ? { ticker: args.ticker } : undefined,
    });
  },
};
