import { apiClient } from "@/lib/http/client";
import type { CreateExchangeInput, ExchangeRequest, ExchangeTransitionInput } from "./types";

export async function fetchMyExchanges(): Promise<ExchangeRequest[]> {
  const response = await apiClient.get<ExchangeRequest[]>("/api/v1/exchanges/");
  return response.data;
}

export async function createExchange(
  payload: CreateExchangeInput,
  idempotencyKey: string,
): Promise<ExchangeRequest> {
  const response = await apiClient.post<ExchangeRequest>("/api/v1/exchanges/", payload, {
    headers: { "Idempotency-Key": idempotencyKey },
  });
  return response.data;
}

export async function cancelExchange(id: number): Promise<ExchangeRequest> {
  const response = await apiClient.post<ExchangeRequest>(`/api/v1/exchanges/${String(id)}/cancel/`);
  return response.data;
}

export async function confirmReplacementReceived(id: number): Promise<ExchangeRequest> {
  const response = await apiClient.post<ExchangeRequest>(
    `/api/v1/exchanges/${String(id)}/confirm-received/`,
  );
  return response.data;
}

export async function fetchAdminExchanges(status?: string): Promise<ExchangeRequest[]> {
  const response = await apiClient.get<ExchangeRequest[]>("/api/v1/admin/exchanges/", {
    params: status ? { status } : undefined,
  });
  return response.data;
}

export async function transitionAdminExchange(
  id: number,
  payload: ExchangeTransitionInput,
): Promise<ExchangeRequest> {
  const response = await apiClient.post<ExchangeRequest>(
    `/api/v1/admin/exchanges/${String(id)}/transitions/`,
    payload,
  );
  return response.data;
}
