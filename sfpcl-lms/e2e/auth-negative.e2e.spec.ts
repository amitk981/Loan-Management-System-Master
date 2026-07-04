import { test, expect } from '@playwright/test';
import { E2E_PASSWORD, TRACER_EMAIL, ZERO_EMAIL, staffLogin } from './helpers';

const STAFF_NAV_LABELS = [
  'Task Inbox',
  'Applications',
  'Completeness',
  'Members & Borrowers',
  'Appraisal',
  'Sanction',
  'Documentation',
  'SAP & Disbursement',
  'Payment Authorisation',
  'Interest Management',
  'Loan Accounts',
  'Repayments',
  'Monitoring',
  'Default & Recovery',
  'Closure & Archive',
  'Compliance',
  'Registers',
  'Reports & MIS',
  'Grievances',
  'Audit & Archive',
  'Settings',
  'Tracer',
];

test.describe('auth negatives and restricted staff UI', () => {
  test('no stored session shows staff login and exposes no tracer route', async ({ page }) => {
    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
    // No authenticated shell affordances leak before login (002EY req 9).
    await expect(page.getByRole('button', { name: 'Tracer' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Dashboard' })).toHaveCount(0);

    await expect(page).toHaveScreenshot('login-missing-session.png', { fullPage: true });
  });

  test('invalid credentials keep the user on the login screen with an error', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder('you@sfpcl.in').fill('nobody@sfpcl.example');
    await page.locator('input[type="password"]').fill('WrongPassword123!');
    await page.getByRole('button', { name: 'Sign in' }).click();

    await expect(page.getByText('Invalid email or password.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Tracer' })).toHaveCount(0);

    await expect(page).toHaveScreenshot('login-invalid.png', { fullPage: true });
  });

  test('zero-permission staff sees the neutral dashboard, no tracer nav, no settings', async ({ page }) => {
    await staffLogin(page, ZERO_EMAIL, E2E_PASSWORD);

    // Neutral backend-staff shell: Dashboard only, no tracer/auditor/admin/borrower
    // affordances for an unmapped zero-permission role (002EY req 11, test case 5).
    await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
    for (const label of STAFF_NAV_LABELS) {
      await expect(page.getByRole('button', { name: label })).toHaveCount(0);
    }

    // Baseline the resting neutral dashboard before opening any menu.
    await expect(page).toHaveScreenshot('dashboard-zero-permission.png', { fullPage: true });

    // The profile menu must not offer a Settings shortcut without settings perms.
    const profileButton = page.getByRole('button', { name: /E2E Zero Permission Staff/ });
    await profileButton.click();
    await expect(page.getByRole('button', { name: 'My Profile' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Settings' })).toHaveCount(0);
  });

  test('tracer-only staff sees Tracer but no other protected staff workspaces', async ({ page }) => {
    await staffLogin(page, TRACER_EMAIL, E2E_PASSWORD);

    await expect(page.getByRole('button', { name: 'Dashboard' })).toBeVisible();
    // exact: true because the profile button ("E2E Tracer Staff") also contains "Tracer".
    await expect(page.getByRole('button', { name: 'Tracer', exact: true })).toBeVisible();

    for (const label of STAFF_NAV_LABELS.filter(label => label !== 'Tracer')) {
      await expect(page.getByRole('button', { name: label })).toHaveCount(0);
    }

    const profileButton = page.getByRole('button', { name: /E2E Tracer Staff/ });
    await profileButton.click();
    await expect(page.getByRole('button', { name: 'My Profile' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Settings' })).toHaveCount(0);
  });

  test('invalid stored session restores to staff login before protected shell items render', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem(
        'sfpcl_staff_auth_session',
        JSON.stringify({ accessToken: 'revoked-access-token', refreshToken: 'revoked-refresh-token' }),
      );
    });

    await page.goto('/');

    await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
    await expect(page.getByText('Your session expired. Please sign in again.')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Dashboard' })).toHaveCount(0);
    for (const label of STAFF_NAV_LABELS) {
      await expect(page.getByRole('button', { name: label })).toHaveCount(0);
    }
  });
});
