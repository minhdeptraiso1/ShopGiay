import { expect, test } from "@playwright/test";

test("CSRF, HttpOnly cookie, reload, profile and logout", async ({ page, context }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(process.env.E2E_USER_EMAIL || "demo@example.com");
  await page.locator('input[name="password"]').fill(process.env.E2E_USER_PASSWORD || "123456");
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).toHaveURL(/\/$/);

  const refreshCookie = (await context.cookies()).find((cookie) => cookie.name === "refresh_token");
  expect(refreshCookie?.httpOnly).toBe(true);
  expect(
    await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })),
  ).toEqual({
    local: 0,
    session: 0,
  });

  await page.reload();
  await expect(page.getByRole("heading", { name: /Xin chào/ })).toBeVisible();
  await page.getByRole("link", { name: "Hồ sơ", exact: true }).click();
  await page.getByLabel("Họ và tên").fill("Người dùng thử");
  await page.getByRole("button", { name: "Lưu thay đổi" }).click();
  await expect(page.getByText("Đã cập nhật hồ sơ.")).toBeVisible();

  await page.getByRole("button", { name: "Đăng xuất" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.reload();
  await expect(page).toHaveURL(/\/login$/);
});
