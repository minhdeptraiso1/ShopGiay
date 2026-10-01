import type { ProductListItem } from "@/modules/catalog/types";

export interface WishlistItem {
  id: number;
  product: ProductListItem;
  created_at: string;
}

export interface Review {
  id: number;
  user: number;
  user_name: string;
  product: number;
  product_name: string;
  order_item: number;
  rating: number;
  content: string;
  status: "pending" | "approved" | "rejected";
  moderation_note: string;
  moderator_email: string | null;
  moderated_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Banner {
  id: number;
  title: string;
  subtitle: string;
  image_url: string;
  target_url: string;
  position: "home_hero" | "home_strip" | "products_top";
  starts_at: string;
  ends_at: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Voucher {
  id: number;
  code: string;
  name: string;
  discount_type: "percent" | "fixed";
  value: string;
  max_discount: string | null;
  min_order_value: string;
  required_points: number;
  starts_at: string;
  ends_at: string;
  usage_limit: number | null;
  per_user_limit: number;
  products: number[];
  categories: number[];
  is_active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export type VoucherInput = Omit<Voucher, "id" | "usage_count" | "created_at" | "updated_at">;
export type BannerInput = Omit<Banner, "id" | "created_at" | "updated_at">;

export interface EligibleVoucher {
  id: number;
  code: string;
  name: string;
  discount_type: "percent" | "fixed";
  value: string;
  max_discount: string | null;
  min_order_value: string;
  required_points: number;
  discount_total: string;
  total: string;
}

export interface EligibleVoucherResult {
  points_balance: number;
  vouchers: EligibleVoucher[];
}
