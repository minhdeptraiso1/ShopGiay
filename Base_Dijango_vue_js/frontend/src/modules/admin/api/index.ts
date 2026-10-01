import { apiClient } from "@/lib/http/client";
import type { AxiosResponse } from "axios";

export interface AdminProduct {
  id: number;
  category: number;
  brand: number;
  name: string;
  slug: string;
  description: string;
  product_type: "footwear" | "accessory" | "care";
  status: "draft" | "published";
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminVariant {
  id: number;
  product: number;
  size: number | null;
  color: number | null;
  option_label: string;
  sku: string;
  price: string;
  currency: string;
  low_stock_threshold: number;
  is_active: boolean;
  inventory_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface StockMovementItem {
  id: number;
  variant: number;
  kind: "receipt" | "adjustment";
  delta: number;
  quantity_before: number;
  quantity_after: number;
  reason: string;
  actor: number | null;
  actor_email: string | null;
  created_at: string;
}

export interface InventoryAdjustmentInput {
  delta: number;
  kind: "receipt" | "adjustment";
  reason: string;
}

export interface RecommendationMetrics {
  days: number;
  requests: number;
  impressions: number;
  clicks: number;
  attributed_add_to_carts: number;
  attributed_purchases: number;
  ctr_percent: string;
  coverage_percent: string;
  requests_by_strategy: Record<string, number>;
}

export async function fetchRecommendationMetrics(): Promise<RecommendationMetrics> {
  const response = await apiClient.get<RecommendationMetrics>(
    "/api/v1/admin/recommendations/metrics/",
  );
  return response.data;
}

export interface AdminCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryInput {
  name: string;
  slug: string;
  description?: string;
  parent?: number | null;
  is_active?: boolean;
}

export interface UpdateCategoryInput {
  name?: string;
  slug?: string;
  description?: string;
  parent?: number | null;
  is_active?: boolean;
}

export interface AdminBrand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateBrandInput {
  name: string;
  slug: string;
  description?: string;
  is_active?: boolean;
}

export interface UpdateBrandInput {
  name?: string;
  slug?: string;
  description?: string;
  is_active?: boolean;
}

export interface CreateProductInput {
  category: number;
  brand: number;
  name: string;
  slug: string;
  description?: string;
  product_type?: "footwear" | "accessory" | "care";
  status?: "draft" | "published";
}

export interface UpdateProductInput {
  category?: number;
  brand?: number;
  name?: string;
  slug?: string;
  description?: string;
  product_type?: "footwear" | "accessory" | "care";
  status?: "draft" | "published";
}

interface PaginatedAdminResponse<T> {
  next: string | null;
  results: T[];
}

async function fetchAllAdminPages<T>(
  initialUrl: string,
  params?: Record<string, number>,
): Promise<T[]> {
  const items: T[] = [];
  let url: string | null = initialUrl;
  let requestParams = params;

  while (url) {
    const response: AxiosResponse<T[] | PaginatedAdminResponse<T>> = await apiClient.get(url, {
      params: requestParams,
    });
    requestParams = undefined;
    if (Array.isArray(response.data)) return [...items, ...response.data];
    items.push(...response.data.results);
    url = response.data.next;
  }

  return items;
}

export async function verifyAdminAccessRequest(): Promise<string> {
  const response = await apiClient.get<{ message: string }>("/api/v1/admin/access/");
  return response.data.message;
}

// Category Admin CRUD
export async function fetchAdminCategories(): Promise<AdminCategory[]> {
  const response = await apiClient.get<AdminCategory[] | { results: AdminCategory[] }>(
    "/api/v1/admin/categories/",
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function createAdminCategory(payload: CreateCategoryInput): Promise<AdminCategory> {
  const response = await apiClient.post<AdminCategory>("/api/v1/admin/categories/", payload);
  return response.data;
}

export async function updateAdminCategory(
  id: number,
  payload: UpdateCategoryInput,
): Promise<AdminCategory> {
  const response = await apiClient.patch<AdminCategory>(`/api/v1/admin/categories/${id}/`, payload);
  return response.data;
}

export async function deleteAdminCategory(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/categories/${id}/`);
}

// Brand Admin CRUD
export async function fetchAdminBrands(): Promise<AdminBrand[]> {
  const response = await apiClient.get<AdminBrand[] | { results: AdminBrand[] }>(
    "/api/v1/admin/brands/",
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function createAdminBrand(payload: CreateBrandInput): Promise<AdminBrand> {
  const response = await apiClient.post<AdminBrand>("/api/v1/admin/brands/", payload);
  return response.data;
}

export async function updateAdminBrand(id: number, payload: UpdateBrandInput): Promise<AdminBrand> {
  const response = await apiClient.patch<AdminBrand>(`/api/v1/admin/brands/${id}/`, payload);
  return response.data;
}

export async function deleteAdminBrand(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/brands/${id}/`);
}

export async function fetchAdminProducts(): Promise<AdminProduct[]> {
  return fetchAllAdminPages<AdminProduct>("/api/v1/admin/products/");
}

export async function createProduct(payload: CreateProductInput): Promise<AdminProduct> {
  const response = await apiClient.post<AdminProduct>("/api/v1/admin/products/", payload);
  return response.data;
}

export async function updateProduct(
  id: number,
  payload: UpdateProductInput,
): Promise<AdminProduct> {
  const response = await apiClient.patch<AdminProduct>(`/api/v1/admin/products/${id}/`, payload);
  return response.data;
}

export async function deleteProduct(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/products/${id}/`);
}

export async function updateProductStatus(
  id: number,
  status: "draft" | "published",
): Promise<AdminProduct> {
  const response = await apiClient.patch<AdminProduct>(`/api/v1/admin/products/${id}/`, { status });
  return response.data;
}

export async function fetchAdminVariants(productId?: number): Promise<AdminVariant[]> {
  const params = productId ? { product: productId } : undefined;
  return fetchAllAdminPages<AdminVariant>("/api/v1/admin/variants/", params);
}

export async function adjustVariantInventory(
  variantId: number,
  payload: InventoryAdjustmentInput,
): Promise<StockMovementItem> {
  const response = await apiClient.post<StockMovementItem>(
    `/api/v1/admin/inventory/variants/${variantId}/adjustments/`,
    payload,
  );
  return response.data;
}

export async function fetchVariantStockMovements(variantId: number): Promise<StockMovementItem[]> {
  const response = await apiClient.get<StockMovementItem[] | { results: StockMovementItem[] }>(
    `/api/v1/admin/inventory/variants/${variantId}/movements/`,
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export interface AdminOrderListItem {
  id: number;
  number?: string;
  customer_email?: string;
  status:
    "pending_confirmation" | "confirmed" | "preparing" | "shipped" | "completed" | "cancelled";
  payment_method: string;
  payment_status: string;
  subtotal: string;
  shipping_fee: string;
  discount_total: string;
  total: string;
  currency: string;
  recipient_name?: string;
  phone_number?: string;
  province?: string;
  district?: string;
  ward?: string;
  street_address?: string;
  shipping_address?: {
    recipient_name: string;
    phone_number: string;
    province: string;
    district: string;
    ward: string;
    street_address: string;
  };
  items: Array<{
    id: number;
    product_name: string;
    sku: string;
    size_label?: string;
    color_name?: string;
    quantity: number;
    unit_price: string;
    line_total: string;
  }>;
  status_history?: Array<{
    id: number;
    from_status: string;
    to_status: string;
    actor_email?: string;
    note?: string;
    created_at: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface OrderTransitionPayload {
  to_status: string;
  expected_updated_at: string;
  note?: string;
}

export async function fetchAdminOrders(statusFilter?: string): Promise<AdminOrderListItem[]> {
  const params = statusFilter ? { status: statusFilter } : undefined;
  const response = await apiClient.get<AdminOrderListItem[] | { results: AdminOrderListItem[] }>(
    "/api/v1/admin/orders/",
    { params },
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function fetchAdminOrderDetail(orderId: number): Promise<AdminOrderListItem> {
  const response = await apiClient.get<AdminOrderListItem>(`/api/v1/admin/orders/${orderId}/`);
  return response.data;
}

export async function transitionAdminOrder(
  orderId: number,
  payload: OrderTransitionPayload,
): Promise<AdminOrderListItem> {
  const response = await apiClient.post<AdminOrderListItem>(
    `/api/v1/admin/orders/${orderId}/transitions/`,
    payload,
  );
  return response.data;
}

// ==========================================
// Size Admin CRUD
// ==========================================
export interface AdminSize {
  id: number;
  brand: number;
  brand_name?: string;
  label: string;
  sort_order: number;
  is_active: boolean;
}

export interface CreateSizeInput {
  brand: number;
  label: string;
  sort_order?: number;
  is_active?: boolean;
}

export interface UpdateSizeInput {
  brand?: number;
  label?: string;
  sort_order?: number;
  is_active?: boolean;
}

export async function fetchAdminSizes(brandId?: number): Promise<AdminSize[]> {
  const params = brandId ? { brand: brandId } : undefined;
  const response = await apiClient.get<AdminSize[] | { results: AdminSize[] }>(
    "/api/v1/admin/sizes/",
    { params },
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function createAdminSize(payload: CreateSizeInput): Promise<AdminSize> {
  const response = await apiClient.post<AdminSize>("/api/v1/admin/sizes/", payload);
  return response.data;
}

export async function updateAdminSize(id: number, payload: UpdateSizeInput): Promise<AdminSize> {
  const response = await apiClient.patch<AdminSize>(`/api/v1/admin/sizes/${id}/`, payload);
  return response.data;
}

export async function deleteAdminSize(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/sizes/${id}/`);
}

// ==========================================
// Color Admin CRUD
// ==========================================
export interface AdminColor {
  id: number;
  name: string;
  slug: string;
  hex_code?: string;
  is_active: boolean;
}

export interface CreateColorInput {
  name: string;
  slug: string;
  hex_code?: string;
  is_active?: boolean;
}

export interface UpdateColorInput {
  name?: string;
  slug?: string;
  hex_code?: string;
  is_active?: boolean;
}

export async function fetchAdminColors(): Promise<AdminColor[]> {
  const response = await apiClient.get<AdminColor[] | { results: AdminColor[] }>(
    "/api/v1/admin/colors/",
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function createAdminColor(payload: CreateColorInput): Promise<AdminColor> {
  const response = await apiClient.post<AdminColor>("/api/v1/admin/colors/", payload);
  return response.data;
}

export async function updateAdminColor(id: number, payload: UpdateColorInput): Promise<AdminColor> {
  const response = await apiClient.patch<AdminColor>(`/api/v1/admin/colors/${id}/`, payload);
  return response.data;
}

export async function deleteAdminColor(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/colors/${id}/`);
}

// ==========================================
// Product Variant CRUD
// ==========================================
export interface CreateVariantInput {
  product: number;
  size?: number | null;
  color?: number | null;
  option_label?: string;
  sku: string;
  price: string | number;
  currency?: string;
  low_stock_threshold?: number;
  is_active?: boolean;
}

export interface UpdateVariantInput {
  product?: number;
  size?: number | null;
  color?: number | null;
  option_label?: string;
  sku?: string;
  price?: string | number;
  currency?: string;
  low_stock_threshold?: number;
  is_active?: boolean;
}

export async function createAdminVariant(payload: CreateVariantInput): Promise<AdminVariant> {
  const response = await apiClient.post<AdminVariant>("/api/v1/admin/variants/", payload);
  return response.data;
}

export async function updateAdminVariant(
  id: number,
  payload: UpdateVariantInput,
): Promise<AdminVariant> {
  const response = await apiClient.patch<AdminVariant>(`/api/v1/admin/variants/${id}/`, payload);
  return response.data;
}

export async function deleteAdminVariant(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/variants/${id}/`);
}

// ==========================================
// Product Image Admin CRUD
// ==========================================
export interface AdminProductImage {
  id: number;
  product: number;
  image_url: string;
  alt_text?: string;
  sort_order: number;
  is_primary: boolean;
  created_at: string;
}

export async function fetchAdminProductImages(productId?: number): Promise<AdminProductImage[]> {
  const params = productId ? { product: productId } : undefined;
  const response = await apiClient.get<AdminProductImage[] | { results: AdminProductImage[] }>(
    "/api/v1/admin/product-images/",
    { params },
  );
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function uploadAdminProductImage(formData: FormData): Promise<AdminProductImage> {
  const response = await apiClient.post<AdminProductImage>(
    "/api/v1/admin/product-images/",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return response.data;
}

export async function updateAdminProductImage(
  id: number,
  payload: { alt_text?: string; sort_order?: number; is_primary?: boolean },
): Promise<AdminProductImage> {
  const response = await apiClient.patch<AdminProductImage>(
    `/api/v1/admin/product-images/${id}/`,
    payload,
  );
  return response.data;
}

export async function deleteAdminProductImage(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/product-images/${id}/`);
}
