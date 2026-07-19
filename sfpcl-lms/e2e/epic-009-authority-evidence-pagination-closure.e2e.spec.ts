import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidence = process.env.RALPH_EVIDENCE_DIR;
if (!evidence) throw new Error('RALPH_EVIDENCE_DIR is required');
fs.mkdirSync(evidence, { recursive: true });
test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

test('Loan Account 360 retains every governed tab as explicitly unavailable', async ({ page }) => {
  await staffSession(page);
  await page.route('**/api/v1/auth/me/', route => json(route, staffUser));
  await page.route('**/api/v1/loan-accounts/**', route => {
    const list = new URL(route.request().url()).pathname === '/api/v1/loan-accounts/';
    return json(route, list ? [loan] : loan, list ? pagination : undefined);
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Loan Accounts', exact: true }).click();
  await page.getByText('LN-E2E-009L3', { exact: true }).click();
  await page.getByRole('button', { name: 'Loan Ledger', exact: true }).click();
  await expect(page.getByText('Loan Ledger is not available yet.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Repayment Schedule' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Audit Trail' })).toBeVisible();
  await page.screenshot({ path: path.join(evidence, 'loan-account-tabs-unavailable.png'), fullPage: true });
});

test('MP14 uses the selected finance application in both opposite list orders', async ({ page }) => {
  await portalSession(page);
  await page.route('**/api/v1/auth/me/', route => json(route, portalUser));
  let applications = [otherApplication, selectedApplication];
  await page.route('**/api/v1/portal/dashboard/', route => json(route, dashboard));
  await page.route('**/api/v1/portal/applications/', route => json(route, { items: applications }));
  await page.route('**/api/v1/portal/applications/app-selected/', route => json(route, selectedApplication));
  await page.route('**/api/v1/portal/applications/*/disbursement-status/', async route => {
    expect(new URL(route.request().url()).pathname).toContain('/app-selected/');
    await json(route, disbursementStatus);
  });

  for (const reverse of [false, true]) {
    applications = reverse
      ? [selectedApplication, otherApplication]
      : [otherApplication, selectedApplication];
    await page.goto('/');
    await page.getByRole('navigation').getByRole('button', { name: 'My Applications', exact: true }).click();
    await page.getByText('APP-SELECTED', { exact: true }).click();
    await page.getByRole('navigation').getByRole('button', { name: 'Disbursement', exact: true }).click();
    await expect(page.getByText('Loan amount transferred.', { exact: true }).first()).toBeVisible();
  }
  await page.screenshot({ path: path.join(evidence, 'mp14-opposite-order-selection.png'), fullPage: true });
});

const staffSession = (page: Page) => page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'staff', refreshToken: 'staff' })));
const portalSession = (page: Page) => page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'portal', refreshToken: 'portal' })));
const json = (route: Route, data: unknown, extra?: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...(extra ? { pagination: extra } : {}) }) });
const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const staffUser = { user_id: 'staff', full_name: 'Accounts Head', email: 'accounts@example.test', status: 'active', roles: [{ role_code: 'accounts_head', role_name: 'Accounts Head' }], teams: [], role_codes: ['accounts_head'], team_codes: [], permissions: ['finance.loan_account.read'], available_actions: [] };
const portalUser = { user_id: 'portal', full_name: 'Portal Member', email: 'portal@example.test', status: 'active', roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }], teams: [], role_codes: ['borrower_portal_user'], team_codes: [], permissions: ['portal.loan_application.read_own'], available_actions: [], member_id: 'member-1', portal_account_id: 'portal-1', portal_role: 'borrower_member', member_display_name: 'Portal Member' };
const loan = { loan_account_id: 'loan-009l3', loan_account_number: 'LN-E2E-009L3', loan_application_id: 'app-selected', application_reference_number: 'APP-SELECTED', member: { member_id: 'member-1', display_name: 'Portal Member' }, sap_customer_code: '******-009', loan_type: 'short_term', facility_type: 'short_term', interest_rate_type: 'floating', current_interest_rate: '9.2500', sanctioned_amount: '400000.00', disbursed_amount: '400000.00', principal_outstanding: '400000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '400000.00', loan_account_status: 'active', tenure_start_date: '2026-07-19', tenure_end_date: null, repayment_date: '2027-07-19', tenure_months: 12, created_at: '2026-07-19T05:00:00Z', activated_at: '2026-07-19T05:00:00Z' };
const member = { member_id: 'member-1', member_number: 'MEM-1', member_type: 'individual_farmer', display_name: 'Portal Member', folio_number: 'FOL-1', membership_status: 'active', kyc_status: 'verified', default_status: 'no_default', share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 }, active_member_status: { status: 'active', verified_at: null } };
const selectedApplication = { loan_application_id: 'app-selected', application_reference_number: 'APP-SELECTED', display_reference: 'APP-SELECTED', application_date: '2026-07-18', submitted_at: '2026-07-18T08:00:00Z', required_loan_amount: '400000.00', declared_purpose: 'Crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term', requested_tenure_months: 12, application_status: 'approved_by_sanction_committee', current_stage: 'disbursement', completeness_status: 'complete', pending_with: 'Finance', borrower_action: 'No action required', open_deficiency_count: 0, created_at: '2026-07-18T07:00:00Z', updated_at: '2026-07-18T08:00:00Z', member, timeline: [], deficiencies: [] };
const otherApplication = { ...selectedApplication, loan_application_id: 'app-other', application_reference_number: 'APP-OTHER', display_reference: 'APP-OTHER' };
const dashboard = { member, application_counts: { total: 2 }, loan_counts: { active: 1 }, pending_actions: {}, notices: [] };
const disbursementStatus = { loan_application_id: 'app-selected', loan_account_id: 'loan-009l3', status_code: 'disbursed', status_label: 'Loan amount transferred.', sanctioned_amount: '400000.00', disbursement_amount: '400000.00', destination_account_last4: '4321', disbursed_at: '2026-07-19T05:00:00Z', bank_reference_last4: '9876', advice_available: true, timeline: [['documentation_complete', 'Documents completed.'], ['sap_setup', 'Finance setup complete.'], ['payment_initiated', 'Payment processing started.'], ['cfc_authorisation', 'Payment approved.'], ['transfer_completed', 'Loan amount transferred.'], ['advice_issued', 'Advice issued']].map(([code, label]) => ({ code, label, status: 'complete', completed_at: '2026-07-19T05:00:00Z' })) };
