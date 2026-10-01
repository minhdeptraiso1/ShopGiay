import { apiClient } from "@/lib/http/client";
import type { Cart, CartItem, CheckoutQuote, CreateOrderInput, Order } from "./types";

export function generateIdempotencyKey(): string {
  if (typeof globalThis.crypto.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return `order-${Math.random().toString(36).substring(2, 15)}-${String(Date.now())}`;
}

export async function fetchCart(): Promise<Cart> {
  const response = await apiClient.get<Cart>("/api/v1/cart/");
  return response.data;
}

export async function addToCart(
  variantId: number,
  quantity: number = 1,
  recommendationContextId?: string,
): Promise<CartItem> {
  const response = await apiClient.post<CartItem>("/api/v1/cart/items/", {
    variant: variantId,
    quantity,
    recommendation_context_id: recommendationContextId,
  });
  return response.data;
}

export async function updateCartItemQuantity(itemId: number, quantity: number): Promise<CartItem> {
  const response = await apiClient.patch<CartItem>(`/api/v1/cart/items/${String(itemId)}/`, {
    quantity,
  });
  return response.data;
}

export async function removeCartItem(itemId: number): Promise<void> {
  await apiClient.delete(`/api/v1/cart/items/${String(itemId)}/`);
}

export async function getCheckoutQuote(payload: {
  address_id: number;
  cart_item_ids: number[];
  voucher_code?: string;
}): Promise<CheckoutQuote> {
  const response = await apiClient.post<CheckoutQuote>("/api/v1/checkout/quote/", payload);
  return response.data;
}

export async function createOrder(
  payload: CreateOrderInput,
  idempotencyKey: string,
): Promise<Order> {
  const response = await apiClient.post<Order>("/api/v1/orders/", payload, {
    headers: {
      "Idempotency-Key": idempotencyKey,
    },
  });
  return response.data;
}

export async function createCodOrder(
  payload: Omit<CreateOrderInput, "payment_method">,
  idempotencyKey: string,
): Promise<Order> {
  return createOrder({ ...payload, payment_method: "cod" }, idempotencyKey);
}

export async function fetchMyOrders(): Promise<Order[]> {
  const response = await apiClient.get<Order[] | { results: Order[] }>("/api/v1/orders/");
  if (Array.isArray(response.data)) return response.data;
  if ("results" in response.data) return response.data.results;
  return [];
}

export async function fetchOrderDetail(orderId: number): Promise<Order> {
  const response = await apiClient.get<Order>(`/api/v1/orders/${String(orderId)}/`);
  return response.data;
}

export async function cancelOrder(orderId: number): Promise<Order> {
  const response = await apiClient.post<Order>(`/api/v1/orders/${String(orderId)}/cancel/`);
  return response.data;
}

export async function confirmOrderReceived(orderId: number): Promise<Order> {
  const response = await apiClient.post<Order>(
    `/api/v1/orders/${String(orderId)}/confirm-received/`,
  );
  return response.data;
}

export interface OrderPaymentInfo {
  id: number;
  provider: string;
  status: string;
  amount: string;
  currency: string;
  provider_transaction_no: string;
  paid_at: string | null;
  attempts: PaymentAttempt[];
  created_at: string;
  updated_at: string;
}

export interface PaymentAttempt {
  id: number;
  reference: string;
  status: string;
  checkout_url: string;
  expires_at: string;
  created_at: string;
}

export async function fetchOrderPayment(orderId: number): Promise<OrderPaymentInfo> {
  const response = await apiClient.get<OrderPaymentInfo>(
    `/api/v1/orders/${String(orderId)}/payment/`,
  );
  return response.data;
}

export async function createOrderPaymentAttempt(
  orderId: number,
  idempotencyKey: string,
  payload: { return_url?: string } = {},
): Promise<PaymentAttempt> {
  const response = await apiClient.post<PaymentAttempt>(
    `/api/v1/orders/${String(orderId)}/payment/`,
    payload,
    {
      headers: {
        "Idempotency-Key": idempotencyKey,
      },
    },
  );
  return response.data;
}

export interface VnpayReturnResult {
  response_code: string;
  message: string;
  order_status: string;
  payment_status: string;
}

export async function verifyVnpayReturn(
  orderId: number,
  params: Record<string, string>,
): Promise<VnpayReturnResult> {
  const response = await apiClient.post<VnpayReturnResult>(
    `/api/v1/orders/${String(orderId)}/payment/vnpay-return/`,
    { params },
  );
  return response.data;
}
