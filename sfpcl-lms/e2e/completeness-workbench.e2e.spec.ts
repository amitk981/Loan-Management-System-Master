import fs from 'fs';
import path from 'path';
import { expect, test, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('completeness workbench uses backend actions and captures required states', async ({ page }) => {
  let passed = false;
  let returned = false;
  let resolved = false;
  let rejected = false;
  let stalePassCalls = 0;
  let forcedLoadStatus: 403 | 500 | null = null;
  const actionBodies: Record<string, unknown> = {};
  const actionCalls: Record<string, number> = { pass: 0, return: 0, resolve: 0, reject: 0 };
  const canonicalReads: Record<string, number> = {};
  const countRead = (applicationId: string, resource: string) => {
    const key = `${applicationId}:${resource}`;
    canonicalReads[key] = (canonicalReads[key] ?? 0) + 1;
  };

  await page.addInitScript(() => {
    localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
      accessToken: 'completeness-access',
      refreshToken: 'completeness-refresh',
    }));
  });
  await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'deputy_manager_finance', cards: [], tasks: [] }));
  await page.route('**/api/v1/deficiencies/**', route => {
    actionCalls.resolve += 1;
    actionBodies.resolve = route.request().postDataJSON();
    resolved = true;
    return json(route, { ...openDeficiency, resolution_status: 'resolved', resolution_notes: 'Verified replacement received.' });
  });
  await page.route('**/api/v1/loan-applications/**', async route => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (pathname === '/api/v1/loan-applications/') {
      const status = new URL(request.url()).searchParams.get('application_status');
      return json(route, status === 'submitted' ? applications : [], pagination);
    }
    if (pathname.endsWith('/completeness-check/pass/')) {
      if (pathname.includes('app-stale')) {
        stalePassCalls += 1;
        return route.fulfill({ status: 409, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code: 'INVALID_STATE_TRANSITION', message: 'This application changed on the server.' } }) });
      }
      actionCalls.pass += 1;
      actionBodies.pass = request.postDataJSON();
      passed = true;
      return json(route, { ...applications[0], application_reference_number: 'LO00000042', application_status: 'reference_generated' });
    }
    if (pathname.endsWith('/return-with-deficiencies/')) {
      actionCalls.return += 1;
      actionBodies.return = request.postDataJSON();
      returned = true;
      return json(route, { ...applications[1], application_status: 'incomplete_returned', items: [openDeficiency] });
    }
    if (pathname.endsWith('/rejection-note/')) {
      actionCalls.reject += 1;
      actionBodies.reject = request.postDataJSON();
      rejected = true;
      return json(route, { rejection_note_id: 'note-1', loan_application_id: 'app-reject', note_status: 'draft' });
    }
    if (pathname.endsWith('/document-checklist/')) {
      const applicationId = pathname.split('/')[4];
      countRead(applicationId, 'checklist');
      const first = pathname.includes('app-ready');
      const application = applications.find(item => pathname.includes(item.loan_application_id)) ?? null;
      const items = pathname.includes('app-deficient')
        ? deficientCompleteness(returned, resolved).required_checklist_items
        : application
          ? readyCompletenessFor(application, false, rejected).required_checklist_items
          : readyCompleteness(passed).required_checklist_items;
      return json(route, {
        loan_application_id: application?.loan_application_id ?? (first ? 'app-ready' : 'app-deficient'),
        items,
      });
    }
    if (pathname.endsWith('/completeness-check/')) {
      const applicationId = pathname.split('/')[4];
      countRead(applicationId, 'completeness');
      if (forcedLoadStatus && (pathname.includes('app-error') || forcedLoadStatus === 403)) {
        const forbidden = forcedLoadStatus === 403;
        return route.fulfill({
          status: forcedLoadStatus,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            error: {
              code: forbidden ? 'OBJECT_ACCESS_DENIED' : 'SERVICE_UNAVAILABLE',
              message: forbidden
                ? 'This actor cannot access the selected application.'
                : 'Completeness service unavailable for browser proof.',
            },
          }),
        });
      }
      const first = pathname.includes('app-ready');
      if (pathname.includes('app-reject')) return json(route, readyCompletenessFor(applications[2], false, rejected));
      if (pathname.includes('app-stale')) return json(route, readyCompletenessFor(applications[3], false, false, true));
      if (pathname.includes('app-error')) return json(route, readyCompletenessFor(applications[4], false, false));
      return json(route, first ? readyCompleteness(passed) : deficientCompleteness(returned, resolved));
    }
    if (pathname.endsWith('/deficiencies/')) {
      const applicationId = pathname.split('/')[4];
      countRead(applicationId, 'deficiencies');
      const first = pathname.includes('app-ready');
      return json(route, { loan_application_id: first ? 'app-ready' : 'app-deficient', items: first ? [] : [{ ...openDeficiency, ...(resolved ? { resolution_status: 'resolved', resolution_notes: 'Verified replacement received.' } : {}) }, resolvedDeficiency], available_actions: first ? readyCompleteness(passed).available_actions : deficientCompleteness(returned, resolved).available_actions });
    }
    return route.abort();
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Completeness' }).click();
  await expect(page.getByText('Visual Ready Borrower').first()).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'queue-detail.png'), fullPage: true });

  const readyReadsBeforePass = readsFor('app-ready', canonicalReads);
  await page.getByRole('button', { name: 'Generate reference number' }).click();
  await expect(page.getByText('Reference generated · LO00000042')).toBeVisible();
  expect(actionBodies.pass).toEqual({});
  expect(actionCalls.pass).toBe(1);
  expect(readsFor('app-ready', canonicalReads)).toEqual(incrementedReads(readyReadsBeforePass));
  await page.screenshot({ path: path.join(evidenceDir, 'pass.png'), fullPage: true });

  await page.getByText('Visual Deficient Borrower').click();
  await expect(page.getByText('Current PAN copy is missing.')).toBeVisible();
  await expect(page.getByText('Verified replacement from borrower.')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'deficiency.png'), fullPage: true });

  await page.getByPlaceholder('Required communication, rejection reason, or resolution notes').fill('Please submit the missing PAN copy.');
  await page.getByPlaceholder('Optional deficiency remark').fill('Current PAN copy is missing.');
  const deficientReadsBeforeReturn = readsFor('app-deficient', canonicalReads);
  await page.getByRole('button', { name: 'Return for deficiency' }).click();
  await expect(page.getByText('Returned for Rectification').first()).toBeVisible();
  expect(actionBodies.return).toEqual({
    communication_mode: 'email',
    message: 'Please submit the missing PAN copy.',
    items: [{ item_code: 'borrower_pan', remarks: 'Current PAN copy is missing.' }],
  });
  expect(actionCalls.return).toBe(1);
  expect(readsFor('app-deficient', canonicalReads)).toEqual(incrementedReads(deficientReadsBeforeReturn));
  await page.screenshot({ path: path.join(evidenceDir, 'returned.png'), fullPage: true });

  await page.getByPlaceholder('Required communication, rejection reason, or resolution notes').fill('Verified replacement received.');
  const deficientReadsBeforeResolve = readsFor('app-deficient', canonicalReads);
  await page.getByRole('button', { name: 'Resolve' }).first().click();
  await expect(page.locator('p').filter({ hasText: 'Verified replacement received.' })).toBeVisible();
  expect(actionBodies.resolve).toEqual({ resolution_notes: 'Verified replacement received.' });
  expect(actionCalls.resolve).toBe(1);
  expect(readsFor('app-deficient', canonicalReads)).toEqual(incrementedReads(deficientReadsBeforeResolve));
  await page.screenshot({ path: path.join(evidenceDir, 'resolved.png'), fullPage: true });

  await page.getByText('Visual Rejection Borrower').click();
  await page.getByPlaceholder('Required communication, rejection reason, or resolution notes').fill('Required evidence cannot be supplied.');
  const rejectionReadsBeforeAction = readsFor('app-reject', canonicalReads);
  await page.getByRole('button', { name: 'Recommend rejection' }).click();
  await expect(page.getByText('Recommend rejection: Unavailable for this canonical application state.')).toBeVisible();
  expect(actionBodies.reject).toEqual({ rejection_stage: 'completeness', rejection_reason_category: 'missing_document', detailed_reason: 'Required evidence cannot be supplied.', reapply_allowed_flag: true, communication_mode: 'email' });
  expect(actionCalls.reject).toBe(1);
  expect(readsFor('app-reject', canonicalReads)).toEqual(incrementedReads(rejectionReadsBeforeAction));
  await page.screenshot({ path: path.join(evidenceDir, 'rejected.png'), fullPage: true });

  await page.getByText('Visual Stale Borrower').click();
  await page.getByRole('button', { name: 'Generate reference number' }).click();
  await expect(page.getByText(/changed on the server/i)).toBeVisible();
  expect(stalePassCalls).toBe(1);
  await page.screenshot({ path: path.join(evidenceDir, 'stale.png'), fullPage: true });
  await page.getByRole('button', { name: 'Refresh' }).click();
  expect(stalePassCalls).toBe(1);

  forcedLoadStatus = 500;
  await page.getByText('Visual Error Borrower').click();
  await expect(page.getByText('Completeness service unavailable for browser proof.')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'api-error.png'), fullPage: true });

  forcedLoadStatus = 403;
  await page.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('You are not authorised to access this completeness review.')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'denied.png'), fullPage: true });
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
  {
    loan_application_id: 'app-reject', application_reference_number: null,
    member: { member_id: 'member-reject', display_name: 'Visual Rejection Borrower', member_type: 'individual_farmer', folio_number: 'FOL-REJECT', kyc_status: 'verified' },
    application_date: '2026-07-11', required_loan_amount: '190000.00', declared_purpose: 'Farm equipment', purpose_category: 'farm_equipment', application_status: 'submitted', current_stage: 'initial_loan_request', completeness_status: 'not_started',
  },
  {
    loan_application_id: 'app-stale', application_reference_number: null,
    member: { member_id: 'member-stale', display_name: 'Visual Stale Borrower', member_type: 'individual_farmer', folio_number: 'FOL-STALE', kyc_status: 'verified' },
    application_date: '2026-07-11', required_loan_amount: '200000.00', declared_purpose: 'Crop production', purpose_category: 'crop_production', application_status: 'submitted', current_stage: 'initial_loan_request', completeness_status: 'not_started',
  },
  {
    loan_application_id: 'app-error', application_reference_number: null,
    member: { member_id: 'member-error', display_name: 'Visual Error Borrower', member_type: 'individual_farmer', folio_number: 'FOL-ERROR', kyc_status: 'verified' },
    application_date: '2026-07-11', required_loan_amount: '210000.00', declared_purpose: 'Agriculture activity', purpose_category: 'agriculture_activity', application_status: 'submitted', current_stage: 'initial_loan_request', completeness_status: 'not_started',
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
  available_actions: complete
    ? completenessActions()
    : completenessActions({ pass_completeness: true, create_rejection_note: true }),
});

const readyCompletenessFor = (application: typeof applications[number], complete: boolean, hasRejection: boolean, stale = false) => ({
  ...readyCompleteness(complete),
  loan_application_id: application.loan_application_id,
  member: application.member,
  available_actions: hasRejection
    ? completenessActions()
    : completenessActions(stale ? { pass_completeness: true } : { create_rejection_note: true }),
});

const deficientCompleteness = (isReturned: boolean, isResolved = false) => ({
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
  available_actions: isReturned
    ? completenessActions({ resolve_deficiency: !isResolved })
    : completenessActions({ return_with_deficiencies: true, create_rejection_note: true }),
});

const completenessActions = (enabled: Record<string, boolean> = {}) => [
  ['pass_completeness', 'Generate reference number', 'applications.loan_application.complete_check', 'deputy_manager_finance'],
  ['return_with_deficiencies', 'Return for deficiency', 'applications.loan_application.return_deficiency', 'deputy_manager_finance'],
  ['resolve_deficiency', 'Resolve deficiency', 'applications.deficiency.resolve', 'deputy_manager_finance'],
  ['create_rejection_note', 'Recommend rejection', 'applications.rejection_note.create', 'credit_manager'],
].map(([action_code, label, required_permission, required_role]) => ({
  action_code,
  label,
  enabled: enabled[action_code] ?? false,
  disabled_reason: enabled[action_code] ? null : 'Unavailable for this canonical application state.',
  required_permission,
  required_role,
}));

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
  permissions: [
    'applications.loan_application.read',
    'applications.loan_application.complete_check',
    'applications.loan_application.return_deficiency',
    'applications.deficiency.resolve',
    'applications.rejection_note.create',
  ],
  available_actions: [],
};

const readsFor = (applicationId: string, reads: Record<string, number>) => ({
  checklist: reads[`${applicationId}:checklist`] ?? 0,
  completeness: reads[`${applicationId}:completeness`] ?? 0,
  deficiencies: reads[`${applicationId}:deficiencies`] ?? 0,
});

const incrementedReads = (reads: ReturnType<typeof readsFor>) => ({
  checklist: reads.checklist + 1,
  completeness: reads.completeness + 1,
  deficiencies: reads.deficiencies + 1,
});

const pagination = { pagination: { page: 1, page_size: 100, total_count: 2, total_pages: 1, has_next: false, has_previous: false } };

const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, ...extra }),
});
