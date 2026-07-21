import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import {
  postAndAllocateDirectRepayment,
} from '../../../../../sfpcl-lms/src/services/servicingApi';
import {
  clearStoredAuthSession,
  storedAuthSession,
} from '../../../../../sfpcl-lms/src/services/authSession';

const permissions = [
  'finance.repayment.create',
  'finance.repayment.mark_sap_posted',
  'finance.repayment.allocate',
];

const storage = new Map<string, string>();

const capture = {
  repayment_id: 'repayment-review-1',
  loan_account_id: 'account-review-1',
  repayment_source: 'direct_farmer',
  amount_received: '100000.00',
  received_date: '2026-12-04',
  payment_method: 'rtgs',
  bank_reference_number: 'UTR-REVIEW-001',
  bank_statement_line_id: null,
  statement_match_status: 'not_linked',
  allocation_status: 'pending',
  sap_posting: {
    status: 'pending', due_date: '2026-12-07',
    sap_entry_reference: null, posted_at: null,
  },
};

const allocation = {
  repayment_allocation_id: 'allocation-review-1',
  repayment_id: capture.repayment_id,
  allocation_rule: 'principal_first',
  allocation_rule_version: 'v1',
  allocation_status: 'allocated',
  allocated_to_principal: '100000.00',
  allocated_to_interest: '0.00',
  allocated_to_charges: '0.00',
  unallocated_amount: '0.00',
  exception_reason: null,
  loan_account: {
    principal_outstanding: '300000.00', interest_outstanding: '0.00',
    charges_outstanding: '0.00', total_outstanding: '300000.00',
  },
};

const ok = (data: unknown): Response => ({
  ok: true,
  status: 200,
  json: async () => ({ success: true, data }),
}) as Response;

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'review-token', refreshToken: 'review-refresh' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

it('resumes the canonical SAP/allocation owner after capture succeeded before a transport failure', async () => {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(ok(capture))
    .mockResolvedValueOnce({
      ok: false,
      status: 503,
      json: async () => ({
        success: false,
        error: { code: 'UPSTREAM_UNAVAILABLE', message: 'SAP step unavailable.' },
      }),
    } as Response)
    .mockResolvedValueOnce(ok({
      idempotency_replayed: true,
      original_response: capture,
    }))
    .mockResolvedValueOnce(ok({
      ...capture,
      sap_posting: {
        status: 'posted', due_date: '2026-12-07',
        sap_entry_reference: 'SAP-REVIEW-001', posted_at: '2026-12-04T10:00:00Z',
      },
    }))
    .mockResolvedValueOnce(ok(allocation));
  vi.stubGlobal('fetch', fetchMock);

  const attempt = {
    loanAccountId: capture.loan_account_id,
    capture: {
      repayment_source: 'direct_farmer' as const,
      amount_received: capture.amount_received,
      received_date: capture.received_date,
      payment_method: 'rtgs',
      bank_reference_number: capture.bank_reference_number,
      remarks: 'Confirmed direct receipt.',
    },
    sapPosting: {
      sap_entry_reference: 'SAP-REVIEW-001',
      sap_posted_at: '2026-12-04T10:00:00Z',
      remarks: 'SAP receipt confirmed.',
    },
    idempotencyKey: 'review-partial-repayment-attempt',
    permissions,
    roleCodes: ['accounts_head'],
  };

  await expect(postAndAllocateDirectRepayment(attempt)).rejects.toThrow(
    'SAP step unavailable.',
  );
  await expect(postAndAllocateDirectRepayment(attempt)).resolves.toMatchObject({
    allocation: { repayment_id: capture.repayment_id },
  });
  expect(fetchMock).toHaveBeenCalledTimes(5);
});
