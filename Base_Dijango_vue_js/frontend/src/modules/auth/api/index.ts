import type { AxiosRequestConfig } from "axios";

import { authClient, apiClient } from "@/lib/http/client";
import { ensureCsrfToken } from "@/lib/http/csrf";
import { toAppError } from "@/lib/http/errors";

import type { LoginCredentials, LoginResponse, RefreshResponse, User } from "../types";

async function csrfPost<T>(url: string, data: unknown = {}): Promise<T> {
  async function send(forceCsrf = false) {
    const token = await ensureCsrfToken(forceCsrf);
    const config: AxiosRequestConfig = { headers: { "X-CSRFToken": token } };
    return authClient.post<T>(url, data, config);
  }

  try {
    return (await send()).data;
  } catch (error) {
    if (toAppError(error).kind !== "csrf") throw error;
    return (await send(true)).data;
  }
}

export function loginRequest(credentials: LoginCredentials): Promise<LoginResponse> {
  return csrfPost("/api/v1/auth/login/", credentials);
}

export function refreshRequest(): Promise<RefreshResponse> {
  return csrfPost("/api/v1/auth/refresh/");
}

export async function logoutRequest(): Promise<void> {
  await csrfPost("/api/v1/auth/logout/");
}

export async function meRequest(): Promise<User> {
  return (await apiClient.get<User>("/api/v1/auth/me/")).data;
}
