export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Size {
  id: number;
  brand: number;
  brand_name?: string;
  label: string;
  sort_order: number;
  is_active: boolean;
}

export interface Color {
  id: number;
  name: string;
  slug: string;
  hex_code?: string;
  is_active: boolean;
}

export interface ProductImage {
  id: number;
  product: number;
  image_url: string;
  alt_text?: string;
  sort_order: number;
  is_primary: boolean;
  created_at: string;
}

export interface ProductVariant {
  id: number;
  sku: string;
  size: Size | null;
  color: Color | null;
  option_label: string;
  price: string;
  currency: string;
  inventory_quantity: number;
  is_available: boolean;
}

export interface ProductListItem {
  id: number;
  name: string;
  slug: string;
  category: Category | null;
  brand: Brand | null;
  product_type: "footwear" | "accessory" | "care";
  primary_image: ProductImage | null;
  min_price: string | null;
  max_price: string | null;
  currency: string | null;
  is_available: boolean;
  published_at: string | null;
}

export interface ProductDetail extends ProductListItem {
  description: string;
  variants: ProductVariant[];
  images: ProductImage[];
}

export interface ProductQueryParams {
  search?: string;
  category?: string;
  brand?: string;
  size?: string;
  color?: string;
  min_price?: number | string;
  max_price?: number | string;
  in_stock?: boolean;
  ordering?: "newest" | "name" | "-name" | "price" | "-price";
  page?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type ProductEventType =
  | "view"
  | "recommendation_impression"
  | "recommendation_click"
  | "wishlist_add"
  | "wishlist_remove";

export interface ProductEventPayload {
  client_event_id?: string;
  schema_version?: number;
  event_type: ProductEventType;
  source?: string;
  product: number;
  anonymous_id?: string | null;
  recommendation_context_id?: string | null;
}

export interface RecommendationResponse {
  request_id: string;
  strategy: "popular" | "similar" | "personalized";
  fallback_used: boolean;
  results: ProductListItem[];
}
