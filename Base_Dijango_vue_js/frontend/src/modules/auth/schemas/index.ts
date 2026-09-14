import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

export const loginValuesSchema = z.object({
  email: z.string().min(1, "Vui lòng nhập email.").email("Email chưa đúng định dạng."),
  password: z.string().min(1, "Vui lòng nhập mật khẩu."),
});

export const loginSchema = toTypedSchema(loginValuesSchema);
