import { apiClient } from "@/lib/http/client";

import type { Address, AddressPayload } from "../types";

const ADDRESS_URL = "/api/v1/account/addresses/";
const addressUrl = (id: number) => `${ADDRESS_URL}${String(id)}/`;

export async function listAddressesRequest(): Promise<Address[]> {
  return (await apiClient.get<Address[]>(ADDRESS_URL)).data;
}

export async function createAddressRequest(payload: AddressPayload): Promise<Address> {
  return (await apiClient.post<Address>(ADDRESS_URL, payload)).data;
}

export async function updateAddressRequest(id: number, payload: AddressPayload): Promise<Address> {
  return (await apiClient.patch<Address>(addressUrl(id), payload)).data;
}

export async function deleteAddressRequest(id: number): Promise<void> {
  await apiClient.delete(addressUrl(id));
}

export async function setDefaultAddressRequest(id: number): Promise<Address> {
  return (await apiClient.post<Address>(`${addressUrl(id)}set-default/`)).data;
}
