import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';
import { E2E_PASSWORD, staffLogin } from './helpers';
const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for recovery acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });
const email = 'e2e.credit.manager@sfpcl.example';
const pagination = { page: 1, page_size: 100, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const row = { default_case_id: 'case-1', loan_account_id: 'loan-1', loan_account_number: 'LN-REC-001', borrower_name: 'Browser Recovery Borrower', total_outstanding: '345000.00', default_case_status: 'recovery_approved', recovery_decision: { recovery_decision_id: 'decision-1', decision: 'invoke_sh4', status: 'approved', available_actions: [{ action_code: 'execute_recovery' }] }, recovery_action: null };
const companySecretary = { user_id: 'cs-1', full_name: 'Browser Company Secretary', email: 'cs@example.test', status: 'active', roles: [{ role_code: 'company_secretary', role_name: 'Company Secretary' }], teams: [], role_codes: ['company_secretary'], team_codes: [], permissions: ['recovery.action.initiate', 'recovery.action.complete'], available_actions: [] };
test('S57 blocks execution when no approved action is exposed', async ({ page }) => {
  await page.route('**/api/v1/default-cases/**', route => json(route, [], { ...pagination, total_count: 0, total_pages: 1 }));
  await staffLogin(page, email, E2E_PASSWORD);
  await openRecovery(page);
  await expect(page.getByText('Security Invocation Locked')).toBeVisible();
  await capture(page, 'recovery-action-blocked.png');
});
test('S57 renders the exact approved route and evidence controls', async ({ page }) => {
  await page.route('**/api/v1/auth/me/', route => json(route, companySecretary));
  await page.route('**/api/v1/default-cases/**', route => json(route, [row], pagination));
  await staffLogin(page, email, E2E_PASSWORD);
  await openRecovery(page);
  await expect(page.getByText(/Browser Recovery Borrower/)).toBeVisible();
  await expect(page.getByText('invoke sh4')).toBeVisible();
  await expect(page.getByLabel('Recovery evidence')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Initiate Approved Recovery' })).toBeDisabled();
  await capture(page, 'recovery-action-approved.png');
});
async function openRecovery(page: Page) {
  await page.getByRole('button', { name: 'Default & Recovery' }).click();
  await page.getByRole('button', { name: 'Security Invocation' }).click();
}
const json = (route: Route, data: unknown, extra?: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...(extra ? { pagination: extra } : {}) }) });
const capture = (page: Page, name: string) => page.screenshot({ path: path.join(evidenceDir, name), fullPage: true, animations: 'disabled' });
