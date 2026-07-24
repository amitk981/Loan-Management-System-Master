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
  actions?: ApplicationAvailableAction[];
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
  available_actions?: ApplicationAvailableAction[];
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

export interface ApplicationWitness {
  witness_id: string;
  loan_application_id: string;
  member_id: string;
  verification_shareholding_id: string | null;
  folio_number: string | null;
  witness_name: string;
  address: string;
  mobile: string;
  pan: { masked: string | null; can_view_full: boolean };
  aadhaar: { masked: string | null; can_view_full: boolean };
  shareholder_verified_flag: boolean;
  verification_status: string;
  verified_at: string | null;
  version: number;
  actions: ApplicationAvailableAction[];
}

export interface ApplicationWitnessCollection {
  items: ApplicationWitness[];
  actions: ApplicationAvailableAction[];
}

export interface CreateApplicationWitnessPayload {
  member_id: string;
  witness_name: string;
  pan: string;
  aadhaar: string;
  address: string;
  mobile: string;
}

export interface ApplicationAvailableAction {
  action_code: string;
  label: string;
  enabled: boolean;
  disabled_reason: string | null;
  required_permission: string;
  required_role: string | null;
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
  required_flag?: string | boolean;
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

export interface ApplicationCompleteness {
  loan_application_id: string;
  application_reference_number: string | null;
  application_status: string;
  current_stage: string;
  completeness_status: string;
  member: StaffApplicationMember;
  nominee: ApplicationNomineeSummary | null;
  nominee_selection_status: string;
  required_checklist_items: ApplicationDocumentChecklistItem[];
  blocking_document_types: string[];
  can_generate_reference: boolean;
  available_actions: ApplicationAvailableAction[];
}

export const joinChecklistProjections = (
  completeness: ApplicationCompleteness,
  documents: ApplicationDocumentChecklist,
): ApplicationCompleteness => {
  if (documents.loan_application_id !== completeness.loan_application_id) {
    throw new Error('Checklist projections disagree on the loan application.');
  }
  const documentRows = new Map(documents.items.map(item => [item.document_type, item]));
  if (documentRows.size !== completeness.required_checklist_items.length) {
    throw new Error('Checklist projections disagree on required document types.');
  }
  const required_checklist_items = completeness.required_checklist_items.map(item => {
    const document = documentRows.get(item.document_type);
    const same = document
      && document.submission_status === item.submission_status
      && document.verification_status === item.verification_status
      && (document.latest_application_document_id ?? null) === (item.latest_application_document_id ?? null);
    if (!same) throw new Error(`Checklist projections disagree for ${item.document_type}.`);
    return { ...item, ...document, complete: item.complete, reason_code: item.reason_code };
  });
  return { ...completeness, required_checklist_items };
};

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
  available_actions?: ApplicationAvailableAction[];
}

export interface ReturnWithDeficienciesPayload {
  communication_mode: string;
  message: string;
  items: Array<{ item_code: string; remarks?: string }>;
}

export interface ReturnedApplicationDeficiencies extends ApplicationDeficiencies {
  application_reference_number: string | null;
  application_status: string;
  current_stage: string;
  completeness_status: string;
  communication_mode: string;
  message: string;
}

export interface ApplicationRejectionNote {
  rejection_note_id: string;
  loan_application_id?: string;
  note_status: string;
  rejection_stage?: string;
  rejection_reason_category?: string;
}

export interface RejectionNotePayload {
  rejection_stage: 'completeness';
  rejection_reason_category: string;
  detailed_reason: string;
  reapply_allowed_flag: boolean;
  communication_mode: string;
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

export const applicationFiltersFromLocation = <T extends string>(
  search: string,
  allowedStatuses: readonly T[],
): {
  status: T;
  currentStage?: string;
} => {
  const params = new URLSearchParams(search);
  const status = params.get('status');
  return {
    status: status && allowedStatuses.includes(status as T)
      ? status as T
      : allowedStatuses[0],
    currentStage: params.get('current_stage') || undefined,
  };
};

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

export const fetchApplicationWitnesses = async (applicationId: string): Promise<ApplicationWitnessCollection> => {
  const envelope = await request<ApplicationWitness[]>(`/api/v1/loan-applications/${applicationId}/witnesses/`);
  return { items: envelope.data ?? [], actions: (envelope as ApiEnvelope<ApplicationWitness[]> & { actions?: ApplicationAvailableAction[] }).actions ?? [] };
};

export const createApplicationWitness = async (
  applicationId: string,
  payload: CreateApplicationWitnessPayload,
): Promise<ApplicationWitness> => {
  const envelope = await request<ApplicationWitness>(`/api/v1/loan-applications/${applicationId}/witnesses/`, 'POST', payload);
  return envelope.data as ApplicationWitness;
};

export const updateApplicationWitness = async (
  applicationId: string,
  witnessId: string,
  payload: { version: number; witness_name?: string; address?: string; mobile?: string; pan?: string; aadhaar?: string },
): Promise<ApplicationWitness> => {
  const envelope = await request<ApplicationWitness>(`/api/v1/loan-applications/${applicationId}/witnesses/${witnessId}/`, 'PATCH', payload);
  return envelope.data as ApplicationWitness;
};

export const fetchApplicationDocumentChecklist = async (
  applicationId: string,
): Promise<ApplicationDocumentChecklist> => {
  const envelope = await request<ApplicationDocumentChecklist>(`/api/v1/loan-applications/${applicationId}/document-checklist/`);
  return envelope.data ?? { loan_application_id: applicationId, items: [] };
};

export const fetchApplicationCompleteness = async (
  applicationId: string,
): Promise<ApplicationCompleteness> => {
  const envelope = await request<ApplicationCompleteness>(`/api/v1/loan-applications/${applicationId}/completeness-check/`);
  return envelope.data as ApplicationCompleteness;
};

export const fetchApplicationDeficiencies = async (
  applicationId: string,
): Promise<ApplicationDeficiencies> => {
  const envelope = await request<ApplicationDeficiencies>(`/api/v1/loan-applications/${applicationId}/deficiencies/`);
  return envelope.data ?? { loan_application_id: applicationId, items: [], available_actions: [] };
};

export const passApplicationCompleteness = async (
  applicationId: string,
): Promise<StaffApplication> => {
  const envelope = await request<StaffApplication>(`/api/v1/loan-applications/${applicationId}/completeness-check/pass/`, 'POST', {});
  return envelope.data as StaffApplication;
};

export const returnApplicationWithDeficiencies = async (
  applicationId: string,
  payload: ReturnWithDeficienciesPayload,
): Promise<ReturnedApplicationDeficiencies> => {
  const envelope = await request<ReturnedApplicationDeficiencies>(`/api/v1/loan-applications/${applicationId}/return-with-deficiencies/`, 'POST', payload);
  return envelope.data as ReturnedApplicationDeficiencies;
};

export const resolveApplicationDeficiency = async (
  deficiencyId: string,
  payload: { resolution_notes: string },
): Promise<ApplicationDeficiency> => {
  const envelope = await request<ApplicationDeficiency>(`/api/v1/deficiencies/${deficiencyId}/resolve/`, 'POST', payload);
  return envelope.data as ApplicationDeficiency;
};

export const createApplicationRejectionNote = async (
  applicationId: string,
  payload: RejectionNotePayload,
): Promise<ApplicationRejectionNote> => {
  const envelope = await request<ApplicationRejectionNote>(`/api/v1/loan-applications/${applicationId}/rejection-note/`, 'POST', payload);
  return envelope.data as ApplicationRejectionNote;
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
