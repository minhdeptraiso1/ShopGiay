import { createPinia, setActivePinia } from "pinia";
import { beforeEach, vi } from "vitest";

import { refreshRequest } from "../api";
import { useAuthStore } from "../stores/auth";
import { refreshAccessToken } from "./refresh";

vi.mock("../api", () => ({ refreshRequest: vi.fn() }));

describe("refreshAccessToken", () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
  });

  it("uses one refresh flight for concurrent 401 requests in a tab", async () => {
    vi.mocked(refreshRequest).mockResolvedValue({ access: "new-access" });
    const [first, second] = await Promise.all([refreshAccessToken(), refreshAccessToken()]);
    expect(first).toBe("new-access");
    expect(second).toBe("new-access");
    expect(refreshRequest).toHaveBeenCalledTimes(1);
    expect(useAuthStore().accessToken).toBe("new-access");
  });

  it("does not restore access from a refresh completed after logout", async () => {
    let resolveRefresh!: (value: { access: string }) => void;
    vi.mocked(refreshRequest).mockReturnValue(
      new Promise((resolve) => {
        resolveRefresh = resolve;
      }),
    );
    const pending = refreshAccessToken();
    const auth = useAuthStore();
    auth.clearSession();
    auth.markLogoutPending(true);
    resolveRefresh({ access: "stale-access" });

    await expect(pending).rejects.toThrow("stale");
    expect(auth.accessToken).toBeNull();
  });
});
