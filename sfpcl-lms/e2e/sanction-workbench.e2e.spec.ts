import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for sanction workbench visual acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('sanction workbench preserves the prototype composition across authoritative states', async ({ page }) => {
  let mode: 'pending' | 'approved' | 'rejected' | 'returned_for_clarification' | 'empty' | 'denied' | 'error' | 'malformed' = 'pending';
  let currentCases = [caseFor('pending')];
  let release: (() => void) | undefined;
  let delayPendingPage = false;
  let releaseDelayedPending: (() => void) | undefined;
  let delayedActionCaseId: string | undefined;
  let releaseDelayedActionDetail: (() => void) | undefined;
  let hold = true;
  const waiting = new Promise<void>(resolve => { release = resolve; });
  const observedApiPaths: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.startsWith('/api/v1/')) observedApiPaths.push(url.pathname);
  });

  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'sanction-access', refreshToken: 'sanction-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'cfo', cards: [], tasks: [] }));
  await page.route('**/api/v1/loan-applications/*/sanction-decision/', route => json(route, sanctionDecision));
  await page.route('**/api/v1/approval-cases/**', async route => {
    const url = new URL(route.request().url());
    if (route.request().method() === 'POST' && /\/approve\/$/.test(url.pathname)) {
      delayedActionCaseId = url.pathname.split('/').filter(Boolean).at(-2);
      const acted = currentCases.find(item => item.approval_case_id === delayedActionCaseId) ?? currentCases[0];
      return json(route, { ...acted, current_status: 'approved', available_actions: [] });
    }
    if (url.pathname === '/api/v1/approval-cases/') {
      const requestMode = mode;
      expect(url.searchParams.get('approval_type')).toBe('sanction');
      expect(url.searchParams.get('page_size')).toBe('20');
      expect(url.searchParams.get('page')).toMatch(/^\d+$/);
      if (requestMode === 'pending' || requestMode === 'denied') {
        expect(url.searchParams.get('current_status')).toBe('pending');
        expect(url.searchParams.get('assigned_to_me')).toBe('true');
      } else if (requestMode === 'approved' || requestMode === 'rejected' || requestMode === 'returned_for_clarification' || requestMode === 'malformed') {
        const expectedStatus = requestMode === 'malformed' ? 'approved' : requestMode;
        expect(url.searchParams.get('current_status')).toBe(expectedStatus);
        expect(url.searchParams.has('assigned_to_me')).toBe(false);
      } else {
        expect(url.searchParams.has('current_status')).toBe(false);
        expect(url.searchParams.has('assigned_to_me')).toBe(false);
      }
      if (hold) await waiting;
      if (requestMode === 'denied') return failure(route, 403, 'OBJECT_ACCESS_DENIED', 'You cannot access this approval case.');
      if (requestMode === 'error') return failure(route, 500, 'SERVICE_UNAVAILABLE', 'Approval-case service unavailable.');
      if (requestMode === 'malformed') return json(route, []);
      const requestedPage = Number(url.searchParams.get('page'));
      if (requestMode === 'empty') return paginated(route, [], requestedPage, 0);
      const total = requestMode === 'pending' ? 121 : requestMode === 'approved' ? 25 : 1;
      const pageSize = requestedPage < Math.ceil(total / 20) ? 20 : total - ((requestedPage - 1) * 20);
      const responseCases = Array.from({ length: pageSize }, (_, index) => caseFor(requestMode, requestedPage, index + 1));
      if (delayPendingPage && requestMode === 'pending') {
        await new Promise<void>(resolve => {
          releaseDelayedPending = () => {
            currentCases = responseCases;
            void paginated(route, responseCases, requestedPage, total);
            resolve();
          };
        });
        return;
      }
      currentCases = responseCases;
      return paginated(route, currentCases, requestedPage, total);
    }
    const caseId = url.pathname.split('/').filter(Boolean).at(-1);
    if (caseId === delayedActionCaseId) {
      const staleActionDetail = {
        ...(currentCases.find(item => item.approval_case_id === caseId) ?? caseFor('pending')),
        current_status: 'approved',
        review_facts: { ...caseFor('pending').review_facts, borrowing_history: 'Stale browser action refresh.' },
        available_actions: [],
      };
      await new Promise<void>(resolve => {
        releaseDelayedActionDetail = () => {
          void json(route, staleActionDetail);
          resolve();
        };
      });
      delayedActionCaseId = undefined;
      return;
    }
    return json(route, currentCases.find(item => item.approval_case_id === caseId) ?? currentCases[0]);
  });

  await page.goto('/');
  await page.getByRole('button', { name: /^Sanction(?:\s+\d+)?$/ }).click();
  await expect(page.getByText('Loading sanction workbench')).toBeVisible();
  hold = false; release?.();
  await expect(page.getByRole('heading', { name: 'LOVIS0101' })).toBeVisible();
  await expect(page.getByText('Approved frozen package.')).toBeVisible();
  await expect(page.getByText('Confirmed at 2026-07-13T10:00:00Z')).toBeVisible();
  await expect(page.getByText('121 cases from the approval-case service')).toBeVisible();
  await expect(page.getByText('Page 1 of 7')).toBeVisible();
  await capture(page, 'pending-special-conflict');

  await page.getByRole('button', { name: 'Record My Decision' }).click();
  await page.getByLabel('Decision reason').fill('Approved before changing the browser filter.');
  await page.getByRole('button', { name: 'Confirm Decision' }).click();
  await expect.poll(() => Boolean(releaseDelayedActionDetail)).toBe(true);
  mode = 'approved';
  await page.getByLabel('Sanction case status').selectOption('approved');
  await expect(page.getByText('25 cases from the approval-case service')).toBeVisible();
  await expect(page.getByText('Page 1 of 2')).toBeVisible();
  releaseDelayedActionDetail?.();
  await expect(page.getByText('25 cases from the approval-case service')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'LOVIS0101' })).toBeVisible();
  await expect(page.getByText('Stale browser action refresh.')).toHaveCount(0);
  await capture(page, 'action-filter-race');

  mode = 'pending';
  await page.getByLabel('Sanction case status').selectOption('pending');
  await expect(page.getByText('121 cases from the approval-case service')).toBeVisible();
  await expect(page.getByText('Page 1 of 7')).toBeVisible();

  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByText('Page 2 of 7')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'LOVIS0201' })).toBeVisible();

  delayPendingPage = true;
  await page.getByRole('button', { name: 'Previous' }).click();
  await expect.poll(() => Boolean(releaseDelayedPending)).toBe(true);
  mode = 'approved'; delayPendingPage = false;
  await page.getByLabel('Sanction case status').selectOption('approved');
  await expect(page.getByText('25 cases from the approval-case service')).toBeVisible();
  await expect(page.getByText('Page 1 of 2')).toBeVisible();
  releaseDelayedPending?.();
  await expect(page.getByText('25 cases from the approval-case service')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'LOVIS0101' })).toBeVisible();
  await expect(page.getByText('Page 1 of 2')).toBeVisible();
  await capture(page, 'paginated-filtered-queue');
  await capture(page, 'approved');

  for (const [value, name] of [['rejected', 'rejected'], ['returned_for_clarification', 'returned']] as const) {
    mode = value;
    await page.getByLabel('Sanction case status').selectOption(value);
    await expect(page.getByRole('heading', { name: 'LOVIS0101' })).toBeVisible();
    await capture(page, name);
  }

  mode = 'empty';
  await page.getByLabel('Sanction case status').selectOption('all');
  await expect(page.getByText('Sanction queue is clear')).toBeVisible();
  await capture(page, 'empty');

  mode = 'denied';
  await page.getByLabel('Sanction case status').selectOption('pending');
  await expect(page.getByText('Sanction access denied')).toBeVisible();
  await capture(page, 'denied');

  mode = 'error';
  await page.getByLabel('Sanction case status').selectOption('all');
  await expect(page.getByText(/Approval-case service unavailable/)).toBeVisible();
  await capture(page, 'error');

  mode = 'malformed';
  await page.getByLabel('Sanction case status').selectOption('approved');
  await expect(page.getByText(/invalid paginated response/)).toBeVisible();

  expect(observedApiPaths.some(pathname => pathname.includes('appraisal-note'))).toBe(false);
  expect(observedApiPaths.some(pathname => pathname.includes('loan-policy'))).toBe(false);
});

const caseFor = (status: 'pending' | 'approved' | 'rejected' | 'returned_for_clarification', page = 1, index = 1) => ({
  approval_case_id: `case-visual-${status}-${page}-${index}`, cycle_number: status === 'returned_for_clarification' ? 1 : 2,
  approval_type: 'sanction', related_entity_type: 'loan_application', related_entity_id: 'application-visual-007', loan_application_id: 'application-visual-007',
  application_reference_number: `LOVIS${String(page).padStart(2, '0')}${String(index).padStart(2, '0')}`, amount: '675000.00', current_status: status, decision_date: '2026-07-13', version: 6,
  approval_matrix_rule_id: 'rule-visual', approval_matrix_rule_version: 4, sanction_committee_id: 'committee-visual', sanction_committee_version: 3,
  route_approvers: [approver('cfo', 'cfo-visual', 'Visual CFO'), approver('director', 'director-conflict', 'Conflicted Director'), approver('director', 'director-visual', 'Visual Director')],
  required_approvers: [
    { ...approver('cfo', 'cfo-visual', 'Visual CFO'), decision: 'approved', acted_at: '2026-07-13T10:00:00Z' },
    { ...approver('director', 'director-visual', 'Visual Director'), decision: status === 'pending' ? null : status === 'approved' ? 'approved' : status === 'rejected' ? 'rejected' : 'returned_for_clarification', acted_at: status === 'pending' ? null : '2026-07-13T11:00:00Z', replacement_for_user_id: 'director-conflict' },
  ],
  approval_actions: [{ approval_action_id: 'action-cfo', ...approver('cfo', 'cfo-visual', 'Visual CFO'), decision: 'approved', comments: 'Approved frozen package.', acted_at: '2026-07-13T10:00:00Z' }],
  excluded_approvers: [{ user_id: 'director-conflict', conflict_code: 'director_relative', reason: 'Borrower is a relative of the routed Director.' }],
  general_meeting_evidence_required: true,
  general_meeting_approval: { general_meeting_approval_id: 'meeting-visual', loan_application_id: 'application-visual-007', related_party_type: 'director_relative', related_party_user_id: 'director-conflict', relationship_description: 'Borrower is a relative of a Director.', meeting_date: '2026-07-12', notice_document_id: 'notice-visual', minutes_document_id: 'minutes-visual', resolution_document_id: 'resolution-visual', approval_status: 'approved', recorded_by_user_id: 'secretary-visual', recorded_at: '2026-07-12T12:00:00Z', supersedes_general_meeting_approval_id: null, evidence_scope: status === 'pending' ? 'current_pending' : 'cycle_frozen' },
  conflict_block_reason: null, reason_for_approval: 'Credit review recommends the requested exception.', exception_condition_code: 'exceeds_permissible_limit', exception_reason: 'Seasonal working-capital need exceeds the verified limit.',
  matrix_projection: { required_director_count: 2, authority_summary: 'CFO + two Directors — exception route' }, committee_projection: {}, loan_limit_provenance: { policy_name: 'Board Loan Policy FY 2026' },
  review_facts: { maker_checker: {}, eligibility: { overall_result: 'eligible' }, loan_amounts: { requested_amount: '700000.00', eligible_amount: '625000.00', recommended_amount: '675000.00' }, purpose: { category: 'crop_production', description: 'Kharif crop production and procurement.' }, compliance_checks: { member_active_check: 'pass', default_check: 'no_default', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned' }, borrowing_history: 'Prior seasonal loan repaid on schedule.', risk: { overall_risk_rating: 'medium', risk_mitigation_notes: 'Crop insurance and receivable controls verified.' }, documentation_completeness: { status: 'complete', document_check: 'complete' }, source_references: {} },
  workbench_summary: {
    borrower_name: 'Visual Farmer Member', member_type: 'individual_farmer',
    requested_amount: '700000.00', recommended_amount: '675000.00', eligible_amount: '625000.00',
    approval_path: 'CFO + 2 Directors — special approval', exception_flag: true, related_party_flag: true,
    risk_rating: 'medium', submitted_at: '2026-07-13T09:00:00Z', current_decision_status: status === 'pending' ? 'partially_approved' : status,
    pending_age: status === 'pending' ? { label: 'Elapsed pending time', elapsed_seconds: 9000, display: '2h 30m' } : null,
  },
  available_actions: status === 'pending' ? ['approve', 'reject', 'return', 'abstain'].map(code => ({ action_code: code, label: code, enabled: code !== 'abstain', disabled_reason: code === 'abstain' ? 'No self-declared conflict exists.' : null, required_permission: code === 'return' ? 'approvals.case.return' : code === 'reject' ? 'approvals.case.reject' : 'approvals.case.approve' })) : [],
});

const approver = (role_code: string, user_id: string, full_name: string) => ({ role_code, user_id, full_name });
const currentUser = { user_id: 'cfo-visual', full_name: 'Visual CFO', email: 'visual.cfo@sfpcl.example', status: 'active', roles: [{ role_code: 'cfo', role_name: 'CFO' }], teams: [], role_codes: ['cfo'], team_codes: [], permissions: ['approvals.case.read', 'approvals.case.approve', 'approvals.case.reject', 'approvals.case.return', 'approvals.sanction.read'], available_actions: [] };
const sanctionDecision = { sanction_decision_id: 'sanction-visual', decision: 'sanctioned', sanctioned_amount: '675000.00', sanctioned_tenure_months: null, interest_rate_type: null, interest_rate_value: null, repayment_date: null, penal_interest_rate: null, charges: {}, security_required_summary: null, conditions_precedent: null, decision_reason: 'Approved by the frozen exception-route authority.' };
const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data }) });
const paginated = (route: Route, data: unknown[], page: number, totalCount: number) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, pagination: { page, page_size: 20, total_count: totalCount, total_pages: Math.max(1, Math.ceil(totalCount / 20)), has_next: page < Math.max(1, Math.ceil(totalCount / 20)), has_previous: page > 1 } }) });
const failure = (route: Route, status: number, code: string, message: string) => route.fulfill({ status, contentType: 'application/json', body: JSON.stringify({ success: false, error: { code, message, details: {}, field_errors: {} } }) });

async function capture(page: Page, name: string) {
  await page.screenshot({ path: path.join(evidenceDir, `sanction-${name}.png`), fullPage: true, animations: 'disabled' });
}
