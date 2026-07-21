// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../../../services/authSession';
import * as portalApi from '../../../../services/portalApi';
import MP15_MyLoans from './MP15_MyLoans';
import MP16_LoanAccountDetail from './MP16_LoanAccountDetail';
import MP17_Repayments from './MP17_Repayments';
import MP18_DirectRepaymentInfo from './MP18_DirectRepaymentInfo';
import mp15Source from './MP15_MyLoans.tsx?raw';
import mp16Source from './MP16_LoanAccountDetail.tsx?raw';
import mp17Source from './MP17_Repayments.tsx?raw';
import mp18Source from './MP18_DirectRepaymentInfo.tsx?raw';

vi.mock('../../../../services/portalApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../../../services/portalApi')>(),
  fetchPortalLoanAccounts: vi.fn(),
  fetchPortalLoanAccount: vi.fn(),
  fetchPortalLoanSchedule: vi.fn(),
  fetchPortalRepaymentHistory: vi.fn(),
  fetchPortalInterestInvoices: vi.fn(),
  fetchPortalDirectRepaymentInstructions: vi.fn(),
}));

const listMock = vi.mocked(portalApi.fetchPortalLoanAccounts);
const detailMock = vi.mocked(portalApi.fetchPortalLoanAccount);
const scheduleMock = vi.mocked(portalApi.fetchPortalLoanSchedule);
const historyMock = vi.mocked(portalApi.fetchPortalRepaymentHistory);
const invoicesMock = vi.mocked(portalApi.fetchPortalInterestInvoices);
const instructionsMock = vi.mocked(portalApi.fetchPortalDirectRepaymentInstructions);

beforeEach(() => {
  listMock.mockResolvedValue([loan]);
  detailMock.mockResolvedValue(detail);
  scheduleMock.mockResolvedValue([schedule]);
  historyMock.mockResolvedValue([repayment]);
  invoicesMock.mockResolvedValue([]);
  instructionsMock.mockResolvedValue(instructions);
});
afterEach(() => { cleanup(); vi.clearAllMocks(); });

describe('MP15-MP18 portal loan views', () => {
  it('loads own loans and preserves explicit account selection for every destination', async () => {
    const select = vi.fn();
    render(<MP15_MyLoans onSelectLoan={select} />);
    expect(screen.getByText('Loading your loans…')).toBeTruthy();
    expect(await screen.findByText('LN-PORTAL-001')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'View Loan' }));
    await userEvent.click(screen.getByRole('button', { name: 'View Repayments' }));
    await userEvent.click(screen.getByRole('button', { name: 'Repayment Instructions' }));
    expect(select.mock.calls).toEqual([
      ['loan-1', 'detail'], ['loan-1', 'repayments'], ['loan-1', 'instructions'],
    ]);
  });

  it('shows empty, API error, and unauthorised list states without fixtures', async () => {
    listMock.mockResolvedValueOnce([]);
    const empty = render(<MP15_MyLoans onSelectLoan={vi.fn()} />);
    expect(await screen.findByText('No active loan accounts.')).toBeTruthy();
    empty.unmount();
    listMock.mockRejectedValueOnce(new Error('backend detail must not leak'));
    const failed = render(<MP15_MyLoans onSelectLoan={vi.fn()} />);
    expect(await screen.findByText('Loan information could not be loaded. Please try again.')).toBeTruthy();
    expect(screen.queryByText('backend detail must not leak')).toBeNull();
    failed.unmount();
    listMock.mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Denied', 403));
    render(<MP15_MyLoans onSelectLoan={vi.fn()} />);
    expect(await screen.findByText('You are not authorised to view these loan details.')).toBeTruthy();
  });

  it('renders detail, schedule, confirmed history, invoice empty state, and long mobile-safe rows', async () => {
    historyMock.mockResolvedValueOnce(Array.from({ length: 24 }, (_, index) => ({ ...repayment, repayment_id: `repayment-${index}`, reference: `SAFE-${index}` })));
    render(<MP16_LoanAccountDetail loanAccountId="loan-1" onBack={vi.fn()} onViewRepayments={vi.fn()} />);
    expect(await screen.findByText('LN-PORTAL-001')).toBeTruthy();
    expect(screen.getByText('Confirmed Repayment History')).toBeTruthy();
    expect(screen.getByText('No issued interest invoices.')).toBeTruthy();
    expect(detailMock).toHaveBeenCalledWith('loan-1');
    expect(scheduleMock).toHaveBeenCalledWith('loan-1');
    expect(historyMock).toHaveBeenCalledWith('loan-1');
    expect(invoicesMock).toHaveBeenCalledWith('loan-1');
  });

  it('never ranks an account when repayments or instructions have no explicit selection', () => {
    const repaymentsView = render(<MP17_Repayments loanAccountId={null} onBack={vi.fn()} />);
    expect(screen.getByText('Select a loan from My Loans to view confirmed repayments.')).toBeTruthy();
    repaymentsView.unmount();
    render(<MP18_DirectRepaymentInfo loanAccountId={null} onBack={vi.fn()} />);
    expect(screen.getByText('Select a loan from My Loans to view repayment instructions.')).toBeTruthy();
    expect(detailMock).not.toHaveBeenCalled();
    expect(instructionsMock).not.toHaveBeenCalled();
  });

  it('shows only confirmed repayment data and read-only approved masked instructions', async () => {
    const repaymentView = render(<MP17_Repayments loanAccountId="loan-1" onBack={vi.fn()} />);
    expect(await screen.findByText('SAFE-REFERENCE')).toBeTruthy();
    expect(screen.getByText('Confirmed')).toBeTruthy();
    expect(screen.queryByText('Under verification')).toBeNull();
    repaymentView.unmount();
    render(<MP18_DirectRepaymentInfo loanAccountId="loan-1" onBack={vi.fn()} />);
    expect(await screen.findByText('********4321')).toBeTruthy();
    expect(screen.getByText('LN-PORTAL-001')).toBeTruthy();
    expect(screen.queryByLabelText(/UTR/i)).toBeNull();
    expect(screen.queryByRole('button', { name: /submit/i })).toBeNull();
  });

  it('contains no mock source or inline business fixture in MP15-MP18', () => {
    const source = [mp15Source, mp16Source, mp17Source, mp18Source].join('\n');
    expect(source).not.toContain('mockData');
    expect(source).not.toContain('LO00000042');
    expect(source).not.toContain('UTR2026');
    expect(source).not.toContain('RBL Bank');
    expect(source).not.toContain('useState(false)');
  });
});

const loan: portalApi.PortalLoanAccountSummary = { loan_account_id: 'loan-1', loan_account_number: 'LN-PORTAL-001', application_id: 'app-1', application_reference: 'APP-001', status: 'active', closure_status: 'active', disbursed_amount: '400000.00', principal_outstanding: '300000.00', next_due_date: '2026-12-31', next_due_amount: '100000.00' };
const detail: portalApi.PortalLoanAccountDetail = { ...loan, interest_outstanding: '5000.00', charges_outstanding: '0.00', total_outstanding: '305000.00', repayment_route: 'direct', closed_at: null };
const schedule: portalApi.PortalLoanScheduleItem = { schedule_id: 'schedule-1', installment_number: 1, due_date: '2026-12-31', principal_due: '100000.00', interest_due: '5000.00', charges_due: '0.00', total_due: '105000.00', paid_principal: '0.00', paid_interest: '0.00', paid_amount: '0.00', status: 'pending' };
const repayment: portalApi.PortalRepaymentHistoryItem = { repayment_id: 'repayment-1', receipt_date: '2026-10-01', amount_received: '100000.00', allocated_to_principal: '95000.00', allocated_to_interest: '5000.00', payment_mode: 'neft', repayment_source: 'direct_farmer', reference: 'SAFE-REFERENCE', acknowledgement: null, status: 'confirmed' };
const instructions: portalApi.PortalDirectRepaymentInstructions = { available: true, projection_version: 'PORTAL-REPAYMENT-2026-01', approved_at: '2026-04-01T00:00:00Z', beneficiary_name: 'SFPCL Collections', bank_name: 'Approved Bank', account_number_masked: '********4321', ifsc: 'APPR0001234', required_narration: 'LN-PORTAL-001', amount_due: '305000.00', proof_submission_enabled: false, available_actions: [], disclaimer: 'Repayment updates after verification and posting.' };
