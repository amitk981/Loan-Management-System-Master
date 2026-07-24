import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import {
  E2E_PASSWORD,
  freezeDashboardClock,
  staffLogin,
} from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
}
fs.mkdirSync(evidenceDir, { recursive: true });

const staffEmail = 'e2e.credit.finance@sfpcl.example';

test.use({ viewport: { width: 1280, height: 720 } });

test('012E renders populated operational dashboard data', async ({ page }) => {
  await freezeDashboardClock(page);
  await page.route('**/api/v1/dashboard/', route => dashboard(route, {
    role_context: 'credit_manager',
    cards: [
      {
        code: 'applications_pending_completeness',
        label: 'Applications pending completeness',
        count: 7,
        link: '/applications?status=submitted&current_stage=initial_loan_request',
      },
      {
        code: 'appraisals_due_today',
        label: 'Appraisals due today',
        count: 2,
        link: '/credit/appraisals?due=today',
      },
      {
        code: 'dpd_buckets',
        label: 'DPD buckets',
        count: 3,
        link: '/monitoring/dpd',
      },
    ],
    tasks: [],
  }));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByText('Applications pending completeness')).toBeVisible();
  await expect(page.getByText('Credit Manager Dashboard')).toBeVisible();
  await expect(page.getByText('No pending tasks for your role.')).toBeVisible();
  await capture(page, 'operational-dashboard-populated.png');
});

test('012E renders the empty operational dashboard state', async ({ page }) => {
  await freezeDashboardClock(page);
  await page.route('**/api/v1/dashboard/', route => dashboard(route, {
    role_context: 'credit_manager',
    cards: [],
    tasks: [],
  }));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByText('No dashboard summary cards available')).toBeVisible();
  await capture(page, 'operational-dashboard-empty.png');
});

test('012E renders the operational dashboard error state', async ({ page }) => {
  await freezeDashboardClock(page);
  await page.route('**/api/v1/dashboard/', route => dashboardError(
    route,
    503,
    'SERVICE_UNAVAILABLE',
    'Dashboard service unavailable.',
  ));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByText('Dashboard could not be loaded', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Refresh dashboard' })).toBeVisible();
  await capture(page, 'operational-dashboard-error.png');
});

test('012E renders the forbidden operational dashboard state', async ({ page }) => {
  await freezeDashboardClock(page);
  await page.route('**/api/v1/dashboard/', route => dashboardError(
    route,
    403,
    'PERMISSION_DENIED',
    'You do not have permission to read dashboard summaries.',
  ));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByText('Dashboard unavailable')).toBeVisible();
  await expect(page.getByText('You do not have permission to read dashboard summaries.')).toBeVisible();
  await capture(page, 'operational-dashboard-forbidden.png');
});

const dashboard = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    meta: { api_version: 'v1', request_id: 'e2e-dashboard' },
  }),
});

const dashboardError = (
  route: Route,
  status: number,
  code: string,
  message: string,
) => route.fulfill({
  status,
  contentType: 'application/json',
  body: JSON.stringify({
    success: false,
    error: { code, message },
    meta: { api_version: 'v1', request_id: 'e2e-dashboard' },
  }),
});

const capture = async (page: Page, fileName: string) => {
  const output = path.join(evidenceDir!, fileName);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
};
