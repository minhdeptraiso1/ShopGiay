import { apiClient } from "@/lib/http/client";
import type {
  Brand,
  Category,
  Color,
  PaginatedResponse,
  ProductDetail,
  ProductEventPayload,
  ProductListItem,
  ProductQueryParams,
  RecommendationResponse,
  Size,
} from "./types";

function createUuid(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (character) =>
    (
      Number(character) ^
      (Math.floor(Math.random() * 256) & (15 >> (Number(character) / 4)))
    ).toString(16),
  );
}

export function getOrCreateAnonymousId(): string {
  if (typeof window === "undefined") return "00000000-0000-0000-0000-000000000000";
  const STORAGE_KEY = "catalog_anonymous_id";
  let anonId = localStorage.getItem(STORAGE_KEY);
  if (!anonId) {
    anonId = createUuid();
    localStorage.setItem(STORAGE_KEY, anonId);
  }
  return anonId;
}

export function generateEventId(): string {
  return createUuid();
}

const ATTRIBUTION_KEY = "recommendation_last_clicks";
type RecommendationAttribution = Record<string, { requestId: string; clickedAt: number }>;

function readRecommendationAttribution(): RecommendationAttribution {
  try {
    return JSON.parse(localStorage.getItem(ATTRIBUTION_KEY) || "{}") as RecommendationAttribution;
  } catch {
    localStorage.removeItem(ATTRIBUTION_KEY);
    return {};
  }
}

export function rememberRecommendationClick(productId: number, requestId: string): void {
  if (typeof window === "undefined") return;
  const current = readRecommendationAttribution();
  current[String(productId)] = { requestId, clickedAt: Date.now() };
  localStorage.setItem(ATTRIBUTION_KEY, JSON.stringify(current));
}

export function getRecommendationAttribution(productId: number): string | undefined {
  if (typeof window === "undefined") return undefined;
  const current = readRecommendationAttribution();
  const item = current[String(productId)];
  if (!item || Date.now() - item.clickedAt > 7 * 86_400_000) return undefined;
  return item.requestId;
}

export async function fetchCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Category[]>("/api/v1/categories/");
  return data;
}

export async function fetchBrands(): Promise<Brand[]> {
  const { data } = await apiClient.get<Brand[]>("/api/v1/brands/");
  return data;
}

export async function fetchSizes(brandSlug?: string): Promise<Size[]> {
  const { data } = await apiClient.get<Size[]>("/api/v1/sizes/", {
    params: brandSlug ? { brand: brandSlug } : undefined,
  });
  return data;
}

export async function fetchColors(): Promise<Color[]> {
  const { data } = await apiClient.get<Color[]>("/api/v1/colors/");
  return data;
}

export async function fetchProducts(
  params?: ProductQueryParams,
): Promise<PaginatedResponse<ProductListItem>> {
  const { data } = await apiClient.get<PaginatedResponse<ProductListItem>>("/api/v1/products/", {
    params,
  });
  return data;
}

export async function fetchProductDetail(slug: string): Promise<ProductDetail> {
  const { data } = await apiClient.get<ProductDetail>(`/api/v1/products/${slug}/`);
  return data;
}

export async function fetchPopularRecommendations(limit = 8): Promise<RecommendationResponse> {
  const { data } = await apiClient.get<RecommendationResponse>("/api/v1/recommendations/popular/", {
    params: { anonymous_id: getOrCreateAnonymousId(), limit },
  });
  return data;
}

export async function fetchPersonalizedRecommendations(limit = 8): Promise<RecommendationResponse> {
  const { data } = await apiClient.get<RecommendationResponse>(
    "/api/v1/recommendations/personalized/",
    { params: { anonymous_id: getOrCreateAnonymousId(), limit } },
  );
  return data;
}

export async function fetchSimilarRecommendations(
  productId: number,
  limit = 6,
): Promise<RecommendationResponse> {
  const { data } = await apiClient.get<RecommendationResponse>(
    `/api/v1/products/${String(productId)}/recommendations/`,
    { params: { anonymous_id: getOrCreateAnonymousId(), limit } },
  );
  return data;
}

export async function sendProductEvent(
  payload: Omit<ProductEventPayload, "client_event_id" | "schema_version" | "source"> & {
    client_event_id?: string;
  },
): Promise<void> {
  try {
    const fullPayload: ProductEventPayload = {
      client_event_id: payload.client_event_id || generateEventId(),
      schema_version: 1,
      event_type: payload.event_type,
      source: payload.event_type.startsWith("recommendation_") ? "recommendation" : "storefront",
      product: payload.product,
      anonymous_id: payload.anonymous_id ?? getOrCreateAnonymousId(),
      recommendation_context_id: payload.recommendation_context_id ?? null,
    };
    await apiClient.post("/api/v1/events/", fullPayload);
  } catch (err) {
    // Event ingestion errors should be non-blocking for storefront experience
    console.debug("[Event Ingestion] Non-blocking notice:", err);
  }
}
