import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
}
fs.mkdirSync(evidenceDir, { recursive: true });

const staffEmail = 'e2e.credit.finance@sfpcl.example';

test.use({ viewport: { width: 1440, height: 900 } });

test('012EB renders the populated S03 Task Inbox', async ({ page }) => {
  await page.route('**/api/v1/tasks/?**', route => taskList(route, [appraisalTask, overdueTask]));
  await openTaskInbox(page);

  await expect(page.getByText('Seeded Appraisal Borrower')).toBeVisible();
  await expect(page.getByText('2 pending tasks')).toBeVisible();
  await expect(page.getByText('SLA / TAT').first()).toBeVisible();
  await capture(page, 'task-inbox-populated.png');
});

test('012EB sends the due-today filter to the task API', async ({ page }) => {
  await page.route('**/api/v1/tasks/?**', route => {
    const dueToday = new URL(route.request().url()).searchParams.get('due_today') === 'true';
    return taskList(route, dueToday ? [appraisalTask] : [appraisalTask, overdueTask]);
  });
  await openTaskInbox(page);

  await page.getByRole('button', { name: 'Advanced Filters' }).click();
  await page.getByLabel('Time').selectOption('due_today');
  await expect(page.getByText('1 pending task')).toBeVisible();
  await expect(page.getByText('Seeded Appraisal Borrower')).toBeVisible();
  await expect(page.getByText('Seeded Overdue Borrower')).not.toBeVisible();
  await capture(page, 'task-inbox-filtered.png');
});

test('012EB completes a permitted task comment', async ({ page }) => {
  await page.route('**/api/v1/tasks/?**', route => taskList(route, [appraisalTask]));
  await page.route(`**/api/v1/tasks/${appraisalTask.task_id}/comments/`, route => taskAction(route, appraisalTask));
  await openTaskInbox(page);

  await page.getByRole('button', { name: `Actions for ${appraisalTask.task_reference}` }).click();
  await page.getByRole('button', { name: 'Add Comment' }).click();
  await page.getByLabel('Comment').fill('Browser acceptance follow-up');
  await page.getByRole('button', { name: 'Add Comment' }).click();
  await expect(page.getByText('Task updated')).toBeVisible();
  await expect(page.getByText(`Add Comment completed for ${appraisalTask.task_reference}.`)).toBeVisible();
  await capture(page, 'task-inbox-action.png');
});

test('012EB renders a task-scope denial without prototype fallback', async ({ page }) => {
  await page.route('**/api/v1/tasks/?**', route => route.fulfill({
    status: 403,
    contentType: 'application/json',
    body: JSON.stringify({
      success: false,
      error: {
        code: 'FORBIDDEN',
        message: 'You are not authorised to view staff tasks.',
      },
      meta: { api_version: 'v1', request_id: 'e2e-task-denied' },
    }),
  }));
  await openTaskInbox(page);

  await expect(page.getByText('Task Inbox unavailable')).toBeVisible();
  await expect(page.getByText('You are not authorised to view staff tasks.')).toBeVisible();
  await expect(page.getByText('Seeded Appraisal Borrower')).not.toBeVisible();
  await capture(page, 'task-inbox-unauthorised.png');
});

const openTaskInbox = async (page: Page) => {
  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await page.getByRole('button', { name: 'Task Inbox', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Task Inbox' })).toBeVisible();
};

const taskList = (route: Route, rows: unknown[]) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data: rows,
    pagination: {
      page: 1,
      page_size: 20,
      total_count: rows.length,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
    meta: { api_version: 'v1', request_id: 'e2e-task-list' },
  }),
});

const taskAction = (route: Route, row: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data: row,
    meta: { api_version: 'v1', request_id: 'e2e-task-action' },
  }),
});

const capture = async (page: Page, fileName: string) => {
  const output = path.join(evidenceDir!, fileName);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
};

const appraisalTask = {
  task_id: '11111111-1111-4111-8111-111111111111',
  task_reference: 'TSK-E2E-APPRAISAL',
  task_type: 'appraisal',
  title: 'Prepare appraisal',
  application_or_loan_id: '22222222-2222-4222-8222-222222222222',
  linked_entity_type: 'loan_application',
  borrower: 'Seeded Appraisal Borrower',
  borrower_type: 'individual_farmer',
  amount: '250000.00',
  priority: 'high',
  sla_tat: { due_at: '2026-07-25T10:00:00Z', overdue_days: 0 },
  current_status: 'draft',
  assigned_to: {
    role_code: 'credit_manager',
    team_code: 'credit_assessment',
    user: null,
  },
  blocked: false,
  blocked_reason: null,
  special_case: false,
  exception_required: false,
  created_date: '2026-07-24T10:00:00Z',
  due_date: '2026-07-25T10:00:00Z',
  closed_at: null,
  action: { code: 'open', url: '/tasks/11111111-1111-4111-8111-111111111111' },
};

const overdueTask = {
  ...appraisalTask,
  task_id: '33333333-3333-4333-8333-333333333333',
  task_reference: 'TSK-E2E-OVERDUE',
  task_type: 'default_review',
  title: 'Review default case',
  application_or_loan_id: '44444444-4444-4444-8444-444444444444',
  linked_entity_type: 'loan_account',
  borrower: 'Seeded Overdue Borrower',
  amount: '500000.00',
  priority: 'critical',
  sla_tat: { due_at: '2026-07-20T10:00:00Z', overdue_days: 4 },
  current_status: 'grace_period_expired',
  due_date: '2026-07-20T10:00:00Z',
};
