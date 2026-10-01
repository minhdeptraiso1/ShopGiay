import { loginValuesSchema, registerValuesSchema } from ".";

describe("loginValuesSchema", () => {
  it("rejects malformed email and an empty password", () => {
    const result = loginValuesSchema.safeParse({ email: "not-an-email", password: "" });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.flatten().fieldErrors.email).toContain("Email chưa đúng định dạng.");
    expect(result.error.flatten().fieldErrors.password).toContain("Vui lòng nhập mật khẩu.");
  });

  it("rejects mismatched registration passwords", () => {
    const result = registerValuesSchema.safeParse({
      fullName: "Nguyễn Văn A",
      email: "customer@example.com",
      password: "StrongPass!123",
      passwordConfirm: "different",
    });
    expect(result.success).toBe(false);
    if (!result.success) expect(result.error.flatten().fieldErrors.passwordConfirm).toBeDefined();
  });
});
