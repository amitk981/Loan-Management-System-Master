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

const dashboardRequestCounts: number[] = [];

for (const repetition of [1, 2]) {
  test(`012F2 populated dashboard performance smoke repetition ${repetition}`, async ({ page }) => {
    await freezeDashboardClock(page);
    let dashboardRequestCount = 0;
    await page.route('**/api/v1/dashboard/', route => {
      dashboardRequestCount += 1;
      return populatedDashboard(route);
    });

    const startedAt = Date.now();
    await staffLogin(page, staffEmail, E2E_PASSWORD);
    await expect(page.getByText('Credit Manager Dashboard')).toBeVisible();
    await expect(page.getByText('Applications pending completeness')).toBeVisible();
    await expect(page.getByText('DPD buckets')).toBeVisible();
    const elapsedMilliseconds = Date.now() - startedAt;

    expect(dashboardRequestCount).toBeGreaterThan(0);
    if (dashboardRequestCounts.length > 0) {
      expect(dashboardRequestCount).toBe(dashboardRequestCounts[0]);
    }
    dashboardRequestCounts.push(dashboardRequestCount);
    expect(elapsedMilliseconds).toBeLessThan(3_000);
    await capture(
      page,
      repetition === 1
        ? 'performance-readiness-dashboard.png'
        : 'performance-readiness-dashboard-run-2.png',
    );
  });
}

const populatedDashboard = (route: Route) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data: {
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
    },
    meta: { api_version: 'v1', request_id: 'e2e-performance-readiness' },
  }),
});

const capture = async (page: Page, fileName: string) => {
  const output = path.join(evidenceDir!, fileName);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
};
