import { AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import { vi } from "vitest";

import { apiClient, configureAuthTransport } from "./client";

function rejection(status: number, config: InternalAxiosRequestConfig) {
  const response = { status, statusText: "Error", config, headers: {}, data: {} } as AxiosResponse;
  return new AxiosError("request failed", "ERR_BAD_RESPONSE", config, undefined, response);
}

describe("API refresh interceptor", () => {
  it("does not refresh a 403 response", async () => {
    const refresh = vi.fn<() => Promise<string>>();
    configureAuthTransport({
      getAccessToken: () => "old",
      refreshAccessToken: refresh,
      onSessionInvalid: vi.fn(),
    });
    await expect(
      apiClient.get("/forbidden", {
        adapter: async (config) => Promise.reject(rejection(403, config)),
      }),
    ).rejects.toBeInstanceOf(AxiosError);
    expect(refresh).not.toHaveBeenCalled();
  });

  it("refreshes a 401 and retries the original request once", async () => {
    const refresh = vi.fn().mockResolvedValue("new-access");
    configureAuthTransport({
      getAccessToken: () => "old",
      refreshAccessToken: refresh,
      onSessionInvalid: vi.fn(),
    });
    let calls = 0;
    const response = await apiClient.get("/protected", {
      adapter: (config) => {
        calls += 1;
        if (calls === 1) return Promise.reject(rejection(401, config));
        return Promise.resolve({
          data: { ok: true },
          status: 200,
          statusText: "OK",
          headers: {},
          config,
        });
      },
    });
    expect(response.data).toEqual({ ok: true });
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(calls).toBe(2);
  });
});
