import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  createPortalApplicationDraft,
  fetchPortalApplication,
  fetchPortalApplications,
  fetchPortalDashboard,
  fetchPortalProduceSupply,
  fetchPortalProfile,
  submitPortalApplication,
  updatePortalApplicationDraft,
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

  it('surfaces backend nominee field errors for portal forms', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(
      400,
      'VALIDATION_ERROR',
      { nominee_id: 'Selected nominee must be at least 18 years old.' },
    )));

    await expect(createPortalApplicationDraft({ nominee_id: 'minor-nominee' })).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      fieldErrors: { nominee_id: 'Selected nominee must be at least 18 years old.' },
    });
  });

  it('creates, updates, submits, lists, and reads portal applications with the stored bearer token', async () => {
    const application = {
      loan_application_id: 'app-1',
      display_reference: 'APP-1',
      application_status: 'draft',
      required_loan_amount: '250000.00',
      pending_with: 'Borrower',
      open_deficiency_count: 0,
      timeline: [],
      deficiencies: [],
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok(application))
      .mockResolvedValueOnce(ok({ ...application, required_loan_amount: '300000.00' }))
      .mockResolvedValueOnce(ok({ ...application, application_status: 'submitted', pending_with: 'SFPCL' }))
      .mockResolvedValueOnce(ok({ items: [application] }))
      .mockResolvedValueOnce(ok(application));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createPortalApplicationDraft({ nominee_id: 'nominee-1', required_loan_amount: '250000.00', declared_purpose: 'Crop production', purpose_category: 'crop_production' })).resolves.toMatchObject({ loan_application_id: 'app-1' });
    await expect(updatePortalApplicationDraft('app-1', { nominee_id: 'nominee-1', required_loan_amount: '300000.00' })).resolves.toMatchObject({ required_loan_amount: '300000.00' });
    await expect(submitPortalApplication('app-1')).resolves.toMatchObject({ application_status: 'submitted', pending_with: 'SFPCL' });
    await expect(fetchPortalApplications()).resolves.toMatchObject({ items: [{ loan_application_id: 'app-1' }] });
    await expect(fetchPortalApplication('app-1')).resolves.toMatchObject({ display_reference: 'APP-1' });

    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://127.0.0.1:8000/api/v1/portal/applications/', request('POST', {
      nominee_id: 'nominee-1',
      required_loan_amount: '250000.00',
      declared_purpose: 'Crop production',
      purpose_category: 'crop_production',
    }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/', request('PATCH', {
      nominee_id: 'nominee-1',
      required_loan_amount: '300000.00',
    }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/submit/', request('POST', {}));
    expect(fetchMock).toHaveBeenNthCalledWith(4, 'http://127.0.0.1:8000/api/v1/portal/applications/', request());
    expect(fetchMock).toHaveBeenNthCalledWith(5, 'http://127.0.0.1:8000/api/v1/portal/applications/app-1/', request());
  });
});

const request = (method = 'GET', body?: unknown) => expect.objectContaining({
  method,
  headers: expect.objectContaining({
    Accept: 'application/json',
    Authorization: 'Bearer portal-access-token',
    ...(body ? { 'Content-Type': 'application/json' } : {}),
  }),
  ...(body ? { body: JSON.stringify(body) } : {}),
});

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, meta: {} }) } as Response;
}

function error(status: number, code: string, fieldErrors?: Record<string, string>): Response {
  return {
    ok: false,
    status,
    json: async () => ({ success: false, error: { code, message: 'Portal request failed.', field_errors: fieldErrors }, meta: {} }),
  } as Response;
}
