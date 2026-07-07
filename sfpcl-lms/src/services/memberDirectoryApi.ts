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
    field_errors?: Record<string, unknown>;
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

export interface MemberDirectoryItem {
  member_id: string;
  member_number: string | null;
  member_type: string;
  legal_name: string;
  display_name: string;
  folio_number: string;
  membership_status: string;
  kyc_status: string;
  rekyc_due_date: string | null;
  default_status: string;
  mobile_number: string | null;
  email: string | null;
  share_summary: {
    number_of_shares: number | null;
    holding_mode: string | null;
    available_share_count: number | null;
  };
  active_member_status: {
    status: string | null;
    verified_at: string | null;
  };
}

export interface MemberDirectoryFilters {
  search?: string;
  memberType?: string;
  membershipStatus?: string;
  kycStatus?: string;
  defaultStatus?: string;
  page?: number;
  pageSize?: number;
}

export interface MemberDirectoryList {
  items: MemberDirectoryItem[];
  pagination: Pagination;
}

export const fetchMemberDirectory = async (
  filters: MemberDirectoryFilters = {},
): Promise<MemberDirectoryList> => {
  const params = new URLSearchParams();
  setParam(params, 'search', filters.search);
  setParam(params, 'member_type', filters.memberType);
  setParam(params, 'membership_status', filters.membershipStatus);
  setParam(params, 'kyc_status', filters.kycStatus);
  setParam(params, 'default_status', filters.defaultStatus);
  if (filters.page) params.set('page', String(filters.page));
  if (filters.pageSize) params.set('page_size', String(filters.pageSize));
  const query = params.toString();
  const envelope = await request<MemberDirectoryItem[]>(
    `/api/v1/members/${query ? `?${query}` : ''}`,
  );
  return {
    items: normalizeMembers(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

const request = async <T>(path: string): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
    },
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return envelope;
};

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const setParam = (params: URLSearchParams, key: string, value?: string) => {
  if (value && value !== 'all') params.set(key, value);
};

const normalizeMembers = (items: MemberDirectoryItem[]): MemberDirectoryItem[] =>
  Array.isArray(items) ? items.map(normalizeMember) : [];

const normalizeMember = (item: MemberDirectoryItem): MemberDirectoryItem => ({
  member_id: String(item?.member_id ?? ''),
  member_number: item?.member_number ? String(item.member_number) : null,
  member_type: String(item?.member_type ?? ''),
  legal_name: String(item?.legal_name ?? ''),
  display_name: String(item?.display_name ?? item?.legal_name ?? ''),
  folio_number: String(item?.folio_number ?? ''),
  membership_status: String(item?.membership_status ?? ''),
  kyc_status: String(item?.kyc_status ?? ''),
  rekyc_due_date: item?.rekyc_due_date ?? null,
  default_status: String(item?.default_status ?? ''),
  mobile_number: item?.mobile_number ? String(item.mobile_number) : null,
  email: item?.email ? String(item.email) : null,
  share_summary: {
    number_of_shares: numberOrNull(item?.share_summary?.number_of_shares),
    holding_mode: item?.share_summary?.holding_mode ? String(item.share_summary.holding_mode) : null,
    available_share_count: numberOrNull(item?.share_summary?.available_share_count),
  },
  active_member_status: {
    status: item?.active_member_status?.status ? String(item.active_member_status.status) : null,
    verified_at: item?.active_member_status?.verified_at ?? null,
  },
});

const numberOrNull = (value: unknown): number | null => (
  Number.isFinite(Number(value)) ? Number(value) : null
);
