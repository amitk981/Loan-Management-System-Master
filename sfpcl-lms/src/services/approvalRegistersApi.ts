import {
  authenticatedPaginatedRequest,
  authenticatedRequest,
  type PaginatedResult,
} from './authSession';
export type { Pagination, PaginatedResult } from './authSession';

export interface SanctionRegisterExceptionReference {
  exception_register_entry_id: string;
  exception_type: string;
  business_reason: string;
  status: string;
  cycle_number: number;
}

export interface SanctionRegisterConflictDetail {
  type: 'conflict' | 'abstention';
  user_id: string;
  full_name: string | null;
  conflict_code: string;
  reason: string;
  approval_action_id: string | null;
  acted_at: string | null;
}

export interface SanctionRegisterMeetingReference {
  general_meeting_approval_id: string;
  approval_status: string;
  meeting_date: string;
  related_party_type: string;
  related_party_user_id: string | null;
  notice_document_id: string;
  minutes_document_id: string;
  resolution_document_id: string;
}

export interface CreditSanctionRegisterRow {
  credit_sanction_register_entry_id: string;
  approval_case_id: string;
  loan_application_id: string;
  sanction_decision_id: string | null;
  workflow_event_id: string;
  application_number: string;
  entry_number: string;
  borrower_name: string;
  borrower_type: string;
  folio_number: string | null;
  loan_type: string | null;
  purpose: { category: string | null; description: string | null };
  risk: { overall_risk_rating?: string | null; [key: string]: unknown };
  requested_amount: string | null;
  eligible_amount: string | null;
  recommended_amount: string | null;
  sanctioned_amount: string | null;
  approval_authority: string;
  approver_names: string[];
  approver_decisions: Array<RegisterApprover & {
    approval_action_id: string;
    comments: string;
  }>;
  approval_date: string;
  decision: 'sanctioned' | 'rejected';
  reasons: string;
  rejection_reason: string | null;
  conditions: string | null;
  communication: {
    communication_id: string;
    status: string;
    sent_at: string | null;
  } | null;
  exception_reference: SanctionRegisterExceptionReference | null;
  conflict_abstention_details: SanctionRegisterConflictDetail[];
  general_meeting_approval_reference: SanctionRegisterMeetingReference | null;
  recorded_at: string;
}

export interface RegisterApprover {
  role_code: string;
  user_id: string;
  full_name: string | null;
  decision?: string | null;
  acted_at?: string | null;
  replacement_for_user_id?: string;
}

export interface ExceptionRegisterRow {
  exception_register_entry_id: string;
  loan_application_id: string | null;
  loan_account_id: string | null;
  approval_case_id: string;
  cycle_number: number;
  exception_type: 'exceeds_loan_limit' | 'stage_bypass' | 'waiver';
  description: string;
  business_reason: string;
  borrower_name: string | null;
  financial_impact: string | null;
  requested_by: { user_id: string; full_name: string } | null;
  decision_date: string | null;
  risk_assessment: string;
  status: 'pending' | 'approved' | 'rejected';
  case_status: string;
  conflict_block_reason: string | null;
  authority_applied_summary: string;
  route_approvers: RegisterApprover[];
  required_approvers: RegisterApprover[];
  approval_actions: Array<RegisterApprover & { approval_action_id: string; comments: string }>;
  supporting_documents: Array<{
    document_id: string;
    file_name: string;
    mime_type: string | null;
    file_size_bytes: number | null;
    sensitivity_level: string;
    uploaded_at: string;
  }>;
  created_at: string;
  closed_at: string | null;
}

export interface ApprovalMatrixRule {
  approval_matrix_rule_id: string;
  decision_type: string;
  amount_min: string | null;
  amount_max: string | null;
  condition_code: string | null;
  required_approver_roles: string[];
  required_director_count: number;
  authority_summary: string;
  minimum_approver_count: number;
  joint_approval_required_flag: boolean;
  register_required: string | null;
  effective_from: string;
  effective_to: string | null;
  status: 'active' | 'inactive' | 'superseded';
  version_number: string;
}

export interface ApprovalMatrixRuleReplacement {
  decision_type: string;
  amount_min: string | null;
  amount_max: string | null;
  condition_code: string | null;
  required_approver_roles: string[];
  required_director_count: number;
  joint_approval_required_flag: boolean;
  register_required: string | null;
  effective_from: string;
  effective_to: string | null;
  version_number: string;
  reason: string;
}

export interface ConfigurationProposalAction {
  action_code: string;
  label: string;
  enabled: boolean;
  disabled_reason: string | null;
  required_permission: string;
  confirmation_required: boolean;
}

export interface ApprovalConfigurationProposal {
  approval_configuration_proposal_id: string;
  proposal_type: string;
  target_entity_id: string | null;
  payload: Omit<ApprovalMatrixRuleReplacement, 'reason'>;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  version: number;
  made_by_user_id: string;
  decided_by_user_id: string | null;
  decided_at: string | null;
  rejection_reason: string | null;
  available_actions: ConfigurationProposalAction[];
}

export const fetchCreditSanctionRegister = async (filters: {
  financialYear?: string;
  decision?: 'sanctioned' | 'rejected';
  page?: number;
  pageSize?: number;
} = {}): Promise<PaginatedResult<CreditSanctionRegisterRow>> => {
  const params = new URLSearchParams();
  setParam(params, 'financial_year', filters.financialYear);
  setParam(params, 'decision', filters.decision);
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  return authenticatedPaginatedRequest<CreditSanctionRegisterRow>(`/api/v1/credit-sanction-register/${query(params)}`);
};

export const fetchExceptionRegister = async (filters: {
  status?: 'pending' | 'approved' | 'rejected';
  exceptionType?: 'exceeds_loan_limit' | 'stage_bypass' | 'waiver';
  page?: number;
  pageSize?: number;
} = {}): Promise<PaginatedResult<ExceptionRegisterRow>> => {
  const params = new URLSearchParams();
  setParam(params, 'status', filters.status);
  setParam(params, 'exception_type', filters.exceptionType);
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  return authenticatedPaginatedRequest<ExceptionRegisterRow>(`/api/v1/exception-register/${query(params)}`);
};

export const fetchApprovalMatrixRules = async (filters: { page?: number; pageSize?: number } = {}): Promise<PaginatedResult<ApprovalMatrixRule>> => {
  const params = new URLSearchParams();
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  return authenticatedPaginatedRequest<ApprovalMatrixRule>(`/api/v1/approval-matrix-rules/${query(params)}`);
};

export const supersedeApprovalMatrixRule = (
  ruleId: string,
  payload: ApprovalMatrixRuleReplacement,
): Promise<ApprovalConfigurationProposal> => authenticatedRequest<ApprovalConfigurationProposal>(
  `/api/v1/approval-matrix-rules/${ruleId}/`,
  { method: 'PATCH', body: payload },
);

function setParam(params: URLSearchParams, key: string, value?: string): void {
  if (value) params.set(key, value);
}

function setNumberParam(params: URLSearchParams, key: string, value?: number): void {
  if (value !== undefined) params.set(key, String(value));
}

function query(params: URLSearchParams): string {
  const value = params.toString();
  return value ? `?${value}` : '';
}
