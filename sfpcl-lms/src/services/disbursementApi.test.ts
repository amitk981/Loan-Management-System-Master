import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  fetchDisbursementWorkspace,
  submitDisbursementAction,
  type DisbursementAction,
} from './disbursementApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'finance-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('disbursement workspace API client', () => {
  it('reads the paginated server-owned workspace projection', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok([workspace], pagination));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchDisbursementWorkspace()).resolves.toMatchObject({
      items: [{ loan_account_number: 'LN-API-001', readiness: { ready_for_disbursement: false } }],
    });
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/disbursement-workspaces/?page=1&page_size=20',
      expect.objectContaining({ method: 'GET' }),
    );
  });

  it('sends the exact server action URL and stable idempotency header', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({
      idempotency_replayed: true,
      original_response: { disbursement_id: 'disbursement-1' },
    }));
    vi.stubGlobal('fetch', fetchMock);
    const action: DisbursementAction = {
      action_code: 'initiate_disbursement', label: 'Initiate payment', enabled: true,
      disabled_reason: null, required_permission: 'finance.disbursement.initiate',
      action_url: '/api/v1/loan-accounts/account-1/disbursements/initiate/', method: 'POST',
      fields: [],
    };

    await submitDisbursementAction(action, { disbursement_amount: '400000.00' }, 'stable-key');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/loan-accounts/account-1/disbursements/initiate/',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Idempotency-Key': 'stable-key' }),
        body: JSON.stringify({ disbursement_amount: '400000.00' }),
      }),
    );
  });

  it('serializes datetime-local fields as exact timezone-aware request bytes', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({ request_status: 'completed' }));
    vi.stubGlobal('fetch', fetchMock);
    const action: DisbursementAction = {
      action_code: 'complete_sap_request', label: 'Confirm SAP customer code', enabled: true,
      disabled_reason: null, required_permission: 'finance.sap_request.complete',
      action_url: '/api/v1/sap-customer-profile-requests/sap-1/complete/', method: 'POST',
      fields: [
        { name: 'sap_customer_code', label: 'SAP code', type: 'text', required: true },
        { name: 'created_at_sap', label: 'Created at', type: 'datetime-local', required: false },
      ],
      fixed_payload: { confirmation_notes: 'Retained fixed note' },
    };
    const localValue = '2026-07-19T10:30';

    await submitDisbursementAction(action, {
      sap_customer_code: 'SAP-001', created_at_sap: localValue,
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/sap-customer-profile-requests/sap-1/complete/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          confirmation_notes: 'Retained fixed note',
          sap_customer_code: 'SAP-001',
          created_at_sap: new Date(localValue).toISOString(),
        }),
      }),
    );
  });
});

const workspace = {
  workspace_id: 'account-1', loan_account_id: 'account-1', disbursement_id: null,
  loan_application_id: 'application-1', application_reference_number: 'LO-API-001',
  loan_account_number: 'LN-API-001', member: { member_id: 'member-1', display_name: 'API Borrower' },
  sanctioned_amount: '400000.00', disbursement_amount: '400000.00',
  sap: { request_id: 'sap-1', status: 'completed', customer_code_masked: '******001' },
  readiness: { ready_for_disbursement: false, evaluated_at: '2026-07-19T03:00:00Z', checks: [] },
  beneficiary_bank: null, source_bank: null, initiation_status: null,
  authorisation_status: null, bank_transfer_status: null, advice_status: 'not_started',
  bank_reference_masked: null, initiated_by: null, initiated_at: null, authorised_at: null,
  disbursed_at: null, available_actions: [],
};

const pagination = {
  page: 1, page_size: 20, total_count: 1, total_pages: 1,
  has_next: false, has_previous: false,
};

function ok(data: unknown, page?: typeof pagination): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, pagination: page }) } as Response;
}
