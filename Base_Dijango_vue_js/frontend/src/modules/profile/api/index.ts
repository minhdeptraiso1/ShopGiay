import { apiClient } from "@/lib/http/client";
import type { User } from "@/modules/auth/types";

export async function updateProfileRequest(fullName: string): Promise<User> {
  return (await apiClient.patch<User>("/api/v1/auth/me/", { full_name: fullName })).data;
}
