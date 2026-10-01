import { test, chromium } from "@playwright/test";

test("take updated screenshots", async () => {
  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const page = await browser.newPage();
  const outputDir = "C:/Users/minh/.gemini/antigravity/brain/c5123508-7a16-4bd9-bd29-4b0b3d88f264";

  const viewports = [
    { name: "desktop-1440px", width: 1440, height: 900 },
    { name: "laptop-1024px", width: 1024, height: 768 },
    { name: "tablet-768px", width: 768, height: 1024 },
    { name: "mobile-390px", width: 390, height: 844 },
  ];

  for (const vp of viewports) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto("http://localhost:5173/", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: `${outputDir}/screenshot_${vp.name}.png` });
    console.log(`Captured ${vp.name}`);
  }

  await browser.close();
});
