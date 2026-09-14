import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

export const profileSchema = toTypedSchema(
  z.object({
    fullName: z.string().max(255, "Họ tên không được vượt quá 255 ký tự."),
  }),
);
