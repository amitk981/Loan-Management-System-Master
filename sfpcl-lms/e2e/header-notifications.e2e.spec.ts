import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

const staffEmail = 'e2e.credit.finance@sfpcl.example';

test.use({ viewport: { width: 1280, height: 720 } });

test('010O header renders the bounded populated notification summary', async ({ page }) => {
  const observed: string[] = [];
  await page.route('**/api/v1/notifications/**', route => {
    observed.push(route.request().url());
    return paginated(route, [notification], 2);
  });

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByRole('button', { name: 'Notifications, 2 unread' })).toBeVisible();
  await page.getByRole('button', { name: 'Notifications, 2 unread' }).click();
  await expect(page.getByText('Review LA-2026-0001')).toBeVisible();
  await expect(page.getByText('LA-2026-0001 requires credit review.')).toBeVisible();

  const requestUrl = new URL(observed.at(-1)!);
  expect(requestUrl.pathname).toBe('/api/v1/notifications/');
  expect(requestUrl.searchParams.get('read_status')).toBe('unread');
  expect(requestUrl.searchParams.get('page_size')).toBe('4');
  await capture(page, 'header-notifications-populated.png');
});

test('010O header renders the empty notification summary', async ({ page }) => {
  await page.route('**/api/v1/notifications/**', route => paginated(route, [], 0));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByRole('button', { name: 'Notifications, 0 unread' })).toBeVisible();
  await page.getByRole('button', { name: 'Notifications, 0 unread' }).click();
  await expect(page.getByText('You have no unread notifications.')).toBeVisible();
  await capture(page, 'header-notifications-empty.png');
});

test('010O header renders the notification API error state', async ({ page }) => {
  await page.route('**/api/v1/notifications/**', route => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({
      success: false,
      error: { code: 'SERVICE_UNAVAILABLE', message: 'Notification service unavailable.' },
    }),
  }));

  await staffLogin(page, staffEmail, E2E_PASSWORD);
  await expect(page.getByRole('button', { name: 'Notifications, 0 unread' })).toBeVisible();
  await page.getByRole('button', { name: 'Notifications, 0 unread' }).click();
  await expect(page.getByText('Notifications could not be loaded.')).toBeVisible();
  await capture(page, 'header-notifications-error.png');
});

const capture = async (page: Page, fileName: string) => {
  const output = path.join(evidenceDir!, fileName);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
};

const paginated = (route: Route, data: unknown[], totalCount: number) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    pagination: {
      page: 1,
      page_size: 4,
      total_count: totalCount,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
  }),
});

const notification = {
  notification_id: '00000000-0000-4000-8000-000000000010',
  communication_id: null,
  notification_type: 'application',
  category: 'Application',
  severity: 'warning',
  title: 'Review LA-2026-0001',
  message: 'LA-2026-0001 requires credit review.',
  related_entity_type: 'loan_application',
  related_entity_id: '00000000-0000-4000-8000-000000000011',
  action_label: 'Open related record',
  action_url: '/applications/detail',
  sender: { user_id: '00000000-0000-4000-8000-000000000012', full_name: 'System User' },
  recipient: { type: 'role', role_code: 'credit_manager' },
  read: false,
  read_at: null,
  read_by_user_id: null,
  read_state_version: 1,
  created_at: '2026-07-22T08:00:00+05:30',
};
