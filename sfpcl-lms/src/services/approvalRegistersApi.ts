import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

export interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedResult<T> {
  items: T[];
  pagination: Pagination;
}

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
  borrower_name: string;
  borrower_type: string;
  requested_amount: string | null;
  eligible_amount: string | null;
  recommended_amount: string | null;
  sanctioned_amount: string | null;
  approval_authority: string;
  approver_names: string[];
  approval_date: string;
  decision: 'sanctioned' | 'rejected';
  reasons: string;
  exception_reference: SanctionRegisterExceptionReference | null;
  conflict_abstention_details: SanctionRegisterConflictDetail[];
  general_meeting_approval_reference: SanctionRegisterMeetingReference | null;
  recorded_at: string;
}

export interface RegisterApprover {
  role_code: string;
  user_id: string;
  full_name: string;
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
  risk_assessment: string;
  status: 'pending' | 'approved' | 'rejected';
  case_status: string;
  conflict_block_reason: string | null;
  authority_applied_summary: string;
  route_approvers: RegisterApprover[];
  required_approvers: RegisterApprover[];
  approval_actions: Array<RegisterApprover & { approval_action_id: string; comments: string }>;
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

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  pagination?: Pagination;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, unknown>;
  };
}

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

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
  return listRequest<CreditSanctionRegisterRow>(`/api/v1/credit-sanction-register/${query(params)}`);
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
  return listRequest<ExceptionRegisterRow>(`/api/v1/exception-register/${query(params)}`);
};

export const fetchApprovalMatrixRules = async (filters: { page?: number; pageSize?: number } = {}): Promise<PaginatedResult<ApprovalMatrixRule>> => {
  const params = new URLSearchParams();
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  return listRequest<ApprovalMatrixRule>(`/api/v1/approval-matrix-rules/${query(params)}`);
};

export const supersedeApprovalMatrixRule = (
  ruleId: string,
  payload: ApprovalMatrixRuleReplacement,
): Promise<ApprovalConfigurationProposal> => request<ApprovalConfigurationProposal>(
  `/api/v1/approval-matrix-rules/${ruleId}/`,
  'PATCH',
  payload,
);

async function listRequest<T>(path: string): Promise<PaginatedResult<T>> {
  const envelope = await envelopeRequest<T[]>(path);
  return { items: envelope.data ?? [], pagination: envelope.pagination ?? emptyPagination };
}

async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const envelope = await envelopeRequest<T>(path, method, body);
  return envelope.data as T;
}

async function envelopeRequest<T>(path: string, method = 'GET', body?: unknown): Promise<ApiEnvelope<T>> {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  let envelope: ApiEnvelope<T>;
  try {
    envelope = await response.json() as ApiEnvelope<T>;
  } catch {
    throw new AuthSessionError('MALFORMED_RESPONSE', 'The server returned an invalid response.', response.status);
  }
  if (!response.ok || !envelope.success || envelope.data === undefined) {
    const fieldErrors = envelope.error?.field_errors
      ? Object.fromEntries(Object.entries(envelope.error.field_errors).map(([field, value]) => [field, String(value)]))
      : undefined;
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
      fieldErrors,
      envelope.error?.details,
    );
  }
  return envelope;
}

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
