import { loginValuesSchema } from ".";

describe("loginValuesSchema", () => {
  it("rejects malformed email and an empty password", () => {
    const result = loginValuesSchema.safeParse({ email: "not-an-email", password: "" });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.flatten().fieldErrors.email).toContain("Email chưa đúng định dạng.");
    expect(result.error.flatten().fieldErrors.password).toContain("Vui lòng nhập mật khẩu.");
  });
});
