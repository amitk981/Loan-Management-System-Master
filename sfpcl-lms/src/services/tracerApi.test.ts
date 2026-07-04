import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { runTracerLifecycle } from './tracerApi';
import { storedAuthSession, clearStoredAuthSession } from './authSession';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function ok(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, meta: { api_version: 'v1' } }),
  } as Response;
}

// The lifecycle makes seven calls, in order:
// member, application, sanction, loan-account, disburse, repayment, close.
function lifecycleFetchMock() {
  return vi
    .fn()
    .mockResolvedValueOnce(ok({ member_id: 'm1', reference: 'MEM-000001', display_name: 'Tracer Member', status: 'active' }))
    .mockResolvedValueOnce(ok({ loan_application_id: 'a1', reference: 'APP-000001', status: 'draft', amount: '400000.00' }))
    .mockResolvedValueOnce(ok({ entity_type: 'loan_application', entity_id: 'a1', previous_status: 'draft', new_status: 'sanctioned' }))
    .mockResolvedValueOnce(ok({ loan_account_id: 'l1', reference: 'LAC-000001', status: 'pending_disbursement', amount: '400000.00' }))
    .mockResolvedValueOnce(ok({ entity_type: 'loan_account', entity_id: 'l1', previous_status: 'pending_disbursement', new_status: 'active' }))
    .mockResolvedValueOnce(ok({ repayment_id: 'r1', reference: 'REP-000001', status: 'posted', amount: '400000.00' }))
    .mockResolvedValueOnce(ok({ entity_type: 'loan_account', entity_id: 'l1', previous_status: 'active', new_status: 'closed' }));
}

describe('runTracerLifecycle', () => {
  it('walks the seven backend transitions and returns closed-state evidence rows', async () => {
    const fetchMock = lifecycleFetchMock();
    vi.stubGlobal('fetch', fetchMock);

    const rows = await runTracerLifecycle();

    expect(fetchMock).toHaveBeenCalledTimes(7);
    const byLabel = Object.fromEntries(rows.map(row => [row.label, row]));

    expect(byLabel['Member'].status).toBe('active');
    expect(byLabel['Loan account'].status).toBe('closed');
    expect(byLabel['Repayment'].status).toBe('posted');
  });

  it('derives the Sanction row status from the real sanction response, not a dead ternary', async () => {
    // Regression for architecture-review 2026-07-04_071340 Finding 2: the Sanction
    // row must reflect the sanction endpoint's new_status, so a non-sanctioned
    // response would surface here instead of the hard-coded 'recorded'.
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(ok({ member_id: 'm1', reference: 'MEM-000001', display_name: 'Tracer Member', status: 'active' }))
      .mockResolvedValueOnce(ok({ loan_application_id: 'a1', reference: 'APP-000001', status: 'draft', amount: '400000.00' }))
      .mockResolvedValueOnce(ok({ entity_type: 'loan_application', entity_id: 'a1', previous_status: 'draft', new_status: 'sanctioned' }))
      .mockResolvedValueOnce(ok({ loan_account_id: 'l1', reference: 'LAC-000001', status: 'pending_disbursement', amount: '400000.00' }))
      .mockResolvedValueOnce(ok({ entity_type: 'loan_account', entity_id: 'l1', previous_status: 'pending_disbursement', new_status: 'active' }))
      .mockResolvedValueOnce(ok({ repayment_id: 'r1', reference: 'REP-000001', status: 'posted', amount: '400000.00' }))
      .mockResolvedValueOnce(ok({ entity_type: 'loan_account', entity_id: 'l1', previous_status: 'active', new_status: 'closed' }));
    vi.stubGlobal('fetch', fetchMock);

    const rows = await runTracerLifecycle();
    const sanction = rows.find(row => row.label === 'Sanction');

    expect(sanction).toBeDefined();
    expect(sanction?.status).toBe('sanctioned');
    expect(sanction?.status).not.toBe('recorded');
  });
});
