import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 1280, height: 720 } });

test('MP15 shows the selected borrower account without internal evidence', async ({ page }) => {
  await portalLogin(page);
  await installProjection(page, 'populated');
  await openMyLoans(page);
  await expect(page.getByText('LN-PORTAL-001', { exact: true })).toBeVisible();
  await expect(page.getByText('₹3,00,000', { exact: true })).toBeVisible();
  await assertSafe(page);
  await shot(page, 'member-portal-repayments-populated.png');
});

test('MP15 preserves the real empty state', async ({ page }) => {
  await portalLogin(page);
  await installProjection(page, 'empty');
  await openMyLoans(page);
  await expect(page.getByText('No active loan accounts.', { exact: true })).toBeVisible();
  await shot(page, 'member-portal-repayments-empty.png');
});

test('MP15 renders a safe backend error', async ({ page }) => {
  await portalLogin(page);
  await installProjection(page, 'error');
  await openMyLoans(page);
  await expect(page.getByText('Loan information could not be loaded. Please try again.', { exact: true })).toBeVisible();
  await expect(page.getByText('provider account failed', { exact: true })).toHaveCount(0);
  await shot(page, 'member-portal-repayments-error.png');
});

test('MP17 and MP18 remain readable and read-only at a narrow viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await portalLogin(page);
  await installProjection(page, 'populated');
  await openMyLoans(page);
  await page.getByRole('button', { name: 'View Repayments', exact: true }).click();
  await expect(page.getByText('SAFE-REFERENCE-23', { exact: true })).toBeVisible();
  await expect(page.getByText('Under verification', { exact: true })).toHaveCount(0);
  await shot(page, 'member-portal-repayments-mobile.png');
  await page.getByRole('navigation').getByRole('button', { name: 'Direct Repayment', exact: true }).click();
  await expect(page.getByText('********4321', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: /submit/i })).toHaveCount(0);
  await assertSafe(page);
});

async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('e2e.portal@sfpcl.example');
  await page.getByLabel('Password').fill('E2eTracer123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}

async function openMyLoans(page: Page) {
  await page.getByRole('navigation').getByRole('button', { name: 'My Loans', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'My Loans', level: 2 })).toBeVisible();
}

async function installProjection(page: Page, state: 'populated' | 'empty' | 'error') {
  await page.route('**/api/v1/portal/loan-accounts/**', async route => {
    const url = new URL(route.request().url());
    expect(route.request().method()).toBe('GET');
    expect(route.request().headers().authorization).toMatch(/^Bearer /);
    if (url.pathname === '/api/v1/portal/loan-accounts/') {
      if (state === 'error') return error(route);
      return ok(route, state === 'empty' ? [] : [loan]);
    }
    if (url.pathname.endsWith('/schedule/')) return ok(route, [schedule]);
    if (url.pathname.endsWith('/repayments/')) return ok(route, repayments);
    if (url.pathname.endsWith('/invoices/')) return ok(route, []);
    if (url.pathname.endsWith('/direct-instructions/')) return ok(route, instructions);
    return ok(route, detail);
  });
}

const ok = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, meta: { request_id: 'portal-repayment-browser' } }) });
const error = (route: Route) => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code: 'SERVICE_UNAVAILABLE', message: 'provider account failed', field_errors: {} }, meta: { request_id: 'portal-repayment-error' } }) });
const shot = (page: Page, name: string) => page.screenshot({ path: path.join(evidenceRoot!, name), fullPage: true, animations: 'disabled' });
async function assertSafe(page: Page) { const body = (await page.locator('body').innerText()).toLowerCase(); for (const value of ['captured_by', 'sap note', 'provider data', '123456789012']) expect(body).not.toContain(value); }

const loan = { loan_account_id: 'loan-1', loan_account_number: 'LN-PORTAL-001', application_id: 'app-1', application_reference: 'APP-001', status: 'active', closure_status: 'active', disbursed_amount: '400000.00', principal_outstanding: '300000.00', next_due_date: '2026-12-31', next_due_amount: '100000.00' };
const detail = { ...loan, interest_outstanding: '5000.00', charges_outstanding: '0.00', total_outstanding: '305000.00', repayment_route: 'direct', closed_at: null };
const schedule = { schedule_id: 'schedule-1', installment_number: 1, due_date: '2026-12-31', principal_due: '100000.00', interest_due: '5000.00', charges_due: '0.00', total_due: '105000.00', paid_principal: '0.00', paid_interest: '0.00', paid_amount: '0.00', status: 'pending' };
const repayments = Array.from({ length: 24 }, (_, index) => ({ repayment_id: `repayment-${index}`, receipt_date: '2026-10-01', amount_received: '100000.00', allocated_to_principal: '95000.00', allocated_to_interest: '5000.00', payment_mode: 'neft', repayment_source: 'direct_farmer', reference: `SAFE-REFERENCE-${index}`, acknowledgement: null, status: 'confirmed' }));
const instructions = { available: true, beneficiary_name: 'SFPCL Collections', bank_name: 'Approved Bank', account_number_masked: '********4321', ifsc: 'APPR0001234', required_narration: 'LN-PORTAL-001', amount_due: '305000.00', proof_submission_enabled: false, disclaimer: 'Repayment will be updated in the portal after SFPCL verifies the bank receipt and posts the repayment in its records.' };
