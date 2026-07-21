import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import {
  authenticatedAllPagesRequest,
  clearStoredAuthSession,
  storedAuthSession,
} from '../../../../../sfpcl-lms/src/services/authSession';
import {
  postAndAllocateDirectRepayment,
  runPortfolioInterestAccrual,
} from '../../../../../sfpcl-lms/src/services/servicingApi';

const storage = new Map<string, string>();

const ok = (data: unknown, pagination?: Record<string, unknown>): Response => ({
  ok: true,
  status: 200,
  json: async () => ({ success: true, data, ...(pagination ? { pagination } : {}) }),
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

it('AR-010-SERVICING-SEAM-001 rejects capture-only command responses without client-side financial mutations', async () => {
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
    sap_posting: { status: 'pending', due_date: '2026-12-07', sap_entry_reference: null, posted_at: null },
  };
  const allocation = {
    repayment_allocation_id: 'allocation-review-1', repayment_id: capture.repayment_id,
    allocation_rule: 'principal_first', allocation_rule_version: 'v1', allocation_status: 'allocated',
    allocated_to_principal: '100000.00', allocated_to_interest: '0.00',
    allocated_to_charges: '0.00', unallocated_amount: '0.00', exception_reason: null,
    loan_account: { principal_outstanding: '300000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '300000.00' },
  };
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(ok(capture))
    .mockResolvedValueOnce(ok({ ...capture, sap_posting: { ...capture.sap_posting, status: 'posted' } }))
    .mockResolvedValueOnce(ok(allocation));
  vi.stubGlobal('fetch', fetchMock);

  let rejected = false;
  try {
    await postAndAllocateDirectRepayment({
      loanAccountId: capture.loan_account_id,
      capture: {
        repayment_source: 'direct_farmer', amount_received: capture.amount_received,
        received_date: capture.received_date, payment_method: 'rtgs',
        bank_reference_number: capture.bank_reference_number, remarks: 'Confirmed receipt.',
      },
      sapPosting: { sap_entry_reference: 'SAP-REVIEW-001', sap_posted_at: '2026-12-04T10:00:00Z', remarks: 'Confirmed SAP posting.' },
      idempotencyKey: 'review-composite-owner',
      permissions: ['finance.repayment.create', 'finance.repayment.mark_sap_posted', 'finance.repayment.allocate'],
      roleCodes: ['accounts_head'],
    });
  } catch {
    rejected = true;
  }

  expect(rejected, 'FAIL: capture-only transport truth must be rejected as malformed').toBe(true);
  expect(fetchMock, 'FAIL: the staff client must invoke only the composite command').toHaveBeenCalledTimes(1);
});

it('AR-010-INTEREST-UI-001 rejects duplicate identities across otherwise stable pages', async () => {
  const first = Array.from({ length: 100 }, (_, index) => ({ id: `loan-${index + 1}` }));
  const pagination = {
    page: 1, page_size: 100, total_count: 101, total_pages: 2,
    has_next: true, has_previous: false,
  };
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce(ok(first, pagination))
    .mockResolvedValueOnce(ok([{ id: 'loan-100' }], {
      ...pagination, page: 2, has_next: false, has_previous: true,
    })));

  await expect(
    authenticatedAllPagesRequest<{ id: string }>(page => `/api/v1/loan-accounts/?page=${page}&page_size=100`),
    'FAIL: repeated page identity silently replaces loan 101',
  ).rejects.toThrow();
});

it('AR-010-INTEREST-UI-001 rejects a portfolio selection duplicated across separate batches', async () => {
  const ids = [
    ...Array.from({ length: 100 }, (_, index) => `loan-${index + 1}`),
    'loan-100',
  ];
  const resultFor = (loan_account_id: string) => ({
    loan_account_id, outcome: 'created', persisted: true, interest_accrued_amount: '10.00',
  });
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce(ok({ accrual_month: '2026-06', dry_run: false, results: ids.slice(0, 100).map(resultFor) }))
    .mockResolvedValueOnce(ok({ accrual_month: '2026-06', dry_run: false, results: [resultFor('loan-100')] })));

  await expect(
    runPortfolioInterestAccrual('2026-06', ids, 'review-portfolio-owner'),
    'FAIL: 101 selected rows contain only 100 unique loans',
  ).rejects.toThrow();
});
