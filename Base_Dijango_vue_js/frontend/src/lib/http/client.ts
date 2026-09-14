import axios, { AxiosHeaders, type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { isSessionRejection } from "./errors";

const baseURL = (import.meta.env.VITE_API_BASE_URL ?? "").trim();

export const apiClient = axios.create({ baseURL, withCredentials: true, timeout: 10_000 });
export const authClient = axios.create({ baseURL, withCredentials: true, timeout: 10_000 });

interface RetryConfig extends InternalAxiosRequestConfig {
  _authRetry?: boolean;
}

interface AuthTransport {
  getAccessToken: () => string | null;
  refreshAccessToken: () => Promise<string>;
  onSessionInvalid: () => void;
}

let transport: AuthTransport | undefined;

export function configureAuthTransport(nextTransport: AuthTransport) {
  transport = nextTransport;
}

apiClient.interceptors.request.use((config) => {
  const accessToken = transport?.getAccessToken();
  if (accessToken) {
    config.headers = AxiosHeaders.from(config.headers);
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return config;
});

apiClient.interceptors.response.use(undefined, async (error: AxiosError) => {
  const config = error.config as RetryConfig | undefined;
  if (!transport || error.response?.status !== 401 || !config || config._authRetry) {
    throw error;
  }

  config._authRetry = true;
  try {
    const accessToken = await transport.refreshAccessToken();
    config.headers = AxiosHeaders.from(config.headers);
    config.headers.set("Authorization", `Bearer ${accessToken}`);
    return await apiClient.request(config);
  } catch (refreshError) {
    if (isSessionRejection(refreshError)) transport.onSessionInvalid();
    throw refreshError;
  }
});
