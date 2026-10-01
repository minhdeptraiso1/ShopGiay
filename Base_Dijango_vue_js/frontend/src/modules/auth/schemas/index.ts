import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

export const loginValuesSchema = z.object({
  email: z.string().min(1, "Vui lòng nhập email.").email("Email chưa đúng định dạng."),
  password: z.string().min(1, "Vui lòng nhập mật khẩu."),
});

export const loginSchema = toTypedSchema(loginValuesSchema);

export const registerValuesSchema = z
  .object({
    fullName: z.string().trim().min(2, "Vui lòng nhập họ và tên.").max(255),
    email: z.string().trim().min(1, "Vui lòng nhập email.").email("Email chưa đúng định dạng."),
    password: z.string().min(8, "Mật khẩu cần ít nhất 8 ký tự."),
    passwordConfirm: z.string().min(1, "Vui lòng nhập lại mật khẩu."),
  })
  .refine((values) => values.password === values.passwordConfirm, {
    path: ["passwordConfirm"],
    message: "Mật khẩu xác nhận không khớp.",
  });

export const registerSchema = toTypedSchema(registerValuesSchema);

export const passwordResetRequestSchema = toTypedSchema(
  z.object({
    email: z.string().trim().min(1, "Vui lòng nhập email.").email("Email chưa đúng định dạng."),
  }),
);

export const passwordResetConfirmValuesSchema = z
  .object({
    password: z.string().min(8, "Mật khẩu cần ít nhất 8 ký tự."),
    passwordConfirm: z.string().min(1, "Vui lòng nhập lại mật khẩu."),
  })
  .refine((values) => values.password === values.passwordConfirm, {
    path: ["passwordConfirm"],
    message: "Mật khẩu xác nhận không khớp.",
  });

export const passwordResetConfirmSchema = toTypedSchema(passwordResetConfirmValuesSchema);
