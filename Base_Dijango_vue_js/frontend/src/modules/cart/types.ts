export interface CartVariantInfo {
  id: number;
  sku: string;
  price: string;
  currency: string;
  inventory_quantity: number;
  is_active?: boolean;
  is_available?: boolean;
  product_name?: string;
  product_slug?: string;
  brand_name?: string;
  size_label?: string;
  color_name?: string;
  option_label?: string;
  primary_image?: { id?: number; image_url: string; is_primary?: boolean } | null;
  size?: { id: number; label: string } | null;
  color?: { id: number; name: string; hex_code?: string } | null;
  product?: {
    id: number;
    name: string;
    slug: string;
    primary_image?: { image_url: string } | null;
  } | null;
}

export interface CartItem {
  id: number;
  variant: CartVariantInfo;
  quantity: number;
  line_total: string;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: number;
  user: number;
  items: CartItem[];
  subtotal: string;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface QuoteLine {
  cart_item_id: number;
  variant_id: number;
  sku: string;
  product_name: string;
  size_label?: string;
  color_name?: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface CheckoutQuote {
  address_id: number;
  lines: QuoteLine[];
  subtotal: string;
  shipping_fee: string;
  discount_total: string;
  total: string;
  currency: string;
  voucher_code: string;
}

export type PaymentMethod = "cod" | "vnpay";

export interface CreateOrderInput {
  address_id: number;
  cart_item_ids: number[];
  payment_method: PaymentMethod;
  voucher_code?: string;
}

export interface AddressSnapshot {
  recipient_name: string;
  phone_number: string;
  province: string;
  district: string;
  ward: string;
  street_address: string;
}

export interface OrderItemSnapshot {
  id: number;
  variant: number;
  product_name: string;
  product_slug: string;
  sku: string;
  size_label?: string;
  color_name?: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface OrderStatusHistoryItem {
  id: number;
  from_status: string;
  to_status: string;
  reason?: string;
  created_at: string;
}

export type OrderStatus =
  "pending_confirmation" | "confirmed" | "preparing" | "shipped" | "completed" | "cancelled";

export interface Order {
  id: number;
  number?: string;
  status: OrderStatus;
  payment_method: PaymentMethod;
  payment_status: string;
  subtotal: string;
  shipping_fee: string;
  discount_total: string;
  voucher_code?: string;
  total: string;
  currency: string;
  recipient_name?: string;
  phone_number?: string;
  province?: string;
  district?: string;
  ward?: string;
  street_address?: string;
  shipping_address?: AddressSnapshot;
  items: OrderItemSnapshot[];
  status_history?: OrderStatusHistoryItem[];
  created_at: string;
  updated_at?: string;
  cancelled_at?: string | null;
}
