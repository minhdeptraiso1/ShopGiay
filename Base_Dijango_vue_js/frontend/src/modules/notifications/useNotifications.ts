import { readonly, ref } from "vue";

import {
  createWebSocketTicket,
  fetchNotifications,
  fetchNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
  type NotificationItem,
} from "./api";

const items = ref<NotificationItem[]>([]);
const unreadCount = ref(0);
const connected = ref(false);
let socket: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof globalThis.setTimeout> | undefined;
let stopped = true;
let retryDelay = 1000;

function shouldReconnect(): boolean {
  return !stopped;
}

function websocketUrl(ticket: string): string {
  const protocol = globalThis.location.protocol === "https:" ? "wss:" : "ws:";
  const configured = (import.meta.env.VITE_API_BASE_URL ?? "").trim();
  if (configured.startsWith("http")) {
    const url = new URL(configured);
    return `${url.protocol === "https:" ? "wss:" : "ws:"}//${url.host}/ws/realtime/?ticket=${encodeURIComponent(ticket)}`;
  }
  return `${protocol}//${globalThis.location.host}/ws/realtime/?ticket=${encodeURIComponent(ticket)}`;
}

async function load(): Promise<void> {
  const [page, count] = await Promise.all([fetchNotifications(), fetchNotificationSummary()]);
  items.value = page.results;
  unreadCount.value = count;
}

async function connect(): Promise<void> {
  stopped = false;
  globalThis.clearTimeout(reconnectTimer);
  try {
    const ticket = await createWebSocketTicket();
    socket = new WebSocket(websocketUrl(ticket));
    socket.onopen = () => {
      connected.value = true;
      retryDelay = 1000;
    };
    socket.onmessage = (message) => {
      if (typeof message.data !== "string") return;
      const data = JSON.parse(message.data) as { event: string; payload: NotificationItem };
      if (data.event === "notification.created") {
        items.value = [
          data.payload,
          ...items.value.filter((item) => item.id !== data.payload.id),
        ].slice(0, 20);
        unreadCount.value += 1;
      }
      globalThis.dispatchEvent(new CustomEvent("hai-duy:realtime", { detail: data }));
    };
    socket.onclose = () => {
      connected.value = false;
      if (!stopped) {
        reconnectTimer = globalThis.setTimeout(() => void connect(), retryDelay);
        retryDelay = Math.min(retryDelay * 2, 30_000);
      }
    };
  } catch {
    connected.value = false;
    if (shouldReconnect()) {
      reconnectTimer = globalThis.setTimeout(() => void connect(), retryDelay);
      retryDelay = Math.min(retryDelay * 2, 30_000);
    }
  }
}

function disconnect(): void {
  stopped = true;
  globalThis.clearTimeout(reconnectTimer);
  socket?.close();
  socket = null;
  connected.value = false;
}

async function read(item: NotificationItem): Promise<void> {
  if (!item.read_at) {
    const updated = await markNotificationRead(item.id);
    items.value = items.value.map((entry) => (entry.id === item.id ? updated : entry));
    unreadCount.value = Math.max(0, unreadCount.value - 1);
  }
}

async function readAll(): Promise<void> {
  await markAllNotificationsRead();
  const now = new Date().toISOString();
  items.value = items.value.map((item) => ({ ...item, read_at: item.read_at ?? now }));
  unreadCount.value = 0;
}

export function useNotifications() {
  return {
    items: readonly(items),
    unreadCount: readonly(unreadCount),
    connected: readonly(connected),
    load,
    connect,
    disconnect,
    read,
    readAll,
  };
}
