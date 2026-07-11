import fs from 'fs';
import path from 'path';
import { expect, test, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for the Epic 006 tracer');
fs.mkdirSync(evidenceDir, { recursive: true });

test('distinct finance roles drive one appraisal to one pending sanction case', async ({ page }) => {
  let role: 'deputy_manager_finance' | 'credit_manager' = 'deputy_manager_finance';
  let status = 'draft';
  let sanction: typeof pendingCase | null = null;
  let reads = 0;
  let patchBody: Record<string, unknown> = {};
  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'epic-006', refreshToken: 'epic-006-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, user(role)));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: role, cards: [], tasks: [] }));
  await page.route('**/api/v1/loan-applications/**', async route => {
    const pathname = new URL(route.request().url()).pathname;
    const method = route.request().method();
    if (pathname === '/api/v1/loan-applications/') return json(route, [application], pagination);
    if (method === 'GET') reads += 1;
    if (pathname.endsWith('/eligibility-assessment/')) return json(route, eligibility);
    if (pathname.endsWith('/loan-limit-assessment/')) return json(route, limit);
    if (pathname.endsWith('/sanction-case/')) return sanction ? json(route, sanction) : failure(route, 404, 'NOT_FOUND', 'No sanction case.');
    if (pathname.endsWith('/appraisal-note/')) {
      if (method === 'PATCH') patchBody = route.request().postDataJSON() as Record<string, unknown>;
      return json(route, appraisal(status, role));
    }
    if (pathname.endsWith('/submit-to-sanction-committee/')) { status = 'submitted_to_sanction_committee'; sanction = pendingCase; return json(route, sanction); }
    return failure(route, 400, 'VALIDATION_ERROR', 'Unexpected tracer request.');
  });
  await page.route('**/api/v1/appraisal-notes/**', route => {
    const pathname = new URL(route.request().url()).pathname;
    if (pathname.endsWith('/submit-for-review/')) status = 'review_pending';
    else if (pathname.endsWith('/review/')) status = 'reviewed';
    return json(route, appraisal(status, role));
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Appraisal' }).click();
  await expect(page.getByRole('button', { name: 'Record Credit Review' })).toHaveCount(0);
  const beforeSaveReads = reads;
  await page.getByRole('button', { name: 'Save Appraisal Draft' }).click();
  await expect.poll(() => reads - beforeSaveReads).toBe(4);
  expect(Object.keys(patchBody).sort()).toEqual(writableKeys);
  expect(Object.keys(patchBody.risk_assessment as Record<string, unknown>).sort()).toEqual(riskKeys);
  await page.getByRole('button', { name: 'Submit for Credit Review' }).click();
  await expect(page.getByText('review pending', { exact: true })).toBeVisible();

  role = 'credit_manager';
  await page.reload();
  await expect(page.getByRole('button', { name: 'Record Credit Review' })).toBeVisible();
  await page.getByLabel('Review comments').fill('Independent review complete.');
  await page.getByRole('button', { name: 'Record Credit Review' }).click();
  await expect(page.getByText('reviewed', { exact: true }).first()).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'epic-006-reviewed.png'), fullPage: true });

  await page.getByLabel('Sanction submission remarks').fill('Reviewed package ready for committee.');
  await page.getByRole('button', { name: 'Submit to Sanction Committee' }).click();
  await expect(page.getByText(`Case ${pendingCase.approval_case_id} · pending.`)).toBeVisible();
  await expect(page.getByText(pendingCase.approval_case_id, { exact: false })).toBeVisible();
  await page.screenshot({ path: path.join(evidenceDir, 'epic-006-pending-sanction.png'), fullPage: true });
});

const action = (action_code: string, enabled: boolean, required_permission: string, required_role: string | null = null) => ({ action_code, label: action_code === 'credit.appraisal.review' ? 'Record Credit Review' : action_code, enabled, disabled_reason: enabled ? null : 'Only an enabled resource action may be used.', required_permission, required_role });
const actions = (status: string, role: string) => [
  action('credit.appraisal.update', status === 'draft' && role === 'deputy_manager_finance', 'credit.appraisal.update'),
  action('credit.appraisal.submit_review', status === 'draft' && role === 'deputy_manager_finance', 'credit.appraisal.submit_review'),
  action('credit.appraisal.review', status === 'review_pending' && role === 'credit_manager', 'credit.appraisal.review', 'credit_manager'),
  action('credit.appraisal.submit_sanction', status === 'reviewed' && role === 'credit_manager', 'credit.appraisal.submit_sanction', 'credit_manager'),
];
const application = { loan_application_id: 'application-006x', application_reference_number: 'LO00000688', member: { member_id: 'member-006x', display_name: 'Epic 006 Tracer Member', member_type: 'individual_farmer', folio_number: 'FOL-006X' }, application_date: '2026-07-11', required_loan_amount: '15000.00', purpose_category: 'crop_production', application_status: 'reference_generated', current_stage: 'credit_assessment', completeness_status: 'complete' };
const eligibility = { eligibility_assessment_id: 'eligibility-006x', loan_application_id: application.loan_application_id, member_active_check: 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid', overall_result: 'eligible', assessment_notes: 'All mandatory checks passed.', assessed_by_user_id: 'finance-006x', assessed_at: '2026-07-11T10:00:00+05:30', available_actions: [] };
const limit = { loan_limit_assessment_id: 'limit-006x', loan_application_id: application.loan_application_id, member_id: 'member-006x', shareholding_id: 'share-006x', number_of_shares: 100, valuation_per_share: '2000.00', share_limit_percentage: '10.0000', per_share_cap_amount: '200.00', shareholding_based_limit_amount: '20000.00', land_area_acres: '5.00', scale_of_finance_per_acre_amount: '20000.00', land_based_limit_amount: '100000.00', final_eligible_loan_amount: '20000.00', requested_amount: '15000.00', amount_within_limit_flag: true, exception_required_flag: false, calculation_rule_version: 'loan-policy-v1.0', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-006x', policy_name: 'Board policy', board_approval_reference: 'BOARD/2026/006C' }, warnings: [], calculated_by_user_id: 'finance-006x', calculated_at: '2026-07-11T10:05:00+05:30', available_actions: [] };
const appraisal = (appraisal_status: string, role: string) => ({ loan_appraisal_note_id: 'appraisal-006x', loan_application_id: application.loan_application_id, eligibility_assessment_id: eligibility.eligibility_assessment_id, loan_limit_assessment_id: limit.loan_limit_assessment_id, eligibility_snapshot: eligibility, loan_limit_snapshot: limit, prerequisite_provenance: 'verified', prepared_by: { user_id: 'finance-006x', full_name: 'Deputy Manager Finance' }, prepared_at: '2026-07-11T10:10:00+05:30', reviewed_by: appraisal_status === 'reviewed' ? { user_id: 'manager-006x', full_name: 'Credit Manager' } : null, reviewed_at: appraisal_status === 'reviewed' ? '2026-07-11T10:20:00+05:30' : null, decision: appraisal_status === 'reviewed' ? 'reviewed' : null, review_comments: appraisal_status === 'reviewed' ? 'Independent review complete.' : null, review_history: appraisal_status === 'reviewed' ? [{ appraisal_review_decision_id: 'decision-006x', decision: 'reviewed', review_comments: 'Independent review complete.', reviewer: { user_id: 'manager-006x', full_name: 'Credit Manager' }, decided_at: '2026-07-11T10:20:00+05:30', from_state: 'review_pending', to_state: 'reviewed', history_provenance: 'native' }] : [], tat_due_at: '2026-07-13T10:10:00+05:30', tat_status: 'within_tat', borrower_summary: 'Verified member and complete application.', eligibility_summary: 'All stored eligibility checks passed.', loan_limit_summary: 'Requested amount is within the frozen limit.', recommended_amount: '15000.00', recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Existing verified security facts reviewed.', repayment_capacity_notes: 'Seasonal crop proceeds cover repayment.', risk_assessment: { risk_assessment_id: 'risk-006x', market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Monitor the stored crop cycle.' }, recommendation: 'approve', appraisal_status, available_actions: actions(appraisal_status, role) });
const pendingCase = { approval_case_id: 'case-006x', loan_application_id: application.loan_application_id, loan_appraisal_note_id: 'appraisal-006x', application_status: 'submitted_to_sanction_committee', appraisal_status: 'submitted_to_sanction_committee', appraisal_review_decision_id: 'decision-006x', workflow_event_id: 'workflow-006x', submission_status: 'pending', exception_required_flag: false, submitted_by: { user_id: 'manager-006x', full_name: 'Credit Manager' }, submitted_at: '2026-07-11T10:25:00+05:30', available_actions: [] };
const permissions = ['applications.loan_application.read', 'credit.appraisal.create', 'credit.appraisal.update', 'credit.appraisal.submit_review', 'credit.appraisal.review', 'credit.appraisal.submit_sanction', 'credit.risk_assessment.manage'];
const user = (role: string) => ({ user_id: `${role}-006x`, full_name: role === 'credit_manager' ? 'Credit Manager' : 'Deputy Manager Finance', email: `${role}@sfpcl.example`, status: 'active', roles: [{ role_code: role, role_name: role }], teams: [], role_codes: [role], team_codes: [], permissions, available_actions: [] });
const writableKeys = ['borrower_summary', 'eligibility_summary', 'loan_limit_summary', 'recommendation', 'recommended_amount', 'recommended_interest_type', 'recommended_security_summary', 'recommended_tenure_months', 'repayment_capacity_notes', 'risk_assessment'].sort();
const riskKeys = ['borrower_risk_rating', 'market_risk_rating', 'operational_risk_rating', 'overall_risk_rating', 'risk_mitigation_notes'].sort();
const pagination = { pagination: { page: 1, page_size: 100, total_count: 1, total_pages: 1, has_next: false, has_previous: false } };
const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...extra }) });
const failure = (route: Route, status: number, code: string, message: string) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message } }) });
