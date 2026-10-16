import { apiClient } from "@/lib/http/client";
import type { PaginatedResponse } from "@/lib/http/pagination";

export interface ReportParams {
  start_date: string;
  end_date: string;
  timezone?: string;
}

export interface DashboardData {
  range: { start: string; end: string; timezone: string };
  queue: Record<string, number>;
  low_stock_count: number;
  recent_activity: Array<{
    order__number: string;
    to_status: string;
    actor__email: string | null;
    created_at: string;
  }>;
  revenue_series: Array<{ date: string; revenue: string }>;
  finance: null | {
    revenue: string;
    net_revenue: string;
    cost_of_goods_sold: string;
    profit: string;
    revenue_change_percent: string | null;
    paid_order_count: number;
    average_order_value: string;
  };
}

export interface SalesReport {
  summary: {
    revenue: string;
    paid_orders: number;
    average_order_value: string;
    cancelled_orders: number;
    cancellation_rate_percent: string;
    net_revenue: string;
    cost_of_goods_sold: string;
    profit: string;
  };
  daily: Array<{ date: string; revenue: string; orders: number }>;
  best_sellers: Array<{
    product_id: number;
    product_name: string;
    quantity: number;
    net_revenue: string;
  }>;
  cancellation_reasons: Array<{ reason: string; count: number }>;
}

export interface InventoryReport {
  summary: { active_skus: number; low_stock_skus: number; units_on_hand: number };
  low_stock: Array<{
    variant_id: number;
    sku: string;
    product_name: string;
    quantity: number;
    threshold: number;
  }>;
  ageing: Array<{
    variant_id: number;
    sku: string;
    product_name: string;
    quantity: number;
    threshold: number;
    age_days: number;
    last_receipt_at: string | null;
  }>;
  movement_summary: Array<{ kind: string; movements: number; net_quantity: number }>;
}

export interface ReturnsReport {
  summary: {
    requests: number;
    completed: number;
    exchange_rate_percent: string;
    average_processing_hours: string;
  };
  by_status: Array<{ status: string; count: number }>;
}

export interface RecommendationReport {
  strategies: Array<{
    strategy: string;
    requests: number;
    impressions: number;
    clicks: number;
    ctr_percent: string;
    add_to_carts: number;
    purchases: number;
    coverage_percent: string;
  }>;
}

export interface StaffAccount {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  roles: string[];
}

export interface AuditLogItem {
  id: number;
  actor: number | null;
  actor_email: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  summary: string;
  metadata: Record<string, unknown>;
  request_id: string;
  created_at: string;
}

export async function fetchDashboard(params: ReportParams): Promise<DashboardData> {
  const response = await apiClient.get<DashboardData>("/api/v1/admin/dashboard/", { params });
  return response.data;
}

export async function fetchSalesReport(params: ReportParams): Promise<SalesReport> {
  const response = await apiClient.get<SalesReport>("/api/v1/admin/reports/sales/", { params });
  return response.data;
}

export async function fetchInventoryReport(params: ReportParams): Promise<InventoryReport> {
  const response = await apiClient.get<InventoryReport>("/api/v1/admin/reports/inventory/", {
    params,
  });
  return response.data;
}

export async function fetchReturnsReport(params: ReportParams): Promise<ReturnsReport> {
  const response = await apiClient.get<ReturnsReport>("/api/v1/admin/reports/returns/", { params });
  return response.data;
}

export async function fetchRecommendationReport(
  params: ReportParams,
): Promise<RecommendationReport> {
  const response = await apiClient.get<RecommendationReport>(
    "/api/v1/admin/reports/recommendations/",
    { params },
  );
  return response.data;
}

export async function downloadReport(
  type: "sales" | "inventory" | "returns" | "recommendations",
  params: ReportParams,
): Promise<Blob> {
  const response = await apiClient.get<Blob>(`/api/v1/admin/reports/${type}/export/`, {
    params,
    responseType: "blob",
  });
  return response.data;
}

export async function downloadConsolidatedReport(params: ReportParams): Promise<Blob> {
  const response = await apiClient.get<Blob>("/api/v1/admin/reports/export/", {
    params,
    responseType: "blob",
  });
  return response.data;
}

export async function fetchStaff(params?: {
  page?: number;
  search?: string;
  is_active?: boolean;
}): Promise<PaginatedResponse<StaffAccount>> {
  const response = await apiClient.get<PaginatedResponse<StaffAccount>>("/api/v1/admin/staff/", {
    params,
  });
  return response.data;
}

export async function createStaff(payload: {
  email: string;
  full_name: string;
  password: string;
}): Promise<StaffAccount> {
  const response = await apiClient.post<StaffAccount>("/api/v1/admin/staff/", payload);
  return response.data;
}

export async function updateStaff(
  id: number,
  payload: { full_name?: string; is_active?: boolean },
): Promise<StaffAccount> {
  const response = await apiClient.patch<StaffAccount>(
    `/api/v1/admin/staff/${String(id)}/`,
    payload,
  );
  return response.data;
}

export async function fetchAuditLogs(params?: {
  action?: string;
  entity_type?: string;
  page?: number;
  search?: string;
  start_date?: string;
  end_date?: string;
}): Promise<PaginatedResponse<AuditLogItem>> {
  const response = await apiClient.get<PaginatedResponse<AuditLogItem>>(
    "/api/v1/admin/audit-logs/",
    {
      params,
    },
  );
  return response.data;
}
