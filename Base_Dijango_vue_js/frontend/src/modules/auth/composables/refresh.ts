import { refreshRequest } from "../api";
import { useAuthStore } from "../stores/auth";
import { broadcastAuthEvent, withAuthLock } from "./coordination";

let refreshFlight: Promise<string> | null = null;

export function refreshAccessToken(): Promise<string> {
  if (refreshFlight) return refreshFlight;

  refreshFlight = withAuthLock(async () => {
    const auth = useAuthStore();
    const operationGeneration = auth.generation;
    const response = await refreshRequest();
    if (auth.generation !== operationGeneration || auth.logoutPending) {
      throw new Error("Refresh result is stale after logout");
    }
    auth.setAccessToken(response.access);
    broadcastAuthEvent({ type: "session-changed" });
    return response.access;
  }).finally(() => {
    refreshFlight = null;
  });

  return refreshFlight;
}
