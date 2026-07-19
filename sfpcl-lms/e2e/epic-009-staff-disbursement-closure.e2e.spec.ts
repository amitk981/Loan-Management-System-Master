import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidence = process.env.RALPH_EVIDENCE_DIR;
if (!evidence) throw new Error('RALPH_EVIDENCE_DIR is required');
fs.mkdirSync(evidence, { recursive: true });
test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

test('S36-S41 and initial Loan Account 360 remain walkable and safely rendered', async ({ page }) => {
  let workspace = row('completed', false, []);
  let accountStatus = 'sanctioned';
  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'epic009', refreshToken: 'epic009' })));
  await page.route('**/api/v1/auth/me/', route => json(route, user));
  await page.route('**/api/v1/disbursement-workspaces/**', route => json(route, [workspace], pagination));
  await page.route('**/api/v1/loan-accounts/**', route => { const list = new URL(route.request().url()).pathname === '/api/v1/loan-accounts/'; return json(route, list ? [loan(accountStatus)] : loan(accountStatus), list ? pagination : undefined); });
  await page.goto('/');

  await open(page, 'Loan Accounts');
  await page.getByText('LN-E2E-009').click();
  await shot(page, 'loan-account-sanctioned-summary.png');
  accountStatus = 'active';
  await open(page, 'Loan Accounts');
  await page.getByText('LN-E2E-009').click();
  await expect(page.getByText('Servicing views are not available yet.')).toBeVisible();
  await shot(page, 'loan-account-active-summary.png');

  workspace = row('sent', false, [action('complete_sap_request', 'Confirm SAP customer code')]);
  await open(page, 'SAP & Disbursement');
  await shot(page, 'sap-request-and-confirmation.png');
  workspace = row('completed', false, []);
  await open(page, 'SAP & Disbursement');
  await expect(page.getByText('Credit Manager sign-off is pending.')).toBeVisible();
  await shot(page, 'disbursement-readiness-blockers.png');
  workspace = row('completed', true, [action('initiate_disbursement', 'Initiate payment')]);
  await open(page, 'SAP & Disbursement');
  await shot(page, 'payment-initiation.png');
  workspace = row('completed', true, [action('authorise_disbursement', 'Authorise payment')]);
  await open(page, 'Payment Authorisation');
  await shot(page, 'cfc-authorisation.png');
  workspace = { ...row('completed', true, [action('send_disbursement_advice', 'Send disbursement advice')]), bank_transfer_status: 'successful', advice_status: 'pending' };
  await open(page, 'SAP & Disbursement');
  await shot(page, 'transfer-and-advice-success.png');

  await page.unroute('**/api/v1/loan-accounts/**');
  await page.route('**/api/v1/loan-accounts/**', route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code: 'UNAVAILABLE', message: 'Safe account error.' } }) }));
  await open(page, 'Loan Accounts');
  await expect(page.getByText('Safe account error.')).toBeVisible();
  await shot(page, 'loan-account-safe-error.png');
});

const open = async (page: Page, name: string) => { await page.getByRole('button', { name, exact: true }).click(); };
const shot = async (page: Page, name: string) => { await page.screenshot({ path: path.join(evidence!, name), fullPage: true, animations: 'disabled' }); };
const json = (route: Route, data: unknown, extra?: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...(extra ? { pagination: extra } : {}) }) });
const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const action = (action_code: string, label: string) => ({ action_code, label, enabled: true, disabled_reason: null, required_permission: `finance.${action_code}`, action_url: '/api/v1/e2e-action/', method: 'POST', fields: [] });
const row = (status: string, ready: boolean, available_actions: unknown[]) => ({ workspace_id: 'workspace-009', loan_account_id: 'loan-009', disbursement_id: 'disb-009', loan_application_id: 'app-009', application_reference_number: 'LO-E2E-009', loan_account_number: 'LN-E2E-009', member: { member_id: 'member-009', display_name: 'Epic 009 Borrower' }, sanctioned_amount: '400000.00', disbursement_amount: '400000.00', sap: { request_id: 'sap-009', status, customer_code_masked: status === 'completed' ? '******0009' : null }, readiness: { ready_for_disbursement: ready, evaluated_at: '2026-07-19T05:00:00Z', checks: ready ? [] : [{ code: 'documentation_complete', label: 'Documentation checklist complete', status: 'fail', reason: 'Credit Manager sign-off is pending.' }] }, beneficiary_bank: null, source_bank: null, initiation_status: null, authorisation_status: 'pending', bank_transfer_status: 'pending', advice_status: 'not_started', bank_reference_masked: null, initiated_by: null, initiated_at: null, authorised_at: null, disbursed_at: null, available_actions });
const loan = (loan_account_status: string) => ({ loan_account_id: 'loan-009', loan_account_number: 'LN-E2E-009', loan_application_id: 'app-009', application_reference_number: 'LO-E2E-009', member: { member_id: 'member-009', display_name: 'Epic 009 Borrower' }, sap_customer_code: 'SAP-E2E-009', loan_type: 'short_term', facility_type: 'short_term', interest_rate_type: 'floating', current_interest_rate: '9.2500', sanctioned_amount: '400000.00', disbursed_amount: loan_account_status === 'active' ? '400000.00' : '0.00', principal_outstanding: loan_account_status === 'active' ? '400000.00' : '0.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: loan_account_status === 'active' ? '400000.00' : '0.00', loan_account_status, tenure_start_date: null, tenure_end_date: null, repayment_date: '2027-06-22', tenure_months: 12, created_at: '2026-07-19T05:00:00Z', activated_at: loan_account_status === 'active' ? '2026-07-19T05:00:00Z' : null });
const user = { user_id: 'staff-009', full_name: 'Epic 009 Staff', email: 'staff009@example.test', status: 'active', roles: [{ role_code: 'senior_manager_finance', role_name: 'Senior Manager Finance' }], teams: [], role_codes: ['senior_manager_finance'], team_codes: [], permissions: ['finance.disbursement.initiate', 'finance.disbursement.authorise', 'finance.loan_account.read'], available_actions: [] };
