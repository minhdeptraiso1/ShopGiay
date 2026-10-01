import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

export const addressValuesSchema = z.object({
  recipientName: z.string().trim().min(2, "Vui lòng nhập tên người nhận.").max(255),
  phoneNumber: z
    .string()
    .trim()
    .regex(/^\+?[0-9][0-9 .-]{7,18}[0-9]$/, "Số điện thoại chưa đúng định dạng."),
  province: z.string().trim().min(2, "Vui lòng nhập tỉnh hoặc thành phố.").max(100),
  district: z.string().trim().min(2, "Vui lòng nhập quận hoặc huyện.").max(100),
  ward: z.string().trim().min(2, "Vui lòng nhập phường hoặc xã.").max(100),
  streetAddress: z.string().trim().min(3, "Vui lòng nhập địa chỉ chi tiết.").max(255),
});

export const addressSchema = toTypedSchema(addressValuesSchema);
