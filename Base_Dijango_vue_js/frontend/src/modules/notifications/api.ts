import { apiClient } from "@/lib/http/client";
import type { PaginatedResponse } from "@/lib/http/pagination";

export interface NotificationItem {
  id: number;
  kind: "order" | "exchange" | "inventory" | "system";
  title: string;
  message: string;
  link: string;
  payload: Record<string, unknown>;
  read_at: string | null;
  created_at: string;
}

export async function fetchNotifications(): Promise<PaginatedResponse<NotificationItem>> {
  const response =
    await apiClient.get<PaginatedResponse<NotificationItem>>("/api/v1/notifications/");
  return response.data;
}

export async function fetchNotificationSummary(): Promise<number> {
  const response = await apiClient.get<{ unread_count: number }>("/api/v1/notifications/summary/");
  return response.data.unread_count;
}

export async function markNotificationRead(id: number): Promise<NotificationItem> {
  const response = await apiClient.post<NotificationItem>(
    `/api/v1/notifications/${String(id)}/read/`,
  );
  return response.data;
}

export async function markAllNotificationsRead(): Promise<void> {
  await apiClient.post("/api/v1/notifications/read-all/");
}

export async function createWebSocketTicket(): Promise<string> {
  const response = await apiClient.post<{ ticket: string }>(
    "/api/v1/notifications/websocket-ticket/",
  );
  return response.data.ticket;
}
