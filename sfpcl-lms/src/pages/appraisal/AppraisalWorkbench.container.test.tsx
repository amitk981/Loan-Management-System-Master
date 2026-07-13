// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AppraisalWorkbench from './AppraisalWorkbench';
import { AuthSessionError, authenticatedRequest, storedAuthSession } from '../../services/authSession';
import type { AppraisalNote, EligibilityAssessment, LoanLimitAssessment } from '../../services/creditAssessmentApi';

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({ currentUser: {
    permissions: ['credit.eligibility.run', 'credit.loan_limit.calculate', 'credit.appraisal.create', 'credit.appraisal.update', 'credit.risk_assessment.manage', 'credit.appraisal.submit_review', 'credit.appraisal.review', 'credit.appraisal.submit_sanction'],
    roleCodes: ['deputy_manager_finance', 'credit_manager'],
  } }),
}));
vi.mock('../../services/authSession', async importOriginal => {
  const actual = await importOriginal<typeof import('../../services/authSession')>();
  return { ...actual, authenticatedRequest: vi.fn() };
});

const application = {
  loan_application_id: 'application-1', application_reference_number: 'LO000001',
  member: { member_id: 'member-1', display_name: 'API Borrower', member_type: 'individual', folio_number: 'FO-1' },
  application_date: '2026-07-10', required_loan_amount: '250000.00', purpose_category: 'crop_production',
  application_status: 'reference_generated', current_stage: 'credit_assessment', completeness_status: 'complete',
};
const action = { action_code: 'credit.eligibility.run', label: 'Run Eligibility Assessment', enabled: true, disabled_reason: null, required_permission: 'credit.eligibility.run', required_role: null };
const eligibility = {
  eligibility_assessment_id: 'eligibility-1', loan_application_id: 'application-1', member_active_check: 'pass',
  default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted',
  purpose_check: 'agriculture_aligned', nominee_check: 'valid', overall_result: 'eligible',
  assessment_notes: 'Stored assessment explanation.', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:00:00+05:30', available_actions: [action],
} satisfies EligibilityAssessment;
const loanLimit = {
  loan_limit_assessment_id: 'limit-1', loan_application_id: 'application-1', member_id: 'member-1', shareholding_id: 'share-1',
  number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00',
  shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00',
  land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: '250000.00',
  amount_within_limit_flag: true, exception_required_flag: false, calculation_rule_version: 'board-policy-2026',
  configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' },
  warnings: [], calculated_by_user_id: 'user-1', calculated_at: '2026-07-10T10:05:00+05:30', available_actions: [],
} satisfies LoanLimitAssessment;
const appraisal = {
  loan_appraisal_note_id: 'appraisal-1', loan_application_id: 'application-1', eligibility_assessment_id: 'eligibility-1', loan_limit_assessment_id: 'limit-1',
  eligibility_snapshot: eligibility, loan_limit_snapshot: loanLimit, prerequisite_provenance: 'verified',
  prepared_by: { user_id: 'user-1', full_name: 'Deputy Manager' }, prepared_at: '2026-07-10T10:10:00+05:30', reviewed_by: null, reviewed_at: null,
  decision: null, review_comments: null, review_history: [], tat_due_at: '2026-07-12T10:10:00+05:30', tat_status: 'within_tat',
  borrower_summary: 'Borrower summary', eligibility_summary: 'Eligible', loan_limit_summary: 'Within stored limit', recommended_amount: '250000.00',
  recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Security', repayment_capacity_notes: 'Capacity',
  risk_assessment: { risk_assessment_id: 'risk-1', market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Controls', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:10:00+05:30' },
  recommendation: 'approve', appraisal_status: 'draft',
  available_actions: [{ action_code: 'credit.appraisal.update', label: 'Update Appraisal Draft', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.update', required_role: null }],
} satisfies AppraisalNote;

describe('default AppraisalWorkbench authenticated HTTP container', () => {
  beforeEach(() => {
    storedAuthSession({ accessToken: 'access', refreshToken: 'refresh' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, status: 200,
      json: async () => ({ success: true, data: [application], pagination: { page: 1, page_size: 100, total_count: 1, total_pages: 1, has_next: false, has_previous: false } }),
    }));
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (path.endsWith('/eligibility-assessment/run/') && options?.method === 'POST') return eligibility as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
  });

  afterEach(() => { cleanup(); vi.clearAllMocks(); vi.unstubAllGlobals(); localStorage.clear(); });

  it('runs eligibility with the exact request and performs one canonical four-read refresh', async () => {
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);
    const button = await screen.findByRole('button', { name: 'Run Eligibility Assessment' });

    await userEvent.click(button);

    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(
      '/api/v1/loan-applications/application-1/eligibility-assessment/run/',
      { method: 'POST', body: {} },
    ));
    const paths = vi.mocked(authenticatedRequest).mock.calls.map(([path]) => path);
    expect(paths.filter(path => path.endsWith('/eligibility-assessment/run/'))).toHaveLength(1);
    expect(paths.filter(path => path.endsWith('/eligibility-assessment/'))).toHaveLength(2);
    expect(paths.filter(path => path.endsWith('/loan-limit-assessment/'))).toHaveLength(2);
    expect(paths.filter(path => path.endsWith('/appraisal-note/'))).toHaveLength(2);
    expect(paths.filter(path => path.endsWith('/sanction-case/'))).toHaveLength(2);
  });

  it('PATCHes only the appraisal allowlist and refreshes the canonical resources once', async () => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (path.endsWith('/loan-limit-assessment/')) return loanLimit as never;
      if (path.endsWith('/appraisal-note/') && options?.method === 'PATCH') return appraisal as never;
      if (path.endsWith('/appraisal-note/')) return appraisal as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);

    await userEvent.click(await screen.findByRole('button', { name: 'Save Appraisal Draft' }));

    const patchCall = await waitFor(() => {
      const found = vi.mocked(authenticatedRequest).mock.calls.find(([, options]) => options?.method === 'PATCH');
      expect(found).toBeDefined();
      return found!;
    });
    expect(patchCall[0]).toBe('/api/v1/loan-applications/application-1/appraisal-note/');
    expect(patchCall[1]?.body).toEqual({
      borrower_summary: 'Borrower summary', eligibility_summary: 'Eligible', loan_limit_summary: 'Within stored limit', recommended_amount: '250000.00',
      recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Security', repayment_capacity_notes: 'Capacity',
      risk_assessment: { market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Controls' }, recommendation: 'approve',
    });
    const paths = vi.mocked(authenticatedRequest).mock.calls.map(([path]) => path);
    expect(paths.filter(path => path.endsWith('/eligibility-assessment/'))).toHaveLength(2);
    expect(paths.filter(path => path.endsWith('/loan-limit-assessment/'))).toHaveLength(2);
    expect(paths.filter(path => path.endsWith('/appraisal-note/'))).toHaveLength(3);
    expect(paths.filter(path => path.endsWith('/sanction-case/'))).toHaveLength(2);
  });

  it('renders a stale 409 without retry, synthesis, or refresh', async () => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (path.endsWith('/loan-limit-assessment/')) return loanLimit as never;
      if (path.endsWith('/appraisal-note/') && options?.method === 'PATCH') throw new AuthSessionError('INVALID_STATE_TRANSITION', 'The appraisal changed.', 409);
      if (path.endsWith('/appraisal-note/')) return appraisal as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);

    await userEvent.click(await screen.findByRole('button', { name: 'Save Appraisal Draft' }));

    expect(await screen.findByText(/INVALID_STATE_TRANSITION: The appraisal changed/)).toBeTruthy();
    const calls = vi.mocked(authenticatedRequest).mock.calls;
    expect(calls.filter(([, options]) => options?.method === 'PATCH')).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/eligibility-assessment/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/loan-limit-assessment/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/appraisal-note/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/sanction-case/'))).toHaveLength(1);
  });

  it.each([
    [400, 'VALIDATION_ERROR', 'recommended_amount: Must be within the frozen limit.'],
    [403, 'OBJECT_ACCESS_DENIED', 'You cannot access this application.'],
  ])('renders HTTP %s once without retry or refresh', async (status, code, message) => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (path.endsWith('/loan-limit-assessment/')) return loanLimit as never;
      if (path.endsWith('/appraisal-note/') && options?.method === 'PATCH') throw new AuthSessionError(code, message, status);
      if (path.endsWith('/appraisal-note/')) return appraisal as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);

    await userEvent.click(await screen.findByRole('button', { name: 'Save Appraisal Draft' }));

    expect(await screen.findByText(new RegExp(code))).toBeTruthy();
    const calls = vi.mocked(authenticatedRequest).mock.calls;
    expect(calls.filter(([, options]) => options?.method === 'PATCH')).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/eligibility-assessment/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/loan-limit-assessment/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/sanction-case/'))).toHaveLength(1);
  });

  it('keeps absent and disabled backend actions non-invokable and renders the stable reason', async () => {
    const disabled = { ...appraisal, available_actions: [{ action_code: 'credit.appraisal.update', label: 'Update Appraisal Draft', enabled: false, disabled_reason: 'Only draft appraisal notes can be updated.', required_permission: 'credit.appraisal.update', required_role: null }] };
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path.endsWith('/eligibility-assessment/')) return { ...eligibility, available_actions: [] } as never;
      if (path.endsWith('/loan-limit-assessment/')) return loanLimit as never;
      if (path.endsWith('/appraisal-note/')) return disabled as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);

    expect(await screen.findByText(/Only draft appraisal notes can be updated/)).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Save Appraisal Draft' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Run Eligibility Assessment' })).toBeNull();
  });

  it.each([
    {
      name: 'create', button: 'Create Appraisal Draft', resource: null,
      actions: [{ action_code: 'credit.appraisal.create', label: 'Create Appraisal Draft', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.create', required_role: null }],
      path: '/api/v1/loan-applications/application-1/appraisal-note/', method: 'POST',
      body: { borrower_summary: '', eligibility_summary: '', loan_limit_summary: '', recommended_amount: '250000.00', recommended_interest_type: 'floating', recommended_security_summary: '', repayment_capacity_notes: '', risk_assessment: { market_risk_rating: '', operational_risk_rating: '', borrower_risk_rating: '', overall_risk_rating: '', risk_mitigation_notes: '' }, recommendation: '' },
    },
    {
      name: 'revalidate', button: 'Revalidate Prerequisites', resource: { ...appraisal, prerequisite_provenance: 'legacy_unverified' },
      actions: [{ action_code: 'revalidate_appraisal_prerequisites', label: 'Revalidate Prerequisites', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.update', required_role: null }],
      path: '/api/v1/appraisal-notes/appraisal-1/revalidate-prerequisites/', method: 'POST', body: {},
    },
    {
      name: 'submit review', button: 'Submit for Credit Review', resource: appraisal,
      actions: [{ action_code: 'credit.appraisal.submit_review', label: 'Submit for Credit Review', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.submit_review', required_role: null }],
      path: '/api/v1/appraisal-notes/appraisal-1/submit-for-review/', method: 'POST', body: { remarks: '' },
    },
    {
      name: 'reviewed decision', button: 'Record Credit Review', resource: { ...appraisal, appraisal_status: 'review_pending' },
      actions: [{ action_code: 'credit.appraisal.review', label: 'Record Credit Review', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.review', required_role: 'credit_manager' }],
      path: '/api/v1/appraisal-notes/appraisal-1/review/', method: 'POST', body: { decision: 'reviewed', review_comments: '' },
    },
    {
      name: 'sanction', button: 'Submit to Sanction Committee', resource: { ...appraisal, appraisal_status: 'reviewed' },
      actions: [{ action_code: 'credit.appraisal.submit_sanction', label: 'Submit to Sanction Committee', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.submit_sanction', required_role: 'credit_manager' }],
      path: '/api/v1/loan-applications/application-1/submit-to-sanction-committee/', method: 'POST', body: { remarks: '' },
    },
  ])('clicks $name through the authenticated boundary and refreshes four reads', async ({ button, resource, actions, path, method, body }) => {
    const projectedLimit = { ...loanLimit, available_actions: resource ? [] : actions };
    const projectedAppraisal = resource ? { ...resource, available_actions: actions } : null;
    vi.mocked(authenticatedRequest).mockImplementation(async (requestPath, options) => {
      if (requestPath === path && options?.method === method) return (projectedAppraisal ?? appraisal) as never;
      if (requestPath.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (requestPath.endsWith('/loan-limit-assessment/')) return projectedLimit as never;
      if (requestPath.endsWith('/appraisal-note/')) {
        if (projectedAppraisal) return projectedAppraisal as never;
        throw new AuthSessionError('NOT_FOUND', 'missing', 404);
      }
      if (requestPath.endsWith('/sanction-case/')) throw new AuthSessionError('NOT_FOUND', 'missing', 404);
      throw new Error(`Unexpected request ${requestPath}`);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);

    await userEvent.click(await screen.findByRole('button', { name: button }));

    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(path, { method, body }));
    const calls = vi.mocked(authenticatedRequest).mock.calls;
    expect(calls.filter(([calledPath, options]) => calledPath === path && options?.method === method)).toHaveLength(1);
    expect(calls.filter(([calledPath]) => calledPath.endsWith('/eligibility-assessment/'))).toHaveLength(2);
    expect(calls.filter(([calledPath]) => calledPath.endsWith('/loan-limit-assessment/'))).toHaveLength(2);
    expect(calls.filter(([calledPath, options]) => calledPath.endsWith('/appraisal-note/') && options?.method === 'GET')).toHaveLength(2);
    expect(calls.filter(([calledPath]) => calledPath.endsWith('/sanction-case/'))).toHaveLength(2);
  });

  it('calculates a limit from entered source IDs and refreshes four reads', async () => {
    const limitAction = { action_code: 'credit.loan_limit.calculate', label: 'Calculate Loan Limit', enabled: true, disabled_reason: null, required_permission: 'credit.loan_limit.calculate', required_role: null };
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return { ...eligibility, available_actions: [limitAction] } as never;
      if (path.endsWith('/loan-limit-assessment/calculate/') && options?.method === 'POST') return loanLimit as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: /Step 2.*Appraise/ }));
    await userEvent.type(screen.getByLabelText('Shareholding ID'), 'share-1');
    await userEvent.type(screen.getByLabelText('Land holding IDs (comma separated)'), 'land-1, land-2');
    await userEvent.type(screen.getByLabelText('Crop plan ID'), 'crop-1');
    const date = (screen.getByLabelText('Calculation date') as HTMLInputElement).value;

    await userEvent.click(screen.getByRole('button', { name: 'Calculate Stored Loan Limit' }));

    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(
      '/api/v1/loan-applications/application-1/loan-limit-assessment/calculate/',
      { method: 'POST', body: { shareholding_id: 'share-1', land_holding_ids: ['land-1', 'land-2'], crop_plan_id: 'crop-1', requested_amount: '250000.00', calculation_date: date } },
    ));
    const calls = vi.mocked(authenticatedRequest).mock.calls;
    expect(calls.filter(([path]) => path.endsWith('/loan-limit-assessment/calculate/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/eligibility-assessment/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/loan-limit-assessment/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/appraisal-note/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/sanction-case/'))).toHaveLength(2);
  });

  it.each(['returned', 'rejected'] as const)('posts the %s Credit Manager decision once', async decision => {
    const reviewAction = { action_code: 'credit.appraisal.review', label: 'Record Credit Review', enabled: true, disabled_reason: null, required_permission: 'credit.appraisal.review', required_role: 'credit_manager' };
    const reviewPending = { ...appraisal, appraisal_status: 'review_pending', available_actions: [reviewAction] };
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.endsWith('/eligibility-assessment/')) return eligibility as never;
      if (path.endsWith('/loan-limit-assessment/')) return loanLimit as never;
      if (path.endsWith('/review/') && options?.method === 'POST') return reviewPending as never;
      if (path.endsWith('/appraisal-note/')) return reviewPending as never;
      throw new AuthSessionError('NOT_FOUND', 'missing', 404);
    });
    render(<AppraisalWorkbench onOpenApplication={vi.fn()} />);
    await screen.findByRole('button', { name: 'Record Credit Review' });
    await userEvent.selectOptions(screen.getByLabelText('Decision'), decision);
    if (decision === 'rejected') await userEvent.type(screen.getByLabelText('Detailed rejection reason'), 'Policy evidence failed.');

    await userEvent.click(screen.getByRole('button', { name: 'Record Credit Review' }));

    const expected = decision === 'rejected'
      ? { decision, review_comments: '', rejection_reason_category: 'eligibility', detailed_reason: 'Policy evidence failed.', reapply_allowed_flag: true, communication_mode: 'email' }
      : { decision, review_comments: '' };
    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith('/api/v1/appraisal-notes/appraisal-1/review/', { method: 'POST', body: expected }));
    const calls = vi.mocked(authenticatedRequest).mock.calls;
    expect(calls.filter(([path]) => path.endsWith('/review/'))).toHaveLength(1);
    expect(calls.filter(([path]) => path.endsWith('/eligibility-assessment/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/loan-limit-assessment/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/appraisal-note/'))).toHaveLength(2);
    expect(calls.filter(([path]) => path.endsWith('/sanction-case/'))).toHaveLength(2);
  });
});
