import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 1280, height: 720 } });

test('MP14 preserves the borrower composition for current SAP-complete processing', async ({ page }) => {
  const statusUrl = await loginSelectApprovedAndRoute(page);
  await page.route(statusUrl, route => portalProjection(route, processingProjection));

  await page.getByRole('navigation').getByRole('button', { name: 'Disbursement', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'Disbursement Status', level: 2 })).toBeVisible();
  await expect(page.getByText('Finance setup in progress.', { exact: true })).toBeVisible();
  await expect(page.getByText('Documents completed.', { exact: true })).toBeVisible();
  await expect(page.getByText('Finance setup complete.', { exact: true })).toBeVisible();
  await expect(page.getByText('Payment processing started.', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Advice unavailable' })).toBeDisabled();
  await assertNoInternalEvidence(page);
  await page.screenshot({ path: path.join(evidenceRoot, 'mp14-processing.png'), fullPage: true });
});

test('MP14 preserves masked transfer facts and accepted-advice availability', async ({ page }) => {
  const statusUrl = await loginSelectApprovedAndRoute(page);
  await page.route(statusUrl, route => portalProjection(route, disbursedProjection));

  await page.getByRole('navigation').getByRole('button', { name: 'Disbursement', exact: true }).click();

  await expect(page.getByText('Loan amount transferred.', { exact: true }).first()).toBeVisible();
  await expect(page.getByText('••••4321', { exact: true })).toBeVisible();
  await expect(page.getByText('••••9876', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download Advice' })).toBeEnabled();
  await assertNoInternalEvidence(page);
  await page.screenshot({ path: path.join(evidenceRoot, 'mp14-disbursed-advice.png'), fullPage: true });
});

test('MP14 renders a safe unavailable state for an exact status failure', async ({ page }) => {
  const statusUrl = await loginSelectApprovedAndRoute(page);
  await page.route(statusUrl, route => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({
      success: false,
      data: null,
      error: { code: 'SERVICE_UNAVAILABLE', message: 'Unavailable.', field_errors: {} },
      meta: { request_id: 'mp14-safe-error' },
    }),
  }));

  await page.getByRole('navigation').getByRole('button', { name: 'Disbursement', exact: true }).click();

  await expect(page.getByText('Disbursement status could not be loaded. Please try again.', { exact: true })).toBeVisible();
  await expect(page.getByText('Unavailable.', { exact: true })).toHaveCount(0);
  await assertNoInternalEvidence(page);
  await page.screenshot({ path: path.join(evidenceRoot, 'mp14-safe-error.png'), fullPage: true });
});

async function loginSelectApprovedAndRoute(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('e2e.portal@sfpcl.example');
  await page.getByLabel('Password').fill('E2eTracer123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();

  const applicationId = await page.evaluate(async () => {
    const session = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const response = await fetch('http://127.0.0.1:8000/api/v1/portal/applications/', {
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });
    if (!response.ok) throw new Error(`Portal applications failed with ${response.status}`);
    const payload = await response.json();
    const approved = payload.data.items.find(
      (item: { application_reference_number: string }) => item.application_reference_number === 'LO000008L4',
    );
    if (!approved) throw new Error('The deterministic approved portal application is missing.');
    return approved.loan_application_id as string;
  });

  await page.getByRole('navigation').getByRole('button', { name: 'My Applications', exact: true }).click();
  await page.getByText('LO000008L4', { exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Application LO000008L4', level: 2 })).toBeVisible();
  return `http://127.0.0.1:8000/api/v1/portal/applications/${applicationId}/disbursement-status/`;
}

async function portalProjection(route: Route, projection: unknown) {
  const request = route.request();
  expect(request.method()).toBe('GET');
  expect(request.headers().authorization).toMatch(/^Bearer /);
  const applicationId = new URL(request.url()).pathname.split('/').at(-3);
  expect(applicationId).toBeTruthy();
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      success: true,
      data: { ...(projection as Record<string, unknown>), loan_application_id: applicationId },
      error: null,
      meta: { request_id: 'mp14-browser' },
    }),
  });
}

async function assertNoInternalEvidence(page: Page) {
  const body = await page.locator('body').innerText();
  for (const forbidden of ['RBLUTR1234569876', '12345678904321', 'authorised_by', 'checksum', 'outbox']) {
    expect(body.toLowerCase()).not.toContain(forbidden.toLowerCase());
  }
}

const timeline = [
  ['documentation_complete', 'Documents completed.'],
  ['sap_setup', 'Finance setup complete.'],
  ['payment_initiated', 'Payment processing started.'],
  ['cfc_authorisation', 'Payment approved.'],
  ['transfer_completed', 'Loan amount transferred.'],
  ['advice_issued', 'Disbursement advice issued.'],
] as const;

const processingProjection = {
  loan_application_id: 'selected-by-real-django',
  loan_account_id: 'loan-processing',
  status_code: 'finance_setup_pending',
  status_label: 'Finance setup in progress.',
  sanctioned_amount: '400000.00',
  disbursement_amount: null,
  destination_account_last4: null,
  disbursed_at: null,
  bank_reference_last4: null,
  advice_available: false,
  timeline: timeline.map(([code, label], index) => ({
    code,
    label,
    status: index < 2 ? 'complete' : 'pending',
    completed_at: index === 0 ? '2026-07-16T08:00:00Z' : index === 1 ? '2026-07-17T08:00:00Z' : null,
  })),
};

const disbursedProjection = {
  ...processingProjection,
  loan_account_id: 'loan-disbursed',
  status_code: 'disbursed',
  status_label: 'Loan amount transferred.',
  disbursement_amount: '400000.00',
  destination_account_last4: '4321',
  disbursed_at: '2026-07-18T12:00:00Z',
  bank_reference_last4: '9876',
  advice_available: true,
  timeline: timeline.map(([code, label], index) => ({
    code,
    label,
    status: 'complete',
    completed_at: `2026-07-${String(13 + index).padStart(2, '0')}T08:00:00Z`,
  })),
};
