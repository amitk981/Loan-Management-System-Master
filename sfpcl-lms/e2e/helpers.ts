import { expect, type Page } from '@playwright/test';

// Deterministic staff users seeded by the backend command `seed_e2e_users`
// (sfpcl_credit/identity/management/commands/seed_e2e_users.py). Credentials are
// non-secret and for the local E2E suite only.
export const TRACER_EMAIL = 'e2e.tracer@sfpcl.example';
export const ZERO_EMAIL = 'e2e.zero@sfpcl.example';
export const E2E_PASSWORD = 'E2eTracer123!';

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
