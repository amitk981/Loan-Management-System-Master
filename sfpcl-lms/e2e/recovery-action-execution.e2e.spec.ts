import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for recovery acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

const email = 'e2e.credit.manager@sfpcl.example';

test('S57 stays unavailable until 011PB wires its server-owned action contract', async ({ page }) => {
  const mutationRequests: string[] = [];
  await page.route('**/api/v1/default-cases/**', route => {
    const pathname = new URL(route.request().url()).pathname;
    return pathname === '/api/v1/default-cases/'
      ? listJson(route, [row])
      : json(route, row);
  });

  await staffLogin(page, email, E2E_PASSWORD);
  page.on('request', request => {
    const pathname = new URL(request.url()).pathname;
    if (pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutationRequests.push(`${request.method()} ${pathname}`);
    }
  });
  await openRecovery(page);
  await expect(page.getByText('Browser Recovery Borrower').first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Recovery Approval' })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Security Invocation' })).toBeDisabled();
  await expect(page.getByText(/remain unavailable until the server-owned S56\/S57 action contract/i)).toBeVisible();
  expect(mutationRequests).toEqual([]);
  await capture(page, 'recovery-action-blocked.png');
});

async function openRecovery(page: Page) {
  await page.getByRole('button', { name: 'Default & Recovery' }).click();
}

const json = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data }),
});

const listJson = (route: Route, data: unknown[]) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    pagination: {
      page: 1,
      page_size: 100,
      total_count: data.length,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
  }),
});

const capture = (page: Page, name: string) => page.screenshot({
  path: path.join(evidenceDir, name),
  fullPage: true,
  animations: 'disabled',
});

const row = {
  default_case_id: 'case-1',
  loan_account_id: 'loan-1',
  loan_account_number: 'LN-REC-001',
  member_id: 'member-1',
  borrower_name: 'Browser Recovery Borrower',
  principal_outstanding: '300000.00',
  interest_outstanding: '45000.00',
  total_outstanding: '345000.00',
  trigger_event: 'missed_principal_repayment',
  scheduled_due_date: '2025-04-15',
  repayment_schedule_id: 'schedule-1',
  default_case_status: 'recovery_approved',
  grace_period_start_date: '2025-04-15',
  grace_period_end_date: '2025-07-15',
  grace_state: 'expired',
  reason: 'Approved server decision remains read-only in 011PA.',
  current_assessment: null,
  extension_note: null,
  non_payment_note: null,
  recovery_decision: {
    recovery_decision_id: 'decision-1',
    decision: 'invoke_sh4',
    status: 'approved',
    available_actions: [{ action_code: 'execute_recovery' }],
  },
  recovery_action: null,
  available_actions: [],
};
