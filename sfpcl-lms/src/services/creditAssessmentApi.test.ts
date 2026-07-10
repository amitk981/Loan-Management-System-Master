import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  calculateLoanLimit, createAppraisal, fetchAppraisal, fetchEligibilityAssessment,
  fetchLoanLimitAssessment, revalidateAppraisalPrerequisites, reviewAppraisal,
  runEligibilityAssessment, submitAppraisalForReview, submitAppraisalToSanction, updateAppraisal,
} from './creditAssessmentApi';

const eligibility = { eligibility_assessment_id: 'eligibility-1', loan_application_id: 'application-1', member_active_check: 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid', overall_result: 'eligible', assessment_notes: 'All checks passed.', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:00:00+05:30' } as const;
const loanLimit = { loan_limit_assessment_id: 'limit-1', loan_application_id: 'application-1', member_id: 'member-1', shareholding_id: 'share-1', number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00', shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00', land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: '250000.00', amount_within_limit_flag: true, exception_required_flag: false, calculation_rule_version: 'board-policy-2026', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' }, warnings: [], calculated_by_user_id: 'user-1', calculated_at: '2026-07-10T10:05:00+05:30' } as const;
const appraisal = { loan_appraisal_note_id: 'appraisal-1', loan_application_id: 'application-1', appraisal_status: 'draft' };
const sanction = { approval_case_id: 'case-1', loan_application_id: 'application-1', loan_appraisal_note_id: 'appraisal-1', submission_status: 'pending', exception_required_flag: false, submitted_by: { user_id: 'manager-1', full_name: 'Credit Manager' }, submitted_at: '2026-07-10T11:00:00+05:30' };
const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', { getItem: vi.fn((key: string) => storage.get(key) ?? null), setItem: vi.fn((key: string, value: string) => storage.set(key, value)), removeItem: vi.fn((key: string) => storage.delete(key)) });
  storage.clear(); storedAuthSession({ accessToken: 'staff-token', refreshToken: 'refresh-token' });
});
afterEach(() => { clearStoredAuthSession(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });

describe('credit assessment API client', () => {
  it('uses the completed eligibility and loan-limit paths without changing decimal strings', async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok(eligibility)); vi.stubGlobal('fetch', fetchMock);
    await fetchEligibilityAssessment('application-1'); await runEligibilityAssessment('application-1');
    const payload = { shareholding_id: 'share-1', land_holding_ids: ['land-1'], crop_plan_id: 'crop-1', requested_amount: '250000.00', calculation_date: '2026-07-10' };
    fetchMock.mockResolvedValue(ok(loanLimit));
    await fetchLoanLimitAssessment('application-1');
    await expect(calculateLoanLimit('application-1', payload)).resolves.toMatchObject({ final_eligible_loan_amount: '250000.00' });
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      endpoint('/api/v1/loan-applications/application-1/eligibility-assessment/'), endpoint('/api/v1/loan-applications/application-1/eligibility-assessment/run/'),
      endpoint('/api/v1/loan-applications/application-1/loan-limit-assessment/'), endpoint('/api/v1/loan-applications/application-1/loan-limit-assessment/calculate/'),
    ]);
    expect(fetchMock).toHaveBeenLastCalledWith(expect.any(String), request('POST', payload));
  });

  it('maps every appraisal action and sends sanction as exactly remarks', async () => {
    const fetchMock = vi.fn().mockResolvedValue(ok(appraisal)); vi.stubGlobal('fetch', fetchMock);
    const draft = { borrower_summary: 'Borrower', eligibility_summary: 'Eligible', loan_limit_summary: 'Within limit', recommended_amount: '250000.00', recommended_tenure_months: 12, recommended_interest_type: 'floating', recommended_security_summary: 'Stored security', repayment_capacity_notes: 'Stored capacity', risk_assessment: { market_risk_rating: 'low', operational_risk_rating: 'low', borrower_risk_rating: 'low', overall_risk_rating: 'low', risk_mitigation_notes: 'Stored controls' }, recommendation: 'approve' } as const;
    await createAppraisal('application-1', draft); await updateAppraisal('application-1', { recommended_amount: '225000.00' }); await fetchAppraisal('application-1');
    await revalidateAppraisalPrerequisites('appraisal-1'); await submitAppraisalForReview('appraisal-1', { remarks: 'Ready.' }); await reviewAppraisal('appraisal-1', { decision: 'reviewed', review_comments: 'Reviewed.' });
    fetchMock.mockResolvedValue(ok(sanction));
    await expect(submitAppraisalToSanction('application-1', { remarks: 'Submit.' })).resolves.toEqual(sanction);
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      endpoint('/api/v1/loan-applications/application-1/appraisal-note/'), endpoint('/api/v1/loan-applications/application-1/appraisal-note/'), endpoint('/api/v1/loan-applications/application-1/appraisal-note/'), endpoint('/api/v1/appraisal-notes/appraisal-1/revalidate-prerequisites/'), endpoint('/api/v1/appraisal-notes/appraisal-1/submit-for-review/'), endpoint('/api/v1/appraisal-notes/appraisal-1/review/'), endpoint('/api/v1/loan-applications/application-1/submit-to-sanction-committee/'),
    ]);
    expect(fetchMock).toHaveBeenLastCalledWith(endpoint('/api/v1/loan-applications/application-1/submit-to-sanction-committee/'), request('POST', { remarks: 'Submit.' }));
  });

  it('surfaces the standard stale error and never retries', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: false, status: 409, json: async () => ({ success: false, error: { code: 'INVALID_STATE_TRANSITION', message: 'State changed.', field_errors: { remarks: 'Refresh.' } } }) });
    vi.stubGlobal('fetch', fetchMock);
    await expect(submitAppraisalToSanction('application-1', { remarks: 'Submit.' })).rejects.toMatchObject({ code: 'INVALID_STATE_TRANSITION', status: 409, fieldErrors: { remarks: 'Refresh.' } });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

const endpoint = (path: string) => `http://127.0.0.1:8000${path}`;
const request = (method = 'GET', body?: unknown) => expect.objectContaining({ method, headers: expect.objectContaining({ Accept: 'application/json', Authorization: 'Bearer staff-token', ...(body ? { 'Content-Type': 'application/json' } : {}) }), ...(body ? { body: JSON.stringify(body) } : {}) });
const ok = (data: unknown) => ({ ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) });
