// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import RepaymentsHub from './RepaymentsHub';
import { fetchLoanAccounts } from '../../services/loanAccountsApi';
import {
  fetchBankStatementLines,
  fetchLoanLedger,
  fetchRepayments,
  postAndAllocateDirectRepayment,
} from '../../services/servicingApi';
import pageSource from './RepaymentsHub.tsx?raw';
import ledgerSource from '../../components/loan/RepaymentLedger.tsx?raw';
import { AuthSessionError } from '../../services/authSession';

vi.mock('../../contexts/RoleContext', () => ({ useRole: () => ({ currentUser }) }));
vi.mock('../../services/loanAccountsApi', () => ({ fetchLoanAccounts: vi.fn() }));
vi.mock('../../services/servicingApi', () => ({
  fetchBankStatementLines: vi.fn(), fetchLoanLedger: vi.fn(), fetchRepayments: vi.fn(),
  postAndAllocateDirectRepayment: vi.fn(),
  canPostAndAllocateRepayment: (_permissions: string[], roles: string[]) => roles.includes('accounts_head'),
}));

describe('010MA Repayments Hub wiring', () => {
  beforeEach(() => {
    vi.mocked(fetchLoanAccounts).mockResolvedValue({ items: [account], pagination });
    vi.mocked(fetchLoanLedger).mockResolvedValue({ items: [ledgerRow], pagination });
    vi.mocked(fetchRepayments).mockResolvedValue({ items: [subsidiary], pagination });
    vi.mocked(fetchBankStatementLines).mockImplementation(status => Promise.resolve(
      status === 'unmatched'
        ? { items: [statementLine], pagination }
        : { items: [], pagination: emptyPagination },
    ));
    vi.mocked(postAndAllocateDirectRepayment).mockResolvedValue({ replayed: false, capture, allocation });
  });
  afterEach(() => { currentUser.roleCodes = ['accounts_head']; cleanup(); vi.clearAllMocks(); });

  it('renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence', async () => {
    render(<RepaymentsHub />);
    expect(screen.getByText('Loading repayment workspace…')).toBeTruthy();
    expect(await screen.findByText('UTR-SERVER-001')).toBeTruthy();
    expect(screen.getAllByText('₹3,00,000.00').length).toBeGreaterThanOrEqual(2);

    await userEvent.click(screen.getByText('Statement Exceptions'));
    expect(await screen.findByText('no exact receipt candidate')).toBeTruthy();
    expect(screen.getByText('₹75,000.00')).toBeTruthy();

    await userEvent.click(screen.getByText('Subsidiary Reconciliation'));
    expect(await screen.findByText('PRODUCE-PAY-001')).toBeTruthy();
    expect(screen.getByText('Pending Statement')).toBeTruthy();
    expect(screen.getByText('₹50,000.00')).toBeTruthy();
    expect(screen.getByText('₹25,000.00')).toBeTruthy();
  });

  it('posts one governed direct attempt, displays backend allocation, and refreshes reads', async () => {
    render(<RepaymentsHub />);
    await screen.findByText('UTR-SERVER-001');
    await userEvent.click(screen.getByRole('button', { name: 'Record Receipt' }));
    await userEvent.clear(screen.getByLabelText('Amount Received (₹)'));
    await userEvent.type(screen.getByLabelText('Amount Received (₹)'), '100000.00');
    await userEvent.type(screen.getByLabelText('Bank Reference / UTR'), 'UTR-NEW-001');
    await userEvent.type(screen.getByLabelText('SAP Entry Reference'), 'SAP-NEW-001');
    await userEvent.click(screen.getByRole('button', { name: 'Post and Allocate' }));

    await waitFor(() => expect(postAndAllocateDirectRepayment).toHaveBeenCalledTimes(1));
    expect(await screen.findByText('₹1,00,000.00 allocated to principal')).toBeTruthy();
    expect(screen.getByText('₹0.00 allocated to interest')).toBeTruthy();
    expect(fetchLoanAccounts).toHaveBeenCalledTimes(2);
    expect(fetchLoanLedger).toHaveBeenCalledTimes(2);
  });

  it('pages each statement queue independently through canonical server pagination', async () => {
    vi.mocked(fetchBankStatementLines).mockReset()
      .mockResolvedValueOnce({ items: [statementLine], pagination: { ...pagination, has_next: true, total_count: 21, total_pages: 2 } })
      .mockResolvedValueOnce({ items: [], pagination: emptyPagination })
      .mockResolvedValueOnce({ items: [{ ...statementLine, bank_statement_line_id: 'line-2', line_number: 21 }], pagination: { ...pagination, page: 2, has_previous: true, has_next: false, total_count: 21, total_pages: 2 } });
    render(<RepaymentsHub />);
    await screen.findByText('UTR-SERVER-001');
    await userEvent.click(screen.getByText('Statement Exceptions'));
    await userEvent.click(screen.getAllByRole('button', { name: /Next/ })[0]);
    await waitFor(() => expect(fetchBankStatementLines).toHaveBeenCalledWith('unmatched', 2, 20));
    expect(await screen.findByText('21')).toBeTruthy();
  });

  it('does not expose the combined action to a permission-bearing non-source role', async () => {
    currentUser.roleCodes = ['senior_manager_finance'];
    render(<RepaymentsHub />);
    await screen.findByText('UTR-SERVER-001');
    expect(screen.queryByRole('button', { name: 'Record Receipt' })).toBeNull();
  });

  it('ignores an older loan response after the selected account changes', async () => {
    let resolveFirstLedger!: (value: { items: Array<typeof ledgerRow>; pagination: typeof pagination }) => void;
    vi.mocked(fetchLoanAccounts).mockResolvedValue({ items: [account, secondAccount], pagination: { ...pagination, total_count: 2 } });
    vi.mocked(fetchLoanLedger).mockImplementation(loanId => loanId === 'account-1'
      ? new Promise(resolve => { resolveFirstLedger = resolve; })
      : Promise.resolve({ items: [secondLedgerRow], pagination }));
    vi.mocked(fetchRepayments).mockResolvedValue({ items: [], pagination: emptyPagination });

    render(<RepaymentsHub />);
    await userEvent.click(await screen.findByText('LN-API-002'));
    expect(await screen.findByText('UTR-SECOND')).toBeTruthy();
    resolveFirstLedger({ items: [ledgerRow], pagination });
    await waitFor(() => expect(screen.queryByText('UTR-SERVER-001')).toBeNull());
    expect(screen.getByText('UTR-SECOND')).toBeTruthy();
  });

  it('renders a subsidiary-specific unauthorized state without stale rows', async () => {
    vi.mocked(fetchRepayments).mockRejectedValue(
      new AuthSessionError('FORBIDDEN', 'Subsidiary reconciliation scope denied.', 403),
    );
    render(<RepaymentsHub />);
    expect((await screen.findAllByText('Subsidiary reconciliation scope denied.')).length).toBeGreaterThanOrEqual(1);
    await userEvent.click(screen.getByText('Subsidiary Reconciliation'));
    expect(screen.getAllByText('Access Denied').length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText('PRODUCE-PAY-001')).toBeNull();
  });

  it.each([
    new AuthSessionError('VALIDATION_ERROR', 'Amount must be a positive decimal.', 400),
    new AuthSessionError('CONFLICT', 'This bank reference is already recorded.', 409),
  ])('shows backend posting denial without retry or canonical refresh: %s', async denial => {
    vi.mocked(postAndAllocateDirectRepayment).mockRejectedValueOnce(denial);
    render(<RepaymentsHub />);
    await screen.findByText('UTR-SERVER-001');
    await userEvent.click(screen.getByRole('button', { name: 'Record Receipt' }));
    await userEvent.type(screen.getByLabelText('Amount Received (₹)'), '100000.00');
    await userEvent.type(screen.getByLabelText('Bank Reference / UTR'), 'UTR-DENIED');
    await userEvent.type(screen.getByLabelText('SAP Entry Reference'), 'SAP-DENIED');
    await userEvent.click(screen.getByRole('button', { name: 'Post and Allocate' }));
    expect(await screen.findByText(denial.message)).toBeTruthy();
    expect(postAndAllocateDirectRepayment).toHaveBeenCalledTimes(1);
    expect(fetchLoanAccounts).toHaveBeenCalledTimes(1);
  });

  it('removes every inherited mock and client-owned financial calculation', () => {
    for (const source of [pageSource, ledgerSource]) {
      expect(source).not.toContain('mockData');
      expect(source).not.toMatch(/\.reduce\(/);
      expect(source).not.toContain('allocationPreview');
    }
  });
});

const currentUser = { permissions: ['finance.loan_account.read', 'finance.repayment.create', 'finance.repayment.mark_sap_posted', 'finance.repayment.allocate', 'finance.bank_statement.read'], roleCodes: ['accounts_head'] };
const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const emptyPagination = { ...pagination, total_count: 0 };
const account = { loan_account_id: 'account-1', loan_account_number: 'LN-API-001', loan_application_id: 'application-1', application_reference_number: 'LO-API-001', member: { member_id: 'member-1', display_name: 'API Borrower' }, sap_customer_code: '******001', loan_type: 'short_term', facility_type: 'short_term', interest_rate_type: 'floating', current_interest_rate: '9.2500', sanctioned_amount: '400000.00', disbursed_amount: '400000.00', principal_outstanding: '300000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '300000.00', loan_account_status: 'active', tenure_start_date: '2026-06-22', tenure_end_date: null, repayment_date: '2027-06-22', tenure_months: 12, created_at: '2026-06-20T10:00:00Z', activated_at: '2026-06-22T14:00:00Z' };
const secondAccount = { ...account, loan_account_id: 'account-2', loan_account_number: 'LN-API-002', member: { ...account.member, member_id: 'member-2', display_name: 'Second API Borrower' } };
const ledgerRow = { transaction_date: '2026-12-04', transaction_type: 'repayment', owner_reference: { entity_type: 'repayment_allocation', entity_id: 'allocation-1' }, reference: 'UTR-SERVER-001', debit: '0.00', credit: '100000.00', principal_balance: '300000.00', interest_balance: '0.00', total_outstanding: '300000.00', actor: { user_id: 'user-1', display_name: 'Accounts User' }, sap_status: 'posted', remarks: 'Repayment allocated principal first.' };
const secondLedgerRow = { ...ledgerRow, owner_reference: { ...ledgerRow.owner_reference, entity_id: 'allocation-2' }, reference: 'UTR-SECOND' };
const subsidiary = { repayment_id: 'repayment-sub-1', loan_account_id: 'account-1', repayment_source: 'subsidiary_deduction' as const, amount_received: '75000.00', received_date: '2026-12-15', payment_method: 'subsidiary_transfer', bank_reference_number: 'SUB-001', bank_statement_line_id: null, statement_match_status: 'not_linked', allocation_status: 'allocated', sap_posting_status: 'pending', sap_posting_due_date: '2026-12-16', sap_entry_reference: null, sap_posted_at: null, allocation: { allocated_to_principal: '50000.00', allocated_to_interest: '25000.00', allocated_to_charges: '0.00', unallocated_amount: '0.00', exception_reason: null }, subsidiary_reconciliation: { subsidiary_company_id: 'company-1', produce_payment_reference: 'PRODUCE-PAY-001', transfer_reference: 'SUB-001', tri_party_agreement_id: 'agreement-1', reconciliation_status: 'pending_statement', treasury_verification_status: 'pending' } };
const statementLine = { bank_statement_line_id: 'line-1', line_number: 1, transaction_date: '2026-12-15', value_date: '2026-12-15', amount: '75000.00', parse_status: 'parsed', match_status: 'unmatched', match_reason_code: 'no_exact_receipt_candidate', matched_repayment_id: null, repayment_evidence: null };
const capture = { repayment_id: 'repayment-new', loan_account_id: 'account-1', repayment_source: 'direct_farmer', amount_received: '100000.00', received_date: '2026-12-04', payment_method: 'rtgs', bank_reference_number: 'UTR-NEW-001', bank_statement_line_id: null, statement_match_status: 'not_linked', allocation_status: 'pending', sap_posting: { status: 'pending', due_date: '2026-12-07', sap_entry_reference: null, posted_at: null } };
const allocation = { repayment_allocation_id: 'allocation-new', repayment_id: 'repayment-new', allocation_rule: 'principal_first' as const, allocation_rule_version: 'v1', allocation_status: 'allocated', allocated_to_principal: '100000.00', allocated_to_interest: '0.00', allocated_to_charges: '0.00', unallocated_amount: '0.00', exception_reason: null, loan_account: { principal_outstanding: '200000.00', interest_outstanding: '0.00', charges_outstanding: '0.00', total_outstanding: '200000.00' } };
