export type ExchangeStatus =
  | "pending"
  | "approved"
  | "received"
  | "inspected"
  | "replacement_ready"
  | "replacement_shipped"
  | "completed"
  | "rejected"
  | "cancelled";

export interface ExchangeItem {
  id: number;
  order_item: number;
  product_name: string;
  product_slug: string;
  source_variant_id: number;
  source_sku: string;
  source_size: string;
  source_color: string;
  target_variant: number;
  target_sku: string;
  target_size: string;
  target_color: string;
  quantity: number;
  received_quantity: number;
  accepted_quantity: number;
  disposition: "pending" | "restock" | "damaged";
  inspection_note: string;
}

export interface ExchangeHistory {
  id: number;
  from_status: string;
  to_status: string;
  actor_email: string | null;
  note: string;
  created_at: string;
}

export interface ExchangeRequest {
  id: number;
  order: number;
  order_number: string;
  customer_email: string;
  status: ExchangeStatus;
  reason: string;
  evidence_url: string;
  customer_note: string;
  staff_note: string;
  tracking_number: string;
  approved_by_email: string | null;
  reservation_expires_at: string | null;
  items: ExchangeItem[];
  status_history: ExchangeHistory[];
  created_at: string;
  updated_at: string;
}

export interface CreateExchangeInput {
  order_id: number;
  reason: string;
  evidence_url?: string;
  customer_note?: string;
  items: Array<{ order_item_id: number; target_variant_id: number; quantity: number }>;
}

export interface ExchangeTransitionInput {
  action: "approve" | "reject" | "receive" | "inspect" | "prepare" | "ship";
  expected_updated_at: string;
  note?: string;
  tracking_number?: string;
  received_items?: Array<{ item_id: number; received_quantity: number }>;
  inspected_items?: Array<{
    item_id: number;
    accepted_quantity: number;
    disposition: "restock" | "damaged";
    inspection_note?: string;
  }>;
}
