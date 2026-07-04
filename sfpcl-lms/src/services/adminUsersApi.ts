import {
  API_BASE_URL,
  AuthSessionError,
  loadStoredAuthSession,
  type BackendRole,
  type BackendTeam,
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

export interface AdminUser {
  user_id: string;
  full_name: string;
  email: string;
  mobile_number: string;
  status: string;
  roles: BackendRole[];
  teams: BackendTeam[];
}

export interface AdminUsersList {
  users: AdminUser[];
  pagination: Pagination;
}

export const listAdminUsers = async (): Promise<AdminUsersList> => {
  const envelope = await requestEnvelope<AdminUser[]>('/api/v1/admin/users/?page=1&page_size=50', {
    method: 'GET',
  });
  return {
    users: envelope.data ?? [],
    pagination: envelope.pagination ?? {
      page: 1,
      page_size: 50,
      total_count: envelope.data?.length ?? 0,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
  };
};

export const getAdminUser = async (userId: string): Promise<AdminUser> => (
  request<AdminUser>(`/api/v1/admin/users/${userId}/`, { method: 'GET' })
);

export const assignAdminUserRole = async (userId: string, roleCode: string): Promise<AdminUser> => (
  request<AdminUser>(`/api/v1/admin/users/${userId}/roles/`, {
    method: 'POST',
    body: JSON.stringify({ role_code: roleCode }),
  })
);

export const addAdminUserTeam = async (userId: string, teamCode: string): Promise<AdminUser> => (
  request<AdminUser>(`/api/v1/admin/users/${userId}/teams/`, {
    method: 'POST',
    body: JSON.stringify({ team_code: teamCode }),
  })
);

export const removeAdminUserTeam = async (userId: string, teamCode: string): Promise<AdminUser> => (
  request<AdminUser>(`/api/v1/admin/users/${userId}/teams/${teamCode}/`, {
    method: 'DELETE',
  })
);

export const setAdminUserStatus = async (userId: string, status: 'active' | 'suspended'): Promise<AdminUser> => (
  request<AdminUser>(`/api/v1/admin/users/${userId}/status/`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
);

const request = async <T>(path: string, options: RequestInit): Promise<T> => {
  const envelope = await requestEnvelope<T>(path, options);
  if (!envelope.data) throw new AuthSessionError('REQUEST_FAILED', 'Request failed.');
  return envelope.data;
};

const requestEnvelope = async <T>(path: string, options: RequestInit): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(options.headers || {}),
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
