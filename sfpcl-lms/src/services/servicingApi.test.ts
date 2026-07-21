import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  canPostAndAllocateRepayment,
  fetchLoanLedger,
  fetchRepaymentSchedule,
  postAndAllocateDirectRepayment,
} from './servicingApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'accounts-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('servicing API module', () => {
  it('requires an active source role as well as every combined-action permission', () => {
    const permissions = [
      'finance.repayment.create', 'finance.repayment.mark_sap_posted',
      'finance.repayment.allocate',
    ];
    expect(canPostAndAllocateRepayment(permissions, ['accounts_head'])).toBe(true);
    expect(canPostAndAllocateRepayment(permissions, ['credit_manager'])).toBe(true);
    expect(canPostAndAllocateRepayment(permissions, ['senior_manager_finance'])).toBe(false);
  });

  it('reads schedule and ledger pages through authenticated standard pagination', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([scheduleRow], pagination))
      .mockResolvedValueOnce(ok([ledgerRow], {
        ...pagination, page: 3, total_count: 41, total_pages: 3,
      }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchRepaymentSchedule('account-1', 2, 20)).resolves.toMatchObject({
      items: [{ principal_due: '400000.00', total_due: '410000.00' }],
      pagination: { page: 2 },
    });
    await expect(fetchLoanLedger('account-1', 3, 20)).resolves.toMatchObject({
      items: [{ credit: '100000.00', principal_balance: '300000.00' }],
      pagination: { page: 3 },
    });
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/loan-accounts/account-1/repayment-schedule/?page=2&page_size=20',
      'http://127.0.0.1:8000/api/v1/loan-accounts/account-1/ledger/?page=3&page_size=20',
    ]);
  });

  it('delegates capture, SAP posting, and allocation to one backend-owned command', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({ replayed: false, capture, allocation }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(postAndAllocateDirectRepayment({
      loanAccountId: 'account-1',
      capture: {
        repayment_source: 'direct_farmer', amount_received: '100000.00',
        received_date: '2026-12-04', payment_method: 'rtgs',
        bank_reference_number: 'UTR-001', remarks: 'Confirmed direct receipt.',
      },
      sapPosting: {
        sap_entry_reference: 'SAP-001', sap_posted_at: '2026-12-04T10:00:00.000Z',
        remarks: 'SAP receipt confirmed.',
      },
      idempotencyKey: 'repayment-attempt-1',
      permissions: [
        'finance.repayment.create', 'finance.repayment.mark_sap_posted',
        'finance.repayment.allocate',
      ],
      roleCodes: ['accounts_head'],
    })).resolves.toEqual({ replayed: false, capture, allocation });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(
      'http://127.0.0.1:8000/api/v1/loan-accounts/account-1/direct-repayment-command/',
    );
    expect(fetchMock.mock.calls[0][1]).toEqual(expect.objectContaining({
      method: 'POST', headers: expect.objectContaining({ 'Idempotency-Key': 'repayment-attempt-1' }),
    }));
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
      capture: expect.objectContaining({ bank_reference_number: 'UTR-001' }),
      sap_posting: expect.objectContaining({ sap_entry_reference: 'SAP-001' }),
    });
  });

  it('stops an exact capture replay before a second SAP or allocation mutation', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({
      replayed: true, capture, allocation,
    }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(postAndAllocateDirectRepayment({
      loanAccountId: 'account-1', capture: {
        repayment_source: 'direct_farmer', amount_received: '100000.00',
        received_date: '2026-12-04', payment_method: 'rtgs',
        bank_reference_number: 'UTR-001', remarks: 'Confirmed direct receipt.',
      },
      sapPosting: { sap_entry_reference: 'SAP-001', sap_posted_at: '2026-12-04T10:00:00.000Z', remarks: 'SAP receipt confirmed.' },
      idempotencyKey: 'repayment-attempt-1',
      permissions: ['finance.repayment.create', 'finance.repayment.mark_sap_posted', 'finance.repayment.allocate'],
      roleCodes: ['credit_manager'],
    })).resolves.toEqual({ replayed: true, capture, allocation });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

const pagination = { page: 2, page_size: 20, total_count: 21, total_pages: 2, has_next: false, has_previous: true };
const scheduleRow = { repayment_schedule_id: 'schedule-1', installment_number: 1, due_date: '2027-06-22', principal_due: '400000.00', interest_due: '10000.00', charges_due: '0.00', total_due: '410000.00', paid_principal: '0.00', paid_interest: '0.00', paid_charges: '0.00', amount_received: '0.00', schedule_status: 'pending', extended_due_date: null, created_at: '2026-06-22T00:00:00Z' };
const ledgerRow = { transaction_date: '2026-12-04', transaction_type: 'repayment', owner_reference: { entity_type: 'repayment_allocation', entity_id: 'allocation-1' }, reference: 'UTR-001', debit: '0.00', credit: '100000.00', principal_balance: '300000.00', interest_balance: '0.00', total_outstanding: '300000.00', actor: { user_id: 'user-1', display_name: 'Accounts User' }, sap_status: 'posted', remarks: 'Repayment allocated principal first.' };
const capture = { repayment_id: 'repayment-1', loan_account_id: 'account-1', repayment_source: 'direct_farmer', amount_received: '100000.00', received_date: '2026-12-04', payment_method: 'rtgs', bank_reference_number: 'UTR-001', bank_statement_line_id: null, statement_match_status: 'not_linked', allocation_status: 'pending', sap_posting: { status: 'pending', due_date: '2026-12-07', sap_entry_reference: null, posted_at: null } };
const allocation = { repayment_allocation_id: 'allocation-1', repayment_id: 'repayment-1', allocation_rule: 'principal_first', allocation_rule_version: 'v1', allocation_status: 'allocated', allocated_to_principal: '100000.00', allocated_to_interest: '0.00', allocated_to_charges: '0.00', unallocated_amount: '0.00', exception_reason: null, loan_account: { principal_outstanding: '300000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '300000.00' } };

function ok(data: unknown, page?: typeof pagination): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, pagination: page }) } as Response;
}
