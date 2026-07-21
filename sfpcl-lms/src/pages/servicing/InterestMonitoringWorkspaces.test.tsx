// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import InterestManagement from '../interest/InterestManagement';
import MonitoringDashboard from '../monitoring/MonitoringDashboard';
import { fetchLoanAccounts } from '../../services/loanAccountsApi';
import * as servicing from '../../services/servicingApi';
import { AuthSessionError } from '../../services/authSession';

let permissions: string[] = [];
vi.mock('../../contexts/RoleContext', () => ({ useRole: () => ({ currentUser: { permissions } }) }));
vi.mock('../../services/loanAccountsApi', () => ({ fetchLoanAccounts: vi.fn() }));
vi.mock('../../services/servicingApi', async importOriginal => ({ ...(await importOriginal<typeof servicing>()), fetchInterestInvoices: vi.fn(), generateInterestInvoice: vi.fn(), runInterestAccrual: vi.fn(), previewInterestCapitalisations: vi.fn(), capitaliseInterest: vi.fn(), fetchDpdPortfolio: vi.fn(), fetchReminders: vi.fn() }));

const pagination = { page: 1, page_size: 100, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
const account = { loan_account_id: 'account-1', loan_account_number: 'LN-API-001', member: { member_id: 'member-1', display_name: 'Canonical Member' }, principal_outstanding: '300000.00', interest_outstanding: '27750.00', repayment_date: '2027-03-31' };

beforeEach(() => {
  vi.clearAllMocks(); permissions = ['finance.loan_account.read', 'monitoring.dpd.read'];
  vi.mocked(fetchLoanAccounts).mockResolvedValue({ items: [account], pagination } as never);
  vi.mocked(servicing.fetchInterestInvoices).mockResolvedValue({ items: [{ interest_invoice_id: 'invoice-1', loan_account_id: 'account-1', invoice_number: 'INV-API-001', financial_year: 'FY2026-27', interest_amount: '27750.00', invoice_status: 'issued', delivery_status: 'sent', invoice_date: '2027-03-31' }], pagination } as never);
  vi.mocked(servicing.previewInterestCapitalisations).mockResolvedValue({ financial_year: 'FY2026-27', as_of_date: '2027-05-01', dry_run: true, results: [{ loan_account_id: 'account-1', eligible: true, reason_code: 'eligible_unpaid_interest', old_principal_amount: '300000.00', unpaid_interest_amount: '27750.00', new_principal_amount: '327750.00' }] });
});
afterEach(cleanup);

describe('interest and monitoring workspaces', () => {
  it('renders canonical interest values and uses the exact accrual permission', async () => {
    permissions.push('finance.accrual.bulk_generate');
    vi.mocked(servicing.runInterestAccrual).mockResolvedValue({ accrual_month: '2026-06', dry_run: false, results: [{ loan_account_id: 'account-1', outcome: 'created', persisted: true, interest_accrued_amount: '2312.50' }] });
    render(<InterestManagement />);
    await screen.findByText('No canonical accrual run has been loaded.');
    fireEvent.click(screen.getByRole('button', { name: 'Yearly Invoices' }));
    expect(screen.getByText('INV-API-001')).toBeTruthy();
    expect(screen.getByText('₹27,750.00')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Monthly Interest Accrual' }));
    fireEvent.click(screen.getByRole('button', { name: 'Run Monthly Accrual' }));
    expect(await screen.findByText('₹2,312.50')).toBeTruthy();
    expect(servicing.runInterestAccrual).toHaveBeenCalledWith('2026-06', ['account-1'], expect.any(String));
  });

  it('renders backend DPD buckets and retained reminders and fails the whole view on one reminder read error', async () => {
    vi.mocked(servicing.fetchDpdPortfolio).mockResolvedValue({ sop_bucket_counts: { current: 0, one_to_two_years: 1, two_to_three_years: 0, more_than_three_years: 0 }, total_count: 1, rows: [{ dpd_status_id: 'dpd-1', loan_account_id: 'account-1', loan_account_number: 'LN-API-001', member_display_name: 'Canonical Member', loan_account_status: 'overdue', principal_outstanding: '300000.00', interest_outstanding: '27750.00', repayment_date: '2027-03-31', as_of_date: '2026-06-30', days_past_due: 367, sop_bucket: 'one_to_two_years', standard_bucket: 'over_90', principal_overdue_amount: '1000.00', interest_overdue_amount: '100.00', total_overdue_amount: '1100.00' }] });
    vi.mocked(servicing.fetchReminders).mockResolvedValue([{ reminder_id: 'reminder-1', loan_account_id: 'account-1', member_id: 'member-1', quarter_end_date: '2026-06-30', eligibility_decision: { eligible: true, reason: 'outstanding_beyond_one_year' }, reminder_type: 'outstanding_beyond_one_year', origin: 'automatic', channel: 'sms', delivery_status: 'sent', status_reason: null, next_follow_up_date: '2026-07-07', call_outcome: null, created_by: { user_id: 'user-1', display_name: 'Credit Manager' }, created_at: '2026-06-30T10:00:00Z' }]);
    const { unmount } = render(<MonitoringDashboard onOpenLoan={vi.fn()} />);
    expect(await screen.findByText('LN-API-001')).toBeTruthy();
    expect(screen.getByText('1–2 years')).toBeTruthy(); fireEvent.click(screen.getByRole('button', { name: /View All/ })); expect(screen.getByText('Sent')).toBeTruthy();
    unmount(); vi.mocked(servicing.fetchReminders).mockRejectedValue(new Error('Reminder projection unavailable.'));
    render(<MonitoringDashboard onOpenLoan={vi.fn()} />);
    expect(await screen.findByText('Monitoring Unavailable')).toBeTruthy();
    await waitFor(() => expect(screen.queryByText('LN-API-001')).toBeNull());
  });

  it('retains backend 403 and validation truth without optimistic interest state', async () => {
    permissions.push('finance.interest_invoice.create', 'finance.interest_capitalise');
    vi.mocked(servicing.generateInterestInvoice).mockRejectedValue(new AuthSessionError('FORBIDDEN', 'Configured invoice ownership is required.', 403));
    render(<InterestManagement />); await screen.findByText('No canonical accrual run has been loaded.');
    fireEvent.click(screen.getByRole('button', { name: 'Yearly Invoices' })); fireEvent.click(screen.getByRole('button', { name: /Generate Invoice/ }));
    expect(await screen.findByText('Access Denied')).toBeTruthy(); expect(screen.getByText('INV-API-001')).toBeTruthy();
    vi.mocked(servicing.previewInterestCapitalisations).mockRejectedValue(new AuthSessionError('VALIDATION_ERROR', 'Capitalisation check failed.', 400, { financial_year: 'Use FYyyyy-yy.' }));
    fireEvent.click(screen.getByRole('button', { name: 'Interest Capitalisation' })); fireEvent.click(screen.getByRole('button', { name: 'Preview Capitalisation' }));
    expect(await screen.findByText('Validation Error')).toBeTruthy(); expect(screen.getByText('Financial Year: Use FYyyyy-yy.')).toBeTruthy();
  });
});
