import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import {
  clearStoredAuthSession,
  storedAuthSession,
} from '../../../../../sfpcl-lms/src/services/authSession';
import { postAndAllocateDirectRepayment } from '../../../../../sfpcl-lms/src/services/servicingApi';

const storage = new Map<string, string>();

const ok = (data: unknown): Response => ({
  ok: true,
  status: 200,
  json: async () => ({ success: true, data }),
}) as Response;

const attempt = {
  loanAccountId: 'account-review-1',
  capture: {
    repayment_source: 'direct_farmer' as const,
    amount_received: '100000.00',
    received_date: '2026-12-04',
    payment_method: 'rtgs' as const,
    bank_reference_number: 'UTR-REVIEW-001',
    remarks: 'Confirmed receipt.',
  },
  sapPosting: {
    sap_entry_reference: 'SAP-REVIEW-001',
    sap_posted_at: '2026-12-04T10:00:00Z',
    remarks: 'Confirmed SAP posting.',
  },
  idempotencyKey: 'review-composite-owner',
  permissions: [
    'finance.repayment.create',
    'finance.repayment.mark_sap_posted',
    'finance.repayment.allocate',
  ],
  roleCodes: ['accounts_head'],
};

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

it('AR-010-SERVICING-SEAM-001 rejects identifier-only composite truth', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok({
    replayed: false,
    capture: { repayment_id: 'repayment-review-1' },
    allocation: { repayment_allocation_id: 'allocation-review-1' },
  })));

  await expect(
    postAndAllocateDirectRepayment(attempt),
    'FAIL: incomplete nested capture/allocation truth is accepted as a complete financial result',
  ).rejects.toThrow('malformed');
});

it('AR-010-SERVICING-SEAM-001 rejects cross-repayment composite truth', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok({
    replayed: false,
    capture: { repayment_id: 'repayment-review-1' },
    allocation: {
      repayment_allocation_id: 'allocation-review-1',
      repayment_id: 'different-repayment-review-2',
    },
  })));

  await expect(
    postAndAllocateDirectRepayment(attempt),
    'FAIL: allocation ownership is not bound to the returned capture',
  ).rejects.toThrow('malformed');
});
