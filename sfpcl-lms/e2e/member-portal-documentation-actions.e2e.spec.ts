import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test('MP07 upload authority, signed download, and completed status are routed', async ({ page }) => {
  let uploaded = false;
  let documentationReads = 0;
  await routePortal(page, async route => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/portal/auth/login/') return json(route, session);
    if (url.pathname === '/api/v1/auth/me/') return json(route, portalUser);
    if (url.pathname === '/api/v1/portal/dashboard/') return json(route, dashboard);
    if (url.pathname === '/api/v1/portal/applications/') return json(route, { items: [approvedApplication] });
    if (url.pathname === `/api/v1/portal/applications/${applicationId}/documentation-actions/`) {
      documentationReads += 1;
      return json(route, projection(uploaded));
    }
    if (url.pathname.endsWith('/documentation-actions/term_sheet/upload/')) {
      if (uploaded) return error(route, 409, 'INVALID_STATE_TRANSITION', 'This documentation action is not currently available for upload.');
      uploaded = true;
      return json(route, { action_code: 'term_sheet', status: 'submitted', document: uploadDocument });
    }
    if (url.pathname.endsWith('/documentation-actions/term_sheet/download/')) {
      if (url.searchParams.get('content') !== '1') {
        return json(route, {
          download_url: `/api/v1/portal/applications/${applicationId}/documentation-actions/term_sheet/download/?content=1&token=signed-current-term-sheet`,
          expires_at: '2026-07-15T16:00:00Z',
        });
      }
      if (url.searchParams.get('token') !== 'signed-current-term-sheet') {
        return error(route, 404, 'NOT_FOUND', 'Document was not found.');
      }
      return route.fulfill({ status: 200, contentType: 'application/pdf', body: '%PDF current term sheet' });
    }
    return error(route, 404, 'NOT_FOUND', 'Test route was not found.');
  });

  await portalLogin(page);
  await page.getByRole('navigation').getByRole('button', { name: 'My Documents', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'My Documents', exact: true, level: 2 })).toBeVisible();
  await page.getByRole('button', { name: 'Upload Term Sheet' }).click();
  await expect(page.getByText('Click to select file or drag and drop')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-documentation-upload-modal.png'), fullPage: true });

  await page.getByLabel('Document file').setInputFiles({
    name: 'signed-term-sheet.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF signed term sheet'),
  });
  await page.getByLabel('Notes (optional)').fill('Signed by borrower.');
  await page.getByRole('button', { name: 'Upload', exact: true }).click();
  await expect(page.getByText('Document uploaded for SFPCL review.')).toBeVisible();
  expect(documentationReads).toBe(2);

  await expect(page.getByText('Complete', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download Term Sheet' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Upload Term Sheet' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Re-upload Term Sheet' })).toHaveCount(0);

  const contract = await page.evaluate(async ({ appId }) => {
    const auth = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const headers = { Authorization: `Bearer ${auth.accessToken}` };
    const root = `http://127.0.0.1:8000/api/v1/portal/applications/${appId}/documentation-actions/term_sheet`;
    const descriptorResponse = await fetch(`${root}/download/`, { headers });
    const descriptor = (await descriptorResponse.json()).data;
    const content = await fetch(`http://127.0.0.1:8000${descriptor.download_url}`, { headers });
    const tampered = await fetch(`http://127.0.0.1:8000${descriptor.download_url.replace('signed-current', 'tampered')}`, { headers });
    const crafted = await fetch(`${root}/upload/`, {
      method: 'POST', headers, body: new FormData(),
    });
    return { descriptorStatus: descriptorResponse.status, contentStatus: content.status, tamperedStatus: tampered.status, craftedStatus: crafted.status };
  }, { appId: applicationId });
  expect(contract).toEqual({ descriptorStatus: 200, contentStatus: 200, tamperedStatus: 404, craftedStatus: 409 });
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-documentation-complete-upload-denied.png'), fullPage: true });
});

const applicationId = 'application-documentation';
const approvedApplication = {
  loan_application_id: applicationId, application_reference_number: 'LO000008L3', display_reference: 'LO000008L3',
  application_date: '2026-07-15', submitted_at: '2026-07-15T08:00:00Z', required_loan_amount: '400000.00',
  declared_purpose: 'Crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term',
  application_status: 'approved_by_sanction_committee', current_stage: 'credit_assessment', completeness_status: 'complete',
  pending_with: 'Borrower', borrower_action: 'Complete documentation', open_deficiency_count: 0,
  created_at: '2026-07-15T07:00:00Z', updated_at: '2026-07-15T09:00:00Z',
};
const action = (complete: boolean) => ({
  action_code: 'term_sheet', label: 'Term Sheet', section: 'Sanction', required: true, applicable: true,
  status: complete ? 'complete' : 'pending_borrower', updated_date: '2026-07-15',
  instruction: 'Download the current Term Sheet, sign it, and upload the signed copy.', note: null,
  upload_allowed: !complete, reupload_allowed: false,
  download: { file_name: 'term-sheet-LO000008L3.pdf', mime_type: 'application/pdf', action_url: `/api/v1/portal/applications/${applicationId}/documentation-actions/term_sheet/download/` },
});
const projection = (complete: boolean) => ({
  loan_application_id: applicationId, application_reference_number: 'LO000008L3',
  application_status: 'approved_by_sanction_committee', availability: 'available', unavailable_reason: null,
  actions: [action(complete)],
});
const uploadDocument = { document_id: 'document-upload', file_name: 'signed-term-sheet.pdf', mime_type: 'application/pdf', file_size_bytes: 22, checksum_sha256: 'safe-checksum', uploaded_at: '2026-07-15T10:00:00Z' };

async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('portal.008l3@example.test');
  await page.getByLabel('Password').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}
const routePortal = (page: Page, handler: (route: Route) => Promise<unknown>) => page.route('**/api/v1/**', handler);
const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, meta: {} }) });
const error = (route: Route, status: number, code: string, message: string) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message, field_errors: {} }, meta: {} }) });
const session = { access_token: 'portal-contract-access', refresh_token: 'portal-contract-refresh', expires_in: 300, user: {} };
const portalUser = { user_id: 'portal-user', full_name: 'Portal Contract Member', email: 'portal.008l3@example.test', status: 'active', roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }], teams: [], role_codes: ['borrower_portal_user'], team_codes: [], permissions: [], available_actions: [], member_id: 'member-contract', portal_account_id: 'portal-account-contract', portal_role: 'borrower_member', member_display_name: 'Portal Contract Member' };
const dashboard = { member: { member_id: 'member-contract', member_number: 'MEM-008L3', member_type: 'individual_farmer', display_name: 'Portal Contract Member', folio_number: 'FOL-008L3', membership_status: 'active', kyc_status: 'verified', default_status: 'no_default', share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 }, active_member_status: { status: 'active', verified_at: '2026-07-15T08:00:00Z' } }, application_counts: {}, loan_counts: {}, pending_actions: {}, notices: [] };
