import { authenticatedMultipartRequest, authenticatedPaginatedRequest, authenticatedRequest } from './authSession';
export interface RecoveryActionProjection {
  recovery_action_id: string; action_status: 'pending' | 'completed' | 'failed';
  action_type: string; source_security: { security_type: string; security_id: string; status: string };
  initiated_at: string; amount_recovered: string | null; external_sap_status: string;
  interaction_log: Array<{ interaction_at: string; interaction_mode: string; summary: string; grievance_reference: string }>;
  ledger_posting: Record<string, string>; available_actions: Array<{ action_code: string }>;
}
export interface RecoveryCaseProjection {
  default_case_id: string; loan_account_id: string; loan_account_number: string;
  borrower_name: string; total_outstanding: string; default_case_status: string;
  recovery_decision: null | { recovery_decision_id: string; decision: string; status: string; available_actions: Array<{ action_code: string }> };
  recovery_action: RecoveryActionProjection | null;
}
export const fetchRecoveryCases = () => authenticatedPaginatedRequest<RecoveryCaseProjection>('/api/v1/default-cases/?page_size=100');
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
