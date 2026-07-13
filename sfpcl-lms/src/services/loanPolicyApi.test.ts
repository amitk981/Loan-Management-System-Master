import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import { createLoanPolicyVersion, fetchLoanPolicyVersions, type CreateLoanPolicyVersion } from './loanPolicyApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'policy-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('loan policy API client', () => {
  it('reads retained versions and creates successors only through the collection boundary', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([policy]))
      .mockResolvedValueOnce(ok({ ...policy, loan_policy_config_id: 'policy-2', status: 'draft' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchLoanPolicyVersions({ page: 1, pageSize: 100 })).resolves.toEqual([policy]);
    await expect(createLoanPolicyVersion(successor)).resolves.toMatchObject({ loan_policy_config_id: 'policy-2', status: 'draft' });

    expect(fetchMock).toHaveBeenNthCalledWith(1,
      'http://127.0.0.1:8000/api/v1/config/loan-policy/?page=1&page_size=100', request());
    expect(fetchMock).toHaveBeenNthCalledWith(2,
      'http://127.0.0.1:8000/api/v1/config/loan-policy/', request('POST', successor));
    expect(fetchMock.mock.calls.flat().join(' ')).not.toContain('/activate/');
  });

  it('surfaces a direct permission denial without fallback data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'FORBIDDEN')));

    await expect(fetchLoanPolicyVersions({ page: 1, pageSize: 100 })).rejects.toMatchObject({ code: 'FORBIDDEN', status: 403 });
  });
});

const successor: CreateLoanPolicyVersion = {
  policy_name: 'Board policy', policy_version: 'LP-2', effective_from: '2027-04-01', effective_to: null,
  short_term_duration_months: 12, min_secured_loan_months: 12, max_secured_loan_years: 3,
  approval_threshold_amount: '500000.00', default_scale_of_finance_per_acre_amount: '20000.00',
  share_limit_percentage: '10.0000', per_share_cap_amount: '200.00', interest_rate_type: 'floating',
  interest_benchmark: 'Board benchmark', penal_interest_rate: null, rekyc_frequency_months: 24,
  record_retention_years: 8, grace_period_months: 3, non_intentional_extension_months: 12,
  board_approval_reference: 'BOARD-2',
};

const policy = { loan_policy_config_id: 'policy-1', status: 'active', ...successor };

function request(method = 'GET', body?: unknown): RequestInit {
  return {
    method,
    headers: expect.objectContaining({
      Accept: 'application/json', Authorization: 'Bearer policy-token', 'X-Request-ID': expect.any(String),
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
    }) as unknown as HeadersInit,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  };
}

function ok(data: unknown): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data }) } as Response;
}

function error(status: number, code: string): Response {
  return { ok: false, status, json: async () => ({ success: false, error: { code, message: 'Denied.' } }) } as Response;
}
