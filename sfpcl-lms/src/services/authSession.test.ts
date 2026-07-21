import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  CANONICAL_TO_PROTOTYPE_PERMISSIONS,
  authenticatedAllPagesRequest,
  authenticatedMultipartRequest,
  authenticatedPaginatedRequest,
  clearStoredAuthSession,
  loadStoredAuthSession,
  loginAndLoadCurrentUser,
  logoutSession,
  mapBackendUserToFrontendUser,
  mapCanonicalPermissions,
  portalLoginAndLoadCurrentUser,
  restoreCurrentUserFromStoredSession,
  startPortalActivation,
  completePortalActivation,
  startPortalPasswordReset,
  completePortalPasswordReset,
  changePortalPassword,
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

const portalCurrentUserEnvelope = {
  success: true,
  data: {
    user_id: 'portal-user-1',
    full_name: 'Ganesh Thorat',
    email: 'ganesh.thorat@sfpcl.example',
    mobile_number: '+919800000042',
    status: 'active',
    roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }],
    teams: [],
    permissions: ['portal.loan_application.read_own'],
    available_actions: ['portal.loan_application.read_own'],
    member_id: 'member-42',
    portal_account_id: 'portal-account-42',
    portal_role: 'borrower_member',
    member_display_name: 'Ganesh Thorat',
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
  it('returns typed list data and pagination through the shared authenticated envelope boundary', async () => {
    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    const fetchMock = vi.fn().mockResolvedValueOnce(response(200, {
      success: true,
      data: [{ approval_matrix_rule_id: 'rule-1' }],
      pagination: { page: 2, page_size: 10, total_count: 11, total_pages: 2, has_next: false, has_previous: true },
      meta: {},
    }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(authenticatedPaginatedRequest<{ approval_matrix_rule_id: string }>(
      '/api/v1/approval-matrix-rules/?page=2&page_size=10',
    )).resolves.toEqual({
      items: [{ approval_matrix_rule_id: 'rule-1' }],
      pagination: { page: 2, page_size: 10, total_count: 11, total_pages: 2, has_next: false, has_previous: true },
    });
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/approval-matrix-rules/?page=2&page_size=10',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer list-access',
          'X-Request-ID': expect.any(String),
        }),
      }),
    );
  });

  it('loads all 101 canonical records through truthful continuation metadata', async () => {
    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    const firstPage = Array.from({ length: 100 }, (_, index) => ({ id: index + 1 }));
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(response(200, {
        success: true,
        data: firstPage,
        pagination: { page: 1, page_size: 100, total_count: 101, total_pages: 2, has_next: true, has_previous: false },
      }))
      .mockResolvedValueOnce(response(200, {
        success: true,
        data: [{ id: 101 }],
        pagination: { page: 2, page_size: 100, total_count: 101, total_pages: 2, has_next: false, has_previous: true },
      }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(authenticatedAllPagesRequest<{ id: number }>(
      page => `/api/v1/loan-accounts/?page=${page}&page_size=100`,
    )).resolves.toEqual({
      items: [...firstPage, { id: 101 }],
      totalCount: 101,
      totalPages: 2,
      pageSize: 100,
    });
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/loan-accounts/?page=1&page_size=100',
      'http://127.0.0.1:8000/api/v1/loan-accounts/?page=2&page_size=100',
    ]);
  });

  it('rejects pagination that changes while a canonical collection is loading', async () => {
    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(response(200, {
        success: true,
        data: Array.from({ length: 100 }, (_, index) => ({ id: index + 1 })),
        pagination: { page: 1, page_size: 100, total_count: 101, total_pages: 2, has_next: true, has_previous: false },
      }))
      .mockResolvedValueOnce(response(200, {
        success: true,
        data: Array.from({ length: 100 }, (_, index) => ({ id: index + 101 })),
        pagination: { page: 2, page_size: 100, total_count: 201, total_pages: 3, has_next: true, has_previous: true },
      })));

    await expect(authenticatedAllPagesRequest<{ id: number }>(
      page => `/api/v1/loan-accounts/?page=${page}&page_size=100`,
    )).rejects.toMatchObject({
      code: 'MALFORMED_RESPONSE',
      message: 'The server changed pagination while the collection was loading.',
    });
  });

  it.each([
    ['empty collection', [], { page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false }],
    ['full first page', Array.from({ length: 10 }, (_, index) => ({ id: index })), { page: 1, page_size: 10, total_count: 21, total_pages: 3, has_next: true, has_previous: false }],
    ['full middle page', Array.from({ length: 10 }, (_, index) => ({ id: index + 10 })), { page: 2, page_size: 10, total_count: 21, total_pages: 3, has_next: true, has_previous: true }],
    ['exact final remainder', [{ id: 20 }], { page: 3, page_size: 10, total_count: 21, total_pages: 3, has_next: false, has_previous: true }],
  ])('accepts a collection envelope with an exact %s page', async (_label, data, pagination) => {
    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(200, {
      success: true, data, pagination, meta: {},
    })));

    await expect(authenticatedPaginatedRequest('/api/v1/approval-cases/')).resolves.toEqual({
      items: data,
      pagination,
    });
  });

  it.each([
    ['non-array data', { success: true, data: { approval_matrix_rule_id: 'rule-1' }, pagination: { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false } }],
    ['missing pagination', { success: true, data: [] }],
    ['missing pagination field', { success: true, data: [], pagination: { page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false } }],
    ['negative pagination field', { success: true, data: [], pagination: { page: 1, page_size: 20, total_count: -1, total_pages: 1, has_next: false, has_previous: false } }],
    ['non-integer pagination field', { success: true, data: [], pagination: { page: 1.5, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false } }],
    ['inconsistent total pages', { success: true, data: [{ approval_matrix_rule_id: 'rule-1' }], pagination: { page: 1, page_size: 10, total_count: 11, total_pages: 1, has_next: false, has_previous: false } }],
    ['inconsistent navigation flags', { success: true, data: [{ approval_matrix_rule_id: 'rule-1' }], pagination: { page: 1, page_size: 10, total_count: 11, total_pages: 2, has_next: false, has_previous: true } }],
    ['page data beyond the total', { success: true, data: [{ approval_matrix_rule_id: 'rule-1' }], pagination: { page: 2, page_size: 10, total_count: 10, total_pages: 1, has_next: false, has_previous: true } }],
    ['under-filled first page', { success: true, data: [{ id: 1 }], pagination: { page: 1, page_size: 10, total_count: 11, total_pages: 2, has_next: true, has_previous: false } }],
    ['under-filled middle page', { success: true, data: [{ id: 11 }], pagination: { page: 2, page_size: 10, total_count: 21, total_pages: 3, has_next: true, has_previous: true } }],
    ['under-filled final remainder', { success: true, data: [], pagination: { page: 2, page_size: 10, total_count: 11, total_pages: 2, has_next: false, has_previous: true } }],
    ['over-filled final remainder', { success: true, data: [{ id: 10 }, { id: 11 }], pagination: { page: 2, page_size: 10, total_count: 11, total_pages: 2, has_next: false, has_previous: true } }],
    ['nonempty zero-total page', { success: true, data: [{ id: 1 }], pagination: { page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false } }],
  ])('rejects a successful collection envelope with %s', async (_label, body) => {
    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(200, body)));

    await expect(authenticatedPaginatedRequest('/api/v1/approval-cases/')).rejects.toMatchObject({
      code: 'MALFORMED_RESPONSE',
      status: 200,
    });
  });

  it('preserves authentication and server-error behavior for paginated requests', async () => {
    await expect(authenticatedPaginatedRequest('/api/v1/approval-cases/')).rejects.toMatchObject({
      code: 'AUTH_REQUIRED',
      status: 401,
    });

    storedAuthSession({ accessToken: 'list-access', refreshToken: 'list-refresh' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(403, {
      success: false,
      error: { code: 'FORBIDDEN', message: 'Approval case read is not permitted.' },
    })));
    await expect(authenticatedPaginatedRequest('/api/v1/approval-cases/')).rejects.toMatchObject({
      code: 'FORBIDDEN',
      status: 403,
    });
  });

  it('sends multipart bodies through the shared authenticated envelope boundary', async () => {
    storedAuthSession({ accessToken: 'upload-access', refreshToken: 'upload-refresh' });
    const fetchMock = vi.fn().mockResolvedValueOnce(response(201, {
      success: true,
      data: { document_id: 'document-1' },
      meta: {},
    }));
    vi.stubGlobal('fetch', fetchMock);
    await expect(authenticatedMultipartRequest<{ document_id: string }>(
      '/api/v1/document-files/',
      { document_category: 'legal' },
    )).resolves.toEqual({ document_id: 'document-1' });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/document-files/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer upload-access',
          'X-Request-ID': expect.any(String),
        }),
        body: expect.any(FormData),
      }),
    );
    const body = fetchMock.mock.calls[0][1]?.body as FormData;
    expect(body.get('document_category')).toBe('legal');
  });

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

describe('member portal auth API flow', () => {
  it('posts portal credentials, stores tokens, and maps borrower member scope from /auth/me/', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response(200, loginEnvelope))
      .mockResolvedValueOnce(response(200, portalCurrentUserEnvelope));
    vi.stubGlobal('fetch', fetchMock);

    const user = await portalLoginAndLoadCurrentUser({
      identifier: 'ganesh.thorat@sfpcl.example',
      password: 'CorrectPortal123!',
    });

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/portal/auth/login/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ identifier: 'ganesh.thorat@sfpcl.example', password: 'CorrectPortal123!' }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/auth/me/',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(user.role).toBe('borrower');
    expect(user.memberId).toBe('member-42');
    expect(user.portalRole).toBe('borrower_member');
    expect(user.permissions).toEqual(['portal.loan_application.read_own']);
    expect(loadStoredAuthSession()).toEqual({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
  });

  it('calls portal activation and password reset endpoints using standard envelopes', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(response(200, { success: true, data: { challenge_id: 'activation-challenge', masked_contact: 'ga***@sfpcl.example' }, meta: {} }))
      .mockResolvedValueOnce(response(200, { success: true, data: { portal_account: { member_id: 'member-42', status: 'active' } }, meta: {} }))
      .mockResolvedValueOnce(response(200, { success: true, data: { challenge_id: 'reset-challenge', masked_contact: 'ga***@sfpcl.example' }, meta: {} }))
      .mockResolvedValueOnce(response(200, { success: true, data: { reset: true }, meta: {} }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(startPortalActivation({
      folioOrMemberId: 'FOLIO-42',
      contact: 'ganesh.thorat@sfpcl.example',
      panLast4: '234F',
      aadhaarLast4: '9012',
    })).resolves.toMatchObject({ challengeId: 'activation-challenge' });
    await expect(completePortalActivation({
      challengeId: 'activation-challenge',
      otp: '246810',
      password: 'CorrectPortal123!',
      confirmPassword: 'CorrectPortal123!',
    })).resolves.toMatchObject({ memberId: 'member-42', status: 'active' });
    await expect(startPortalPasswordReset({ identifier: 'ganesh.thorat@sfpcl.example' })).resolves.toMatchObject({ challengeId: 'reset-challenge' });
    await expect(completePortalPasswordReset({
      challengeId: 'reset-challenge',
      otp: '246810',
      password: 'NewPortal123!',
      confirmPassword: 'NewPortal123!',
    })).resolves.toEqual({ reset: true });
  });

  it('posts portal password changes with the stored bearer token', async () => {
    storedAuthSession({ accessToken: 'portal-access-token', refreshToken: 'portal-refresh-token' });
    const fetchMock = vi.fn().mockResolvedValueOnce(response(200, { success: true, data: { password_changed: true }, meta: {} }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(changePortalPassword({
      currentPassword: 'CorrectPortal123!',
      newPassword: 'ChangedPortal123!',
      confirmPassword: 'ChangedPortal123!',
    })).resolves.toEqual({ passwordChanged: true });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/portal/auth/password/change/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer portal-access-token' }),
      }),
    );
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

  it('maps approval register and matrix permissions to resource-scoped navigation gates', () => {
    expect(mapCanonicalPermissions([
      'approvals.sanction_register.read',
      'approvals.exception_register.read',
      'approvals.matrix.read',
      'approvals.matrix.manage',
    ])).toEqual(['view_approval_registers', 'view_approval_matrix']);
  });

  it('maps only the explicit tracer permission to the tracer workspace action', () => {
    expect(mapCanonicalPermissions([
      'tracer.lifecycle.run',
      'unknown.future.tracer_permission',
    ])).toEqual(['run_tracer']);
  });

  it('keeps tracer lifecycle mapping isolated from every non-tracer prototype permission', () => {
    expect(CANONICAL_TO_PROTOTYPE_PERMISSIONS['tracer.lifecycle.run']).toBe('run_tracer');

    const mappedTracerPermissions = mapCanonicalPermissions(['tracer.lifecycle.run']);

    expect(mappedTracerPermissions).toEqual(['run_tracer']);
    expect(mappedTracerPermissions).not.toContain('view_members');
    expect(mappedTracerPermissions).not.toContain('view_applications');
    expect(mappedTracerPermissions).not.toContain('view_loan_accounts');
    expect(mappedTracerPermissions).not.toContain('view_reports');
    expect(mappedTracerPermissions).not.toContain('view_settings');
    expect(mappedTracerPermissions).not.toContain('view_audit');
    expect(mappedTracerPermissions).not.toContain('manage_settings');
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

  it('maps zero-permission IT Head to a neutral backend staff role without auditor/admin/borrower behavior', () => {
    const user = mapBackendUserToFrontendUser({
      ...currentUserEnvelope.data,
      roles: [{ role_code: 'it_head', role_name: 'IT Head' }],
      teams: [{ team_code: 'it', team_name: 'IT' }],
      permissions: [],
      available_actions: [],
    });

    expect(user.role).toBe('backend_staff');
    expect(user.role).not.toBe('auditor');
    expect(user.role).not.toBe('admin');
    expect(user.role).not.toBe('borrower');
    expect(user.roleName).toBe('IT Head');
    expect(user.roleCodes).toEqual(['it_head']);
    expect(user.teamName).toBe('IT');
    expect(mapCanonicalPermissions(user.permissions)).toEqual([]);
    expect(user.availableActions).toEqual([]);
  });

  it('maps zero-permission Management Viewer to a neutral backend staff role without prototype permissions', () => {
    const user = mapBackendUserToFrontendUser({
      ...currentUserEnvelope.data,
      roles: [{ role_code: 'management_viewer', role_name: 'Management Viewer' }],
      teams: [],
      permissions: [],
      available_actions: [],
    });

    expect(user.role).toBe('backend_staff');
    expect(user.roleName).toBe('Management Viewer');
    expect(user.roleCodes).toEqual(['management_viewer']);
    expect(mapCanonicalPermissions(user.permissions)).toEqual([]);
  });

  it('maps unknown and empty-role current-user responses to neutral backend staff without prototype permissions', () => {
    const unknownRoleUser = mapBackendUserToFrontendUser({
      ...currentUserEnvelope.data,
      roles: [{ role_code: 'future_unknown_role', role_name: 'Future Unknown Role' }],
      teams: [],
      permissions: [],
      available_actions: [],
    });
    const emptyRoleUser = mapBackendUserToFrontendUser({
      ...currentUserEnvelope.data,
      roles: [],
      teams: [],
      permissions: [],
      available_actions: [],
    });

    expect(unknownRoleUser.role).toBe('backend_staff');
    expect(unknownRoleUser.roleName).toBe('Future Unknown Role');
    expect(mapCanonicalPermissions(unknownRoleUser.permissions)).toEqual([]);
    expect(emptyRoleUser.role).toBe('backend_staff');
    expect(emptyRoleUser.roleName).toBe('Staff User');
    expect(mapCanonicalPermissions(emptyRoleUser.permissions)).toEqual([]);
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
