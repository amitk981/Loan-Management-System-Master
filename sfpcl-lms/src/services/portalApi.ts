import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string; field_errors?: Record<string, unknown> };
}

export interface MaskedValue {
  masked: string | null;
  can_view_full?: boolean;
}

export interface PortalMember {
  member_id: string;
  member_number: string | null;
  member_type: string;
  legal_name?: string;
  display_name: string;
  folio_number: string;
  membership_status: string;
  kyc_status: string;
  default_status: string;
  mobile_number?: string | null;
  email?: string | null;
  pan?: MaskedValue;
  aadhaar?: MaskedValue;
  registered_address?: Record<string, string | null>;
  share_summary?: {
    number_of_shares: number | null;
    holding_mode: string | null;
    available_share_count: number | null;
  };
  active_member_status?: { status: string | null; verified_at: string | null };
  individual_profile?: {
    primary_crop: string | null;
    land_area_under_cultivation_acres: string | null;
  } | null;
  producer_institution_profile?: { produce_supply_years: string | null } | null;
}

export interface PortalDashboard {
  member: PortalMember;
  application_counts: Record<string, number>;
  loan_counts: Record<string, number>;
  pending_actions: Record<string, number>;
  notices: { title: string; message?: string; created_at?: string | null }[];
}

export interface PortalProfile {
  member: PortalMember;
  nominees: PortalNominee[];
  shareholdings: { folio_number: string; number_of_shares: number; holding_mode: string; available_share_count: number; status: string }[];
  land_holdings: { survey_number: string | null; village: string | null; area_acres: string; verification_status: string }[];
  crop_plans: { season: string | null; crop_type: string; planned_area_acres: string; verification_status: string }[];
  bank_accounts: { account_holder_name: string; account_number: MaskedValue; ifsc: string; bank_name: string | null; branch_name: string | null; verification_status: string }[];
  cancelled_cheques: { account_number: MaskedValue; ifsc: string; branch_name: string | null; verification_status: string }[];
  kyc_profile: { kyc_status: string; rekyc_due_date: string | null; risk_rating: string | null } | null;
}

export interface PortalNominee {
  nominee_id?: string;
  nominee_name: string;
  date_of_birth?: string | null;
  relationship_to_borrower: string | null;
  age_at_application?: number | null;
  minor_flag?: boolean;
  signature_required_flag?: boolean;
  pan: MaskedValue;
  aadhaar: MaskedValue;
  kyc_status: string;
}

export interface PortalProduceSupply {
  records: { financial_year: string; crop_type: string | null; quantity: string | null; value_amount: string | null; verified_flag: boolean }[];
  summary: { continuous_supply_years?: string | null; total_quantity?: string | null; total_value?: string | null };
  source_status: string;
}

export interface PortalApplication {
  loan_application_id: string;
  application_reference_number: string | null;
  display_reference: string;
  application_date: string;
  submitted_at: string | null;
  required_loan_amount: string | null;
  declared_purpose: string;
  purpose_category: string;
  loan_type_requested: string | null;
  application_status: string;
  current_stage: string;
  completeness_status: string;
  pending_with: string;
  borrower_action: string;
  open_deficiency_count: number;
  created_at: string | null;
  updated_at: string | null;
  member?: PortalMember;
  requested_tenure_months?: number | null;
  borrower_request_notes?: string;
  terms_acceptance_flag?: boolean;
  nominee?: {
    nominee_id: string;
    nominee_name: string;
    date_of_birth?: string | null;
    age_at_application: number | null;
    minor_flag: boolean;
    kyc_status: string;
    relationship_to_borrower: string | null;
    signature_required_flag: boolean;
  } | null;
  timeline?: { event: string; at: string | null; owner: string }[];
  deficiencies?: {
    deficiency_id: string;
    item_code: string;
    deficiency_type: string;
    description: string;
    resolution_status: string;
    raised_at: string | null;
  }[];
}

export interface PortalApplicationList {
  items: PortalApplication[];
}

export interface PortalDeficiencyResponseDocument {
  document_id: string;
  file_name: string;
  mime_type: string | null;
  file_size_bytes: number;
  checksum_sha256: string | null;
  uploaded_at: string;
  action_url: string;
}

export interface PortalDeficiencyItem {
  deficiency_id: string;
  item_code: string;
  deficiency_type: string;
  description: string;
  resolution_status: string;
  raised_at: string;
  upload_contract: {
    document_category: string;
    sensitivity_level: string;
    allowed_extensions: string[];
    max_size_bytes: number;
  };
  response: {
    deficiency_response_id: string;
    response_status: 'responded';
    response_remark: string | null;
    document: PortalDeficiencyResponseDocument;
    responded_at: string;
  } | null;
  draft: {
    response_remark: string;
    updated_at: string;
  } | null;
}

export interface PortalDeficiencyProjection {
  loan_application_id: string;
  application_reference_number: string | null;
  application_status: string;
  deficiency_note_action_url: string;
  resubmission_allowed: boolean;
  items: PortalDeficiencyItem[];
}

export interface PortalDeficiencyResubmission {
  loan_application_id: string;
  application_status: string;
  completeness_status: string;
  current_stage: string;
  pending_with: string;
  responded_deficiency_count: number;
}

export interface PortalApplicationLimitProjection {
  status: 'available' | 'unavailable';
  unavailable_reason: string | null;
  shareholding_based_limit_amount: string | null;
  land_based_limit_amount: string | null;
  final_eligible_loan_amount: string | null;
  requested_amount: string | null;
  amount_within_limit_flag: boolean | null;
  exception_required_flag: boolean | null;
  calculated_as_of_date: string | null;
  calculation_rule_version: string | null;
}

export interface PortalDocumentationDownload {
  file_name: string;
  mime_type: string | null;
  action_url: string;
}

export interface PortalDocumentationAction {
  action_code: string;
  label: string;
  section: string;
  required: boolean;
  applicable: boolean;
  status: string;
  updated_date: string | null;
  instruction: string;
  note: string | null;
  upload_allowed: boolean;
  reupload_allowed: boolean;
  download: PortalDocumentationDownload | null;
}

export interface PortalDocumentationProjection {
  loan_application_id: string;
  application_reference_number: string | null;
  application_status: string;
  availability: 'available' | 'blocked';
  unavailable_reason: string | null;
  actions: PortalDocumentationAction[];
}

export interface PortalDocumentationUploadResult {
  action_code: string;
  status: string;
  document: {
    document_id: string;
    file_name: string;
    mime_type: string | null;
    file_size_bytes: number;
    checksum_sha256: string;
    uploaded_at: string;
  };
}

export interface PortalDownloadDescriptor {
  download_url: string;
  expires_at: string;
}

export interface PortalApplicationDraftPayload {
  nominee_id?: string | null;
  required_loan_amount?: string;
  requested_tenure_months?: number | null;
  declared_purpose?: string;
  purpose_category?: string;
  loan_type_requested?: string;
  borrower_request_notes?: string;
  terms_acceptance_flag?: boolean;
}

export const fetchPortalDashboard = () => request<PortalDashboard>('/api/v1/portal/dashboard/');
export const fetchPortalProfile = () => request<PortalProfile>('/api/v1/portal/profile/');
export const fetchPortalProduceSupply = () => request<PortalProduceSupply>('/api/v1/portal/produce-supply/');
export const fetchPortalApplicationLimitProjection = (requestedAmount?: string) => request<PortalApplicationLimitProjection>(
  `/api/v1/portal/application-limit-projection/${requestedAmount ? `?requested_amount=${encodeURIComponent(requestedAmount)}` : ''}`,
);
export const fetchPortalApplications = () => request<PortalApplicationList>('/api/v1/portal/applications/');
export const fetchPortalApplication = (applicationId: string) => request<PortalApplication>(`/api/v1/portal/applications/${applicationId}/`);
export const createPortalApplicationDraft = (payload: PortalApplicationDraftPayload) => request<PortalApplication>('/api/v1/portal/applications/', { method: 'POST', body: payload });
export const updatePortalApplicationDraft = (applicationId: string, payload: PortalApplicationDraftPayload) => request<PortalApplication>(`/api/v1/portal/applications/${applicationId}/`, { method: 'PATCH', body: payload });
export const submitPortalApplication = (applicationId: string) => request<PortalApplication>(`/api/v1/portal/applications/${applicationId}/submit/`, { method: 'POST', body: {} });
export const fetchPortalApplicationDeficiencies = (applicationId: string) => request<PortalDeficiencyProjection>(`/api/v1/portal/applications/${applicationId}/deficiencies/`);
export const uploadPortalDeficiencyResponse = (applicationId: string, item: PortalDeficiencyItem, file: File, responseRemark?: string) => {
  const formData = new FormData();
  formData.append('file', file, file.name);
  formData.append('document_category', item.upload_contract.document_category);
  formData.append('sensitivity_level', item.upload_contract.sensitivity_level);
  if (responseRemark?.trim()) formData.append('response_remark', responseRemark.trim());
  return request<{ deficiency_id: string; response_status: string; response: PortalDeficiencyItem['response']; document: PortalDeficiencyResponseDocument }>(
    `/api/v1/portal/applications/${applicationId}/deficiencies/${item.deficiency_id}/upload/`,
    { method: 'POST', formData },
  );
};
export const savePortalDeficiencyResponseDraft = (
  applicationId: string,
  deficiencyId: string,
  responseRemark: string,
) => request<{ deficiency_id: string; response_remark: string; updated_at: string }>(
  `/api/v1/portal/applications/${applicationId}/deficiencies/${deficiencyId}/draft/`,
  { method: 'POST', body: { response_remark: responseRemark.trim() } },
);
export const downloadPortalDeficiencyNote = (applicationId: string) => fetchPortalDocumentContent(
  `/api/v1/portal/applications/${applicationId}/deficiencies/note/`,
);
export const resubmitPortalApplicationDeficiencies = (applicationId: string) => request<PortalDeficiencyResubmission>(
  `/api/v1/portal/applications/${applicationId}/deficiencies/resubmit/`,
  { method: 'POST', body: {} },
);
export const downloadPortalDeficiencyResponse = (actionUrl: string) => {
  if (!actionUrl.startsWith('/api/v1/portal/applications/') || !actionUrl.includes('/deficiencies/')) {
    throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Deficiency response download action is invalid.', 400);
  }
  return request<PortalDownloadDescriptor>(actionUrl);
};
export const fetchPortalDocumentationActions = (applicationId: string) => request<PortalDocumentationProjection>(`/api/v1/portal/applications/${applicationId}/documentation-actions/`);
export const uploadPortalDocumentationAction = (applicationId: string, actionCode: string, file: File, notes?: string) => {
  const formData = new FormData();
  formData.append('file', file, file.name);
  if (notes?.trim()) formData.append('notes', notes.trim());
  return request<PortalDocumentationUploadResult>(
    `/api/v1/portal/applications/${applicationId}/documentation-actions/${actionCode}/upload/`,
    { method: 'POST', formData },
  );
};
export const downloadPortalDocumentationAction = (actionUrl: string) => {
  if (!actionUrl.startsWith('/api/v1/portal/applications/')) {
    throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download action is invalid.', 400);
  }
  return request<PortalDownloadDescriptor>(actionUrl);
};

export const fetchPortalDocumentContent = async (downloadUrl: string) => {
  if (!downloadUrl.startsWith('/api/v1/portal/applications/')) {
    throw new AuthSessionError('INVALID_DOWNLOAD_ACTION', 'Document download URL is invalid.', 400);
  }
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Member portal session is required.', 401);
  const response = await fetch(`${API_BASE_URL}${downloadUrl}`, {
    headers: { Authorization: `Bearer ${session.accessToken}` },
  });
  if (!response.ok) throw new AuthSessionError('DOWNLOAD_FAILED', 'Document download failed.', response.status);
  return response.blob();
};

async function request<T>(path: string, options: { method?: 'GET' | 'POST' | 'PATCH'; body?: unknown; formData?: FormData } = {}): Promise<T> {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Member portal session is required.', 401);
  }
  const method = options.method ?? 'GET';
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(method === 'GET' || options.formData ? {} : { 'Content-Type': 'application/json' }),
    },
    ...(method === 'GET' ? {} : {
      body: options.formData ?? JSON.stringify(options.body ?? {}),
    }),
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
      normalizeFieldErrors(envelope.error?.field_errors),
    );
  }
  return envelope.data;
}

const normalizeFieldErrors = (fieldErrors?: Record<string, unknown>) => {
  if (!fieldErrors) return undefined;
  return Object.fromEntries(
    Object.entries(fieldErrors).map(([field, value]) => [field, String(value)]),
  );
};
