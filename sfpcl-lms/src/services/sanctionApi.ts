import { API_BASE_URL, AuthSessionError, authenticatedRequest, loadStoredAuthSession } from './authSession';

export interface ApprovalAvailableAction {
  action_code: 'approve' | 'reject' | 'return' | 'abstain' | 'record_general_meeting_approval';
  label: string;
  enabled: boolean;
  disabled_reason: string | null;
  required_permission: string;
  required_role?: string | null;
}

export interface ApprovalApprover {
  role_code: string;
  user_id: string;
  full_name: string;
  decision?: string | null;
  acted_at?: string | null;
  replacement_for_user_id?: string;
}

export interface ApprovalActionRecord extends ApprovalApprover {
  approval_action_id: string;
  decision: string;
  comments: string;
  acted_at: string;
}

export interface GeneralMeetingApproval {
  general_meeting_approval_id: string;
  loan_application_id: string;
  related_party_type: string;
  related_party_user_id: string | null;
  relationship_description: string;
  meeting_date: string;
  notice_document_id: string;
  minutes_document_id: string;
  resolution_document_id: string;
  approval_status: 'pending' | 'approved' | 'rejected';
  recorded_by_user_id: string;
  recorded_at: string;
  supersedes_general_meeting_approval_id: string | null;
  evidence_scope?: 'current_pending' | 'cycle_frozen';
}

export interface ApprovalReviewFacts {
  maker_checker: Record<string, unknown>;
  eligibility: Record<string, unknown>;
  loan_amounts: { requested_amount: string | null; eligible_amount: string | null; recommended_amount: string | null };
  purpose: { category: string | null; description: string | null };
  compliance_checks: Record<string, unknown>;
  borrowing_history: string;
  risk: Record<string, unknown>;
  documentation_completeness: Record<string, unknown>;
  source_references: Record<string, string>;
}

export interface ApprovalCase {
  approval_case_id: string;
  cycle_number: number;
  approval_type: string;
  related_entity_type: string;
  related_entity_id: string;
  loan_application_id: string;
  application_reference_number: string;
  amount: string;
  current_status: string;
  decision_date: string;
  version: number;
  approval_matrix_rule_id: string;
  approval_matrix_rule_version: number;
  sanction_committee_id: string;
  sanction_committee_version: number;
  route_approvers: ApprovalApprover[];
  required_approvers: ApprovalApprover[];
  approval_actions: ApprovalActionRecord[];
  excluded_approvers: Array<{ user_id: string; conflict_code: string; reason: string }>;
  general_meeting_evidence_required: boolean;
  general_meeting_approval: GeneralMeetingApproval | null;
  conflict_block_reason: string | null;
  reason_for_approval: string;
  exception_condition_code: string | null;
  exception_reason: string | null;
  matrix_projection: Record<string, unknown>;
  committee_projection: Record<string, unknown>;
  loan_limit_provenance: Record<string, unknown>;
  review_facts: ApprovalReviewFacts;
  available_actions: ApprovalAvailableAction[];
}

export interface SanctionDecision {
  sanction_decision_id: string;
  decision: string;
  sanctioned_amount: string;
  sanctioned_tenure_months: number | null;
  interest_rate_type: string | null;
  interest_rate_value: string | null;
  repayment_date: string | null;
  penal_interest_rate: string | null;
  charges: Record<string, unknown>;
  security_required_summary: string | null;
  conditions_precedent: string | null;
  decision_reason: string;
}

export interface GeneralMeetingPayload {
  related_party_type: 'director' | 'director_relative' | 'committee_member';
  related_party_user_id: string | null;
  relationship_description: string;
  meeting_date: string;
  notice_document_id: string;
  minutes_document_id: string;
  resolution_document_id: string;
  approval_status: 'pending' | 'approved' | 'rejected';
}

interface DocumentUploadEnvelope {
  success: boolean;
  data?: { document_id: string };
  error?: { code: string; message: string; field_errors?: Record<string, string>; details?: Record<string, unknown> };
}

export const listApprovalCases = (status = 'pending') => {
  const params = new URLSearchParams();
  if (status === 'pending') params.set('assigned_to_me', 'true');
  if (status !== 'all' && status !== 'pending') params.set('current_status', status);
  params.set('page_size', '100');
  return authenticatedRequest<ApprovalCase[]>(`/api/v1/approval-cases/?${params.toString()}`);
};

export const fetchApprovalCase = (caseId: string) =>
  authenticatedRequest<ApprovalCase>(`/api/v1/approval-cases/${caseId}/`);

export const recordApprovalAction = (
  caseId: string,
  action: ApprovalAvailableAction['action_code'],
  version: number,
  comments: string,
) => authenticatedRequest<ApprovalCase>(
  `/api/v1/approval-cases/${caseId}/${action === 'return' ? 'return-for-clarification' : action}/`,
  { method: 'POST', body: { version, comments } },
);

export const fetchSanctionDecision = (applicationId: string) =>
  authenticatedRequest<SanctionDecision>(`/api/v1/loan-applications/${applicationId}/sanction-decision/`);

export const recordGeneralMeetingApproval = (applicationId: string, payload: GeneralMeetingPayload) =>
  authenticatedRequest<GeneralMeetingApproval>(
    `/api/v1/loan-applications/${applicationId}/general-meeting-approval/`,
    { method: 'POST', body: payload },
  );

export const uploadGeneralMeetingDocument = async (applicationId: string, file: File) => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const body = new FormData();
  body.set('file', file);
  body.set('document_category', 'legal');
  body.set('sensitivity_level', 'restricted');
  body.set('related_entity_type', 'application');
  body.set('related_entity_id', applicationId);
  const response = await fetch(`${API_BASE_URL}/api/v1/document-files/`, {
    method: 'POST', headers: { Accept: 'application/json', Authorization: `Bearer ${session.accessToken}` }, body,
  });
  const envelope = await response.json() as DocumentUploadEnvelope;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(envelope.error?.code ?? 'REQUEST_FAILED', envelope.error?.message ?? 'Document upload failed.', response.status, envelope.error?.field_errors, envelope.error?.details);
  }
  return envelope.data.document_id;
};
