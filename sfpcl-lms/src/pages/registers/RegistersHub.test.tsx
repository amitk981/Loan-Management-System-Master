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
      .mockResolvedValueOnce({ items: [sanctionRow], pagination: { ...pagination, page: 2, total_count: 21, total_pages: 2, has_previous: true } })
      .mockResolvedValueOnce({ items: [{ ...sanctionRow, decision: 'rejected', sanctioned_amount: null, rejection_reason: 'Frozen rejection reason', conditions: null }], pagination: { ...pagination, total_count: 1 } });

    render(<RegistersHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Credit sanction register' }));

    expect(await screen.findByText('Frozen Borrower')).toBeTruthy();
    const sanctionEvidence = (await screen.findByTestId('sanction-source-evidence')).textContent ?? '';
    expect(sanctionEvidence).toContain('CSR-2026-0001');
    expect(screen.getByText('FOL-APPROVAL-QUEUE-001')).toBeTruthy();
    expect(sanctionEvidence).toMatch(/individual farmer.*Loan type: short term/i);
    expect(sanctionEvidence).toMatch(/Crop production · crop production/i);
    expect(sanctionEvidence).toMatch(/Risk: medium/i);
    expect(sanctionEvidence).toContain('Director approved with conditions.');
    expect(sanctionEvidence).toContain('Complete legal documents.');
    expect(sanctionEvidence).toMatch(/pending · not sent/i);
    expect(sanctionEvidence).toContain('Frozen sanction reason');
    expect(screen.getByTestId('sanction-approver-decisions').textContent).toMatch(/13 Jul 2026, 14:30/i);
    expect(sanctionEvidence).toContain('Frozen exception business reason');
    expect(sanctionEvidence).toMatch(/approved · cycle 1/i);
    expect(sanctionEvidence).toMatch(/self declared abstention/i);
    expect(sanctionEvidence).toMatch(/director relative/i);
    expect(sanctionEvidence).toMatch(/Notice: notice-1/i);
    expect(screen.queryByText('Hidden invalid borrower')).toBeNull();
    expect(screen.getByText('21 records')).toBeTruthy();
    expect(screen.getByText('Page 2 of 2')).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Application' })).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Approval authority' })).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Credit sanction register entry details' })).toBeTruthy();

    await userEvent.selectOptions(screen.getByLabelText('Sanction decision'), 'rejected');
    await waitFor(() => expect(fetchCreditSanctionRegister).toHaveBeenLastCalledWith({
      financialYear: undefined, decision: 'rejected', page: 1, pageSize: 20,
    }));
    expect(await screen.findByText('Page 1 of 1')).toBeTruthy();
    await waitFor(() => expect(screen.getByTestId('sanction-source-evidence').textContent).toContain('Frozen rejection reason'));
    expect(screen.getByTestId('sanction-source-evidence').textContent).toMatch(/Conditions: —/i);
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

    expect((await screen.findAllByText('Frozen exception description')).length).toBeGreaterThan(0);
    const exceptionEvidence = (await screen.findByTestId('exception-source-evidence')).textContent ?? '';
    expect(screen.getByText('Frozen Borrower')).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Exception ID' })).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Required authority' })).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Exception register entry details' })).toBeTruthy();
    expect(exceptionEvidence).toContain('₹4,40,000.00');
    expect(exceptionEvidence).toMatch(/Case Preparer/);
    expect(exceptionEvidence).toContain('13 Jul 2026');
    expect(exceptionEvidence).toContain('Frozen exception business reason');
    expect(exceptionEvidence).toContain('CFO approved with monitoring.');
    expect(exceptionEvidence).toContain('cash-flow-evidence.pdf');
    expect(exceptionEvidence).toMatch(/restricted/i);
    expect(screen.queryByRole('button', { name: /download/i })).toBeNull();
    expect(screen.queryByRole('link', { name: /download/i })).toBeNull();
    expect(fetchCreditSanctionRegister).not.toHaveBeenCalled();

    await userEvent.selectOptions(screen.getByLabelText('Exception status'), 'approved');
    await waitFor(() => expect(fetchExceptionRegister).toHaveBeenLastCalledWith({
      status: 'approved', exceptionType: undefined, page: 1, pageSize: 20,
    }));
  });

  it('selects a null-safe legacy S23 row without fabricating unavailable source facts', async () => {
    const legacyRow = {
      ...sanctionRow,
      credit_sanction_register_entry_id: 'register-legacy',
      entry_number: 'CSR-LEGACY-0001',
      application_number: 'LO-LEGACY-001',
      folio_number: null,
      loan_type: null,
      purpose: null,
      risk: null,
      approver_names: [],
      approver_decisions: [],
      reasons: '',
      rejection_reason: null,
      conditions: null,
      communication: null,
      exception_reference: null,
      conflict_abstention_details: [],
      general_meeting_approval_reference: null,
    };
    vi.mocked(fetchCreditSanctionRegister).mockResolvedValue({
      items: [sanctionRow, legacyRow],
      pagination: { ...pagination, total_count: 2 },
    });

    render(<RegistersHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'View CSR-LEGACY-0001' }));

    const evidence = screen.getByTestId('sanction-source-evidence').textContent ?? '';
    expect(evidence).toContain('CSR-LEGACY-0001');
    expect(evidence).toMatch(/Folio number:\s*—/i);
    expect(evidence).toMatch(/Loan type:\s*—/i);
    expect(evidence).toMatch(/Purpose:\s*—/i);
    expect(evidence).toMatch(/Risk:\s*—/i);
    expect(evidence).toMatch(/Approver decisions:\s*—/i);
    expect(evidence).toMatch(/Communication:\s*—/i);
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
  entry_number: 'CSR-2026-0001', folio_number: 'FOL-APPROVAL-QUEUE-001', loan_type: 'short_term',
  borrower_name: 'Frozen Borrower', borrower_type: 'individual_farmer', requested_amount: '500000.00', eligible_amount: '450000.00',
  recommended_amount: '440000.00', sanctioned_amount: '440000.00', approval_authority: 'CFO + one Director',
  approver_names: ['CFO One', 'Director One'], approval_date: '2026-07-13', decision: 'sanctioned' as const,
  approver_decisions: [{ approval_action_id: 'action-2', role_code: 'director', user_id: 'director-1', full_name: 'Director One', decision: 'approved', comments: 'Director approved with conditions.', acted_at: '2026-07-13T09:00:00Z' }],
  purpose: { category: 'crop_production', description: 'Crop production' }, risk: { overall_risk_rating: 'medium' }, rejection_reason: null,
  conditions: 'Complete legal documents.', communication: { communication_id: 'communication-1', status: 'pending', sent_at: null },
  reasons: 'Frozen sanction reason', exception_reference: { exception_register_entry_id: 'exception-1', exception_type: 'exceeds_loan_limit', business_reason: 'Frozen exception business reason', status: 'approved', cycle_number: 1 },
  conflict_abstention_details: [{ type: 'abstention' as const, user_id: 'director-1', full_name: 'Director One', conflict_code: 'self_declared_abstention', reason: 'Borrower is my relative.', approval_action_id: 'action-1', acted_at: '2026-07-13T09:00:00Z' }],
  general_meeting_approval_reference: { general_meeting_approval_id: 'meeting-1', approval_status: 'approved', meeting_date: '2026-07-12', related_party_type: 'director_relative', related_party_user_id: 'director-1', notice_document_id: 'notice-1', minutes_document_id: 'minutes-1', resolution_document_id: 'resolution-1' }, recorded_at: '2026-07-13T10:00:00Z',
};

const exceptionRow = {
  exception_register_entry_id: 'exception-1', loan_application_id: 'application-valid', loan_account_id: null, approval_case_id: 'case-valid', cycle_number: 1,
  exception_type: 'stage_bypass' as const, description: 'Frozen exception description', business_reason: 'Frozen exception business reason', risk_assessment: 'Medium',
  borrower_name: 'Frozen Borrower', financial_impact: '440000.00', requested_by: { user_id: 'preparer-1', full_name: 'Case Preparer' }, decision_date: '2026-07-13',
  status: 'pending' as const, case_status: 'pending', conflict_block_reason: null, authority_applied_summary: 'CFO: CFO One (pending)',
  route_approvers: [], required_approvers: [], approval_actions: [{ approval_action_id: 'action-1', role_code: 'cfo', user_id: 'cfo-1', full_name: 'CFO One', decision: 'approved', comments: 'CFO approved with monitoring.', acted_at: '2026-07-13T11:30:00Z' }],
  supporting_documents: [{ document_id: 'document-1', file_name: 'cash-flow-evidence.pdf', mime_type: 'application/pdf', file_size_bytes: 2048, sensitivity_level: 'restricted', uploaded_at: '2026-07-13T09:00:00Z' }],
  created_at: '2026-07-13T10:00:00Z', closed_at: null,
};
