import { expect, test, type Page, type Route } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 390, height: 844 } });

test('MP11 uploads every correction and returns the application to SFPCL review', async ({ page }) => {
  let responded = false;
  let resubmitted = false;
  await page.route('**/api/v1/**', async route => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/portal/auth/login/') return json(route, session);
    if (url.pathname === '/api/v1/auth/me/') return json(route, portalUser);
    if (url.pathname === '/api/v1/portal/dashboard/') return json(route, dashboard);
    if (url.pathname === '/api/v1/portal/applications/') return json(route, { items: [application(resubmitted)] });
    if (url.pathname === `/api/v1/portal/applications/${applicationId}/`) return json(route, application(resubmitted));
    if (url.pathname === `/api/v1/portal/applications/${applicationId}/deficiencies/`) return json(route, deficiencyProjection(responded));
    if (url.pathname.endsWith(`/deficiencies/${deficiencyId}/upload/`)) {
      responded = true;
      return json(route, { deficiency_id: deficiencyId, response_status: 'responded', response, document: response.document });
    }
    if (url.pathname.endsWith('/deficiencies/resubmit/')) {
      if (!responded || resubmitted) return error(route, 409, 'INVALID_STATE_TRANSITION', 'Resubmission is not available.');
      resubmitted = true;
      return json(route, { loan_application_id: applicationId, application_status: 'submitted', completeness_status: 'not_started', current_stage: 'initial_loan_request', pending_with: 'SFPCL', responded_deficiency_count: 1 });
    }
    return error(route, 404, 'NOT_FOUND', 'Test route was not found.');
  });

  await portalLogin(page);
  await page.getByRole('button', { name: 'My Applications', exact: true }).click();
  await page.getByText('LO000008L3-R').click();
  await page.getByRole('button', { name: 'Submitted Data & Deficiencies' }).click();
  await expect(page.getByRole('heading', { name: 'Deficiency Response', exact: true })).toBeVisible();
  await expect(page.getByText('Upload the missing six-month bank statement.')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-deficiency-mobile-response.png'), fullPage: true });

  await page.getByLabel('Replacement document').setInputFiles({
    name: 'corrected-bank-statement.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF corrected bank statement'),
  });
  await page.getByLabel('Borrower response remark').fill('The complete six-month statement is attached.');
  await page.getByRole('button', { name: 'Upload response' }).click();
  await expect(page.getByText('Response uploaded for SFPCL review.')).toBeVisible();
  await page.getByRole('button', { name: 'Resubmit corrections' }).click();
  const applicationHeader = page.getByRole('heading', { name: `Application LO000008L3-R`, exact: true }).locator('..');
  await expect(applicationHeader.getByText('Submitted - Pending Completeness Check', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Deficiency Response', exact: true })).toHaveCount(0);
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-deficiency-resubmitted.png'), fullPage: true });
});

const applicationId = 'application-returned';
const deficiencyId = 'deficiency-bank-statement';
const application = (submitted: boolean) => ({
  loan_application_id: applicationId, application_reference_number: 'LO000008L3-R', display_reference: 'LO000008L3-R',
  application_date: '2026-07-14', submitted_at: '2026-07-14T08:00:00Z', required_loan_amount: '250000.00',
  declared_purpose: 'Crop production', purpose_category: 'crop_production', loan_type_requested: 'short_term',
  application_status: submitted ? 'submitted' : 'incomplete_returned', current_stage: 'initial_loan_request', completeness_status: submitted ? 'not_started' : 'incomplete',
  pending_with: submitted ? 'SFPCL' : 'Borrower', borrower_action: submitted ? 'Await completeness review' : 'Review deficiencies', open_deficiency_count: submitted ? 0 : 1,
  created_at: '2026-07-14T07:00:00Z', updated_at: '2026-07-15T09:00:00Z', timeline: [], member: null, nominee: null,
});
const response = { deficiency_response_id: 'response-bank-statement', response_status: 'responded', response_remark: 'The complete six-month statement is attached.', responded_at: '2026-07-15T10:00:00Z', document: { document_id: 'document-bank-statement', file_name: 'corrected-bank-statement.pdf', mime_type: 'application/pdf', file_size_bytes: 29, checksum_sha256: 'safe-checksum', uploaded_at: '2026-07-15T10:00:00Z', action_url: `/api/v1/portal/applications/${applicationId}/deficiencies/${deficiencyId}/download/` } };
const deficiencyProjection = (responded: boolean) => ({
  loan_application_id: applicationId, application_reference_number: 'LO000008L3-R', application_status: 'incomplete_returned',
  deficiency_note_action_url: `/api/v1/portal/applications/${applicationId}/deficiencies/note/`, resubmission_allowed: responded,
  open_deficiency_count: 1, responded_deficiency_count: responded ? 1 : 0,
  items: [{ deficiency_id: deficiencyId, item_code: 'six_month_bank_statement', deficiency_type: 'missing_document', description: 'Upload the missing six-month bank statement.', resolution_status: 'open', upload_contract: { document_category: 'finance', sensitivity_level: 'confidential', allowed_extensions: ['pdf', 'jpg', 'jpeg', 'png'], max_size_bytes: 5242880 }, response: responded ? response : null, draft: null }],
});

async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('portal.008l3@example.test');
  await page.getByLabel('Password').fill('correct horse battery staple');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}
const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, meta: {} }) });
const error = (route: Route, status: number, code: string, message: string) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message, field_errors: {} }, meta: {} }) });
const session = { access_token: 'portal-contract-access', refresh_token: 'portal-contract-refresh', expires_in: 300, user: {} };
const portalUser = { user_id: 'portal-user', full_name: 'Portal Contract Member', email: 'portal.008l3@example.test', status: 'active', roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }], teams: [], role_codes: ['borrower_portal_user'], team_codes: [], permissions: [], available_actions: [], member_id: 'member-contract', portal_account_id: 'portal-account-contract', portal_role: 'borrower_member', member_display_name: 'Portal Contract Member' };
const dashboard = { member: { member_id: 'member-contract', member_number: 'MEM-008L3', member_type: 'individual_farmer', display_name: 'Portal Contract Member', folio_number: 'FOL-008L3', membership_status: 'active', kyc_status: 'verified', default_status: 'no_default', share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 }, active_member_status: { status: 'active', verified_at: '2026-07-15T08:00:00Z' } }, application_counts: {}, loan_counts: {}, pending_actions: {}, notices: [] };
