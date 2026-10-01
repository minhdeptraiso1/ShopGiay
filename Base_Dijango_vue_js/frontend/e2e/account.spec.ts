import { expect, test } from "@playwright/test";

test("registration, login and owned delivery address", async ({ page }, testInfo) => {
  const email = `e2e-${testInfo.project.name}-${String(Date.now())}@example.com`;
  const password = "StrongPass!123";

  await page.goto("/register");
  await page.getByLabel("Họ và tên").fill("Khách hàng E2E");
  await page.getByLabel("Email").fill(email);
  await page.locator('input[name="password"]').fill(password);
  await page.getByLabel("Nhập lại mật khẩu").fill(password);
  await page.getByRole("button", { name: "Đăng ký", exact: true }).click();
  await expect(page).toHaveURL(/\/login\?registered=1$/);
  await expect(page.getByText("Tạo tài khoản thành công")).toBeVisible();

  await page.getByLabel("Email").fill(email);
  await page.locator('input[name="password"]').fill(password);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/\/$/);

  await page.getByRole("link", { name: "Hồ sơ", exact: true }).click();
  await page.getByRole("link", { name: "Địa chỉ", exact: true }).click();
  await page.getByLabel("Người nhận").fill("Khách hàng E2E");
  await page.getByLabel("Số điện thoại").fill("0901234567");
  await page.getByLabel("Tỉnh/Thành phố").fill("Hà Nội");
  await page.getByLabel("Quận/Huyện").fill("Ba Đình");
  await page.getByLabel("Phường/Xã").fill("Điện Biên");
  await page.getByLabel("Địa chỉ chi tiết").fill("12 Đường Độc Lập");
  await page.getByRole("button", { name: "Thêm địa chỉ" }).click();

  await expect(page.getByText("Đã thêm địa chỉ.")).toBeVisible();
  await expect(page.getByText("Mặc định", { exact: true })).toBeVisible();
  await expect(page.getByText(/12 Đường Độc Lập/)).toBeVisible();
});
