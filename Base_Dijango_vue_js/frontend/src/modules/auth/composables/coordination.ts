type AuthEvent = { type: "logout" } | { type: "session-changed" };

const channel =
  typeof BroadcastChannel !== "undefined" ? new BroadcastChannel("django-base-auth") : null;

export async function withAuthLock<T>(task: () => Promise<T>): Promise<T> {
  if (typeof navigator !== "undefined" && "locks" in navigator) {
    return navigator.locks.request("django-base-auth-refresh", { mode: "exclusive" }, task);
  }
  return task();
}

export function broadcastAuthEvent(event: AuthEvent) {
  channel?.postMessage(event);
}

export function onAuthEvent(callback: (event: AuthEvent) => void): () => void {
  if (!channel) return () => undefined;
  const listener = (message: MessageEvent<AuthEvent>) => {
    callback(message.data);
  };
  channel.addEventListener("message", listener);
  return () => {
    channel.removeEventListener("message", listener);
  };
}
