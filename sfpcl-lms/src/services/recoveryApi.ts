import { authenticatedMultipartRequest, authenticatedPaginatedRequest, authenticatedRequest } from './authSession';

export interface DefaultAssessmentProjection {
  default_assessment_id: string;
  default_case_id: string;
  assessment_type: string;
  payment_failure_classification: string;
  reason_summary: string;
  evidence_document_ids: string[];
  borrower_interaction_summary: string;
  recommended_action: string;
  assessed_by_user_id: string;
  assessed_at: string;
}

export interface ExtensionNoteProjection {
  extension_note_id: string;
  default_case_id: string;
  loan_account_id: string;
  extension_reason: string;
  extension_start_date: string;
  extension_end_date: string;
  document_id: string;
  prepared_by_user_id: string;
  approved_by_user_id: string | null;
  status: string;
}

export interface NonPaymentNoteProjection {
  non_payment_note_id: string;
  default_case_id: string;
  loan_account_id: string;
  reason_for_non_payment: string;
  intentionality_assessment: string;
  outstanding_principal_amount: string;
  outstanding_interest_amount: string;
  recommended_recovery_action: string;
  evidence_document_ids: string[];
  frozen_case_facts: Record<string, string | null>;
  document_id: string;
  prepared_by_user_id: string;
  status: string;
  approval_case_id: string | null;
  submitted_to_sanction_committee_at: string | null;
  available_actions?: Array<{ action_code: string }>;
}

export interface RecoveryActionProjection {
  recovery_action_id: string; action_status: 'pending' | 'completed' | 'failed';
  action_type: string; source_security: { security_type: string; security_id: string; status: string };
  initiated_at: string; amount_recovered: string | null; external_sap_status: string;
  interaction_log: Array<{ interaction_at: string; interaction_mode: string; summary: string; grievance_reference: string }>;
  ledger_posting: Record<string, string>; available_actions: Array<{ action_code: string }>;
}

export interface DefaultCaseProjection {
  default_case_id: string;
  loan_account_id: string;
  loan_account_number: string;
  member_id: string;
  borrower_name: string;
  principal_outstanding: string;
  interest_outstanding: string;
  total_outstanding: string;
  trigger_event: string;
  scheduled_due_date: string;
  repayment_schedule_id: string;
  default_case_status: string;
  grace_period_start_date: string;
  grace_period_end_date: string;
  grace_state: string;
  current_assessment: DefaultAssessmentProjection | null;
  extension_note: ExtensionNoteProjection | null;
  non_payment_note: NonPaymentNoteProjection | null;
  recovery_decision: null | { recovery_decision_id: string; decision: string; status: string; available_actions: Array<{ action_code: string }> };
  recovery_action: RecoveryActionProjection | null;
  reason: string;
  available_actions?: string[];
}

export type RecoveryCaseProjection = DefaultCaseProjection;

export const fetchDefaultCases = () =>
  authenticatedPaginatedRequest<DefaultCaseProjection>('/api/v1/default-cases/?page_size=100');

export const fetchDefaultCase = (defaultCaseId: string) =>
  authenticatedRequest<DefaultCaseProjection>(`/api/v1/default-cases/${defaultCaseId}/`);

// Retained for the 011F reverse consumer until 011PB owns the S56/S57 page wiring.
export const fetchRecoveryCases = fetchDefaultCases;

export const uploadRecoveryEvidence = async (loanAccountId: string, file: File) => (
  await authenticatedMultipartRequest<{ document_id: string }>('/api/v1/document-files/', {
    file, document_category: 'recovery', sensitivity_level: 'restricted',
    related_entity_type: 'loan_account', related_entity_id: loanAccountId,
  })
).document_id;
export const initiateRecoveryAction = (decisionId: string, body: Record<string, unknown>) =>
  authenticatedRequest<RecoveryActionProjection>(`/api/v1/recovery-decisions/${decisionId}/actions/`, { method: 'POST', body });
export const completeRecoveryAction = (actionId: string, body: Record<string, unknown>) =>
  authenticatedRequest<RecoveryActionProjection>(`/api/v1/recovery-actions/${actionId}/complete/`, { method: 'POST', body });
