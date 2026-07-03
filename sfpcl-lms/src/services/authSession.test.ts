import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  clearStoredAuthSession,
  loadStoredAuthSession,
  loginAndLoadCurrentUser,
  logoutSession,
  mapBackendUserToFrontendUser,
  mapCanonicalPermissions,
  restoreCurrentUserFromStoredSession,
  storedAuthSession,
} from './authSession';

const loginEnvelope = {
  success: true,
  data: {
    access_token: 'access-token-1',
    refresh_token: 'refresh-token-1',
    expires_in: 900,
    user: {
      user_id: 'user-login',
      full_name: 'Login User',
      email: 'login.user@sfpcl.example',
      role_codes: ['credit_manager'],
      team_codes: ['credit_assessment'],
    },
  },
  meta: { api_version: 'v1' },
};

const currentUserEnvelope = {
  success: true,
  data: {
    user_id: 'user-1',
    full_name: 'Credit Manager',
    email: 'credit.manager@sfpcl.example',
    mobile_number: '+919999999999',
    status: 'active',
    roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }],
    teams: [{ team_code: 'credit_assessment', team_name: 'Credit Assessment' }],
    role_codes: ['ignored_if_roles_present'],
    team_codes: ['ignored_if_teams_present'],
    permissions: ['applications.loan_application.read', 'finance.loan_account.read', 'reports.export'],
    available_actions: ['applications.loan_application.read'],
  },
  meta: { api_version: 'v1' },
};

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('auth session API flow', () => {
  it('posts credentials, stores tokens, calls /auth/me/, and returns backend current user state', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response(200, loginEnvelope))
      .mockResolvedValueOnce(response(200, currentUserEnvelope));
    vi.stubGlobal('fetch', fetchMock);

    const user = await loginAndLoadCurrentUser({ email: 'credit.manager@sfpcl.example', password: 'secret' });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/auth/login/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ email: 'credit.manager@sfpcl.example', password: 'secret' }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/auth/me/',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(user.name).toBe('Credit Manager');
    expect(user.role).toBe('credit_manager');
    expect(user.roleCodes).toEqual(['credit_manager']);
    expect(user.teamCodes).toEqual(['credit_assessment']);
    expect(user.permissions).toEqual(['applications.loan_application.read', 'finance.loan_account.read', 'reports.export']);
    expect(loadStoredAuthSession()).toEqual({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
  });

  it('does not store a session when login returns invalid credentials', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(401, errorEnvelope('INVALID_CREDENTIALS'))));

    await expect(loginAndLoadCurrentUser({ email: 'bad@sfpcl.example', password: 'wrong' })).rejects.toMatchObject({
      code: 'INVALID_CREDENTIALS',
    });

    expect(loadStoredAuthSession()).toBeNull();
  });

  it('clears stored auth when /auth/me/ rejects an expired or invalid token', async () => {
    storedAuthSession({ accessToken: 'expired-access', refreshToken: 'refresh-token-1' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(401, errorEnvelope('TOKEN_EXPIRED'))));

    await expect(restoreCurrentUserFromStoredSession()).rejects.toMatchObject({ code: 'TOKEN_EXPIRED' });

    expect(loadStoredAuthSession()).toBeNull();
  });

  it('posts the refresh token on logout and clears local auth state', async () => {
    storedAuthSession({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
    const fetchMock = vi.fn().mockResolvedValueOnce(response(200, { success: true, data: { logged_out: true }, meta: {} }));
    vi.stubGlobal('fetch', fetchMock);

    await logoutSession();

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/auth/logout/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ refresh_token: 'refresh-token-1' }),
      }),
    );
    expect(loadStoredAuthSession()).toBeNull();
  });
});

describe('backend current-user mapping', () => {
  it('uses roles and teams objects for display and derives compatibility codes from those arrays', () => {
    const user = mapBackendUserToFrontendUser(currentUserEnvelope.data);

    expect(user.roleName).toBe('Credit Manager');
    expect(user.teamName).toBe('Credit Assessment');
    expect(user.roleCodes).toEqual(['credit_manager']);
    expect(user.teamCodes).toEqual(['credit_assessment']);
  });

  it('maps canonical backend permissions to existing prototype permission checks without granting unknown codes', () => {
    expect(mapCanonicalPermissions([
      'applications.loan_application.read',
      'applications.loan_application.create',
      'finance.loan_account.read',
      'reports.export',
      'unknown.future.permission',
    ])).toEqual(['view_applications', 'create_application', 'view_loan_accounts', 'export_registers']);
  });

  it('keeps zero-permission roles restricted to unrestricted routes', () => {
    const user = mapBackendUserToFrontendUser({
      ...currentUserEnvelope.data,
      roles: [{ role_code: 'sales_team_user', role_name: 'Sales Team User' }],
      permissions: [],
    });

    expect(user.role).toBe('sales_team_user');
    expect(mapCanonicalPermissions(user.permissions)).toEqual([]);
  });
});

function response(status: number, body: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function errorEnvelope(code: string) {
  return {
    success: false,
    error: { code, message: code, details: {}, field_errors: {} },
    meta: { api_version: 'v1' },
  };
}

afterEach(() => {
  clearStoredAuthSession();
});
