import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 390, height: 844 } });

test('member sees the borrower-safe KYC correction decision on mobile', async ({ page }) => {
  await mountPortal(page, [approvedCorrection]);
  await openProfile(page);

  await expect(page.getByRole('heading', { name: 'Request a KYC correction' })).toBeVisible();
  await expect(page.getByText('Approved', { exact: true })).toBeVisible();
  await expect(page.getByText(/PAN \*{6}234F/)).toBeVisible();
  await expect(page.getByText('internal evidence accepted', { exact: true })).toHaveCount(0);
  await page.screenshot({
    path: path.join(evidenceRoot, 'portal-kyc-correction-decision.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('member uploads self-attested evidence and submits one own-scope correction', async ({ page }) => {
  const requests: Array<{ url: string; method: string }> = [];
  await mountPortal(page, [], requests);
  await openProfile(page);

  await page.getByLabel('Correct value').fill('ABCDE1234F');
  await page.getByLabel('Reason for correction').fill('My verified PAN record is stale.');
  await page.getByLabel('Self-attested evidence').setInputFiles({
    name: 'corrected-pan.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4 synthetic portal evidence'),
  });
  await page.getByRole('button', { name: 'Submit correction request' }).click();

  await expect(page.getByText('Submitted', { exact: true })).toBeVisible();
  expect(requests).toEqual([
    { url: '/api/v1/portal/kyc-corrections/evidence/', method: 'POST' },
    { url: '/api/v1/portal/kyc-corrections/', method: 'POST' },
  ]);
});

async function mountPortal(
  page: Page,
  corrections: object[],
  requests: Array<{ url: string; method: string }> = [],
) {
  await page.route('**/api/v1/portal/auth/login/', route => ok(route, {
    access_token: 'portal-kyc-access',
    refresh_token: 'portal-kyc-refresh',
    expires_in: 300,
    user: {},
  }));
  await page.route('**/api/v1/auth/me/', route => ok(route, currentUser));
  await page.route('**/api/v1/portal/dashboard/', route => ok(route, dashboard));
  await page.route('**/api/v1/portal/profile/', route => ok(route, profile));
  await page.route('**/api/v1/portal/kyc-corrections/evidence/', route => {
    requests.push({ url: new URL(route.request().url()).pathname, method: route.request().method() });
    return ok(route, { document_id: 'uploaded-evidence' });
  });
  await page.route('**/api/v1/portal/kyc-corrections/', route => {
    if (route.request().method() === 'POST') {
      requests.push({ url: new URL(route.request().url()).pathname, method: 'POST' });
      return ok(route, submittedCorrection);
    }
    return ok(route, { items: corrections });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('portal.kyc@example.test');
  await page.getByLabel('Password').fill('KycCorrection123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal KYC Member' })).toBeVisible();
}

async function openProfile(page: Page) {
  await page.getByRole('navigation').getByRole('button', { name: 'My Profile', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Portal KYC Member' })).toBeVisible();
}

const member = {
  member_id: 'member-kyc',
  member_number: 'MEM-KYC',
  member_type: 'individual_farmer',
  legal_name: 'Portal KYC Member',
  display_name: 'Portal KYC Member',
  folio_number: 'FOL-KYC',
  membership_status: 'active',
  kyc_status: 'verified',
  default_status: 'no_default',
  pan: { masked: '******000F', can_view_full: false },
  aadhaar: { masked: '********0000', can_view_full: false },
  registered_address: {},
  share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 },
  active_member_status: { status: 'active', verified_at: '2026-07-01T10:00:00Z' },
};
const currentUser = {
  user_id: 'portal-kyc-user',
  full_name: 'Portal KYC Member',
  email: 'portal.kyc@example.test',
  status: 'active',
  roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }],
  teams: [],
  role_codes: ['borrower_portal_user'],
  team_codes: [],
  permissions: [],
  available_actions: [],
  member_id: 'member-kyc',
  portal_account_id: 'portal-account-kyc',
};
const dashboard = {
  member,
  application_counts: {},
  loan_counts: {},
  pending_actions: {},
  notices: [],
};
const profile = {
  member,
  nominees: [],
  shareholdings: [],
  land_holdings: [],
  crop_plans: [],
  bank_accounts: [],
  cancelled_cheques: [],
  kyc_profile: { kyc_status: 'verified', rekyc_due_date: '2028-07-01', risk_rating: 'low' },
};
const approvedCorrection = {
  kyc_correction_request_id: 'correction-approved',
  status: 'approved',
  changes: { pan: '******234F' },
  reason: 'My verified PAN record was stale.',
  rejection_reason: null,
  submitted_at: '2026-07-22T08:00:00Z',
  review_started_at: '2026-07-22T09:00:00Z',
  decided_at: '2026-07-22T10:00:00Z',
  evidence: [{ document_id: 'evidence-approved', file_name: 'corrected-pan.pdf', mime_type: 'application/pdf', uploaded_at: '2026-07-22T08:00:00Z' }],
};
const submittedCorrection = {
  ...approvedCorrection,
  kyc_correction_request_id: 'correction-submitted',
  status: 'submitted',
  decided_at: null,
  review_started_at: null,
};
const ok = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, meta: { request_id: 'portal-kyc-browser' } }),
});
