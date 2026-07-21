import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

const managerEmail = 'e2e.credit.manager@sfpcl.example';
test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

test('S43 and S46 render canonical schedule and ledger projections', async ({ page }) => {
  await staffLogin(page, managerEmail, E2E_PASSWORD);
  await installServicingProjection(page);
  await page.getByRole('button', { name: 'Loan Accounts', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Loan Accounts', exact: true })).toBeVisible();
  await page.getByText(account.loan_account_number, { exact: true }).click();
  await page.getByRole('button', { name: 'Loan Ledger', exact: true }).click();
  await expect(page.getByText('UTR-SERVICING-001', { exact: true })).toBeVisible();
  await expect(page.getByText('₹3,00,000.00', { exact: true }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Repayment Schedule', exact: true }).click();
  await expect(page.getByText('₹4,10,000.00', { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'servicing-ledger.png'), fullPage: true, animations: 'disabled' });
});

test('S44 posts one direct receipt and displays the backend allocation', async ({ page }) => {
  await staffLogin(page, managerEmail, E2E_PASSWORD);
  const observed: Array<{ path: string; key?: string }> = [];
  await installServicingProjection(page, observed);
  await page.getByRole('button', { name: 'Repayments', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Repayments Hub', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Record Receipt', exact: true }).click();
  await page.getByLabel('Payment Date').fill('2026-12-04');
  await page.getByLabel('Amount Received (₹)').fill('100000.00');
  await page.getByLabel('Bank Reference / UTR').fill('UTR-SERVICING-NEW');
  await page.getByLabel('SAP Entry Reference').fill('SAP-SERVICING-NEW');
  await page.getByRole('button', { name: 'Post and Allocate', exact: true }).click();

  await expect(page.getByText('Receipt Posted and Allocated', { exact: true })).toBeVisible();
  await expect(page.getByText('₹1,00,000.00 allocated to principal', { exact: true })).toBeVisible();
  expect(observed).toHaveLength(1);
  expect(observed[0]).toMatchObject({ path: `/api/v1/loan-accounts/${account.loan_account_id}/direct-repayment-command/` });
  expect(observed[0].key).toBeTruthy();
  await page.screenshot({ path: path.join(evidenceDir, 'direct-repayment-posting.png'), fullPage: true, animations: 'disabled' });
});

test('S47-S49 render canonical interest values', async ({ page }) => {
  await staffLogin(page, managerEmail, E2E_PASSWORD);
  await installServicingProjection(page);
  await page.route('**/api/v1/interest-invoices/**', route => ok(route, [invoice], pagination));
  await page.getByRole('button', { name: 'Interest Management', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Interest Management', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Yearly Invoices', exact: true }).click();
  await expect(page.getByText('INV-SERVICING-001', { exact: true })).toBeVisible();
  await expect(page.getByText('₹27,750.00', { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'interest-management.png'), fullPage: true, animations: 'disabled' });
});

test('S50-S52 render canonical DPD and retained reminder evidence', async ({ page }) => {
  await staffLogin(page, managerEmail, E2E_PASSWORD);
  await page.route('**/api/v1/dpd-statuses/', route => ok(route, dpdPortfolio));
  await page.route('**/api/v1/reminders/**', route => ok(route, [reminder], pagination));
  await page.getByRole('button', { name: /Monitoring/ }).click();
  await expect(page.getByRole('heading', { name: 'Monitoring Dashboard', exact: true })).toBeVisible();
  await expect(page.getByText('LN-SERVICING-001', { exact: true }).first()).toBeVisible();
  await page.getByRole('button', { name: /View All/ }).click();
  await expect(page.getByText('Sent', { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'monitoring-dashboard.png'), fullPage: true, animations: 'disabled' });
});

async function installServicingProjection(page: Page, observed: Array<{ path: string; key?: string }> = []) {
  await page.route('**/api/v1/loan-accounts/**', route => loanRoute(route, observed));
  await page.route('**/api/v1/bank-statement-lines/**', route => ok(route, []));
}

async function loanRoute(route: Route, observed: Array<{ path: string; key?: string }>) {
  const request = route.request();
  const url = new URL(request.url());
  expect(request.headers().authorization).toMatch(/^Bearer /);
  if (request.method() === 'POST' && url.pathname.endsWith('/direct-repayment-command/')) {
    observed.push({ path: url.pathname, key: request.headers()['idempotency-key'] });
    return ok(route, { replayed: false, capture, allocation });
  }
  if (url.pathname === '/api/v1/loan-accounts/') return ok(route, [account], pagination);
  if (url.pathname.endsWith('/repayment-schedule/')) return ok(route, [schedule], pagination);
  if (url.pathname.endsWith('/ledger/')) return ok(route, [ledger], pagination);
  if (url.pathname.endsWith('/repayments/')) return ok(route, [subsidiary], pagination);
  return ok(route, account);
}

const ok = (route: Route, data: unknown, pageData?: typeof pagination) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, ...(pageData ? { pagination: pageData } : {}), meta: { request_id: 'servicing-browser' } }),
});

const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const account = { loan_account_id: '00000000-0000-4000-8000-000000010001', loan_account_number: 'LN-SERVICING-001', loan_application_id: 'application-1', application_reference_number: 'LO-SERVICING-001', member: { member_id: 'member-1', display_name: 'Servicing Browser Member' }, sap_customer_code: '******001', loan_type: 'short_term', facility_type: 'short_term', interest_rate_type: 'floating', current_interest_rate: '9.2500', sanctioned_amount: '400000.00', disbursed_amount: '400000.00', principal_outstanding: '300000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '300000.00', loan_account_status: 'active', tenure_start_date: '2026-06-22', tenure_end_date: null, repayment_date: '2027-06-22', tenure_months: 12, created_at: '2026-06-20T10:00:00Z', activated_at: '2026-06-22T14:00:00Z' };
const schedule = { repayment_schedule_id: 'schedule-1', installment_number: 1, due_date: '2027-06-22', principal_due: '400000.00', interest_due: '10000.00', charges_due: '0.00', total_due: '410000.00', paid_principal: '0.00', paid_interest: '0.00', paid_charges: '0.00', amount_received: '0.00', schedule_status: 'pending', extended_due_date: null, created_at: '2026-06-22T00:00:00Z' };
const ledger = { transaction_date: '2026-12-04', transaction_type: 'repayment', owner_reference: { entity_type: 'repayment_allocation', entity_id: 'allocation-1' }, reference: 'UTR-SERVICING-001', debit: '0.00', credit: '100000.00', principal_balance: '300000.00', interest_balance: '0.00', total_outstanding: '300000.00', actor: { user_id: 'user-1', display_name: 'Accounts User' }, sap_status: 'posted', remarks: 'Repayment allocated principal first.' };
const subsidiary = { repayment_id: 'repayment-sub-1', loan_account_id: account.loan_account_id, repayment_source: 'subsidiary_deduction', amount_received: '75000.00', received_date: '2026-12-15', payment_method: 'subsidiary_transfer', bank_reference_number: 'SUB-001', bank_statement_line_id: null, statement_match_status: 'not_linked', allocation_status: 'pending', sap_posting_status: 'pending', sap_posting_due_date: '2026-12-16', sap_entry_reference: null, sap_posted_at: null, allocation: null, subsidiary_reconciliation: { subsidiary_company_id: 'company-1', produce_payment_reference: 'PRODUCE-PAY-001', transfer_reference: 'SUB-001', tri_party_agreement_id: 'agreement-1', reconciliation_status: 'pending_statement', treasury_verification_status: 'pending' } };
const capture = { repayment_id: 'repayment-new', loan_account_id: account.loan_account_id, repayment_source: 'direct_farmer', amount_received: '100000.00', received_date: '2026-12-04', payment_method: 'rtgs', bank_reference_number: 'UTR-SERVICING-NEW', bank_statement_line_id: null, statement_match_status: 'not_linked', allocation_status: 'pending', sap_posting: { status: 'pending', due_date: '2026-12-07', sap_entry_reference: null, posted_at: null } };
const allocation = { repayment_allocation_id: 'allocation-new', repayment_id: 'repayment-new', allocation_rule: 'principal_first', allocation_rule_version: 'v1', allocation_status: 'allocated', allocated_to_principal: '100000.00', allocated_to_interest: '0.00', allocated_to_charges: '0.00', unallocated_amount: '0.00', exception_reason: null, loan_account: { principal_outstanding: '200000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '200000.00' } };
const invoice = { interest_invoice_id: 'invoice-1', loan_account_id: account.loan_account_id, member_id: 'member-1', financial_year: 'FY2026-27', invoice_number: 'INV-SERVICING-001', invoice_date: '2027-03-31', interest_period_start: '2026-04-01', interest_period_end: '2027-03-31', principal_base_amount: '300000.00', interest_rate: '9.2500', gross_interest_amount: '27750.00', interest_paid_amount: '0.00', tax_amount: '0.00', fixed_fee_amount: '0.00', interest_amount: '27750.00', invoice_status: 'issued', rate_version_number: 3, calculation_version: 'INT-1', document_id: 'document-1', communication_id: 'communication-1', delivery_status: 'sent', generated_by_user_id: 'user-1', generated_at: '2027-04-01T10:00:00Z', issued_by_user_id: 'user-1', issued_at: '2027-04-01T11:00:00Z' };
const dpdPortfolio = { sop_bucket_counts: { current: 0, one_to_two_years: 1, two_to_three_years: 0, more_than_three_years: 0 }, total_count: 1, rows: [{ dpd_status_id: 'dpd-1', loan_account_id: account.loan_account_id, loan_account_number: account.loan_account_number, member_display_name: account.member.display_name, loan_account_status: 'overdue', principal_outstanding: '300000.00', interest_outstanding: '27750.00', repayment_date: '2027-03-31', as_of_date: '2026-06-30', days_past_due: 367, sop_bucket: 'one_to_two_years', standard_bucket: 'over_90', principal_overdue_amount: '1000.00', interest_overdue_amount: '100.00', total_overdue_amount: '1100.00' }] };
const reminder = { reminder_id: 'reminder-1', loan_account_id: account.loan_account_id, member_id: 'member-1', quarter_end_date: '2026-06-30', eligibility_decision: { eligible: true, reason: 'outstanding_beyond_one_year' }, reminder_type: 'outstanding_beyond_one_year', origin: 'automatic', channel: 'sms', delivery_status: 'sent', status_reason: null, next_follow_up_date: '2026-07-07', call_outcome: null, created_by: { user_id: 'user-1', display_name: 'Credit Manager' }, created_at: '2026-06-30T10:00:00Z' };
