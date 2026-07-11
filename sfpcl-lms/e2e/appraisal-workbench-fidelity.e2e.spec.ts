import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for appraisal visual acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('appraisal workbench preserves the staged prototype across the required state matrix', async ({ page }) => {
  let mode: 'matrix' | 'empty' | 'denied' | 'error' = 'matrix';
  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'appraisal-access', refreshToken: 'appraisal-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'credit_manager', cards: [], tasks: [] }));
  await page.route('**/api/v1/loan-applications/**', async route => {
    const pathname = new URL(route.request().url()).pathname;
    if (pathname === '/api/v1/loan-applications/') return json(route, mode === 'empty' ? [] : applications, pagination);
    const id = applications.find(item => pathname.includes(item.loan_application_id))?.loan_application_id ?? 'eligible';
    if (mode === 'denied') return failure(route, 403, 'OBJECT_ACCESS_DENIED', 'You cannot access this appraisal.');
    if (mode === 'error') return failure(route, 500, 'SERVICE_UNAVAILABLE', 'Appraisal service unavailable for visual proof.');
    if (pathname.endsWith('/eligibility-assessment/')) return json(route, eligibilityFor(id));
    if (pathname.endsWith('/loan-limit-assessment/')) return json(route, limitFor(id));
    if (pathname.endsWith('/appraisal-note/')) return appraisalIds.has(id) ? json(route, appraisalFor(id)) : failure(route, 404, 'NOT_FOUND', 'No appraisal note.');
    if (pathname.endsWith('/sanction-case/')) return id === 'submitted' ? json(route, sanction) : failure(route, 404, 'NOT_FOUND', 'No sanction case.');
    return failure(route, 400, 'VALIDATION_ERROR', 'Recommended amount is required.', { recommended_amount: 'This field is required.' });
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Appraisal' }).click();
  await expect(page.getByRole('heading', { name: 'Appraisal Workbench' })).toBeVisible();
  await capture(page, 'queue');

  for (const id of ['eligible', 'ineligible', 'pending', 'below', 'equal', 'above', 'draft', 'returned', 'review-pending', 'reviewed', 'rejected', 'submitted']) {
    await page.getByText(`Visual ${title(id)} Borrower`).click();
    await expect(page.getByRole('heading', { name: 'Appraisal Workbench' })).toBeVisible();
    await capture(page, id);
  }

  mode = 'error';
  await page.getByText('Visual Eligible Borrower').click();
  await expect(page.getByText(/Appraisal service unavailable/)).toBeVisible();
  await capture(page, 'api-error');

  mode = 'denied';
  await page.reload();
  await expect(page.getByText(/cannot access this appraisal/i)).toBeVisible();
  await capture(page, 'denied');

  mode = 'empty';
  await page.reload();
  await expect(page.getByText('Appraisal queue is clear')).toBeVisible();
  await capture(page, 'empty');

  mode = 'matrix';
  await page.reload();
  await page.getByText('Visual Draft Borrower').click();
  await page.getByRole('button', { name: 'Save Appraisal Draft' }).click();
  await expect(page.getByText(/This field is required/)).toBeVisible();
  await capture(page, 'validation');
});

const capture = async (page: Page, name: string) => {
  await page.screenshot({ path: path.join(evidenceDir, `${name}.png`), fullPage: true });
  await expect(page).toHaveScreenshot(`appraisal-${name}.png`, { fullPage: true, animations: 'disabled' });
};

const states = ['eligible', 'ineligible', 'pending', 'below', 'equal', 'above', 'draft', 'returned', 'review-pending', 'reviewed', 'rejected', 'submitted'];
function title(value: string) { return value.replace(/-/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase()); }
const applications = states.map((id, index) => ({
  loan_application_id: id,
  application_reference_number: `LO00010${String(index).padStart(2, '0')}`,
  member: { member_id: `member-${id}`, display_name: `Visual ${title(id)} Borrower`, member_type: 'individual_farmer', folio_number: `FOL-${index}` },
  application_date: '2026-07-10', required_loan_amount: id === 'above' ? '300000.00' : id === 'below' ? '200000.00' : '250000.00',
  purpose_category: 'crop_production', application_status: id === 'submitted' ? 'submitted_to_sanction_committee' : 'reference_generated', current_stage: 'credit_assessment', completeness_status: 'complete',
}));
const appraisalIds = new Set(['draft', 'returned', 'review-pending', 'reviewed', 'rejected', 'submitted']);
const eligibilityFor = (id: string) => ({
  eligibility_assessment_id: `eligibility-${id}`, loan_application_id: id,
  member_active_check: id === 'ineligible' ? 'fail' : id === 'pending' ? 'pending' : 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid',
  overall_result: id === 'ineligible' ? 'ineligible' : id === 'pending' ? 'pending_manual_evidence' : 'eligible', assessment_notes: `Stored ${id} assessment explanation.`, assessed_by_user_id: 'staff-1', assessed_at: '2026-07-10T10:00:00+05:30', available_actions: actions(),
});
const limitFor = (id: string) => {
  const requested = id === 'below' ? '200000.00' : id === 'above' ? '300000.00' : '250000.00';
  const within = id !== 'above';
  return { loan_limit_assessment_id: `limit-${id}`, loan_application_id: id, member_id: `member-${id}`, shareholding_id: 'share-1', number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00', shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00', land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: requested, amount_within_limit_flag: within, exception_required_flag: !within, calculation_rule_version: 'board-policy-2026', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' }, warnings: within ? [] : [{ code: 'LIMIT_EXCEEDED', message: 'Requested amount exceeds the stored eligible limit.' }], calculated_by_user_id: 'staff-1', calculated_at: '2026-07-10T10:05:00+05:30', available_actions: actions() };
};
const appraisalFor = (id: string) => {
  const status = id === 'returned' || id === 'draft' ? 'draft' : id === 'review-pending' ? 'review_pending' : id;
  return { loan_appraisal_note_id: `appraisal-${id}`, loan_application_id: id, eligibility_assessment_id: `eligibility-${id}`, loan_limit_assessment_id: `limit-${id}`, eligibility_snapshot: eligibilityFor(id), loan_limit_snapshot: limitFor(id), prerequisite_provenance: 'verified', prepared_by: { user_id: 'staff-1', full_name: 'Deputy Manager Finance' }, prepared_at: '2026-07-10T10:10:00+05:30', reviewed_by: null, reviewed_at: null, decision: null, review_comments: null, review_history: id === 'returned' ? [{ appraisal_review_decision_id: 'history-1', decision: 'returned', review_comments: 'Add repayment evidence.', reviewer: { user_id: 'manager-1', full_name: 'Credit Manager' }, decided_at: '2026-07-10T11:00:00+05:30', from_state: 'review_pending', to_state: 'draft', history_provenance: 'native' }] : [], tat_due_at: '2026-07-12T10:10:00+05:30', tat_status: 'within_tat', borrower_summary: 'API-backed borrower summary.', eligibility_summary: 'Stored assessment is eligible.', loan_limit_summary: 'Stored limit reviewed.', recommended_amount: '250000.00', recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Stored security recommendation.', repayment_capacity_notes: 'Stored repayment capacity.', risk_assessment: { risk_assessment_id: 'risk-1', market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Stored mitigations.' }, recommendation: 'approve', appraisal_status: status === 'submitted' ? 'submitted_to_sanction_committee' : status, ...(id === 'rejected' ? { rejection_note: { rejection_note_id: 'reject-1', note_status: 'approved', rejection_reason_category: 'eligibility', reapply_allowed_flag: true, communication_mode: 'email' } } : {}), available_actions: actions(id) };
};
const actions = (id = '') => [
  ['credit.appraisal.update', 'Save Appraisal Draft', id === 'draft' || id === 'returned', 'credit.appraisal.update', null],
  ['credit.appraisal.review', 'Record Credit Review', id === 'review-pending', 'credit.appraisal.review', 'credit_manager'],
  ['credit.appraisal.submit_sanction', 'Submit to Sanction Committee', id === 'reviewed', 'credit.appraisal.submit_sanction', 'credit_manager'],
].map(([action_code, label, enabled, required_permission, required_role]) => ({ action_code, label, enabled: Boolean(enabled), disabled_reason: enabled ? null : 'Unavailable for this canonical application state.', required_permission, required_role }));
const sanction = { approval_case_id: 'case-006H3', loan_application_id: 'submitted', loan_appraisal_note_id: 'appraisal-submitted', application_status: 'submitted_to_sanction_committee', appraisal_status: 'submitted_to_sanction_committee', submission_status: 'pending', exception_required_flag: false, submitted_by: { user_id: 'manager-1', full_name: 'Credit Manager' }, submitted_at: '2026-07-10T12:00:00+05:30', available_actions: actions('submitted') };
const currentUser = { user_id: 'manager-1', full_name: 'Credit Manager', email: 'manager@sfpcl.example', status: 'active', roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }], teams: [], role_codes: ['credit_manager'], team_codes: [], permissions: ['do_appraisal', 'credit.eligibility.run', 'credit.loan_limit.calculate', 'credit.appraisal.create', 'credit.appraisal.update', 'credit.appraisal.submit_review', 'credit.appraisal.review', 'credit.appraisal.submit_sanction', 'credit.risk_assessment.manage'], available_actions: [] };
const pagination = { pagination: { page: 1, page_size: 100, total_count: applications.length, total_pages: 1, has_next: false, has_previous: false } };
const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...extra }) });
const failure = (route: Route, status: number, code: string, message: string, field_errors?: Record<string, string>) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message, field_errors } }) });
