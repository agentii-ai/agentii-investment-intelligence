/** Reads AGENTII_API_KEY (required) and AGENTII_BASE_URL (optional) from process.env */

export function getEnv() {
  const apiKey = process.env.AGENTII_API_KEY;
  if (!apiKey) {
    console.error('AGENTII_API_KEY is required. Generate one at https://agentii.ai/api-keys');
    process.exit(1);
  }
  return {
    apiKey,
    baseUrl: process.env.AGENTII_BASE_URL || 'https://api.agentii.ai',
  };
}
