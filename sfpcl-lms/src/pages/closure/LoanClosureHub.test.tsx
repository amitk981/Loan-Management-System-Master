// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import { fetchAllLoanAccounts, type LoanAccountProjection } from '../../services/loanAccountsApi';
import {
  archiveLoanFile, closeLoan, fetchArchiveRecord, fetchClosureReadiness, fetchNoc,
  issueNoc, recordSecurityReturn, type ArchiveRecordProjection,
  type ClosureReadinessProjection, type LoanClosureProjection, type NocProjection,
  type SecurityReturnProjection,
} from '../../services/recoveryApi';
import LoanClosureHub from './LoanClosureHub';
import closureSource from './LoanClosureHub.tsx?raw';
const currentUser = {
  id: 'staff-011pc', role: 'company_secretary', roleCodes: ['company_secretary'],
  permissions: [
    'finance.loan_account.read', 'closure.readiness.read', 'closure.loan.close',
    'closure.noc.issue', 'closure.security_return.record', 'closure.archive.create',
    'closure.archive.read',
  ],
  availableActions: [], isBackendSession: true,
};
vi.mock('../../contexts/RoleContext', () => ({ useRole: () => ({ currentUser }) }));
vi.mock('../../services/loanAccountsApi', () => ({ fetchAllLoanAccounts: vi.fn() }));

vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchClosureReadiness: vi.fn(),
  closeLoan: vi.fn(),
  fetchNoc: vi.fn(),
  issueNoc: vi.fn(),
  recordSecurityReturn: vi.fn(),
  fetchArchiveRecord: vi.fn(),
  archiveLoanFile: vi.fn(),
}));
const account: LoanAccountProjection = {
  loan_account_id: 'loan-011pc', loan_account_number: 'LN-CLOSURE-011PC',
  loan_application_id: 'application-011pc', application_reference_number: 'APP-CLOSURE-011PC',
  member: { member_id: 'member-011pc', display_name: 'Closure Test Member' },
  sap_customer_code: 'SAP-011PC', loan_type: 'term_loan', facility_type: 'term_loan',
  interest_rate_type: 'fixed', current_interest_rate: '8.5000',
  sanctioned_amount: '500000.00', disbursed_amount: '500000.00',
  principal_outstanding: '0.00', interest_outstanding: '125.00',
  charges_outstanding: '0.00', total_outstanding: '125.00',
  loan_account_status: 'partially_repaid',
  tenure_start_date: '2025-01-01', tenure_end_date: '2026-07-25',
  repayment_date: '2026-07-25', tenure_months: 18,
  created_at: '2025-01-01T10:00:00Z', activated_at: '2025-01-02T10:00:00Z',
};
const blockedReadiness: ClosureReadinessProjection = {
  loan_account_id: account.loan_account_id,
  ready_for_closure: false,
  checks: [
    { code: 'principal_paid', status: 'pass' },
    { code: 'interest_paid_or_approved_adjustment', status: 'fail' },
    { code: 'charges_paid', status: 'pass' },
    { code: 'ledger_reconciled', status: 'pass' },
    { code: 'recovery_clear', status: 'pass' },
    {
      code: 'security_tasks_identified',
      status: 'pass',
      security_return_required: true,
      physical_share_return_required: true,
      demat_unpledge_required: false,
      blank_cheque_return_required: true,
      poa_release_required: false,
    },
  ],
  principal_outstanding: '0.00', interest_outstanding: '125.00',
  charges_outstanding: '0.00', total_outstanding: '125.00',
  interest_adjustment_applied: false, security_return_required: true,
  physical_share_return_required: true, demat_unpledge_required: false,
  blank_cheque_return_required: true, poa_release_required: false,
};
const readyReadiness: ClosureReadinessProjection = {
  ...blockedReadiness,
  ready_for_closure: true,
  interest_outstanding: '0.00',
  total_outstanding: '0.00',
  checks: blockedReadiness.checks.map(check => ({ ...check, status: 'pass' })),
};
const financialClosure: LoanClosureProjection = {
  loan_closure_id: 'closure-011pc', loan_account_id: account.loan_account_id,
  loan_account_status: 'closed', closure_stage: 'financially_closed', closure_type: 'full_repayment',
  closed_at: '2026-07-25T10:00:00Z',
  noc_required: true, security_return_required: true, archive_required: true,
  requirements: { noc: 'pending', security_return: 'pending', archive: 'pending' },
  idempotency_replayed: false,
  available_actions: ['closure.noc.issue', 'closure.security_return.record', 'closure.archive.create'],
};
const noc: NocProjection = {
  noc_id: 'noc-011pc', loan_closure_id: financialClosure.loan_closure_id,
  loan_account_id: account.loan_account_id, member_id: account.member.member_id,
  document_id: 'document-011pc', issued_by_user_id: currentUser.id,
  issued_at: '2026-07-25T10:15:00Z', signatory_user_id: currentUser.id,
  signatory_role_code: 'company_secretary', delivery_mode: 'email', delivery_status: 'queued',
  communication_id: 'communication-011pc', communication_job_id: 'job-011pc',
  borrower_name: account.member.display_name, loan_account_number: account.loan_account_number,
  application_reference: account.application_reference_number!,
  disbursed_amount: account.disbursed_amount,
  full_repayment_at: '2026-07-25T09:30:00Z',
  idempotency_replayed: false,
};
const securityReturn: SecurityReturnProjection = {
  security_return_id: 'security-return-011pc', loan_closure_id: financialClosure.loan_closure_id,
  security_package_id: null, status: 'completed', version: 1,
  completed_at: '2026-07-25T10:30:00Z',
  items: [
    { item_type: 'sh4', status: 'completed', source_item_id: 'sh4-011pc', custody_location: 'Vault A', returned_released_to: 'Closure Test Member' },
    { item_type: 'blank_cheque', status: 'completed', source_item_id: 'cheque-011pc', custody_location: 'Vault A', returned_released_to: 'Closure Test Member' },
    { item_type: 'poa', status: 'not_applicable', source_item_id: null, custody_location: '', returned_released_to: '' },
    { item_type: 'cdsl', status: 'not_applicable', source_item_id: null, custody_location: '', returned_released_to: '' },
  ],
  idempotency_replayed: false,
  available_actions: [],
};
const archive: ArchiveRecordProjection = {
  archive_record_id: 'archive-011pc', loan_closure_id: financialClosure.loan_closure_id,
  loan_account_id: account.loan_account_id, file_location_physical: 'Archive Room / Rack A / Box 12',
  file_location_digital: null, retention_start_date: '2026-07-25', retention_until_date: '2034-07-25',
  archived_by_user_id: currentUser.id, archived_by_role_code: 'company_secretary',
  archived_at: '2026-07-25T10:45:00Z', destruction_eligible: false,
  destruction_certificate_id: null, idempotency_replayed: false,
  available_actions: [],
};
beforeEach(() => {
  currentUser.permissions = [
    'finance.loan_account.read', 'closure.readiness.read', 'closure.loan.close',
    'closure.noc.issue', 'closure.security_return.record', 'closure.archive.create',
    'closure.archive.read',
  ];
  vi.mocked(fetchAllLoanAccounts).mockResolvedValue({
    items: [account], totalCount: 1, totalPages: 1, pageSize: 100,
  });
  vi.mocked(fetchClosureReadiness).mockResolvedValue(blockedReadiness);
  vi.mocked(fetchNoc).mockRejectedValue(new AuthSessionError('NOT_FOUND', 'NOC not found.', 404));
  vi.mocked(fetchArchiveRecord).mockRejectedValue(new AuthSessionError('NOT_FOUND', 'Archive not found.', 404));
});
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
describe('011PC closure readiness and downstream owner wiring', () => {
  it('renders named server blockers and keeps NOC unavailable before financial closure', async () => {
    render(<LoanClosureHub />);
    expect(await screen.findByText('LN-CLOSURE-011PC')).toBeTruthy();
    expect(screen.getByText('Interest Paid Or Approved Adjustment')).toBeTruthy();
    expect(screen.getByText('Failed')).toBeTruthy();
    expect(screen.getAllByText('₹125.00').length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: 'Close Loan Financially' }).hasAttribute('disabled')).toBe(true);
    await userEvent.click(screen.getByRole('button', { name: 'NOC Generation' }));
    expect(screen.getByText('NOC remains blocked until the backend creates a financially-closed loan identity.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Issue NOC' })).toBeNull();
  });

  it('renders loading, empty, unauthorized, and general error states', async () => {
    let resolveAccounts: ((value: Awaited<ReturnType<typeof fetchAllLoanAccounts>>) => void) | undefined;
    vi.mocked(fetchAllLoanAccounts).mockReturnValue(new Promise(resolve => { resolveAccounts = resolve; }));
    const loading = render(<LoanClosureHub />);
    expect(screen.getByText('Loading closure candidates…')).toBeTruthy();
    resolveAccounts?.({ items: [account], totalCount: 1, totalPages: 1, pageSize: 100 });
    await screen.findByText('LN-CLOSURE-011PC');
    loading.unmount();
    vi.mocked(fetchAllLoanAccounts).mockResolvedValueOnce({ items: [], totalCount: 0, totalPages: 1, pageSize: 100 });
    const empty = render(<LoanClosureHub />);
    expect(await screen.findByText('No loan accounts are available in your closure scope.')).toBeTruthy();
    empty.unmount();
    vi.mocked(fetchAllLoanAccounts).mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Closure scope denied.', 403));
    const denied = render(<LoanClosureHub />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Closure scope denied.')).toBeTruthy();
    denied.unmount();
    vi.mocked(fetchAllLoanAccounts).mockRejectedValueOnce(new Error('Closure service unavailable.'));
    render(<LoanClosureHub />);
    expect(await screen.findByText('Closure Hub Unavailable')).toBeTruthy();
    expect(screen.getByText('Closure service unavailable.')).toBeTruthy();
    cleanup();
    vi.mocked(fetchAllLoanAccounts).mockResolvedValueOnce({ items: [account], totalCount: 1, totalPages: 1, pageSize: 100 });
    vi.mocked(fetchClosureReadiness).mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Readiness denied.', 403));
    render(<LoanClosureHub />);
    expect(await screen.findByText('Readiness denied.')).toBeTruthy();
    expect(screen.getByText('Access Denied')).toBeTruthy();
  });

  it('validates notes, closes from server readiness, and refetches canonical downstream reads', async () => {
    vi.mocked(fetchClosureReadiness)
      .mockResolvedValueOnce(readyReadiness)
      .mockResolvedValueOnce(readyReadiness);
    vi.mocked(closeLoan).mockResolvedValue(financialClosure);

    render(<LoanClosureHub />);
    expect((await screen.findAllByText('Ready For Closure')).length).toBeGreaterThan(0);
    await userEvent.click(screen.getByRole('button', { name: 'Close Loan Financially' }));
    expect(screen.getByText('Closure notes are required.')).toBeTruthy();

    await userEvent.type(screen.getByLabelText('Closure notes'), 'Canonical balances and blockers reviewed.');
    await userEvent.click(screen.getByRole('button', { name: 'Close Loan Financially' }));

    await waitFor(() => expect(closeLoan).toHaveBeenCalledWith(account.loan_account_id, {
      closure_notes: 'Canonical balances and blockers reviewed.',
      idempotency_key: expect.stringMatching(/^closure:/),
    }));
    expect(fetchClosureReadiness).toHaveBeenCalledTimes(2);
    expect(fetchNoc).toHaveBeenCalledWith(financialClosure.loan_closure_id);
    expect(fetchArchiveRecord).toHaveBeenCalledWith(financialClosure.loan_closure_id);
    expect(await screen.findByText('Financial closure recorded from canonical backend state.')).toBeTruthy();
    expect(screen.getAllByText('Financially Closed').length).toBeGreaterThan(0);
  });

  it('issues NOC then renders the canonical refetch projection', async () => {
    vi.mocked(fetchClosureReadiness).mockResolvedValue(readyReadiness);
    vi.mocked(closeLoan).mockResolvedValue(financialClosure);
    vi.mocked(issueNoc).mockResolvedValue(noc);
    vi.mocked(fetchNoc)
      .mockRejectedValueOnce(new AuthSessionError('NOT_FOUND', 'NOC not found.', 404))
      .mockResolvedValue(noc);

    render(<LoanClosureHub />);
    await userEvent.type(await screen.findByLabelText('Closure notes'), 'Canonical balances and blockers reviewed.');
    await userEvent.click(screen.getByRole('button', { name: 'Close Loan Financially' }));
    await screen.findByText('Financial closure recorded from canonical backend state.');
    await userEvent.click(screen.getByRole('button', { name: 'NOC Generation' }));
    await userEvent.click(screen.getByRole('button', { name: 'Issue NOC' }));
    expect(screen.getByText('Document ID is required.')).toBeTruthy();

    await userEvent.type(screen.getByLabelText('NOC document ID'), noc.document_id);
    await userEvent.type(screen.getByLabelText('Borrower email'), 'member@example.test');
    await userEvent.click(screen.getByRole('button', { name: 'Issue NOC' }));

    await waitFor(() => expect(issueNoc).toHaveBeenCalledWith(financialClosure.loan_closure_id, {
      document_id: noc.document_id,
      delivery_mode: 'email',
      recipient_email: 'member@example.test',
      signatory_user_id: currentUser.id,
      idempotency_key: expect.stringMatching(/^noc:/),
    }));
    expect(await screen.findByText('NOC issued from canonical backend state.')).toBeTruthy();
    expect(screen.getAllByText('Queued').length).toBeGreaterThan(0);
    expect(screen.getByText(noc.noc_id)).toBeTruthy();
  });

  it('records server-owned security state and archives only after downstream prerequisites', async () => {
    vi.mocked(fetchClosureReadiness).mockResolvedValue(readyReadiness);
    vi.mocked(closeLoan).mockResolvedValue(financialClosure);
    vi.mocked(fetchNoc).mockResolvedValue(noc);
    vi.mocked(recordSecurityReturn).mockResolvedValue(securityReturn);
    vi.mocked(archiveLoanFile).mockResolvedValue(archive);
    vi.mocked(fetchArchiveRecord).mockRejectedValue(
      new AuthSessionError('NOT_FOUND', 'Archive not found.', 404),
    );

    render(<LoanClosureHub />);
    await userEvent.type(await screen.findByLabelText('Closure notes'), 'Canonical balances and blockers reviewed.');
    await userEvent.click(screen.getByRole('button', { name: 'Close Loan Financially' }));
    await screen.findByText('Financial closure recorded from canonical backend state.');

    await userEvent.click(screen.getByRole('button', { name: 'Security Return / Unpledge' }));
    await userEvent.click(screen.getByRole('button', { name: 'Record Security Return' }));
    expect(recordSecurityReturn).toHaveBeenCalledWith(financialClosure.loan_closure_id, {
      payload: {}, idempotency_key: expect.stringMatching(/^security-return:/),
    });
    expect(await screen.findByText('Security return recorded from the canonical action response.')).toBeTruthy();
    expect(screen.getAllByText('Completed').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Vault A').length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole('button', { name: 'Archive' }));
    await userEvent.click(screen.getByRole('button', { name: 'Archive Loan File' }));
    expect(screen.getByText('A physical or digital archive location is required.')).toBeTruthy();
    await userEvent.type(screen.getByLabelText('Physical archive location'), archive.file_location_physical!);
    vi.mocked(fetchArchiveRecord).mockResolvedValue(archive);
    await userEvent.click(screen.getByRole('button', { name: 'Archive Loan File' }));
    expect(await screen.findByText('Archive recorded from canonical backend state.')).toBeTruthy();
    expect(screen.getByText('2034-07-25')).toBeTruthy();
  });

  it('is the final mock-removal owner and contains no inline closure fixtures', () => {
    expect(closureSource).not.toMatch(/mockData|const\s+closureLoans\s*=/);
    expect(closureSource).not.toMatch(/Asha Bhosale|Vijay Patil|Radha Kisan/);
  });
});
