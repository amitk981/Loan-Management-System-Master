import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });
test.use({ viewport: { width: 390, height: 844 } });
test('member communication surfaces remain own-scoped and usable on mobile', async ({ page }) => {
  const requests: string[] = [];
  await portalLogin(page);
  await installCommunications(page, requests);

  await navigate(page, 'Notices & Letters');
  await expect(page.getByText('Authorised closure certificate')).toBeVisible();
  await expect(page.getByText('FOREIGN-MEMBER-NOTICE')).toHaveCount(0);

  await navigate(page, 'Closure & NOC');
  await expect(page.getByText('LN-PORTAL-CLOSED-001')).toBeVisible();
  await expect(page.getByText('Issued', { exact: true })).toBeVisible();
  await expect(page.getByText('Released', { exact: true })).toBeVisible();

  await navigate(page, 'Notifications');
  await page.getByRole('button', { name: 'NOC available — mark as read' }).click();
  await expect(page.getByText('Read', { exact: true })).toBeVisible();
  expect(requests).toContain('POST /api/v1/portal/notifications/notification-own/mark-read/');

  await navigate(page, 'Raise Grievance');
  await expect(page.getByText('Resolved after account review.')).toBeVisible();
  await page.getByLabel('Category').selectOption('repayment_adjustment_issue');
  await page.getByLabel('Subject').fill('Receipt allocation query');
  await page.getByLabel('Message').fill('Please confirm how my latest receipt was allocated.');
  await page.getByRole('button', { name: 'Submit Grievance' }).click();
  await expect(page.getByText('Grievance submitted')).toBeVisible();
  await expect(page.getByText('Reference GRV-2026-PORTAL002.')).toBeVisible();
  expect(requests).toContain('POST /api/v1/portal/grievances/');

  const body = (await page.locator('body').innerText()).toLowerCase();
  for (const privateValue of ['assigned_to_user_id', 'internal_notes', 'foreign-member']) expect(body).not.toContain(privateValue);
  await page.screenshot({ path: path.join(evidenceRoot, 'member-portal-communications-mobile.png'), fullPage: true, animations: 'disabled' });
});
async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('e2e.portal@sfpcl.example');
  await page.getByLabel('Password').fill('E2eTracer123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}
async function navigate(page: Page, label: string) {
  await page.getByRole('navigation').getByRole('button', { name: label, exact: true }).click();
}
async function installCommunications(page: Page, requests: string[]) {
  await page.route('**/api/v1/portal/notices/**', route => {
    requests.push(requestKey(route));
    return paginated(route, [notice]);
  });
  await page.route('**/api/v1/portal/closures/**', route => {
    requests.push(requestKey(route));
    return paginated(route, [closure]);
  });
  await page.route('**/api/v1/portal/notifications/**', route => {
    requests.push(requestKey(route));
    return route.request().method() === 'POST' ? ok(route, { ...notification, read: true, read_at: '2026-07-23T10:05:00Z', read_state_version: 2 }) : paginated(route, [notification]);
  });
  await page.route('**/api/v1/portal/grievances/**', route => {
    requests.push(requestKey(route));
    return route.request().method() === 'POST' ? ok(route, submittedGrievance) : paginated(route, [resolvedGrievance]);
  });
}
const requestKey = (route: Route) => `${route.request().method()} ${new URL(route.request().url()).pathname}`;
const ok = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, meta: { request_id: 'portal-communications-browser' } }) });
const paginated = (route: Route, data: unknown[]) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, pagination: { page: 1, page_size: 100, total_count: data.length, total_pages: 1, has_next: false, has_previous: false }, meta: { request_id: 'portal-communications-browser' } }) });
const notice = {
  notice_id: 'notice-own', notice_type: 'noc', title: 'Authorised closure certificate',
  message: 'Your NOC is available.', status: 'sent', issued_at: '2026-07-23T09:00:00Z',
  related_entity_type: 'loan_account', related_entity_id: 'loan-own', related_loan_account_id: 'loan-own',
  related_reference: 'LN-PORTAL-CLOSED-001',
  download_url: '/api/v1/portal/notices/00000000-0000-0000-0000-000000000001/download/',
};
const closure = {
  loan_account_id: 'loan-own', loan_account_number: 'LN-PORTAL-CLOSED-001',
  full_repayment_status: 'confirmed', closure_review_status: 'complete', closed_at: '2026-07-22T12:00:00Z',
  noc_status: 'issued', noc_download_url: '/api/v1/portal/notices/00000000-0000-0000-0000-000000000001/download/',
  security_return_status: 'returned', cdsl_unpledge_status: 'released',
  security_items: [{ item_type: 'cdsl', status: 'released', acknowledgement_available: true }],
};
const notification = {
  notification_id: 'notification-own', notification_type: 'noc_issued', title: 'NOC available',
  message: 'Your closure certificate is ready.', severity: 'info', read: false, read_at: null,
  read_state_version: 1, created_at: '2026-07-23T10:00:00Z',
};
const resolvedGrievance = {
  grievance_id: 'grievance-own-1', grievance_reference: 'GRV-2026-PORTAL001', grievance_category: 'repayment_adjustment_issue',
  subject: 'Earlier receipt query', description: 'Please verify my receipt.', loan_account_id: 'loan-own',
  loan_application_id: null, received_date: '2026-07-20', resolution_due_date: '2026-07-25',
  status: 'resolved', is_overdue: false, resolution_summary: 'Resolved after account review.',
  closed_at: '2026-07-21T12:00:00Z', borrower_informed: true, borrower_acknowledged: false,
};
const submittedGrievance = {
  ...resolvedGrievance, grievance_id: 'grievance-own-2', grievance_reference: 'GRV-2026-PORTAL002',
  subject: 'Receipt allocation query', received_date: '2026-07-23', resolution_due_date: '2026-07-28',
  description: 'Please confirm how my latest receipt was allocated.',
  status: 'open', resolution_summary: null, closed_at: null, borrower_informed: false,
};
