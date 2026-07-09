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
  nominees: { nominee_name: string; relationship_to_borrower: string | null; pan: MaskedValue; aadhaar: MaskedValue; kyc_status: string }[];
  shareholdings: { folio_number: string; number_of_shares: number; holding_mode: string; available_share_count: number; status: string }[];
  land_holdings: { survey_number: string | null; village: string | null; area_acres: string; verification_status: string }[];
  crop_plans: { season: string | null; crop_type: string; planned_area_acres: string; verification_status: string }[];
  bank_accounts: { account_holder_name: string; account_number: MaskedValue; ifsc: string; bank_name: string | null; branch_name: string | null; verification_status: string }[];
  cancelled_cheques: { account_number: MaskedValue; ifsc: string; branch_name: string | null; verification_status: string }[];
  kyc_profile: { kyc_status: string; rekyc_due_date: string | null; risk_rating: string | null } | null;
}

export interface PortalProduceSupply {
  member_id: string;
  records: { financial_year: string; crop_type: string | null; quantity: string | null; value_amount: string | null; verified_flag: boolean }[];
  summary: { continuous_supply_years?: string | null; total_quantity?: string | null; total_value?: string | null };
  source_status: string;
}

export const fetchPortalDashboard = () => request<PortalDashboard>('/api/v1/portal/dashboard/');
export const fetchPortalProfile = () => request<PortalProfile>('/api/v1/portal/profile/');
export const fetchPortalProduceSupply = () => request<PortalProduceSupply>('/api/v1/portal/produce-supply/');

async function request<T>(path: string): Promise<T> {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Member portal session is required.', 401);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
    },
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success || !envelope.data) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return envelope.data;
}
