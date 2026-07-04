import { test, expect } from '@playwright/test';
import { E2E_PASSWORD, TRACER_EMAIL, staffLogin } from './helpers';

// The five lifecycle rows the closed-state tracer must render (002EY req 15).
const LIFECYCLE_ROWS = ['Member', 'Application', 'Sanction', 'Loan account', 'Repayment'];

test.describe('staff tracer lifecycle (production auth path)', () => {
  test('login screen matches the approved visual baseline', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
    await expect(page).toHaveScreenshot('login.png', { fullPage: true });
  });

  test('logs in, walks the tracer to a closed loan, with dashboard + tracer baselines', async ({ page }) => {
    await staffLogin(page, TRACER_EMAIL, E2E_PASSWORD);

    // Authenticated neutral backend-staff dashboard (002EY req 12): the tracer
    // user's only affordance beyond Dashboard is the Tracer workspace.
    await expect(page.getByRole('button', { name: 'Tracer' })).toBeVisible();
    await expect(page).toHaveScreenshot('dashboard.png', { fullPage: true });

    // Reach the tracer only through the shell nav — no direct API calls (req 15).
    await page.getByRole('button', { name: 'Tracer' }).click();
    await expect(page.getByRole('heading', { name: 'Tracer' })).toBeVisible();

    await page.getByRole('button', { name: 'Run tracer' }).click();

    // All seven backend transitions have completed once every row is visible and
    // the loan-account row shows the Closed status (002EY req 15, test cases).
    for (const label of LIFECYCLE_ROWS) {
      await expect(page.getByText(label, { exact: true })).toBeVisible();
    }
    await expect(page.getByText('Closed', { exact: true })).toBeVisible();

    // Finding 2 (arch review 2026-07-04_071340): the Sanction row status is now
    // derived from the real sanction response ('Sanctioned'), never the old dead
    // 'recorded' branch.
    await expect(page.getByText('Sanctioned', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Recorded', { exact: true })).toHaveCount(0);

    await expect(page).toHaveScreenshot('tracer-closed.png', { fullPage: true });
  });
});
