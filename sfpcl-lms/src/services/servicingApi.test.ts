import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  capitaliseInterest,
  canCapitaliseInterest,
  canGenerateAccrual,
  fetchDpdPortfolio,
  fetchAllInterestInvoices,
  fetchInterestInvoices,
  fetchReminders,
  generateInterestInvoice,
  previewInterestCapitalisations,
  runInterestAccrual,
  runPortfolioInterestAccrual,
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
  it('uses exact canonical permissions for interest mutations', () => {
    expect(canGenerateAccrual(['finance.accrual.bulk_generate'])).toBe(true);
    expect(canGenerateAccrual(['finance.accrual.create'])).toBe(false);
    expect(canCapitaliseInterest(['finance.interest_capitalise'])).toBe(true);
    expect(canCapitaliseInterest(['monitoring.dpd.read'])).toBe(false);
  });

  it('reads canonical interest and monitoring projections without client calculations', async () => {
    const reminderPage = Array.from({ length: 100 }, (_, index) => ({ ...reminder, reminder_id: `reminder-${index + 1}` }));
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([invoice], pagination))
      .mockResolvedValueOnce(ok(dpdPortfolio))
      .mockResolvedValueOnce(ok(reminderPage, { page: 1, page_size: 100, total_count: 101, total_pages: 2, has_next: true, has_previous: false }))
      .mockResolvedValueOnce(ok([{ ...reminder, reminder_id: 'reminder-2' }], { page: 2, page_size: 100, total_count: 101, total_pages: 2, has_next: false, has_previous: true }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchInterestInvoices()).resolves.toMatchObject({ items: [invoice] });
    await expect(fetchDpdPortfolio()).resolves.toEqual(dpdPortfolio);
    await expect(fetchReminders()).resolves.toEqual([...reminderPage, { ...reminder, reminder_id: 'reminder-2' }]);
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/interest-invoices/?page=1&page_size=100',
      'http://127.0.0.1:8000/api/v1/dpd-statuses/',
      'http://127.0.0.1:8000/api/v1/reminders/?page=1&page_size=100',
      'http://127.0.0.1:8000/api/v1/reminders/?page=2&page_size=100',
    ]);
  });

  it('loads complete invoice collections at 1, 100, and 101 records', async () => {
    for (const count of [1, 100, 101]) {
      const rows = Array.from({ length: count }, (_, index) => ({
        ...invoice,
        interest_invoice_id: `invoice-${index + 1}`,
        invoice_number: `INV-${index + 1}`,
      }));
      const firstRows = rows.slice(0, 100);
      const totalPages = count === 101 ? 2 : 1;
      const fetchMock = vi.fn().mockResolvedValueOnce(ok(firstRows, {
        page: 1, page_size: 100, total_count: count, total_pages: totalPages,
        has_next: totalPages > 1, has_previous: false,
      }));
      if (count === 101) {
        fetchMock.mockResolvedValueOnce(ok(rows.slice(100), {
          page: 2, page_size: 100, total_count: 101, total_pages: 2,
          has_next: false, has_previous: true,
        }));
      }
      vi.stubGlobal('fetch', fetchMock);

      await expect(fetchAllInterestInvoices()).resolves.toMatchObject({
        items: rows,
        totalCount: count,
        totalPages,
      });
    }
  });

  it('sends one caller-stable key for each canonical interest mutation', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(invoice))
      .mockResolvedValueOnce(ok(accrualRun))
      .mockResolvedValueOnce(ok(capitalisationPreview))
      .mockResolvedValueOnce(ok(capitalisation));
    vi.stubGlobal('fetch', fetchMock);

    await generateInterestInvoice('account-1', 'FY2026-27', 'invoice-key');
    await runInterestAccrual('2026-06', ['account-1'], 'accrual-key');
    await previewInterestCapitalisations('FY2026-27', '2027-05-01');
    await capitaliseInterest('account-1', 'FY2026-27', '2027-05-01', 'capital-key');

    expect(fetchMock.mock.calls.map(call => [call[0], call[1]?.headers?.['Idempotency-Key']])).toEqual([
      ['http://127.0.0.1:8000/api/v1/loan-accounts/account-1/interest-invoices/', 'invoice-key'],
      ['http://127.0.0.1:8000/api/v1/accrual-entries/bulk-generate/', 'accrual-key'],
      ['http://127.0.0.1:8000/api/v1/interest-capitalisations/check/', undefined],
      ['http://127.0.0.1:8000/api/v1/loan-accounts/account-1/interest-capitalisations/', 'capital-key'],
    ]);
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({
      accrual_month: '2026-06', dry_run: false, loan_account_ids: ['account-1'],
    });
  });

  it('accrues all 101 explicitly selected loans in backend-authorised batches', async () => {
    const loanAccountIds = Array.from({ length: 101 }, (_, index) => `account-${index + 1}`);
    const firstResults = loanAccountIds.slice(0, 100).map(loan_account_id => ({
      loan_account_id, outcome: 'created', persisted: true, interest_accrued_amount: '10.00',
    }));
    const finalResult = {
      loan_account_id: 'account-101', outcome: 'existing', persisted: true,
      interest_accrued_amount: '10.00',
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok({ accrual_month: '2026-06', dry_run: false, results: firstResults }))
      .mockResolvedValueOnce(ok({ accrual_month: '2026-06', dry_run: false, results: [finalResult] }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(runPortfolioInterestAccrual(
      '2026-06', loanAccountIds, 'portfolio-accrual-key',
    )).resolves.toEqual({
      accrual_month: '2026-06',
      dry_run: false,
      results: [...firstResults, finalResult],
      selection: { loan_account_count: 101, batch_count: 2, completed_batches: 2 },
    });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).loan_account_ids).toEqual(loanAccountIds.slice(0, 100));
    expect(JSON.parse(fetchMock.mock.calls[1][1].body).loan_account_ids).toEqual(['account-101']);
    expect(fetchMock.mock.calls.map(call => call[1].headers['Idempotency-Key'])).toEqual([
      'portfolio-accrual-key:batch-1-of-2',
      'portfolio-accrual-key:batch-2-of-2',
    ]);
  });

  it('reports completed membership when a later portfolio accrual batch is denied', async () => {
    const loanAccountIds = Array.from({ length: 101 }, (_, index) => `account-${index + 1}`);
    const firstResults = loanAccountIds.slice(0, 100).map(loan_account_id => ({
      loan_account_id, outcome: 'created', persisted: true, interest_accrued_amount: '10.00',
    }));
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(ok({ accrual_month: '2026-06', dry_run: false, results: firstResults }))
      .mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ success: false, error: { code: 'FORBIDDEN', message: 'Backend scope changed.' } }),
      } as Response));

    await expect(runPortfolioInterestAccrual(
      '2026-06', loanAccountIds, 'portfolio-accrual-key',
    )).rejects.toMatchObject({
      message: 'Portfolio accrual stopped after 100 of 101 selected loans (1 of 2 batches). Backend scope changed.',
      completedRun: {
        results: firstResults,
        selection: { loan_account_count: 101, batch_count: 2, completed_batches: 1 },
      },
    });
  });

  it('rejects an accrual batch whose backend results omit selected membership', async () => {
    const loanAccountIds = Array.from({ length: 101 }, (_, index) => `account-${index + 1}`);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok({
      accrual_month: '2026-06',
      dry_run: false,
      results: loanAccountIds.slice(0, 99).map(loan_account_id => ({
        loan_account_id, outcome: 'created', persisted: true, interest_accrued_amount: '10.00',
      })),
    })));

    await expect(runPortfolioInterestAccrual(
      '2026-06', loanAccountIds, 'portfolio-accrual-key',
    )).rejects.toMatchObject({
      message: 'Portfolio accrual stopped after 0 of 101 selected loans (0 of 2 batches). The backend returned incomplete accrual batch membership.',
      completedRun: { results: [], selection: { completed_batches: 0 } },
    });
  });

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
const invoice = { interest_invoice_id: 'invoice-1', loan_account_id: 'account-1', member_id: 'member-1', financial_year: 'FY2026-27', invoice_number: 'INV-001', invoice_date: '2027-03-31', interest_period_start: '2026-04-01', interest_period_end: '2027-03-31', principal_base_amount: '300000.00', interest_rate: '9.2500', gross_interest_amount: '27750.00', interest_paid_amount: '0.00', tax_amount: '0.00', fixed_fee_amount: '0.00', interest_amount: '27750.00', invoice_status: 'issued', rate_version_number: 3, calculation_version: 'INT-1', document_id: 'document-1', communication_id: 'communication-1', delivery_status: 'sent', generated_by_user_id: 'user-1', generated_at: '2027-04-01T10:00:00Z', issued_by_user_id: 'user-1', issued_at: '2027-04-01T11:00:00Z' };
const accrualRun = { accrual_month: '2026-06', dry_run: false, results: [{ loan_account_id: 'account-1', outcome: 'created', persisted: true, interest_accrued_amount: '2312.50' }] };
const capitalisationPreview = { financial_year: 'FY2026-27', as_of_date: '2027-05-01', dry_run: true, results: [{ loan_account_id: 'account-1', eligible: true, reason_code: 'eligible_unpaid_interest', old_principal_amount: '300000.00', unpaid_interest_amount: '27750.00', new_principal_amount: '327750.00' }] };
const capitalisation = { interest_capitalisation_id: 'capital-1', loan_account_id: 'account-1', financial_year: 'FY2026-27', old_principal_amount: '300000.00', unpaid_interest_amount: '27750.00', new_principal_amount: '327750.00', status: 'capitalised' };
const dpdPortfolio = { sop_bucket_counts: { current: 0, one_to_two_years: 1, two_to_three_years: 0, more_than_three_years: 0 }, total_count: 1, rows: [{ dpd_status_id: 'dpd-1', loan_account_id: 'account-1', loan_account_number: 'LN-001', member_display_name: 'Canonical Member', as_of_date: '2026-06-30', days_past_due: 367, sop_bucket: 'one_to_two_years', standard_bucket: 'over_90', principal_overdue_amount: '1000.00', interest_overdue_amount: '100.00', total_overdue_amount: '1100.00' }] };
const reminder = { reminder_id: 'reminder-1', loan_account_id: 'account-1', member_id: 'member-1', quarter_end_date: '2026-06-30', eligibility_decision: { eligible: true, reason: 'outstanding_beyond_one_year' }, reminder_type: 'outstanding_beyond_one_year', origin: 'automatic', channel: 'sms', delivery_status: 'sent', status_reason: null, next_follow_up_date: '2026-07-07', call_outcome: null, created_by: { user_id: 'user-1', display_name: 'Credit Manager' }, created_at: '2026-06-30T10:00:00Z' };

function ok(data: unknown, page?: typeof pagination): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, pagination: page }) } as Response;
}
