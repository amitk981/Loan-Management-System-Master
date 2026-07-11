import path from 'path';
import { expect, test, type Route } from '@playwright/test';

const evidenceDir = path.resolve(__dirname, '../../.ralph/runs/2026-07-11_140734_normal_run/evidence/screenshots');

test('completeness workbench uses backend actions and captures required states', async ({ page }) => {
  let passed = false;
  let returned = false;
  const actionBodies: Record<string, unknown> = {};

  await page.addInitScript(() => {
    localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
      accessToken: 'completeness-access',
      refreshToken: 'completeness-refresh',
    }));
  });
  await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: {}, cards: [], tasks: [] }));
  await page.route('**/api/v1/loan-applications/**', async route => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (pathname === '/api/v1/loan-applications/') {
      const status = new URL(request.url()).searchParams.get('application_status');
      return json(route, status === 'submitted' ? applications : [], pagination);
    }
    if (pathname.endsWith('/completeness-check/pass/')) {
      actionBodies.pass = request.postDataJSON();
      passed = true;
      return json(route, { ...applications[0], application_reference_number: 'LO00000042', application_status: 'reference_generated' });
    }
    if (pathname.endsWith('/return-with-deficiencies/')) {
      actionBodies.return = request.postDataJSON();
      returned = true;
      return json(route, { ...applications[1], application_status: 'incomplete_returned', items: [openDeficiency] });
    }
    if (pathname.endsWith('/document-checklist/')) {
      const first = pathname.includes('app-ready');
      return json(route, {
        loan_application_id: first ? 'app-ready' : 'app-deficient',
        items: first ? readyCompleteness(passed).required_checklist_items : deficientCompleteness(returned).required_checklist_items,
      });
    }
    if (pathname.endsWith('/completeness-check/')) {
      const first = pathname.includes('app-ready');
      return json(route, first ? readyCompleteness(passed) : deficientCompleteness(returned));
    }
    if (pathname.endsWith('/deficiencies/')) {
      const first = pathname.includes('app-ready');
      return json(route, { loan_application_id: first ? 'app-ready' : 'app-deficient', items: first ? [] : [openDeficiency, resolvedDeficiency] });
    }
    return route.abort();
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Completeness' }).click();
  await expect(page.getByText('Visual Ready Borrower').first()).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'queue-detail.png'), fullPage: true });

  await page.getByRole('button', { name: 'Generate reference number' }).click();
  await expect(page.getByText('Reference generated · LO00000042')).toBeVisible();
  expect(actionBodies.pass).toEqual({});
  await page.screenshot({ path: path.join(evidenceDir, 'pass.png'), fullPage: true });

  await page.getByText('Visual Deficient Borrower').click();
  await expect(page.getByText('Current PAN copy is missing.')).toBeVisible();
  await expect(page.getByText('Verified replacement from borrower.')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'deficiency.png'), fullPage: true });

  await page.getByPlaceholder('Required communication, rejection reason, or resolution notes').fill('Please submit the missing PAN copy.');
  await page.getByPlaceholder('Optional deficiency remark').fill('Current PAN copy is missing.');
  await page.getByRole('button', { name: 'Return for deficiency' }).click();
  await expect(page.getByText('Returned for Rectification').first()).toBeVisible();
  expect(actionBodies.return).toEqual({
    communication_mode: 'email',
    message: 'Please submit the missing PAN copy.',
    items: [{ item_code: 'borrower_pan', remarks: 'Current PAN copy is missing.' }],
  });
  await page.screenshot({ path: path.join(evidenceDir, 'returned.png'), fullPage: true });
});

const applications = [
  {
    loan_application_id: 'app-ready',
    application_reference_number: null,
    member: { member_id: 'member-ready', display_name: 'Visual Ready Borrower', member_type: 'individual_farmer', folio_number: 'FOL-READY', kyc_status: 'verified' },
    application_date: '2026-07-10',
    required_loan_amount: '250000.00',
    declared_purpose: 'Crop production',
    purpose_category: 'crop_production',
    application_status: 'submitted',
    current_stage: 'initial_loan_request',
    completeness_status: 'not_started',
  },
  {
    loan_application_id: 'app-deficient',
    application_reference_number: null,
    member: { member_id: 'member-deficient', display_name: 'Visual Deficient Borrower', member_type: 'individual_farmer', folio_number: 'FOL-DEF', kyc_status: 'verified' },
    application_date: '2026-07-11',
    required_loan_amount: '180000.00',
    declared_purpose: 'Agriculture activity',
    purpose_category: 'agriculture_activity',
    application_status: 'submitted',
    current_stage: 'initial_loan_request',
    completeness_status: 'not_started',
  },
];

const readyCompleteness = (complete: boolean) => ({
  loan_application_id: 'app-ready',
  application_reference_number: complete ? 'LO00000042' : null,
  application_status: complete ? 'reference_generated' : 'submitted',
  current_stage: complete ? 'credit_assessment' : 'initial_loan_request',
  completeness_status: complete ? 'complete' : 'not_started',
  member: applications[0].member,
  nominee: null,
  nominee_selection_status: 'valid',
  required_checklist_items: [{ document_type: 'borrower_pan', submission_status: 'submitted', verification_status: 'verified', complete: true, reason_code: null }],
  blocking_document_types: [],
  can_generate_reference: !complete,
});

const deficientCompleteness = (isReturned: boolean) => ({
  loan_application_id: 'app-deficient',
  application_reference_number: null,
  application_status: isReturned ? 'incomplete_returned' : 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: isReturned ? 'incomplete' : 'not_started',
  member: applications[1].member,
  nominee: null,
  nominee_selection_status: 'valid',
  required_checklist_items: [{ document_type: 'borrower_pan', submission_status: 'missing', verification_status: 'pending', complete: false, reason_code: 'missing_metadata' }],
  blocking_document_types: ['borrower_pan'],
  can_generate_reference: false,
});

const openDeficiency = { deficiency_id: 'def-open', item_code: 'borrower_pan', description: 'Current PAN copy is missing.', resolution_status: 'open' };
const resolvedDeficiency = { deficiency_id: 'def-resolved', item_code: 'borrower_pan', description: 'Earlier PAN copy was unclear.', resolution_status: 'resolved', resolution_notes: 'Verified replacement from borrower.' };

const currentUser = {
  user_id: 'staff-completeness-1',
  full_name: 'Deputy Manager Finance',
  email: 'completeness@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'deputy_manager_finance', role_name: 'Deputy Manager Finance' }],
  teams: [],
  role_codes: ['deputy_manager_finance'],
  team_codes: [],
  permissions: ['applications.loan_application.read', 'applications.loan_application.complete_check'],
  available_actions: [],
};

const pagination = { pagination: { page: 1, page_size: 100, total_count: 2, total_pages: 1, has_next: false, has_previous: false } };

const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, ...extra }),
});
