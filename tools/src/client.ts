/** Thin fetch wrapper around api.agentii.ai with retry, timeout, and credit header propagation */

const BASE_TIMEOUT_MS = 30_000;
const MAX_RETRIES = 2;

interface AgentiiResponse<T = any> {
  data?: T;
  meta?: Record<string, any>;
  error?: { code: string; message: string };
}

export async function agentiiFetch<T = any>(
  path: string,
  apiKey: string,
  baseUrl: string,
  opts?: { method?: string; body?: any; params?: Record<string, string> }
): Promise<{ data?: T; meta?: any; error?: { code: string; message: string }; credits_consumed?: number; credits_remaining?: number }> {
  const url = new URL(path, baseUrl);
  if (opts?.params) {
    for (const [k, v] of Object.entries(opts.params)) {
      url.searchParams.set(k, v);
    }
  }

  let lastError: Error | null = null;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), BASE_TIMEOUT_MS);

      const res = await fetch(url.toString(), {
        method: opts?.method || 'GET',
        headers: {
          'X-API-Key': apiKey,
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: opts?.body ? JSON.stringify(opts.body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timer);

      const json = await res.json();
      const creditsConsumed = parseInt(res.headers.get('X-Credits-Consumed') || '0', 10);
      const creditsRemaining = parseInt(res.headers.get('X-Credits-Remaining') || '0', 10);

      return { ...json, credits_consumed: creditsConsumed, credits_remaining: creditsRemaining };
    } catch (err: any) {
      lastError = err;
      if (attempt < MAX_RETRIES) {
        await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
      }
    }
  }

  return { error: { code: 'NETWORK_ERROR', message: lastError?.message || 'Request failed after retries.' } };
}
