import { apiClient } from "@/lib/http/client";
import type {
  Banner,
  BannerInput,
  EligibleVoucherResult,
  Review,
  Voucher,
  VoucherInput,
  WishlistItem,
} from "./types";

export async function fetchEligibleVouchers(payload: {
  address_id: number;
  cart_item_ids: number[];
}): Promise<EligibleVoucherResult> {
  const response = await apiClient.post<EligibleVoucherResult>(
    "/api/v1/vouchers/eligible/",
    payload,
  );
  return response.data;
}

function unwrapList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

export async function fetchBanners(position?: Banner["position"]): Promise<Banner[]> {
  const response = await apiClient.get<Banner[]>("/api/v1/banners/", {
    params: position ? { position } : undefined,
  });
  return response.data;
}

export async function fetchWishlist(): Promise<WishlistItem[]> {
  const response = await apiClient.get<WishlistItem[]>("/api/v1/wishlist/");
  return response.data;
}

export async function toggleWishlist(product: number): Promise<boolean> {
  const response = await apiClient.post<{ product_id: number; is_wishlisted: boolean }>(
    "/api/v1/wishlist/",
    { product },
  );
  return response.data.is_wishlisted;
}

export async function removeWishlist(productId: number): Promise<void> {
  await apiClient.delete(`/api/v1/wishlist/${String(productId)}/`);
}

export async function fetchProductReviews(productId: number): Promise<Review[]> {
  const response = await apiClient.get<Review[]>(`/api/v1/products/${String(productId)}/reviews/`);
  return response.data;
}

export async function createProductReview(
  productId: number,
  payload: { order_item: number; rating: number; content: string },
): Promise<Review> {
  const response = await apiClient.post<Review>(
    `/api/v1/products/${String(productId)}/reviews/`,
    payload,
  );
  return response.data;
}

export async function fetchAdminVouchers(): Promise<Voucher[]> {
  const response = await apiClient.get<Voucher[] | { results: Voucher[] }>(
    "/api/v1/admin/vouchers/",
  );
  return unwrapList(response.data);
}

export async function createAdminVoucher(payload: VoucherInput): Promise<Voucher> {
  const response = await apiClient.post<Voucher>("/api/v1/admin/vouchers/", payload);
  return response.data;
}

export async function updateAdminVoucher(
  id: number,
  payload: Partial<VoucherInput>,
): Promise<Voucher> {
  const response = await apiClient.patch<Voucher>(`/api/v1/admin/vouchers/${String(id)}/`, payload);
  return response.data;
}

export async function deactivateAdminVoucher(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/vouchers/${String(id)}/`);
}

export async function fetchAdminReviews(status?: Review["status"]): Promise<Review[]> {
  const response = await apiClient.get<Review[] | { results: Review[] }>("/api/v1/admin/reviews/", {
    params: status ? { status } : undefined,
  });
  return unwrapList(response.data);
}

export async function moderateAdminReview(
  id: number,
  status: "approved" | "rejected",
  moderation_note = "",
): Promise<Review> {
  const response = await apiClient.post<Review>(`/api/v1/admin/reviews/${String(id)}/moderate/`, {
    status,
    moderation_note,
  });
  return response.data;
}

export async function fetchAdminBanners(): Promise<Banner[]> {
  const response = await apiClient.get<Banner[] | { results: Banner[] }>("/api/v1/admin/banners/");
  return unwrapList(response.data);
}

export async function createAdminBanner(payload: BannerInput): Promise<Banner> {
  const response = await apiClient.post<Banner>("/api/v1/admin/banners/", payload);
  return response.data;
}

export async function updateAdminBanner(
  id: number,
  payload: Partial<BannerInput>,
): Promise<Banner> {
  const response = await apiClient.patch<Banner>(`/api/v1/admin/banners/${String(id)}/`, payload);
  return response.data;
}

export async function deactivateAdminBanner(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/admin/banners/${String(id)}/`);
}
