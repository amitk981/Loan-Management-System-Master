import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import type { PortalDashboard } from '../src/services/portalApi';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test('available projection renders only the three server amounts', async ({ page }) => {
  const requests = await mountPortal(page, available(false));
  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText('Shareholding Limit')).toBeVisible();
  await expect(page.getByText('₹1,50,000')).toBeVisible();
  await expect(page.getByText('₹90,000')).toHaveCount(2);
  expect(requests).toEqual([{ method: 'GET', url: '/api/v1/portal/application-limit-projection/?requested_amount=500000', body: null }]);
  await expect(page.getByText(/PRIVATE|evidence|staff action|authority id/i)).toHaveCount(0);
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-limit-available.png'), fullPage: true });
});

test('unavailable projection has no invented zero or internal reason', async ({ page }) => {
  await mountPortal(page, unavailable);
  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText('Limit not yet available')).toBeVisible();
  await expect(page.getByText('₹0')).toHaveCount(0);
  await expect(page.getByText('verified_active_member_authority_not_available')).toHaveCount(0);
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-limit-unavailable.png'), fullPage: true });
});

test('over-limit advisory is derived only from the server flag', async ({ page }) => {
  await mountPortal(page, available(true));
  await page.getByRole('button', { name: 'Continue' }).click();
  await expect(page.getByText(/configured exception\/credit workflow/i)).toBeVisible();
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-limit-over-limit-advisory.png'), fullPage: true });
});

test('review repeats the canonical server maximum without recalculation', async ({ page }) => {
  await mountPortal(page, available(false));
  await page.getByRole('button', { name: 'Review' }).click();
  await expect(page.getByText('Maximum Limit').locator('..')).toContainText('₹90,000');
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-limit-review-maximum.png'), fullPage: true });
});

async function mountPortal(page: Page, projection: object) {
  const requests: Array<{ method: string; url: string; body: unknown }> = [];
  await page.route('**/api/v1/portal/auth/login/', route => json(route, {
    access_token: 'portal-real-boundary',
    refresh_token: 'portal-refresh',
    expires_in: 300,
    user: {},
  }));
  await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
  await page.route('**/api/v1/portal/dashboard/', route => json(route, dashboard));
  await page.route('**/api/v1/portal/profile/', route => json(route, { member: {}, nominees: [], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null }));
  await page.route('**/api/v1/portal/application-limit-projection/**', route => {
    const request = route.request();
    requests.push({ method: request.method(), url: new URL(request.url()).pathname + new URL(request.url()).search, body: request.postData() ? request.postDataJSON() : null });
    return json(route, projection);
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('portal@example.test');
  await page.getByLabel('Password').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  const newApplication = page.getByRole('button', { name: 'New Loan Application', exact: true });
  await expect(newApplication).toBeVisible({ timeout: 15_000 });
  await newApplication.click();
  await expect(page.getByRole('heading', { name: 'New Loan Application', exact: true })).toBeVisible();
  return requests;
}

const dashboard = {
  member: {
    member_id: 'member-safe',
    member_number: 'MEM-SAFE',
    member_type: 'individual_farmer',
    display_name: 'Portal Member',
    folio_number: 'FOL-SAFE',
    membership_status: 'active',
    kyc_status: 'verified',
    default_status: 'no_default',
    share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 },
    active_member_status: { status: 'active', verified_at: '2026-07-12T10:00:00Z' },
  },
  application_counts: {},
  loan_counts: {},
  pending_actions: {},
  notices: [],
} satisfies PortalDashboard;

const available = (exception: boolean) => ({ status: 'available', unavailable_reason: null, shareholding_based_limit_amount: '150000.00', land_based_limit_amount: '90000.00', final_eligible_loan_amount: '90000.00', requested_amount: '500000.00', amount_within_limit_flag: !exception, exception_required_flag: exception, calculated_as_of_date: '2026-07-12', calculation_rule_version: 'portal-limit-v1' });
const unavailable = { status: 'unavailable', unavailable_reason: 'verified_active_member_authority_not_available', shareholding_based_limit_amount: null, land_based_limit_amount: null, final_eligible_loan_amount: null, requested_amount: '500000.00', amount_within_limit_flag: null, exception_required_flag: null, calculated_as_of_date: null, calculation_rule_version: null };
const currentUser = { user_id: 'portal-user', full_name: 'Portal Member', email: 'portal@example.test', status: 'active', roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }], teams: [], role_codes: ['borrower_portal_user'], team_codes: [], permissions: [], available_actions: [], member_id: 'member-safe', portal_account_id: 'account-safe', portal_role: 'borrower_member', member_display_name: 'Portal Member' };
const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, meta: {} }) });
