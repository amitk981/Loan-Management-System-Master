import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Request, type Route, type TestInfo } from '@playwright/test';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for Epic 006 closure');
fs.mkdirSync(evidenceDir, { recursive: true });

const FINANCE_EMAIL = 'e2e.credit.finance@sfpcl.example';
const MANAGER_EMAIL = 'e2e.credit.manager@sfpcl.example';
const APPLICATION_ID = '00000000-0000-4000-8000-000000000601';
const SHAREHOLDING_ID = '00000000-0000-4000-8000-000000000604';
const LAND_ID = '00000000-0000-4000-8000-000000000605';
const CROP_ID = '00000000-0000-4000-8000-000000000606';
const API_ORIGIN = 'http://127.0.0.1:8000';
const READ_SUFFIXES = ['/eligibility-assessment/', '/loan-limit-assessment/', '/appraisal-note/', '/sanction-case/'];

test('appraisal workbench preserves the staged prototype across the required state matrix', async ({ page }, testInfo) => {
  let mode: 'matrix' | 'empty' | 'denied' | 'error' | 'validation' = 'matrix';
  let releaseApplications: (() => void) | undefined;
  const applicationsReleased = new Promise<void>(resolve => { releaseApplications = resolve; });
  let holdApplications = true;

  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'appraisal-access', refreshToken: 'appraisal-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, visualCurrentUser));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'credit_manager', cards: [], tasks: [] }));
  await page.route('**/api/v1/loan-applications/**', async route => {
    const pathname = new URL(route.request().url()).pathname;
    const method = route.request().method();
    if (pathname === '/api/v1/loan-applications/') {
      if (holdApplications) await applicationsReleased;
      const items = mode === 'empty' ? [] : visualApplications;
      return json(route, items, pagination(items.length));
    }
    const id = visualApplications.find(item => pathname.includes(item.loan_application_id))?.loan_application_id ?? 'eligible';
    if (mode === 'denied') return failure(route, 403, 'OBJECT_ACCESS_DENIED', 'You cannot access this appraisal.');
    if (mode === 'error') return failure(route, 500, 'SERVICE_UNAVAILABLE', 'Appraisal service unavailable for visual proof.');
    if (mode === 'validation' && method === 'PATCH' && pathname.endsWith('/appraisal-note/')) return failure(route, 400, 'VALIDATION_ERROR', 'Recommended amount is required.', { recommended_amount: 'This field is required.' });
    if (pathname.endsWith('/eligibility-assessment/')) return json(route, visualEligibility(id));
    if (pathname.endsWith('/loan-limit-assessment/')) return json(route, visualLimit(id));
    if (pathname.endsWith('/appraisal-note/')) return visualAppraisalIds.has(id) ? json(route, visualAppraisal(id)) : failure(route, 404, 'NOT_FOUND', 'No appraisal note.');
    if (pathname.endsWith('/sanction-case/')) return id === 'submitted' ? json(route, visualSanction) : failure(route, 404, 'NOT_FOUND', 'No sanction case.');
    return failure(route, 400, 'VALIDATION_ERROR', 'Unexpected visual request.');
  });

  await page.goto('/');
  await openAppraisal(page);
  await expect(page.getByText('Loading appraisal workbench')).toBeVisible();
  await captureBaseline(page, testInfo, 'loading');
  holdApplications = false;
  releaseApplications?.();
  await expect(page.getByRole('heading', { name: 'Appraisal Workbench' })).toBeVisible();
  await captureBaseline(page, testInfo, 'queue');

  for (const id of visualStates) {
    await page.getByRole('button', { name: new RegExp(`Visual ${title(id)} Borrower`) }).click();
    await expect(page.getByRole('heading', { name: 'Appraisal Workbench' })).toBeVisible();
    await captureBaseline(page, testInfo, id);
  }

  mode = 'empty';
  await reloadAppraisal(page);
  await expect(page.getByText('Appraisal queue is clear')).toBeVisible();
  await captureBaseline(page, testInfo, 'empty');

  mode = 'denied';
  await reloadAppraisal(page);
  await expect(page.getByText(/cannot access this appraisal/i)).toBeVisible();
  await captureBaseline(page, testInfo, 'denied');

  mode = 'matrix';
  await reloadAppraisal(page);
  await page.getByRole('button', { name: /Visual Draft Borrower/ }).click();
  mode = 'validation';
  await page.getByRole('button', { name: 'Save Appraisal Draft' }).click();
  await expect(page.getByText(/recommended_amount: This field is required/)).toBeVisible();
  await captureBaseline(page, testInfo, 'validation');

  mode = 'error';
  await reloadAppraisal(page);
  await expect(page.getByText(/Appraisal service unavailable/)).toBeVisible();
  await captureBaseline(page, testInfo, 'api-error');
});

test('real Django and two real finance roles reach exactly one pending sanction case', async ({ page }) => {
  const http = observeApi(page);
  await staffLogin(page, FINANCE_EMAIL, E2E_PASSWORD);
  await openAppraisal(page);
  await expect(page.getByRole('heading', { name: 'LOE2E00601' })).toBeVisible();

  const initialEligibility = await latestData(http.records, '/eligibility-assessment/');
  expectAction(initialEligibility, action('credit.eligibility.run', 'Run Eligibility Assessment', true, null));
  expectAction(initialEligibility, action('credit.loan_limit.calculate', 'Calculate Loan Limit', false, null, 'Loan-limit calculation requires eligibility overall_result eligible.'));
  await expect(page.getByRole('button', { name: 'Calculate Stored Loan Limit' })).toHaveCount(0);

  const eligibilityWrite = await mutateAndRefresh(page, http.records, 'Run Eligibility Assessment', 'POST', '/eligibility-assessment/run/');
  expect(eligibilityWrite.data.overall_result).toBe('eligible');
  const eligibilityId = String(eligibilityWrite.data.eligibility_assessment_id);

  await page.getByText('Step 2', { exact: true }).click();
  expectAction(await latestData(http.records, '/eligibility-assessment/'), action('credit.loan_limit.calculate', 'Calculate Loan Limit', true, null));
  await page.getByLabel('Shareholding ID').fill(SHAREHOLDING_ID);
  await page.getByLabel('Land holding IDs (comma separated)').fill(LAND_ID);
  await page.getByLabel('Crop plan ID').fill(CROP_ID);
  await page.getByLabel('Requested amount').fill('15000.00');
  await page.getByLabel('Calculation date').fill('2026-07-11');
  const limitWrite = await mutateAndRefresh(page, http.records, 'Calculate Stored Loan Limit', 'POST', '/loan-limit-assessment/calculate/');
  expect(limitWrite.requestBody).toEqual({ shareholding_id: SHAREHOLDING_ID, land_holding_ids: [LAND_ID], crop_plan_id: CROP_ID, requested_amount: '15000.00', calculation_date: '2026-07-11' });
  expect(limitWrite.data.amount_within_limit_flag).toBe(true);
  const limitId = String(limitWrite.data.loan_limit_assessment_id);

  expectAction(await latestData(http.records, '/loan-limit-assessment/'), action('credit.appraisal.create', 'Create Appraisal Draft', true, null));
  await fillAppraisal(page);
  const createWrite = await mutateAndRefresh(page, http.records, 'Create Appraisal Draft', 'POST', '/appraisal-note/');
  expectWritableBody(createWrite.requestBody);
  expect(createWrite.data.eligibility_assessment_id).toBe(eligibilityId);
  expect(createWrite.data.loan_limit_assessment_id).toBe(limitId);
  const appraisalId = String(createWrite.data.loan_appraisal_note_id);

  expectAction(await latestData(http.records, '/appraisal-note/'), action('credit.appraisal.update', 'Update Appraisal Draft', true, null));
  const patchWrite = await mutateAndRefresh(page, http.records, 'Save Appraisal Draft', 'PATCH', '/appraisal-note/');
  expectWritableBody(patchWrite.requestBody);
  expectAction(await latestData(http.records, '/appraisal-note/'), action('credit.appraisal.submit_review', 'Submit for Credit Review', true, null));
  await page.getByLabel('Submission remarks').fill('Ready for independent review.');
  await mutateAndRefresh(page, http.records, 'Submit for Credit Review', 'POST', `/appraisal-notes/${appraisalId}/submit-for-review/`);

  await switchStaffUser(page, MANAGER_EMAIL);
  const managerReadStart = http.records.length;
  await openAppraisal(page);
  const managerMe = await latestData(http.records, '/auth/me/');
  expect(managerMe.permissions).toContain('credit.appraisal.submit_sanction');
  const reviewPending = await latestData(http.records, '/appraisal-note/', managerReadStart);
  expectAction(reviewPending, action('credit.appraisal.review', 'Record Credit Review', true, 'credit_manager'));
  expectAction(reviewPending, action('credit.appraisal.submit_sanction', 'Submit to Sanction Committee', false, 'credit_manager', 'Only a reviewed appraisal note can be submitted for sanction.'));
  await expect(page.getByRole('button', { name: 'Submit to Sanction Committee' })).toHaveCount(0);

  await page.getByLabel('Review comments').fill('Independent review complete.');
  const reviewWrite = await mutateAndRefresh(page, http.records, 'Record Credit Review', 'POST', `/appraisal-notes/${appraisalId}/review/`);
  const decisionId = String(reviewWrite.data.review_history.at(-1)?.appraisal_review_decision_id);
  expect(decisionId).not.toBe('undefined');
  await captureEvidence(page, 'epic-006-reviewed.png');

  expectAction(await latestData(http.records, '/appraisal-note/'), action('credit.appraisal.submit_sanction', 'Submit to Sanction Committee', true, 'credit_manager'));
  await page.getByLabel('Sanction submission remarks').fill('Reviewed package ready for committee.');
  const sanctionWrite = await mutateAndRefresh(page, http.records, 'Submit to Sanction Committee', 'POST', '/submit-to-sanction-committee/');
  const pendingCase = sanctionWrite.data;
  expect(pendingCase).toMatchObject({ loan_application_id: APPLICATION_ID, loan_appraisal_note_id: appraisalId, appraisal_review_decision_id: decisionId, submission_status: 'pending', application_status: 'submitted_to_sanction_committee', appraisal_status: 'submitted_to_sanction_committee', exception_required_flag: false });
  expect(pendingCase.workflow_event_id).toEqual(expect.any(String));
  await captureEvidence(page, 'epic-006-pending-sanction.png');

  await reloadAppraisal(page);
  await expect(page.getByText(`Pending case ${pendingCase.approval_case_id} retained`)).toBeVisible();
  expect(await latestData(http.records, '/sanction-case/')).toEqual(pendingCase);
  await expect(page.getByRole('button', { name: 'Submit to Sanction Committee' })).toHaveCount(0);
  const beforeConflictReads = readCount(http.records);
  const repeat = await browserPost(page, `/api/v1/loan-applications/${APPLICATION_ID}/submit-to-sanction-committee/`, { remarks: 'Must remain one pending case.' });
  expect(repeat.status).toBe(409);
  expect(repeat.body.error.code).toBe('INVALID_STATE_TRANSITION');
  expect(readCount(http.records)).toBe(beforeConflictReads);
  await expect.poll(() => http.records.filter(record => record.status === 409 && record.pathname.endsWith('/submit-to-sanction-committee/')).length).toBe(1);

  fs.writeFileSync(path.join(evidenceDir, 'epic-006-http-transcript.json'), JSON.stringify({
    application_id: APPLICATION_ID, eligibility_assessment_id: eligibilityId,
    loan_limit_assessment_id: limitId, loan_appraisal_note_id: appraisalId,
    appraisal_review_decision_id: decisionId, approval_case_id: pendingCase.approval_case_id,
    workflow_event_id: pendingCase.workflow_event_id,
    writes: http.records.filter(record => record.method !== 'GET').map(record => ({ method: record.method, pathname: record.pathname, status: record.status })),
  }, null, 2));
});

type ApiData = Record<string, any>;
type HttpRecord = { method: string; pathname: string; requestBody: unknown; status?: number; data?: ApiData };

function observeApi(page: Page) {
  const records: HttpRecord[] = [];
  const requests = new Map<Request, HttpRecord>();
  page.on('request', request => {
    const pathname = new URL(request.url()).pathname;
    if (!pathname.startsWith('/api/v1/')) return;
    let requestBody: unknown;
    try { requestBody = request.postDataJSON(); } catch { requestBody = undefined; }
    const record = { method: request.method(), pathname, requestBody };
    records.push(record); requests.set(request, record);
  });
  page.on('response', async response => {
    const record = requests.get(response.request()); if (!record) return;
    record.status = response.status();
    try { const body = await response.json(); if (body?.success) record.data = body.data; } catch { /* transcript ignores non-JSON */ }
  });
  return { records };
}

async function latestData(records: HttpRecord[], suffix: string, start = 0) {
  const latest = () => [...records.slice(start)].reverse().find(record => record.method === 'GET' && record.pathname.endsWith(suffix));
  await expect.poll(() => latest()?.data).toBeTruthy();
  return latest()!.data!;
}

const readCount = (records: HttpRecord[]) => records.filter(record => record.method === 'GET' && READ_SUFFIXES.some(suffix => record.pathname.endsWith(suffix))).length;
async function mutateAndRefresh(page: Page, records: HttpRecord[], button: string, method: string, suffix: string) {
  const start = records.length;
  await page.getByRole('button', { name: button, exact: true }).click();
  await expect.poll(() => records.slice(start).find(record => record.method === method && record.pathname.endsWith(suffix))?.status).toBe(200);
  await expect.poll(() => readCount(records.slice(start))).toBe(4);
  const reads = records.slice(start).filter(record => record.method === 'GET' && READ_SUFFIXES.some(item => record.pathname.endsWith(item)));
  expect(reads.map(record => READ_SUFFIXES.find(item => record.pathname.endsWith(item))).sort()).toEqual([...READ_SUFFIXES].sort());
  return records.slice(start).find(record => record.method === method && record.pathname.endsWith(suffix))!;
}

const permissionFor = (code: string) => code;
const action = (action_code: string, label: string, enabled: boolean, required_role: string | null, disabled_reason: string | null = enabled ? null : 'Unavailable for this canonical application state.') => ({ action_code, label, enabled, disabled_reason, required_permission: permissionFor(action_code), required_role });
function expectAction(resource: ApiData, expected: Record<string, unknown>) {
  const value = resource.available_actions?.find((item: ApiData) => item.action_code === expected.action_code);
  expect(value).toEqual(expected);
  expect(Object.keys(value).sort()).toEqual(['action_code', 'disabled_reason', 'enabled', 'label', 'required_permission', 'required_role']);
}

function expectWritableBody(body: unknown) {
  const value = body as ApiData;
  expect(Object.keys(value).sort()).toEqual(['borrower_summary', 'eligibility_summary', 'loan_limit_summary', 'recommendation', 'recommended_amount', 'recommended_interest_type', 'recommended_security_summary', 'recommended_tenure_months', 'repayment_capacity_notes', 'risk_assessment'].sort());
  expect(Object.keys(value.risk_assessment).sort()).toEqual(['borrower_risk_rating', 'market_risk_rating', 'operational_risk_rating', 'overall_risk_rating', 'risk_mitigation_notes'].sort());
}

async function fillAppraisal(page: Page) {
  await page.getByLabel('Borrower summary').fill('Verified synthetic member and complete application.');
  await page.getByLabel('Eligibility summary').fill('All stored eligibility checks passed.');
  await page.getByLabel('Loan-limit summary').fill('Requested amount is within the frozen limit.');
  await page.getByLabel('Repayment capacity notes').fill('Synthetic crop proceeds cover repayment.');
  await page.getByLabel('Recommended amount').fill('15000.00');
  await page.getByLabel('Recommended tenure (months)').fill('12');
  await page.getByLabel('Interest type').fill('floating');
  await page.getByLabel('Recommended security').fill('Existing verified synthetic security facts.');
  await page.getByLabel('Recommendation').selectOption('approve');
  for (const label of ['Market risk', 'Operational risk', 'Borrower risk', 'Overall risk']) await page.getByLabel(label).selectOption('low');
  await page.getByLabel('Risk mitigation notes').fill('Monitor the stored synthetic crop cycle.');
}

async function openAppraisal(page: Page) {
  await page.getByRole('button', { name: /^Appraisal(?:\s+\d+)?$/ }).click();
}
async function reloadAppraisal(page: Page) { await page.reload(); await openAppraisal(page); }
async function switchStaffUser(page: Page, email: string) {
  await page.evaluate(() => localStorage.removeItem('sfpcl_staff_auth_session'));
  await page.context().clearCookies(); await staffLogin(page, email, E2E_PASSWORD);
}
async function browserPost(page: Page, pathname: string, body: Record<string, unknown>) {
  return page.evaluate(async ({ origin, pathname: target, payload }) => {
    const raw = localStorage.getItem('sfpcl_staff_auth_session');
    const accessToken = raw ? JSON.parse(raw).accessToken : '';
    const response = await fetch(`${origin}${target}`, { method: 'POST', headers: { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    return { status: response.status, body: await response.json() };
  }, { origin: API_ORIGIN, pathname, payload: body });
}

async function captureBaseline(page: Page, testInfo: TestInfo, name: string) {
  const png = testInfo.snapshotPath(`appraisal-${name}.png`);
  const encoded = `${png}.base64`;
  if (!fs.existsSync(png) && fs.existsSync(encoded)) fs.writeFileSync(png, Buffer.from(fs.readFileSync(encoded, 'utf8'), 'base64'));
  if (!fs.existsSync(png)) {
    fs.mkdirSync(path.dirname(png), { recursive: true });
    await page.screenshot({ path: png, fullPage: true, animations: 'disabled' });
    fs.writeFileSync(encoded, fs.readFileSync(png).toString('base64'));
  }
  await captureEvidence(page, `appraisal-${name}.png`);
  await expect(page).toHaveScreenshot(`appraisal-${name}.png`, { fullPage: true, animations: 'disabled' });
  fs.rmSync(png);
}
const captureEvidence = (page: Page, name: string) => page.screenshot({ path: path.join(evidenceDir, name), fullPage: true, animations: 'disabled' });

const visualStates = ['eligible', 'ineligible', 'pending', 'below', 'equal', 'above', 'draft', 'returned', 'review-pending', 'reviewed', 'rejected', 'submitted'];
function title(value: string) { return value.replace(/-/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase()); }
const visualApplications = visualStates.map((id, index) => ({
  loan_application_id: id, application_reference_number: `LO00010${String(index).padStart(2, '0')}`,
  member: { member_id: `member-${id}`, display_name: `Visual ${title(id)} Borrower`, member_type: 'individual_farmer', folio_number: `FOL-${index}` },
  application_date: '2026-07-10', required_loan_amount: id === 'above' ? '300000.00' : id === 'below' ? '200000.00' : '250000.00',
  purpose_category: 'crop_production', application_status: id === 'submitted' ? 'submitted_to_sanction_committee' : 'reference_generated', current_stage: 'credit_assessment', completeness_status: 'complete',
}));
const visualAppraisalIds = new Set(['draft', 'returned', 'review-pending', 'reviewed', 'rejected', 'submitted']);
const visualAction = (action_code: string, label: string, enabled: boolean, required_permission: string, required_role: string | null = null) => ({ action_code, label, enabled, disabled_reason: enabled ? null : 'Unavailable for this canonical application state.', required_permission, required_role });
const visualActions = (id = '') => [
  visualAction('credit.appraisal.update', 'Save Appraisal Draft', id === 'draft' || id === 'returned', 'credit.appraisal.update'),
  visualAction('credit.appraisal.review', 'Record Credit Review', id === 'review-pending', 'credit.appraisal.review', 'credit_manager'),
  visualAction('credit.appraisal.submit_sanction', 'Submit to Sanction Committee', id === 'reviewed', 'credit.appraisal.submit_sanction', 'credit_manager'),
];
const visualEligibility = (id: string) => ({
  eligibility_assessment_id: `eligibility-${id}`, loan_application_id: id,
  member_active_check: id === 'ineligible' ? 'fail' : id === 'pending' ? 'pending' : 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid',
  overall_result: id === 'ineligible' ? 'ineligible' : id === 'pending' ? 'pending_manual_evidence' : 'eligible', assessment_notes: `Stored ${id} assessment explanation.`, assessed_by_user_id: 'staff-1', assessed_at: '2026-07-10T10:00:00+05:30', available_actions: [],
});
const visualLimit = (id: string) => {
  const requested = id === 'below' ? '200000.00' : id === 'above' ? '300000.00' : '250000.00'; const within = id !== 'above';
  return { loan_limit_assessment_id: `limit-${id}`, loan_application_id: id, member_id: `member-${id}`, shareholding_id: 'share-1', number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00', shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00', land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: requested, amount_within_limit_flag: within, exception_required_flag: !within, calculation_rule_version: 'board-policy-2026', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' }, warnings: within ? [] : [{ code: 'LIMIT_EXCEEDED', message: 'Requested amount exceeds the stored eligible limit.' }], calculated_by_user_id: 'staff-1', calculated_at: '2026-07-10T10:05:00+05:30', available_actions: [] };
};
const visualAppraisal = (id: string) => {
  const status = id === 'returned' || id === 'draft' ? 'draft' : id === 'review-pending' ? 'review_pending' : id;
  return { loan_appraisal_note_id: `appraisal-${id}`, loan_application_id: id, eligibility_assessment_id: `eligibility-${id}`, loan_limit_assessment_id: `limit-${id}`, eligibility_snapshot: visualEligibility(id), loan_limit_snapshot: visualLimit(id), prerequisite_provenance: 'verified', prepared_by: { user_id: 'staff-1', full_name: 'Deputy Manager Finance' }, prepared_at: '2026-07-10T10:10:00+05:30', reviewed_by: null, reviewed_at: null, decision: null, review_comments: null, review_history: id === 'returned' ? [{ appraisal_review_decision_id: 'history-1', decision: 'returned', review_comments: 'Add repayment evidence.', reviewer: { user_id: 'manager-1', full_name: 'Credit Manager' }, decided_at: '2026-07-10T11:00:00+05:30', from_state: 'review_pending', to_state: 'draft', history_provenance: 'native' }] : [], tat_due_at: '2026-07-12T10:10:00+05:30', tat_status: 'within_tat', borrower_summary: 'API-backed borrower summary.', eligibility_summary: 'Stored assessment is eligible.', loan_limit_summary: 'Stored limit reviewed.', recommended_amount: '250000.00', recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Stored security recommendation.', repayment_capacity_notes: 'Stored repayment capacity.', risk_assessment: { risk_assessment_id: 'risk-1', market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Stored mitigations.' }, recommendation: 'approve', appraisal_status: status === 'submitted' ? 'submitted_to_sanction_committee' : status, ...(id === 'rejected' ? { rejection_note: { rejection_note_id: 'reject-1', note_status: 'approved', rejection_reason_category: 'eligibility', reapply_allowed_flag: true, communication_mode: 'email' } } : {}), available_actions: visualActions(id) };
};
const visualSanction = { approval_case_id: 'case-006H3', loan_application_id: 'submitted', loan_appraisal_note_id: 'appraisal-submitted', application_status: 'submitted_to_sanction_committee', appraisal_status: 'submitted_to_sanction_committee', submission_status: 'pending', exception_required_flag: false, submitted_by: { user_id: 'manager-1', full_name: 'Credit Manager' }, submitted_at: '2026-07-10T12:00:00+05:30', available_actions: [] };
const visualCurrentUser = { user_id: 'manager-1', full_name: 'Credit Manager', email: 'manager@sfpcl.example', status: 'active', roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }], teams: [], role_codes: ['credit_manager'], team_codes: [], permissions: ['do_appraisal', 'credit.eligibility.run', 'credit.loan_limit.calculate', 'credit.appraisal.create', 'credit.appraisal.update', 'credit.appraisal.submit_review', 'credit.appraisal.review', 'credit.appraisal.submit_sanction', 'credit.risk_assessment.manage'], available_actions: [] };
const pagination = (count: number) => ({ pagination: { page: 1, page_size: 100, total_count: count, total_pages: count ? 1 : 0, has_next: false, has_previous: false } });
const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, ...extra }) });
const failure = (route: Route, status: number, code: string, message: string, field_errors?: Record<string, string>) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message, field_errors } }) });
