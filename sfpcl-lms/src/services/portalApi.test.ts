import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  fetchPortalDashboard,
  fetchPortalProduceSupply,
  fetchPortalProfile,
} from './portalApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'portal-access-token', refreshToken: 'portal-refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('portal member API client', () => {
  it('loads dashboard, profile, and produce supply using the stored portal bearer token', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok({ member: { display_name: 'Ganesh Thorat' }, application_counts: { total: 1 }, pending_actions: { open_deficiencies: 1 }, loan_counts: { active: 0 }, notices: [] }))
      .mockResolvedValueOnce(ok({ member: { display_name: 'Ganesh Thorat', pan: { masked: '******234F' } }, nominees: [], shareholdings: [], land_holdings: [], crop_plans: [], bank_accounts: [], cancelled_cheques: [], kyc_profile: null }))
      .mockResolvedValueOnce(ok({ member_id: 'member-1', records: [], summary: {}, source_status: 'model_not_implemented' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchPortalDashboard()).resolves.toMatchObject({ member: { display_name: 'Ganesh Thorat' } });
    await expect(fetchPortalProfile()).resolves.toMatchObject({ member: { pan: { masked: '******234F' } } });
    await expect(fetchPortalProduceSupply()).resolves.toMatchObject({ source_status: 'model_not_implemented' });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/portal/dashboard/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/portal/profile/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/portal/produce-supply/', request());
  });

  it('surfaces portal permission errors without substituting mock member data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'PERMISSION_DENIED')));

    await expect(fetchPortalDashboard()).rejects.toMatchObject({ code: 'PERMISSION_DENIED', status: 403 });
  });
});

const request = () => expect.objectContaining({
  method: 'GET',
  headers: expect.objectContaining({
    Accept: 'application/json',
    Authorization: 'Bearer portal-access-token',
  }),
});

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) } as Response;
}

function error(status: number, code: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({ success: false, error: { code, message: 'Portal request failed.' }, meta: {} }),
  } as Response;
}
