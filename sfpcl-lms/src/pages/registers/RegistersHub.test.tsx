// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import RegistersHub from './RegistersHub';
import {
  fetchCreditSanctionRegister,
  fetchExceptionRegister,
} from '../../services/approvalRegistersApi';
import hubSource from './RegistersHub.tsx?raw';

let permissions = ['approvals.sanction_register.read', 'approvals.exception_register.read'];

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({
    currentUser: { permissions, isBackendSession: true },
    can: (permission: string) => (permission === 'export_registers' && permissions.includes('reports.export'))
      || (permission === 'view_approval_registers' && permissions.some(value => value.endsWith('_register.read'))),
  }),
}));

vi.mock('../../services/approvalRegistersApi', async importOriginal => {
  const actual = await importOriginal<typeof import('../../services/approvalRegistersApi')>();
  return { ...actual, fetchCreditSanctionRegister: vi.fn(), fetchExceptionRegister: vi.fn() };
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  permissions = ['approvals.sanction_register.read', 'approvals.exception_register.read'];
});

describe('RegistersHub owned approval register panels', () => {
  it('renders only the server-scoped frozen sanction page and replaces pagination after a filter change', async () => {
    vi.mocked(fetchCreditSanctionRegister)
      .mockResolvedValueOnce({ items: [sanctionRow], pagination: { ...pagination, page: 2, total_count: 1 } })
      .mockResolvedValueOnce({ items: [{ ...sanctionRow, decision: 'rejected', sanctioned_amount: null }], pagination: { ...pagination, total_count: 1 } });

    render(<RegistersHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Credit sanction register' }));

    expect(await screen.findByText('Frozen Borrower')).toBeTruthy();
    expect(screen.getByText('Frozen sanction reason')).toBeTruthy();
    expect(screen.getByText('Frozen exception business reason')).toBeTruthy();
    expect(screen.getByText(/approved · cycle 1/i)).toBeTruthy();
    expect(screen.getByText(/self declared abstention/i)).toBeTruthy();
    expect(screen.getByText(/director relative/i)).toBeTruthy();
    expect(screen.getByText(/Notice: notice-1/i)).toBeTruthy();
    expect(screen.queryByText('Hidden invalid borrower')).toBeNull();
    expect(screen.getByText('1 record')).toBeTruthy();
    expect(screen.getByText('Page 2 of 1')).toBeTruthy();

    await userEvent.selectOptions(screen.getByLabelText('Sanction decision'), 'rejected');
    await waitFor(() => expect(fetchCreditSanctionRegister).toHaveBeenLastCalledWith({
      financialYear: undefined, decision: 'rejected', page: 1, pageSize: 20,
    }));
    expect(await screen.findByText('Page 1 of 1')).toBeTruthy();
  });

  it('applies only canonical financial-year values', async () => {
    vi.mocked(fetchCreditSanctionRegister).mockResolvedValue({ items: [], pagination: { ...pagination, total_count: 0 } });
    render(<RegistersHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Credit sanction register' }));
    await waitFor(() => expect(fetchCreditSanctionRegister).toHaveBeenCalledTimes(1));

    await userEvent.type(screen.getByLabelText('Financial year'), '2026');
    expect(screen.getByRole('button', { name: 'Apply financial year' })).toHaveProperty('disabled', true);
    expect(fetchCreditSanctionRegister).toHaveBeenCalledTimes(1);

    await userEvent.clear(screen.getByLabelText('Financial year'));
    await userEvent.type(screen.getByLabelText('Financial year'), 'FY2026-99');
    expect(screen.getByRole('button', { name: 'Apply financial year' })).toHaveProperty('disabled', true);

    await userEvent.clear(screen.getByLabelText('Financial year'));
    await userEvent.type(screen.getByLabelText('Financial year'), 'FY2026-27');
    await userEvent.click(screen.getByRole('button', { name: 'Apply financial year' }));
    await waitFor(() => expect(fetchCreditSanctionRegister).toHaveBeenLastCalledWith({
      financialYear: 'FY2026-27', decision: undefined, page: 1, pageSize: 20,
    }));
  });

  it('loads S25 independently with immutable comments and evidence but no inferred download', async () => {
    permissions = ['approvals.exception_register.read'];
    vi.mocked(fetchExceptionRegister).mockResolvedValue({ items: [exceptionRow], pagination });
    render(<RegistersHub />);

    expect(await screen.findByText('Frozen exception description')).toBeTruthy();
    expect(screen.getByText('Frozen exception business reason')).toBeTruthy();
    expect(screen.getByText('CFO approved with monitoring.')).toBeTruthy();
    expect(screen.getByText('cash-flow-evidence.pdf')).toBeTruthy();
    expect(screen.getByText(/restricted/i)).toBeTruthy();
    expect(screen.queryByRole('button', { name: /download/i })).toBeNull();
    expect(screen.queryByRole('link', { name: /download/i })).toBeNull();
    expect(fetchCreditSanctionRegister).not.toHaveBeenCalled();

    await userEvent.selectOptions(screen.getByLabelText('Exception status'), 'approved');
    await waitFor(() => expect(fetchExceptionRegister).toHaveBeenLastCalledWith({
      status: 'approved', exceptionType: undefined, page: 1, pageSize: 20,
    }));
  });

  it('hides export without canonical permission and reports its deferred state when permitted', async () => {
    vi.mocked(fetchCreditSanctionRegister).mockResolvedValue({ items: [], pagination: { ...pagination, total_count: 0 } });
    const view = render(<RegistersHub />);
    expect(screen.queryByRole('button', { name: 'Export Register' })).toBeNull();

    permissions = [...permissions, 'reports.export'];
    view.rerender(<RegistersHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Export Register' }));
    expect(screen.getByText('Register export is scheduled for the reporting export slice.')).toBeTruthy();
  });

  it('shows a nondisclosing denied state with no fallback register facts', async () => {
    vi.mocked(fetchCreditSanctionRegister).mockRejectedValueOnce(new Error('You do not have Credit Sanction Register read permission.'));
    render(<RegistersHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Credit sanction register' }));
    expect(await screen.findByText('Credit sanction register unavailable')).toBeTruthy();
    expect(screen.queryByText('Ganesh Thorat')).toBeNull();
  });

  it('clears scoped register facts when the actor loses canonical permission', async () => {
    permissions = ['approvals.sanction_register.read'];
    vi.mocked(fetchCreditSanctionRegister).mockResolvedValue({ items: [sanctionRow], pagination });
    const view = render(<RegistersHub />);
    expect(await screen.findByText('Frozen Borrower')).toBeTruthy();

    permissions = [];
    view.rerender(<RegistersHub />);
    expect(screen.queryByText('Frozen Borrower')).toBeNull();
    expect(screen.getByText('Registers unavailable')).toBeTruthy();
    expect(screen.queryByText('Ganesh Thorat')).toBeNull();
  });

  it('keeps mock-backed variables outside the owned S23/S25 panel source', () => {
    const sanctionPanel = hubSource.slice(hubSource.indexOf('OWNED S23 START'), hubSource.indexOf('OWNED S23 END'));
    const exceptionPanel = hubSource.slice(hubSource.indexOf('OWNED S25 START'), hubSource.indexOf('OWNED S25 END'));
    expect(sanctionPanel).not.toMatch(/loanApplications|sanctionDecisions|mockData/);
    expect(exceptionPanel).not.toMatch(/loanApplications|const exceptions|mockData/);
  });
});

const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };

const sanctionRow = {
  credit_sanction_register_entry_id: 'register-valid', approval_case_id: 'case-valid', loan_application_id: 'application-valid',
  sanction_decision_id: 'decision-valid', workflow_event_id: 'event-valid', application_number: 'LO00000042',
  borrower_name: 'Frozen Borrower', borrower_type: 'individual_farmer', requested_amount: '500000.00', eligible_amount: '450000.00',
  recommended_amount: '440000.00', sanctioned_amount: '440000.00', approval_authority: 'CFO + one Director',
  approver_names: ['CFO One', 'Director One'], approval_date: '2026-07-13', decision: 'sanctioned' as const,
  reasons: 'Frozen sanction reason', exception_reference: { exception_register_entry_id: 'exception-1', exception_type: 'exceeds_loan_limit', business_reason: 'Frozen exception business reason', status: 'approved', cycle_number: 1 },
  conflict_abstention_details: [{ type: 'abstention' as const, user_id: 'director-1', full_name: 'Director One', conflict_code: 'self_declared_abstention', reason: 'Borrower is my relative.', approval_action_id: 'action-1', acted_at: '2026-07-13T09:00:00Z' }],
  general_meeting_approval_reference: { general_meeting_approval_id: 'meeting-1', approval_status: 'approved', meeting_date: '2026-07-12', related_party_type: 'director_relative', related_party_user_id: 'director-1', notice_document_id: 'notice-1', minutes_document_id: 'minutes-1', resolution_document_id: 'resolution-1' }, recorded_at: '2026-07-13T10:00:00Z',
};

const exceptionRow = {
  exception_register_entry_id: 'exception-1', loan_application_id: 'application-valid', loan_account_id: null, approval_case_id: 'case-valid', cycle_number: 1,
  exception_type: 'stage_bypass' as const, description: 'Frozen exception description', business_reason: 'Frozen exception business reason', risk_assessment: 'Medium',
  status: 'pending' as const, case_status: 'pending', conflict_block_reason: null, authority_applied_summary: 'CFO: CFO One (pending)',
  route_approvers: [], required_approvers: [], approval_actions: [{ approval_action_id: 'action-1', role_code: 'cfo', user_id: 'cfo-1', full_name: 'CFO One', decision: 'approved', comments: 'CFO approved with monitoring.', acted_at: '2026-07-13T11:30:00Z' }],
  supporting_documents: [{ document_id: 'document-1', file_name: 'cash-flow-evidence.pdf', mime_type: 'application/pdf', file_size_bytes: 2048, sensitivity_level: 'restricted', uploaded_at: '2026-07-13T09:00:00Z' }],
  created_at: '2026-07-13T10:00:00Z', closed_at: null,
};
