export interface Address {
  id: number;
  recipient_name: string;
  phone_number: string;
  province: string;
  district: string;
  ward: string;
  street_address: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export type AddressPayload = Omit<Address, "id" | "is_default" | "created_at" | "updated_at">;
