import { agentiiFetch } from '../client.js';

export const searchDocumentsTool = {
  name: 'search_documents',
  description: 'Search SEC filings by ticker, form type, date range. Returns metadata, description, keywords.',
  inputSchema: {
    type: 'object',
    properties: {
      ticker: { type: 'string', description: 'Stock ticker symbol (e.g., LLY, NVDA)' },
      form_type: { type: 'string', description: 'Filing form type (10-K, 10-Q, 8-K)' },
      date_from: { type: 'string', description: 'Start date (YYYY-MM-DD)' },
      date_to: { type: 'string', description: 'End date (YYYY-MM-DD)' },
    },
    required: ['ticker'],
  },
  handler: async (args: any, env: { apiKey: string; baseUrl: string }) => {
    return agentiiFetch('/v1/search_documents', env.apiKey, env.baseUrl, {
      params: { ticker: args.ticker, form_type: args.form_type, date_from: args.date_from, date_to: args.date_to },
    });
  },
};
