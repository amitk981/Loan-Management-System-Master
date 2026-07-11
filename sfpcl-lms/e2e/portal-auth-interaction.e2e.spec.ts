import { expect, test } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

const portalUser = {
  user_id: 'portal-user-1',
  full_name: 'Rendered Portal Member',
  email: 'member@example.test',
  status: 'active',
  roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower / Member' }],
  teams: [],
  role_codes: ['borrower_portal_user'],
  team_codes: [],
  permissions: ['portal.loan_application.read_own'],
  available_actions: ['portal.loan_application.create_own'],
  member_id: 'member-1',
  portal_account_id: 'portal-account-1',
  portal_role: 'borrower_member',
  member_display_name: 'Rendered Portal Member',
};

test.describe('portal auth rendered interaction authority (005FA4)', () => {
  test('empty and populated portal forms have one real-session path', async ({ page }) => {
    let portalLoginCalls = 0;
    let submittedBody: unknown;

    await page.route('**/api/v1/portal/auth/login/', async route => {
      portalLoginCalls += 1;
      submittedBody = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { access_token: 'portal-access', refresh_token: 'portal-refresh', expires_in: 300, user: {} },
        }),
      });
    });
    await page.route('**/api/v1/auth/me/', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: portalUser }),
    }));
    await page.route('**/api/v1/portal/dashboard/', route => route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ success: false, error: { code: 'TEST_ONLY', message: 'Dashboard intentionally unavailable.' } }),
    }));

    await page.goto('/');
    await expect(page.getByText('Demo role (select to preview as any user)')).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Continue with demo role' })).toHaveCount(0);
    await expect(page.getByText('Dashboard', { exact: true })).toHaveCount(0);

    await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
    await page.getByRole('button', { name: 'Sign in securely' }).click();
    await expect(page.getByText('Enter your registered contact and password.')).toBeVisible();
    expect(portalLoginCalls).toBe(0);
    await page.screenshot({ path: path.join(evidenceRoot, 'portal-login-validation.png'), fullPage: true });

    await page.getByLabel('Mobile Number or Email').fill('member@example.test');
    await page.getByLabel('Password').fill('correct horse battery staple');
    await page.getByRole('button', { name: 'Sign in securely' }).click();

    await expect(page.getByText('Rendered Portal Member').first()).toBeVisible();
    expect(portalLoginCalls).toBe(1);
    expect(submittedBody).toEqual({
      identifier: 'member@example.test',
      password: 'correct horse battery staple',
    });
  });

  test('failed network logout clears the backend identity and every protected surface', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
        accessToken: 'portal-access',
        refreshToken: 'portal-refresh',
      }));
    });
    await page.route('**/api/v1/auth/me/', route => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: portalUser }),
    }));
    await page.route('**/api/v1/portal/dashboard/', route => route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ success: false, error: { code: 'TEST_ONLY', message: 'Dashboard intentionally unavailable.' } }),
    }));
    await page.route('**/api/v1/auth/logout/', route => route.abort('failed'));

    await page.goto('/');
    await expect(page.getByText('Rendered Portal Member').first()).toBeVisible();
    await page.getByRole('button', { name: 'Sign out' }).click();

    await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
    await expect(page.getByText('Rendered Portal Member')).toHaveCount(0);
    await expect(page.getByText('Dashboard', { exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Continue with demo role' })).toHaveCount(0);
    await expect(page.evaluate(() => localStorage.getItem('sfpcl_staff_auth_session'))).resolves.toBeNull();
    await page.screenshot({ path: path.join(evidenceRoot, 'portal-post-logout.png'), fullPage: true });
  });
});
