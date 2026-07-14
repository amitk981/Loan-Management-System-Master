import path from 'path';
import { expect, type Locator, type Page } from '@playwright/test';

// Deterministic staff users seeded by the backend command `seed_e2e_users`
// (sfpcl_credit/identity/management/commands/seed_e2e_users.py). Credentials are
// non-secret and for the local E2E suite only.
export const TRACER_EMAIL = 'e2e.tracer@sfpcl.example';
export const ZERO_EMAIL = 'e2e.zero@sfpcl.example';
export const E2E_PASSWORD = 'E2eTracer123!';
const DASHBOARD_BASELINE_INSTANT = new Date('2026-07-10T14:00:00+05:30');

/** Freeze only dashboard screenshot scenarios at the instant committed in their baselines. */
export async function freezeDashboardClock(page: Page): Promise<void> {
  await page.clock.setFixedTime(DASHBOARD_BASELINE_INSTANT);
}

/**
 * Logs in through the real staff auth path — POST /api/v1/auth/login/ followed by
 * GET /api/v1/auth/me/ — by driving the login form. It never injects tokens or
 * mocks the backend, so the suite fails if the login call is bypassed (002EY req 7).
 */
export async function staffLogin(page: Page, email: string, password: string): Promise<void> {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
  await page.getByPlaceholder('you@sfpcl.in').fill(email);
  await page.locator('input[type="password"]').fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  // The staff shell (sidebar) renders only after /auth/me/ resolves.
  await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
}

export async function captureReviewableEvidence(
  page: Page,
  evidence: Locator,
  evidenceDir: string,
  fileName: string,
): Promise<void> {
  await evidence.scrollIntoViewIfNeeded();
  const box = await evidence.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.y).toBeGreaterThanOrEqual(0);
  expect(box!.y + box!.height).toBeLessThanOrEqual(720);
  const screenshot = await page.screenshot({ path: path.join(evidenceDir, fileName), animations: 'disabled' });
  const stats = await page.evaluate(async dataUrl => {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.width; canvas.height = image.height;
    const context = canvas.getContext('2d')!;
    context.drawImage(image, 0, 0);
    const pixels = context.getImageData(0, 0, image.width, image.height).data;
    let opaqueDark = 0;
    const buckets = new Set<number>();
    for (let index = 0; index < pixels.length; index += 16) {
      const red = pixels[index]; const green = pixels[index + 1]; const blue = pixels[index + 2];
      if (red < 12 && green < 12 && blue < 12) opaqueDark += 1;
      buckets.add((red >> 5) * 64 + (green >> 5) * 8 + (blue >> 5));
    }
    const tileSize = 64;
    const columns = Math.ceil(image.width / tileSize);
    const rows = Math.ceil(image.height / tileSize);
    const uniform = Array<boolean>(columns * rows).fill(false);
    for (let tileY = 0; tileY < rows; tileY += 1) {
      for (let tileX = 0; tileX < columns; tileX += 1) {
        let min = 255; let max = 0;
        for (let y = tileY * tileSize; y < Math.min((tileY + 1) * tileSize, image.height); y += 4) {
          for (let x = tileX * tileSize; x < Math.min((tileX + 1) * tileSize, image.width); x += 4) {
            const offset = (y * image.width + x) * 4;
            for (let channel = 0; channel < 3; channel += 1) {
              min = Math.min(min, pixels[offset + channel]); max = Math.max(max, pixels[offset + channel]);
            }
          }
        }
        uniform[tileY * columns + tileX] = max - min <= 4;
      }
    }
    const visited = Array<boolean>(uniform.length).fill(false);
    let largestUniformRegion = 0;
    for (let start = 0; start < uniform.length; start += 1) {
      if (!uniform[start] || visited[start]) continue;
      const queue = [start]; visited[start] = true; let size = 0;
      while (queue.length) {
        const current = queue.pop()!; size += 1;
        const x = current % columns; const y = Math.floor(current / columns);
        for (const next of [x > 0 ? current - 1 : -1, x + 1 < columns ? current + 1 : -1, y > 0 ? current - columns : -1, y + 1 < rows ? current + columns : -1]) {
          if (next >= 0 && uniform[next] && !visited[next]) { visited[next] = true; queue.push(next); }
        }
      }
      largestUniformRegion = Math.max(largestUniformRegion, size);
    }
    return { width: image.width, height: image.height, darkRatio: opaqueDark / (pixels.length / 16), colorBuckets: buckets.size, largestUniformRegionRatio: largestUniformRegion / uniform.length };
  }, `data:image/png;base64,${screenshot.toString('base64')}`);
  expect(stats).toMatchObject({ width: 1280, height: 720 });
  expect(stats.darkRatio).toBeLessThan(0.2);
  expect(stats.colorBuckets).toBeGreaterThan(16);
  expect(stats.largestUniformRegionRatio).toBeLessThan(0.3);
}
