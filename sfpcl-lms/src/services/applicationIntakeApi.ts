import {
  API_BASE_URL,
  AuthSessionError,
  loadStoredAuthSession,
} from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, string>;
  };
  pagination?: Pagination;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface StaffApplicationMember {
  member_id: string;
  display_name: string;
  member_type: string;
  folio_number: string;
  membership_status?: string;
  kyc_status?: string;
}

export interface StaffApplication {
  loan_application_id: string;
  application_reference_number: string | null;
  member: StaffApplicationMember;
  application_date: string;
  required_loan_amount: string | null;
  requested_tenure_months?: number | null;
  declared_purpose?: string;
  purpose_category: string;
  loan_type_requested?: string | null;
  application_status: string;
  current_stage: string;
  completeness_status: string;
  assigned_owner?: { user_id: string; full_name: string } | null;
  tat?: { due_at: string | null; status: string };
  loan_request_register_entry?: LoanRequestRegisterRow | null;
  created_at?: string | null;
  updated_at?: string | null;
  submitted_at?: string | null;
  submitted_by_user_id?: string | null;
  terms_acceptance_flag?: boolean;
  rejection_note?: StaffApplicationRejectionNote | null;
  nominee?: ApplicationNomineeSummary | null;
}

export interface ApplicationNomineeSummary {
  nominee_id: string;
  nominee_name: string;
  age_at_application: number | null;
  minor_flag: boolean;
  kyc_status: string;
  relationship_to_borrower: string | null;
  signature_required_flag: boolean;
}

export interface StaffApplicationRejectionNote {
  rejection_note_id: string;
  note_status: string;
  rejection_stage: string;
  rejection_reason_category: string;
  reapply_allowed_flag: boolean;
  prepared_by_user_id: string;
  approved_by_user_id: string | null;
  communication_mode: string;
  communication_id: string | null;
  sent_by_user_id: string | null;
  sent_at: string | null;
  created_at: string | null;
  updated_at: string | null;
  updated_by_user_id: string | null;
}

export interface ApplicationDocumentChecklistItem {
  document_type: string;
  required_flag?: string;
  submission_status?: string;
  verification_status?: string;
  complete?: boolean;
  reason_code?: string | null;
  latest_application_document_id?: string | null;
}

export interface ApplicationDocumentChecklist {
  loan_application_id: string;
  items: ApplicationDocumentChecklistItem[];
}

export interface ApplicationDeficiency {
  deficiency_id: string;
  item_code: string;
  deficiency_type?: string;
  source_reason_code?: string;
  description: string;
  remarks?: string;
  resolution_status: string;
  raised_at?: string;
  resolved_at?: string | null;
  resolution_notes?: string | null;
}

export interface ApplicationDeficiencies {
  loan_application_id: string;
  items: ApplicationDeficiency[];
}

export interface LoanRequestRegisterRow {
  loan_request_register_entry_id: string;
  loan_application_id: string;
  application_reference_number: string;
  member_id?: string;
  date_received?: string;
  reference_generated_date?: string;
  register_status: string;
  borrower_name: string | null;
  folio_number: string | null;
  member_type: string | null;
  requested_amount: string | null;
  purpose_category?: string | null;
  current_stage?: string | null;
  current_owner_role?: string | null;
  eligibility_status?: string;
  sanction_status?: string;
  documentation_status?: string;
  disbursement_status?: string;
  created_at?: string | null;
}

export interface StaffApplicationFilters {
  search?: string;
  applicationStatus?: string;
  currentStage?: string;
  memberId?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface RegisterFilters {
  search?: string;
  registerStatus?: string;
  currentStage?: string;
  memberType?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface PaginatedResult<T> {
  items: T[];
  pagination: Pagination;
}

export type StaffApplicationPayload = Record<string, string | number | boolean | null | undefined>;

export const fetchStaffApplications = async (
  filters: StaffApplicationFilters = {},
): Promise<PaginatedResult<StaffApplication>> => {
  const params = new URLSearchParams();
  setParam(params, 'search', filters.search);
  setParam(params, 'application_status', filters.applicationStatus);
  setParam(params, 'current_stage', filters.currentStage);
  setParam(params, 'member_id', filters.memberId);
  setParam(params, 'ordering', filters.ordering);
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  const envelope = await request<StaffApplication[]>(`/api/v1/loan-applications/${query(params)}`);
  return { items: envelope.data ?? [], pagination: envelope.pagination ?? emptyPagination };
};

export const fetchLoanRequestRegister = async (
  filters: RegisterFilters = {},
): Promise<PaginatedResult<LoanRequestRegisterRow>> => {
  const params = new URLSearchParams();
  setParam(params, 'search', filters.search);
  setParam(params, 'register_status', filters.registerStatus);
  setParam(params, 'current_stage', filters.currentStage);
  setParam(params, 'member_type', filters.memberType);
  setParam(params, 'ordering', filters.ordering);
  setNumberParam(params, 'page', filters.page);
  setNumberParam(params, 'page_size', filters.pageSize);
  const envelope = await request<LoanRequestRegisterRow[]>(`/api/v1/loan-request-register/${query(params)}`);
  return { items: envelope.data ?? [], pagination: envelope.pagination ?? emptyPagination };
};

export const fetchApplicationDetail = async (applicationId: string): Promise<StaffApplication> => {
  const envelope = await request<StaffApplication>(`/api/v1/loan-applications/${applicationId}/`);
  return envelope.data as StaffApplication;
};

export const fetchApplicationDocumentChecklist = async (
  applicationId: string,
): Promise<ApplicationDocumentChecklist> => {
  const envelope = await request<ApplicationDocumentChecklist>(`/api/v1/loan-applications/${applicationId}/document-checklist/`);
  return envelope.data ?? { loan_application_id: applicationId, items: [] };
};

export const fetchApplicationDeficiencies = async (
  applicationId: string,
): Promise<ApplicationDeficiencies> => {
  const envelope = await request<ApplicationDeficiencies>(`/api/v1/loan-applications/${applicationId}/deficiencies/`);
  return envelope.data ?? { loan_application_id: applicationId, items: [] };
};

export const createStaffApplicationDraft = async (
  payload: StaffApplicationPayload,
): Promise<StaffApplication> => {
  const envelope = await request<StaffApplication>('/api/v1/loan-applications/', 'POST', payload);
  return envelope.data as StaffApplication;
};

export const updateStaffApplicationDraft = async (
  applicationId: string,
  payload: StaffApplicationPayload,
): Promise<StaffApplication> => {
  const envelope = await request<StaffApplication>(`/api/v1/loan-applications/${applicationId}/`, 'PATCH', payload);
  return envelope.data as StaffApplication;
};

export const submitStaffApplication = async (applicationId: string): Promise<StaffApplication> => {
  const envelope = await request<StaffApplication>(`/api/v1/loan-applications/${applicationId}/submit/`, 'POST', {});
  return envelope.data as StaffApplication;
};

const request = async <T>(
  path: string,
  method = 'GET',
  body?: unknown,
): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
      envelope.error?.field_errors,
    );
  }
  return envelope;
};

const query = (params: URLSearchParams) => {
  const value = params.toString();
  return value ? `?${value}` : '';
};

const setParam = (params: URLSearchParams, key: string, value?: string) => {
  if (value && value !== 'all') params.set(key, value);
};

const setNumberParam = (params: URLSearchParams, key: string, value?: number) => {
  if (value) params.set(key, String(value));
};

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};
