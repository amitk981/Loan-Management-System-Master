import fs from 'fs';
import path from 'path';
import { expect, test, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for the 012DAA report acceptance contract');
}
fs.mkdirSync(evidenceDir, { recursive: true });

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => localStorage.setItem(
    'sfpcl_staff_auth_session',
    JSON.stringify({ accessToken: 'report-browser-access', refreshToken: 'report-browser-refresh' }),
  ));
  await page.route('**/api/v1/auth/me/', route => ok(route, reportReader));
  await page.route('**/api/v1/dashboard/', route => ok(route, {
    role_context: 'cfo',
    cards: [],
    tasks: [],
  }));
  await page.route('**/api/v1/reports/loan-portfolio/**', route => {
    const url = new URL(route.request().url());
    const requestedPage = Number(url.searchParams.get('page') ?? '1');
    const rows = requestedPage === 2 ? [portfolioRow(21)] : Array.from(
      { length: 20 },
      (_value, index) => portfolioRow(index + 1),
    );
    return listOk(route, rows, {
      page: requestedPage,
      page_size: 20,
      total_count: 21,
      total_pages: 2,
      has_next: requestedPage === 1,
      has_previous: requestedPage === 2,
    });
  });
});

test('S69 report results retain backend filters, ordering, pagination, and reconciliation', async ({ page }) => {
  const reportRequests: URL[] = [];
  const mutations: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/reports/loan-portfolio/') reportRequests.push(url);
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Reports & MIS' }).click();
  await expect(page.getByRole('heading', { name: 'Reports & MIS Center' })).toBeVisible();
  await expect(page.getByText('LN-BROWSER-REPORT-001')).toBeVisible();
  await expect(page.getByText('21 records')).toBeVisible();

  await page.getByLabel('As of date').fill('2026-06-30');
  await page.getByLabel('Account status').fill('active');
  await page.getByRole('button', { name: 'Apply filters' }).click();
  await expect.poll(() => reportRequests.at(-1)?.search).toContain(
    'status=active&as_of_date=2026-06-30',
  );

  await page.getByRole('button', { name: 'Sort by Total outstanding' }).click();
  await expect.poll(() => reportRequests.at(-1)?.searchParams.get('ordering'))
    .toBe('total_outstanding');
  await expect.poll(() => reportRequests.at(-1)?.searchParams.get('status')).toBe('active');

  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByText('LN-BROWSER-REPORT-021')).toBeVisible();
  await expect(page.getByText('Page 2 of 2')).toBeVisible();
  expect(reportRequests.at(-1)?.searchParams.get('page')).toBe('2');
  expect(reportRequests.at(-1)?.searchParams.get('as_of_date')).toBe('2026-06-30');
  expect(reportRequests.at(-1)?.searchParams.get('status')).toBe('active');
  expect(reportRequests.at(-1)?.searchParams.get('ordering')).toBe('total_outstanding');
  expect(mutations).toEqual([]);

  await page.screenshot({
    path: path.join(evidenceDir, 'report-results.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

const reportReader = {
  user_id: 'report-reader-browser-012daa',
  full_name: 'Browser CFO Report Reader',
  email: 'report-reader-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'cfo', role_name: 'CFO' }],
  teams: [{ team_code: 'finance', team_name: 'Finance' }],
  role_codes: ['cfo'],
  team_codes: ['finance'],
  permissions: [
    'reports.application_pipeline.read',
    'reports.portfolio.read',
    'reports.dpd.read',
    'reports.compliance.read',
    'reports.export',
    'documents.checklist.read',
    'finance.disbursement.readiness',
    'finance.loan_account.read',
    'monitoring.dpd.read',
    'compliance.section186.read',
    'compliance.nbfc_test.read',
  ],
  available_actions: [],
};

const portfolioRow = (index: number) => ({
  loan_account_id: `loan-browser-report-${index}`,
  loan_account_number: `LN-BROWSER-REPORT-${String(index).padStart(3, '0')}`,
  loan_application_id: `application-browser-report-${index}`,
  member_id: `member-browser-report-${index}`,
  borrower_name: index === 21 ? 'Seeded Browser Reconciled Member' : `Scoped Report Member ${index}`,
  loan_account_status: 'active',
  sanctioned_amount: '150000.00',
  disbursed_amount: '150000.00',
  principal_outstanding: index === 21 ? '125000.00' : '100000.00',
  interest_outstanding: index === 21 ? '5000.00' : '2500.00',
  charges_outstanding: '0.00',
  total_outstanding: index === 21 ? '130000.00' : '102500.00',
  loan_type: 'short_term',
  tenure_start_date: '2026-04-01',
  tenure_end_date: '2027-03-31',
  repayment_date: '2026-09-30',
  current_interest_rate: '10.0000',
  created_at: `2026-04-${String(Math.min(index, 28)).padStart(2, '0')}T10:00:00Z`,
});

const ok = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    meta: { request_id: 'report-browser-contract' },
  }),
});

const listOk = (
  route: Route,
  data: unknown[],
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  },
) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    pagination,
    meta: { request_id: 'report-browser-list-contract' },
  }),
});
