import { authClient } from "./client";

let csrfToken: string | null = null;

export async function ensureCsrfToken(force = false): Promise<string> {
  if (csrfToken && !force) return csrfToken;
  const response = await authClient.get<{ csrf_token: string }>("/api/v1/auth/csrf/", {
    headers: { "Cache-Control": "no-cache" },
  });
  csrfToken = response.data.csrf_token;
  return csrfToken;
}

export function clearCsrfToken() {
  csrfToken = null;
}
