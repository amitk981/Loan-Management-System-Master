import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string; field_errors?: Record<string, unknown> };
  pagination?: Pagination;
}

interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface MemberProfileDetail {
  member_id: string;
  member_number: string | null;
  member_type: string;
  legal_name: string;
  display_name: string;
  folio_number: string;
  membership_start_date: string | null;
  membership_status: string;
  kyc_status: string;
  rekyc_due_date: string | null;
  default_status: string;
  mobile_number: string | null;
  email: string | null;
  pan: { masked: string | null; can_view_full: boolean };
  aadhaar: { masked: string | null; can_view_full: boolean };
  registered_address: {
    line1: string | null;
    line2: string | null;
    village_city: string | null;
    district: string | null;
    state: string | null;
    pincode: string | null;
  };
  share_summary: {
    number_of_shares: number | null;
    holding_mode: string | null;
    available_share_count: number | null;
  };
  active_member_status: { status: string | null; verified_at: string | null };
  individual_profile: {
    first_name: string;
    middle_name: string | null;
    last_name: string;
    gender: string | null;
    date_of_birth: string | null;
    occupation: string | null;
    land_area_under_cultivation_acres: string | null;
    primary_crop: string | null;
    services_availed_flag: boolean;
    employment_or_service_years: string | null;
  } | null;
  producer_institution_profile: {
    institution_type: string;
    registration_number: string | null;
    authorised_signatory_name: string;
    board_resolution_required_flag: boolean;
    services_availed_flag: boolean;
    produce_supply_years: string | null;
  } | null;
  available_actions: {
    action_code: string;
    label: string;
    enabled: boolean;
    disabled_reason: string | null;
    required_permission: string;
  }[];
}

export interface MemberNomineeDetail {
  nominee_id: string;
  nominee_name: string;
  date_of_birth: string | null;
  age_at_application: number | null;
  gender: string;
  relationship_to_borrower: string | null;
  pan: { masked: string | null; can_view_full: boolean };
  aadhaar: { masked: string | null; can_view_full: boolean };
  kyc_status: string;
  minor_flag: boolean;
  signature_required_flag: boolean;
  created_at: string;
}

export interface MemberNomineeList {
  items: MemberNomineeDetail[];
  pagination: Pagination;
}

export interface MemberShareholdingDetail {
  shareholding_id: string;
  folio_number: string;
  number_of_shares: number;
  holding_mode: string;
  valuation_per_share: string | null;
  valuation_effective_date: string | null;
  pledged_share_count: number;
  available_share_count: number;
  future_shares_pledge_flag: boolean;
  status: string;
}

export interface MemberShareholdingList {
  items: MemberShareholdingDetail[];
  pagination: Pagination;
}

export interface MemberLandHoldingDetail {
  land_holding_id: string;
  document_type: string;
  survey_number: string | null;
  village: string | null;
  taluka: string | null;
  district: string | null;
  state: string | null;
  area_acres: string;
  document_id: string;
  verification_status: string;
  verified_by_user_id: string | null;
  verified_at: string | null;
  created_at: string;
}

export interface MemberLandHoldingList {
  items: MemberLandHoldingDetail[];
  pagination: Pagination;
}

export interface MemberCropPlanDetail {
  crop_plan_id: string;
  loan_application_id: string | null;
  crop_type: string;
  season: string | null;
  planned_area_acres: string;
  estimated_cost_amount: string | null;
  loan_purpose_alignment: string;
  document_id: string | null;
  verification_status: string;
  verified_by_user_id: string | null;
  verified_at: string | null;
  created_at: string;
}

export interface MemberCropPlanList {
  items: MemberCropPlanDetail[];
  pagination: Pagination;
}

export interface CreateMemberNomineePayload {
  nominee_name: string;
  date_of_birth: string;
  gender: string;
  relationship_to_borrower: string;
  pan: string;
  aadhaar: string;
  signature_required_flag: boolean;
}

export interface CreateMemberShareholdingPayload {
  folio_number: string;
  number_of_shares: number;
  holding_mode: string;
  valuation_per_share: string;
  valuation_effective_date: string;
  pledged_share_count: number;
  future_shares_pledge_flag: boolean;
}

export interface CreateMemberLandHoldingPayload {
  document_type: string;
  survey_number: string;
  village: string;
  taluka: string;
  district: string;
  state: string;
  area_acres: string;
  document_id: string;
}

export interface CreateMemberCropPlanPayload {
  loan_application_id: string;
  crop_type: string;
  season: string;
  planned_area_acres: string;
  estimated_cost_amount: string;
  loan_purpose_alignment: string;
  document_id: string;
}

export const fetchMemberProfile = async (memberId: string): Promise<MemberProfileDetail> => {
  const envelope = await request<MemberProfileDetail>(`/api/v1/members/${memberId}/`, 'GET');
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return normalize(envelope.data);
};

export const fetchMemberNominees = async (memberId: string): Promise<MemberNomineeList> => {
  const envelope = await request<MemberNomineeDetail[]>(`/api/v1/members/${memberId}/nominees/`, 'GET');
  return {
    items: normalizeNominees(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

export const createMemberNominee = async (
  memberId: string,
  payload: CreateMemberNomineePayload,
): Promise<MemberNomineeDetail> => {
  const envelope = await request<MemberNomineeDetail>(
    `/api/v1/members/${memberId}/nominees/`,
    'POST',
    payload,
  );
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return normalizeNominee(envelope.data);
};

export const fetchMemberShareholdings = async (memberId: string): Promise<MemberShareholdingList> => {
  const envelope = await request<MemberShareholdingDetail[]>(`/api/v1/members/${memberId}/shareholdings/`, 'GET');
  return {
    items: normalizeShareholdings(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

export const createMemberShareholding = async (
  memberId: string,
  payload: CreateMemberShareholdingPayload,
): Promise<MemberShareholdingDetail> => {
  const envelope = await request<MemberShareholdingDetail>(
    `/api/v1/members/${memberId}/shareholdings/`,
    'POST',
    payload,
  );
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return normalizeShareholding(envelope.data);
};

export const fetchMemberLandHoldings = async (memberId: string): Promise<MemberLandHoldingList> => {
  const envelope = await request<MemberLandHoldingDetail[]>(`/api/v1/members/${memberId}/land-holdings/`, 'GET');
  return {
    items: normalizeLandHoldings(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

export const createMemberLandHolding = async (
  memberId: string,
  payload: CreateMemberLandHoldingPayload,
): Promise<MemberLandHoldingDetail> => {
  const envelope = await request<MemberLandHoldingDetail>(
    `/api/v1/members/${memberId}/land-holdings/`,
    'POST',
    payload,
  );
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return normalizeLandHolding(envelope.data);
};

export const fetchMemberCropPlans = async (memberId: string): Promise<MemberCropPlanList> => {
  const envelope = await request<MemberCropPlanDetail[]>(`/api/v1/members/${memberId}/crop-plans/`, 'GET');
  return {
    items: normalizeCropPlans(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

export const createMemberCropPlan = async (
  memberId: string,
  payload: CreateMemberCropPlanPayload,
): Promise<MemberCropPlanDetail> => {
  const envelope = await request<MemberCropPlanDetail>(
    `/api/v1/members/${memberId}/crop-plans/`,
    'POST',
    payload,
  );
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return normalizeCropPlan(envelope.data);
};

const request = async <T>(
  path: string,
  method: 'GET' | 'POST',
  body?: unknown,
): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(method === 'POST' ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(method === 'POST' ? { body: JSON.stringify(body ?? {}) } : {}),
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
      normalizeFieldErrors(envelope.error?.field_errors),
    );
  }
  return envelope;
};

const normalize = (profile: MemberProfileDetail): MemberProfileDetail => ({
  ...profile,
  member_id: String(profile.member_id ?? ''),
  member_number: textOrNull(profile.member_number),
  display_name: String(profile.display_name || profile.legal_name || ''),
  mobile_number: textOrNull(profile.mobile_number),
  email: textOrNull(profile.email),
  pan: { masked: textOrNull(profile.pan?.masked), can_view_full: Boolean(profile.pan?.can_view_full) },
  aadhaar: { masked: textOrNull(profile.aadhaar?.masked), can_view_full: Boolean(profile.aadhaar?.can_view_full) },
  share_summary: {
    number_of_shares: numberOrNull(profile.share_summary?.number_of_shares),
    holding_mode: textOrNull(profile.share_summary?.holding_mode),
    available_share_count: numberOrNull(profile.share_summary?.available_share_count),
  },
  available_actions: Array.isArray(profile.available_actions) ? profile.available_actions : [],
});

const textOrNull = (value: unknown) => (
  value === null || value === undefined || value === '' ? null : String(value)
);

const numberOrNull = (value: unknown): number | null => (
  Number.isFinite(Number(value)) ? Number(value) : null
);

const normalizeNominees = (items: MemberNomineeDetail[]): MemberNomineeDetail[] => (
  Array.isArray(items) ? items.map(normalizeNominee) : []
);

const normalizeNominee = (item: MemberNomineeDetail): MemberNomineeDetail => ({
  nominee_id: String(item?.nominee_id ?? ''),
  nominee_name: String(item?.nominee_name ?? ''),
  date_of_birth: textOrNull(item?.date_of_birth),
  age_at_application: numberOrNull(item?.age_at_application),
  gender: String(item?.gender ?? ''),
  relationship_to_borrower: textOrNull(item?.relationship_to_borrower),
  pan: { masked: textOrNull(item?.pan?.masked), can_view_full: Boolean(item?.pan?.can_view_full) },
  aadhaar: { masked: textOrNull(item?.aadhaar?.masked), can_view_full: Boolean(item?.aadhaar?.can_view_full) },
  kyc_status: String(item?.kyc_status ?? ''),
  minor_flag: Boolean(item?.minor_flag),
  signature_required_flag: Boolean(item?.signature_required_flag),
  created_at: String(item?.created_at ?? ''),
});

const normalizeShareholdings = (items: MemberShareholdingDetail[]): MemberShareholdingDetail[] => (
  Array.isArray(items) ? items.map(normalizeShareholding) : []
);

const normalizeShareholding = (item: MemberShareholdingDetail): MemberShareholdingDetail => ({
  shareholding_id: String(item?.shareholding_id ?? ''),
  folio_number: String(item?.folio_number ?? ''),
  number_of_shares: numberOrZero(item?.number_of_shares),
  holding_mode: String(item?.holding_mode ?? ''),
  valuation_per_share: textOrNull(item?.valuation_per_share),
  valuation_effective_date: textOrNull(item?.valuation_effective_date),
  pledged_share_count: numberOrZero(item?.pledged_share_count),
  available_share_count: numberOrZero(item?.available_share_count),
  future_shares_pledge_flag: Boolean(item?.future_shares_pledge_flag),
  status: String(item?.status ?? ''),
});

const normalizeLandHoldings = (items: MemberLandHoldingDetail[]): MemberLandHoldingDetail[] => (
  Array.isArray(items) ? items.map(normalizeLandHolding) : []
);

const normalizeLandHolding = (item: MemberLandHoldingDetail): MemberLandHoldingDetail => ({
  land_holding_id: String(item?.land_holding_id ?? ''),
  document_type: String(item?.document_type ?? ''),
  survey_number: textOrNull(item?.survey_number),
  village: textOrNull(item?.village),
  taluka: textOrNull(item?.taluka),
  district: textOrNull(item?.district),
  state: textOrNull(item?.state),
  area_acres: String(item?.area_acres ?? ''),
  document_id: String(item?.document_id ?? ''),
  verification_status: String(item?.verification_status ?? ''),
  verified_by_user_id: textOrNull(item?.verified_by_user_id),
  verified_at: textOrNull(item?.verified_at),
  created_at: String(item?.created_at ?? ''),
});

const normalizeCropPlans = (items: MemberCropPlanDetail[]): MemberCropPlanDetail[] => (
  Array.isArray(items) ? items.map(normalizeCropPlan) : []
);

const normalizeCropPlan = (item: MemberCropPlanDetail): MemberCropPlanDetail => ({
  crop_plan_id: String(item?.crop_plan_id ?? ''),
  loan_application_id: textOrNull(item?.loan_application_id),
  crop_type: String(item?.crop_type ?? ''),
  season: textOrNull(item?.season),
  planned_area_acres: String(item?.planned_area_acres ?? ''),
  estimated_cost_amount: textOrNull(item?.estimated_cost_amount),
  loan_purpose_alignment: String(item?.loan_purpose_alignment ?? ''),
  document_id: textOrNull(item?.document_id),
  verification_status: String(item?.verification_status ?? ''),
  verified_by_user_id: textOrNull(item?.verified_by_user_id),
  verified_at: textOrNull(item?.verified_at),
  created_at: String(item?.created_at ?? ''),
});

const numberOrZero = (value: unknown): number => (
  Number.isFinite(Number(value)) ? Number(value) : 0
);

const normalizeFieldErrors = (fieldErrors?: Record<string, unknown>): Record<string, string> | undefined => {
  if (!fieldErrors) return undefined;
  const normalized: Record<string, string> = {};
  Object.entries(fieldErrors).forEach(([key, value]) => {
    normalized[key] = Array.isArray(value) ? String(value[0] ?? '') : String(value ?? '');
  });
  return normalized;
};

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};
