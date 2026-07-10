import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

type Envelope<T> = { success: boolean; data?: T; error?: { code: string; message: string; field_errors?: Record<string, string> } };
export type Rating = 'low' | 'medium' | 'high';

export interface EligibilityAssessment {
  eligibility_assessment_id: string; loan_application_id: string;
  member_active_check: string; default_check: string; document_check: string;
  terms_acceptance_check: string; purpose_check: string; nominee_check: string;
  overall_result: string; assessment_notes: string; assessed_by_user_id: string; assessed_at: string;
}
export interface LoanLimitAssessment {
  loan_limit_assessment_id: string; loan_application_id: string; member_id: string;
  shareholding_id: string | null; number_of_shares: number; valuation_per_share: string;
  share_limit_percentage: string | null; per_share_cap_amount: string | null;
  shareholding_based_limit_amount: string; land_area_acres: string;
  scale_of_finance_per_acre_amount: string; land_based_limit_amount: string;
  final_eligible_loan_amount: string; requested_amount: string; amount_within_limit_flag: boolean;
  exception_required_flag: boolean; calculation_rule_version: string;
  configuration_source: { type: string; loan_policy_config_id: string | null; policy_name: string | null; board_approval_reference: string | null };
  warnings: { code: string; message: string }[]; calculated_by_user_id: string | null; calculated_at: string | null;
}
export interface RiskAssessment {
  risk_assessment_id?: string; market_risk_rating: Rating; operational_risk_rating: Rating;
  borrower_risk_rating: Rating; overall_risk_rating: Rating; risk_mitigation_notes: string;
  assessed_by_user_id?: string; assessed_at?: string;
}
export interface AppraisalDraft {
  borrower_summary: string; eligibility_summary: string; loan_limit_summary: string;
  recommended_amount: string; recommended_tenure_months: number | null;
  recommended_interest_type: string; recommended_security_summary: string;
  repayment_capacity_notes: string; risk_assessment: RiskAssessment; recommendation: string;
}
export interface ReviewHistoryItem {
  appraisal_review_decision_id: string; decision: string; review_comments: string;
  reviewer: { user_id: string; full_name: string }; decided_at: string;
  from_state: string; to_state: string; history_provenance: string;
}
export interface RejectionNoteSummary {
  rejection_note_id: string; note_status: string; rejection_reason_category: string;
  reapply_allowed_flag: boolean; communication_mode: string;
}
export interface AppraisalNote extends AppraisalDraft {
  loan_appraisal_note_id: string; loan_application_id: string;
  eligibility_assessment_id: string; loan_limit_assessment_id: string;
  eligibility_snapshot: EligibilityAssessment; loan_limit_snapshot: LoanLimitAssessment;
  prerequisite_provenance: string; prepared_by: { user_id: string; full_name: string };
  prepared_at: string; reviewed_by: { user_id: string; full_name: string } | null;
  reviewed_at: string | null; decision: string | null; review_comments: string | null;
  review_history: ReviewHistoryItem[]; tat_due_at: string; tat_status: string;
  risk_assessment: RiskAssessment & { risk_assessment_id: string };
  appraisal_status: string; rejection_note?: RejectionNoteSummary;
}
export interface LoanLimitRequest { shareholding_id: string; land_holding_ids: string[]; crop_plan_id: string; requested_amount: string; calculation_date: string }
export type AppraisalUpdate = Partial<Omit<AppraisalDraft, 'risk_assessment'>> & { risk_assessment?: Partial<RiskAssessment> };
export interface ReviewRequest { decision: 'reviewed' | 'returned' | 'rejected'; review_comments: string; rejection_reason_category?: string; detailed_reason?: string; reapply_allowed_flag?: boolean; communication_mode?: string }
export interface SanctionSubmission { approval_case_id: string; loan_application_id: string; loan_appraisal_note_id: string; submission_status: string; exception_required_flag: boolean; submitted_by: { user_id: string; full_name: string }; submitted_at: string }

export const fetchEligibilityAssessment = (id: string) => request<EligibilityAssessment>(`/api/v1/loan-applications/${id}/eligibility-assessment/`);
export const runEligibilityAssessment = (id: string) => request<EligibilityAssessment>(`/api/v1/loan-applications/${id}/eligibility-assessment/run/`, 'POST', {});
export const fetchLoanLimitAssessment = (id: string) => request<LoanLimitAssessment>(`/api/v1/loan-applications/${id}/loan-limit-assessment/`);
export const calculateLoanLimit = (id: string, body: LoanLimitRequest) => request<LoanLimitAssessment>(`/api/v1/loan-applications/${id}/loan-limit-assessment/calculate/`, 'POST', body);
export const fetchAppraisal = (id: string) => request<AppraisalNote>(`/api/v1/loan-applications/${id}/appraisal-note/`);
export const createAppraisal = (id: string, body: AppraisalDraft) => request<AppraisalNote>(`/api/v1/loan-applications/${id}/appraisal-note/`, 'POST', appraisalBody(body));
export const updateAppraisal = (id: string, body: AppraisalUpdate) => request<AppraisalNote>(`/api/v1/loan-applications/${id}/appraisal-note/`, 'PATCH', appraisalBody(body));
export const revalidateAppraisalPrerequisites = (id: string) => request<AppraisalNote>(`/api/v1/appraisal-notes/${id}/revalidate-prerequisites/`, 'POST', {});
export const submitAppraisalForReview = (id: string, body: { remarks: string }) => request<AppraisalNote>(`/api/v1/appraisal-notes/${id}/submit-for-review/`, 'POST', body);
export const reviewAppraisal = (id: string, body: ReviewRequest) => request<AppraisalNote>(`/api/v1/appraisal-notes/${id}/review/`, 'POST', body);
export const submitAppraisalToSanction = (id: string, body: { remarks: string }) => request<SanctionSubmission>(`/api/v1/loan-applications/${id}/submit-to-sanction-committee/`, 'POST', body);
const appraisalBody = <T extends AppraisalUpdate>(body: T) => body.recommended_tenure_months == null ? Object.fromEntries(Object.entries(body).filter(([key]) => key !== 'recommended_tenure_months')) : body;

async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { Accept: 'application/json', Authorization: `Bearer ${session.accessToken}`, ...(body ? { 'Content-Type': 'application/json' } : {}) },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const envelope = await response.json() as Envelope<T>;
  if (!response.ok || !envelope.success || envelope.data === undefined) {
    throw new AuthSessionError(envelope.error?.code ?? 'REQUEST_FAILED', envelope.error?.message ?? 'Request failed.', response.status, envelope.error?.field_errors);
  }
  return envelope.data;
}
