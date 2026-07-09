import { API_BASE_URL, AuthSessionError, loadStoredAuthSession } from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: { code: string; message: string };
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

export const fetchMemberProfile = async (memberId: string): Promise<MemberProfileDetail> => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);

  const response = await fetch(`${API_BASE_URL}/api/v1/members/${memberId}/`, {
    method: 'GET',
    headers: { Accept: 'application/json', Authorization: `Bearer ${session.accessToken}` },
  });
  const envelope = await response.json() as ApiEnvelope<MemberProfileDetail>;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return normalize(envelope.data);
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
