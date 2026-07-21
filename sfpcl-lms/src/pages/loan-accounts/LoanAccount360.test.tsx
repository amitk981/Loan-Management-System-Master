// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import LoanAccount360 from './LoanAccount360';
import {
  fetchLoanAccount,
  fetchLoanAccounts,
  type LoanAccountProjection,
} from '../../services/loanAccountsApi';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchLoanLedger,
  fetchRepaymentSchedule,
} from '../../services/servicingApi';
import pageSource from './LoanAccount360.tsx?raw';
import apiSource from '../../services/loanAccountsApi.ts?raw';

vi.mock('../../services/loanAccountsApi', () => ({
  fetchLoanAccounts: vi.fn(),
  fetchLoanAccount: vi.fn(),
}));
vi.mock('../../services/servicingApi', () => ({
  fetchLoanLedger: vi.fn(),
  fetchRepaymentSchedule: vi.fn(),
}));

const account: LoanAccountProjection = {
  loan_account_id: 'account-1', loan_account_number: 'LN-API-001',
  loan_application_id: 'application-1', application_reference_number: 'LO-API-001',
  member: { member_id: 'member-1', display_name: 'API Borrower' },
  sap_customer_code: '******-001', loan_type: 'short_term', facility_type: 'short_term',
  interest_rate_type: 'floating', current_interest_rate: '9.2500',
  sanctioned_amount: '400000.00', disbursed_amount: '400000.00',
  principal_outstanding: '400000.00', interest_outstanding: '0.00',
  charges_outstanding: '0.00', total_outstanding: '400000.00',
  loan_account_status: 'active', tenure_start_date: '2026-06-22', tenure_end_date: null,
  repayment_date: '2027-06-22', tenure_months: 12,
  created_at: '2026-06-20T10:00:00Z', activated_at: '2026-06-22T14:00:00Z',
};

const pagination = {
  page: 1, page_size: 20, total_count: 1, total_pages: 1,
  has_next: false, has_previous: false,
};

describe('009J Loan Account 360 initial API view', () => {
  beforeEach(() => {
    vi.mocked(fetchLoanAccounts).mockResolvedValue({ items: [account], pagination });
    vi.mocked(fetchLoanAccount).mockResolvedValue(account);
    vi.mocked(fetchLoanLedger).mockResolvedValue({ items: [ledgerRow], pagination });
    vi.mocked(fetchRepaymentSchedule).mockResolvedValue({ items: [scheduleRow], pagination });
  });
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('loads the scoped account list and routes the selected server identity', async () => {
    const onSelect = vi.fn();
    render(<LoanAccount360 loanAccountId={null} onSelect={onSelect} />);

    expect(screen.getByText('Loading loan accounts…')).toBeTruthy();
    expect(await screen.findByText('LN-API-001')).toBeTruthy();
    expect(screen.getByText('API Borrower')).toBeTruthy();
    expect(screen.getAllByText('₹4,00,000.00')).toHaveLength(2);
    expect(fetchLoanAccounts).toHaveBeenCalledWith(1, 20);

    await userEvent.click(screen.getByText('LN-API-001'));
    await waitFor(() => expect(onSelect).toHaveBeenCalledWith('account-1'));
  });

  it('renders the header, KPI row, and Summary from exact active server values', async () => {
    render(<LoanAccount360 loanAccountId="account-1" onSelect={vi.fn()} />);

    expect(screen.getByText('Loading loan account summary…')).toBeTruthy();
    expect(await screen.findByRole('heading', { name: 'LN-API-001' })).toBeTruthy();
    expect(fetchLoanAccount).toHaveBeenCalledWith('account-1');
    expect(screen.getAllByText('₹4,00,000.00').length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText('9.2500% Floating')).toBeTruthy();
    expect(screen.getByText('12 months')).toBeTruthy();
    expect(screen.getByText('22 Jun 2026')).toBeTruthy();
    expect(screen.getByText(/22 Jun 2026 at/i)).toBeTruthy();
    expect(screen.queryByText('Scheduled Instalment')).toBeNull();
    expect(screen.queryByText('DPD Bucket')).toBeNull();
    expect(screen.queryByText('Next Action')).toBeNull();
    expect(screen.getByText('Summary')).toBeTruthy();
    expect(screen.getByText('Loan Ledger')).toBeTruthy();
    expect(screen.getByText('Repayment Schedule')).toBeTruthy();
  });

  it('shows honest empty, failure, and unauthorized states without mock fallback', async () => {
    vi.mocked(fetchLoanAccounts).mockResolvedValueOnce({
      items: [], pagination: { ...pagination, total_count: 0 },
    });
    const empty = render(<LoanAccount360 loanAccountId={null} onSelect={vi.fn()} />);
    expect(await screen.findByText('No loan accounts are available in your scope.')).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchLoanAccounts).mockRejectedValueOnce(new Error('Account service unavailable.'));
    const failed = render(<LoanAccount360 loanAccountId={null} onSelect={vi.fn()} />);
    expect(await screen.findByText('Account service unavailable.')).toBeTruthy();
    expect(screen.getByText('Loan Accounts Unavailable')).toBeTruthy();
    failed.unmount();

    vi.mocked(fetchLoanAccount).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Loan account scope denied.', 403),
    );
    render(<LoanAccount360 loanAccountId="account-1" onSelect={vi.fn()} />);
    expect(await screen.findByText('Loan account scope denied.')).toBeTruthy();
    expect(screen.getByText('Access Denied')).toBeTruthy();
    expect(screen.queryByText('Ganesh Thorat')).toBeNull();
  });

  it('uses only the shared authenticated boundary for the initial API projection', () => {
    expect(apiSource).toContain('authenticatedPaginatedRequest');
    expect(apiSource).toContain('authenticatedRequest');
    expect(apiSource).not.toContain('mockData');
    expect(apiSource).not.toContain('fetch(');
    expect(pageSource).toContain('fetchLoanAccounts');
    expect(pageSource).toContain('fetchLoanAccount');
    expect(pageSource).not.toContain("from '../../data/mockData'");
    expect(pageSource).not.toContain('monthlyEMI');
  });

  it('renders canonical ledger and schedule pages without calculating financial truth', async () => {
    render(<LoanAccount360 loanAccountId="account-1" onSelect={vi.fn()} />);
    await screen.findByRole('heading', { name: 'LN-API-001' });

    await userEvent.click(screen.getByText('Loan Ledger'));
    expect(await screen.findByText('UTR-SERVER-001')).toBeTruthy();
    expect(screen.getByText('₹1,00,000.00')).toBeTruthy();
    expect(screen.getAllByText('₹3,00,000.00')).toHaveLength(2);
    expect(screen.getByText('Page 1 of 1')).toBeTruthy();
    expect(fetchLoanLedger).toHaveBeenCalledWith('account-1', 1, 20);

    await userEvent.click(screen.getByText('Repayment Schedule'));
    expect(await screen.findByText('₹4,10,000.00')).toBeTruthy();
    expect(screen.getByText('Pending')).toBeTruthy();
    expect(fetchRepaymentSchedule).toHaveBeenCalledWith('account-1', 1, 20);
  });

  it('resets servicing pagination when the account identity changes', async () => {
    vi.mocked(fetchLoanLedger).mockResolvedValue({
      items: [ledgerRow], pagination: { ...pagination, has_next: true, total_pages: 2 },
    });
    const view = render(<LoanAccount360 loanAccountId="account-1" onSelect={vi.fn()} />);
    await screen.findByRole('heading', { name: 'LN-API-001' });
    await userEvent.click(screen.getByText('Loan Ledger'));
    await userEvent.click(await screen.findByRole('button', { name: /Next/ }));
    await waitFor(() => expect(fetchLoanLedger).toHaveBeenCalledWith('account-1', 2, 20));

    view.rerender(<LoanAccount360 loanAccountId="account-2" onSelect={vi.fn()} />);
    await waitFor(() => expect(fetchLoanLedger).toHaveBeenLastCalledWith('account-2', 1, 20));
  });
});

const ledgerRow = {
  transaction_date: '2026-12-04', transaction_type: 'repayment',
  owner_reference: { entity_type: 'repayment_allocation', entity_id: 'allocation-1' },
  reference: 'UTR-SERVER-001', debit: '0.00', credit: '100000.00',
  principal_balance: '300000.00', interest_balance: '0.00', total_outstanding: '300000.00',
  actor: { user_id: 'user-1', display_name: 'Accounts User' }, sap_status: 'posted',
  remarks: 'Repayment allocated principal first.',
};

const scheduleRow = {
  repayment_schedule_id: 'schedule-1', installment_number: 1, due_date: '2027-06-22',
  principal_due: '400000.00', interest_due: '10000.00', charges_due: '0.00',
  total_due: '410000.00', paid_principal: '0.00', paid_interest: '0.00',
  paid_charges: '0.00', amount_received: '0.00', schedule_status: 'pending',
  extended_due_date: null, created_at: '2026-06-22T00:00:00Z',
};
