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

export interface RecoveryApproverProjection {
  role_code: string;
  user_id: string;
  full_name: string | null;
  decision?: string | null;
  acted_at?: string | null;
}

export interface RecoveryApprovalProjection {
  approval_case_id: string;
  approval_type: string;
  related_entity_type: string;
  related_entity_id: string;
  current_status: string;
  decision_date: string;
  reason_for_approval: string;
  conflict_block_reason: string | null;
  required_approvers: RecoveryApproverProjection[];
  approval_actions: Array<RecoveryApproverProjection & {
    approval_action_id: string;
    decision: string;
    comments: string;
    acted_at: string;
  }>;
  excluded_approvers: Array<{ user_id: string; conflict_code: string; reason: string }>;
  available_actions: Array<{
    action_code: string;
    label: string;
    enabled: boolean;
    disabled_reason: string | null;
    required_permission: string;
  }>;
}

export interface RecoveryDecisionProjection {
  recovery_decision_id: string;
  default_case_id?: string;
  non_payment_note_id?: string;
  approval_case_id: string;
  decision: string;
  decision_reason: string;
  status: string;
  approval_evidence?: {
    approval_case_status?: string;
    approved_action?: string;
    required_approvers?: RecoveryApproverProjection[];
    approval_actions?: Array<{
      approval_action_id: string;
      approver_user_id: string;
      approver_role_code: string;
      approver_display_name: string;
      decision: string;
      acted_at: string;
    }>;
    closed_at?: string;
  };
  decided_by_user_id?: string;
  decided_by_role_code?: string;
  decided_at?: string;
  available_actions: Array<{ action_code: string; action_type?: string; required_permission?: string }>;
}

export interface RecoveryActionProjection {
  recovery_action_id: string; action_status: 'pending' | 'completed' | 'failed';
  action_type: string; source_security: { security_type: string; security_id: string; status: string };
  initiated_at: string; amount_recovered: string | null; external_sap_status: string;
  interaction_log: Array<{ interaction_at: string; interaction_mode: string; summary: string; grievance_reference: string }>;
  ledger_posting: Record<string, string>; available_actions: Array<{ action_code: string }>;
}

export interface RecoveryDecisionControlProjection {
  action_code: 'record_recovery_decision';
  enabled: boolean;
  disabled_reason: string | null;
  approval_case_id: string | null;
  decision: string | null;
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
  recovery_decision: RecoveryDecisionProjection | null;
  recovery_decision_control: RecoveryDecisionControlProjection | null;
  recovery_action: RecoveryActionProjection | null;
  reason: string;
  available_actions?: string[];
}

export type RecoveryCaseProjection = DefaultCaseProjection;

export interface ClosureReadinessCheck {
  code: string;
  status: 'pass' | 'fail';
  approved_adjustment?: boolean;
  security_return_required?: boolean;
  physical_share_return_required?: boolean;
  demat_unpledge_required?: boolean;
  blank_cheque_return_required?: boolean;
  poa_release_required?: boolean;
}

export interface ClosureReadinessProjection {
  loan_account_id: string;
  ready_for_closure: boolean;
  checks: ClosureReadinessCheck[];
  principal_outstanding: string;
  interest_outstanding: string;
  charges_outstanding: string;
  total_outstanding: string;
  interest_adjustment_applied: boolean;
  security_return_required: boolean;
  physical_share_return_required: boolean;
  demat_unpledge_required: boolean;
  blank_cheque_return_required: boolean;
  poa_release_required: boolean;
}

export interface LoanClosureProjection {
  loan_closure_id: string;
  loan_account_id: string;
  loan_account_status: string;
  closure_stage: string;
  closure_type: string;
  closed_at: string;
  noc_required: boolean;
  security_return_required: boolean;
  archive_required: boolean;
  requirements: Record<'noc' | 'security_return' | 'archive', string>;
  idempotency_replayed: boolean;
  available_actions: string[];
}

export interface NocProjection {
  noc_id: string;
  loan_closure_id: string;
  loan_account_id: string;
  member_id: string;
  document_id: string;
  issued_by_user_id: string;
  issued_at: string;
  signatory_user_id: string;
  signatory_role_code: string;
  delivery_mode: string;
  delivery_status: string;
  communication_id: string;
  communication_job_id: string;
  borrower_name: string;
  loan_account_number: string;
  application_reference: string;
  disbursed_amount: string;
  full_repayment_at: string;
  idempotency_replayed: boolean;
}

export interface SecurityReturnItemProjection {
  item_type: string;
  status: string;
  source_item_id: string | null;
  custody_location: string;
  returned_released_to: string;
  psn?: string | null;
  urf_date?: string | null;
  unpledge_type?: string | null;
  pledgor_dp_submitted_at?: string | null;
  pledgee_dp_acted_at?: string | null;
  pledgee_dp_outcome?: string | null;
  auto_unpledge_flag?: boolean;
  completed_at?: string | null;
  pledgor_bo_account?: string | null;
  pledgee_bo_account?: string | null;
}

export interface SecurityReturnProjection {
  security_return_id: string;
  loan_closure_id: string;
  security_package_id: string | null;
  status: string;
  version: number;
  completed_at: string | null;
  items: SecurityReturnItemProjection[];
  idempotency_replayed: boolean;
  available_actions: string[];
}

export interface ArchiveRecordProjection {
  archive_record_id: string;
  loan_closure_id: string;
  loan_account_id: string;
  file_location_physical: string | null;
  file_location_digital: string | null;
  retention_start_date: string;
  retention_until_date: string;
  archived_by_user_id: string;
  archived_by_role_code: string;
  archived_at: string;
  destruction_eligible: boolean;
  destruction_certificate_id: string | null;
  idempotency_replayed: boolean;
  available_actions: string[];
}

export const fetchDefaultCases = () =>
  authenticatedPaginatedRequest<DefaultCaseProjection>('/api/v1/default-cases/?page_size=100');

export const fetchDefaultCase = (defaultCaseId: string) =>
  authenticatedRequest<DefaultCaseProjection>(`/api/v1/default-cases/${defaultCaseId}/`);

export const fetchRecoveryCases = fetchDefaultCases;

export const fetchRecoveryApprovalCase = (approvalCaseId: string) =>
  authenticatedRequest<RecoveryApprovalProjection>(`/api/v1/approval-cases/${approvalCaseId}/`);

export const createRecoveryDecision = (
  defaultCaseId: string,
  body: { approval_case_id: string; decision: string; decision_reason: string },
) => authenticatedRequest<RecoveryDecisionProjection>(
  `/api/v1/default-cases/${defaultCaseId}/recovery-decision/`,
  { method: 'POST', body },
);

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

export const fetchClosureReadiness = (loanAccountId: string) =>
  authenticatedRequest<ClosureReadinessProjection>(
    `/api/v1/loan-accounts/${loanAccountId}/closure-readiness/`,
  );

export const closeLoan = (
  loanAccountId: string,
  input: { closure_notes: string; idempotency_key: string },
) => authenticatedRequest<LoanClosureProjection>(
  `/api/v1/loan-accounts/${loanAccountId}/closure/`,
  {
    method: 'POST',
    body: {
      closure_type: 'full_repayment',
      closure_notes: input.closure_notes,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchNoc = (loanClosureId: string) =>
  authenticatedRequest<NocProjection>(`/api/v1/loan-closures/${loanClosureId}/noc/`);

export const issueNoc = (
  loanClosureId: string,
  input: {
    document_id: string;
    delivery_mode: 'email';
    recipient_email: string;
    signatory_user_id: string;
    idempotency_key: string;
  },
) => authenticatedRequest<NocProjection>(
  `/api/v1/loan-closures/${loanClosureId}/noc/`,
  {
    method: 'POST',
    body: {
      document_id: input.document_id,
      delivery_mode: input.delivery_mode,
      recipient_email: input.recipient_email,
      signatory_user_id: input.signatory_user_id,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const recordSecurityReturn = (
  loanClosureId: string,
  input: { payload: Record<string, unknown>; idempotency_key: string },
) => authenticatedRequest<SecurityReturnProjection>(
  `/api/v1/loan-closures/${loanClosureId}/security-return/`,
  {
    method: 'POST',
    body: input.payload,
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchArchiveRecord = (loanClosureId: string) =>
  authenticatedRequest<ArchiveRecordProjection>(
    `/api/v1/loan-closures/${loanClosureId}/archive/`,
  );

export const archiveLoanFile = (
  loanClosureId: string,
  input: {
    file_location_physical: string;
    file_location_digital: string;
    idempotency_key: string;
  },
) => authenticatedRequest<ArchiveRecordProjection>(
  `/api/v1/loan-closures/${loanClosureId}/archive/`,
  {
    method: 'POST',
    body: {
      file_location_physical: input.file_location_physical,
      file_location_digital: input.file_location_digital,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);
