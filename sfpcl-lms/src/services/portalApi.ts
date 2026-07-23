import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  pagination?: { page: number; page_size: number; total_count: number; total_pages: number };
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

export interface PortalKycCorrection {
  kyc_correction_request_id: string;
  status: 'submitted' | 'under_review' | 'approved' | 'rejected';
  changes: Partial<Record<'pan' | 'aadhaar' | 'mobile_number' | 'email' | 'registered_address', string>>;
  reason: string;
  rejection_reason: string | null;
  submitted_at: string;
  review_started_at: string | null;
  decided_at: string | null;
  evidence: {
    document_id: string;
    file_name: string;
    mime_type: string | null;
    uploaded_at: string;
  }[];
}

export interface PortalKycCorrectionList {
  items: PortalKycCorrection[];
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

export interface PortalDisbursementTimelineItem {
  code: string;
  label: string;
  status: 'complete' | 'pending' | 'blocked';
  completed_at: string | null;
}

export interface PortalDisbursementStatus {
  loan_application_id: string;
  loan_account_id: string | null;
  status_code: string;
  status_label: string;
  sanctioned_amount: string | null;
  disbursement_amount: string | null;
  destination_account_last4: string | null;
  disbursed_at: string | null;
  bank_reference_last4: string | null;
  advice_available: boolean;
  timeline: PortalDisbursementTimelineItem[];
}

export interface PortalLoanAccountSummary {
  loan_account_id: string;
  loan_account_number: string;
  application_id: string;
  application_reference: string | null;
  status: string;
  closure_status: 'active' | 'closed';
  disbursed_amount: string;
  principal_outstanding: string;
  next_due_date: string | null;
  next_due_amount: string | null;
}

export interface PortalLoanAccountDetail extends PortalLoanAccountSummary {
  interest_outstanding: string;
  charges_outstanding: string;
  total_outstanding: string;
  repayment_route: 'direct' | 'subsidiary_deduction' | 'both';
  closed_at: string | null;
}

export interface PortalLoanScheduleItem {
  schedule_id: string;
  installment_number: number;
  due_date: string;
  principal_due: string;
  interest_due: string;
  charges_due: string;
  total_due: string;
  paid_principal: string;
  paid_interest: string;
  paid_amount: string;
  status: string;
}

export interface PortalRepaymentHistoryItem {
  repayment_id: string;
  receipt_date: string;
  amount_received: string;
  allocated_to_principal: string;
  allocated_to_interest: string;
  payment_mode: string;
  repayment_source: string;
  reference: string;
  acknowledgement: null;
  status: 'confirmed';
}

export interface PortalInterestInvoiceSummary {
  invoice_id: string;
  invoice_number: string;
  invoice_date: string;
  financial_year: string;
  interest_amount: string;
  status: 'issued';
}

export interface PortalDirectRepaymentInstructions {
  available: boolean;
  projection_version: string | null;
  approved_at: string | null;
  beneficiary_name: string | null;
  bank_name: string | null;
  account_number_masked: string | null;
  ifsc: string | null;
  required_narration: string;
  amount_due: string;
  proof_submission_enabled: false;
  available_actions: string[];
  disclaimer: string;
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
export const fetchPortalKycCorrections = () => request<PortalKycCorrectionList>('/api/v1/portal/kyc-corrections/');
export const submitPortalKycCorrection = async (
  field: 'pan' | 'aadhaar' | 'mobile_number' | 'email' | 'registered_address',
  value: string,
  reason: string,
  file: File,
) => {
  const formData = new FormData();
  formData.append('file', file, file.name);
  formData.append('document_type', field === 'pan' || field === 'aadhaar' ? field : 'photo');
  formData.append('self_attested_flag', field === 'pan' || field === 'aadhaar' ? 'true' : 'false');
  const evidence = await request<{ document_id: string }>(
    '/api/v1/portal/kyc-corrections/evidence/',
    { method: 'POST', formData },
  );
  return request<PortalKycCorrection>('/api/v1/portal/kyc-corrections/', {
    method: 'POST',
    body: {
      changes: {
        [field]: field === 'registered_address'
          ? { line1: value.trim() }
          : field === 'pan'
            ? value.trim().toUpperCase()
            : value.trim(),
      },
      reason: reason.trim(),
      evidence_document_ids: [evidence.document_id],
    },
  });
};
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
export const fetchPortalDisbursementStatus = (applicationId: string) => request<PortalDisbursementStatus>(
  `/api/v1/portal/applications/${applicationId}/disbursement-status/`,
);
export const fetchPortalLoanAccounts = () => requestAllPages<PortalLoanAccountSummary>('/api/v1/portal/loan-accounts/?page=1&page_size=100');
export const fetchPortalLoanAccount = (loanAccountId: string) => request<PortalLoanAccountDetail>(`/api/v1/portal/loan-accounts/${loanAccountId}/`);
export const fetchPortalLoanSchedule = (loanAccountId: string) => requestAllPages<PortalLoanScheduleItem>(`/api/v1/portal/loan-accounts/${loanAccountId}/schedule/?page=1&page_size=100`);
export const fetchPortalRepaymentHistory = (loanAccountId: string) => requestAllPages<PortalRepaymentHistoryItem>(`/api/v1/portal/loan-accounts/${loanAccountId}/repayments/?page=1&page_size=100`);
export const fetchPortalInterestInvoices = (loanAccountId: string) => requestAllPages<PortalInterestInvoiceSummary>(`/api/v1/portal/loan-accounts/${loanAccountId}/invoices/?page=1&page_size=100`);
export const fetchPortalDirectRepaymentInstructions = (loanAccountId: string) => request<PortalDirectRepaymentInstructions>(`/api/v1/portal/loan-accounts/${loanAccountId}/direct-instructions/`);
export const downloadPortalDisbursementAdvice = async (applicationId: string) => {
  const descriptor = await request<PortalDownloadDescriptor>(
    `/api/v1/portal/applications/${applicationId}/disbursement-advice/download-capability/`,
    { method: 'POST', body: {} },
  );
  const content = await fetchPortalDocumentContent(descriptor.download_url);
  openPortalDocumentBlob(content);
};
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

export const openPortalDocumentBlob = (content: Blob) => {
  const url = URL.createObjectURL(content);
  window.open(url, '_blank', 'noopener,noreferrer');
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
};

async function request<T>(path: string, options: { method?: 'GET' | 'POST' | 'PATCH'; body?: unknown; formData?: FormData } = {}): Promise<T> {
  const envelope = await requestEnvelope<T>(path, options);
  return envelope.data as T;
}

async function requestAllPages<T>(path: string): Promise<T[]> {
  const first = await requestEnvelope<T[]>(path);
  const rows = [...(first.data ?? [])];
  const totalPages = first.pagination?.total_pages ?? 1;
  for (let page = 2; page <= totalPages; page += 1) {
    const url = new URL(path, 'http://portal.local');
    url.searchParams.set('page', String(page));
    const next = await requestEnvelope<T[]>(`${url.pathname}?${url.searchParams.toString()}`);
    rows.push(...(next.data ?? []));
  }
  return rows;
}

async function requestEnvelope<T>(path: string, options: { method?: 'GET' | 'POST' | 'PATCH'; body?: unknown; formData?: FormData } = {}): Promise<ApiEnvelope<T>> {
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
  return envelope;
}

const normalizeFieldErrors = (fieldErrors?: Record<string, unknown>) => {
  if (!fieldErrors) return undefined;
  return Object.fromEntries(
    Object.entries(fieldErrors).map(([field, value]) => [field, String(value)]),
  );
};
