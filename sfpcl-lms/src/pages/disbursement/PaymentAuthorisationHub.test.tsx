// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import PaymentAuthorisationHub from './PaymentAuthorisationHub';
import { AuthSessionError } from '../../services/authSession';
import { fetchDisbursementWorkspace, submitDisbursementAction, type DisbursementWorkspaceRow } from '../../services/disbursementApi';
import pageSource from './PaymentAuthorisationHub.tsx?raw';

vi.mock('../../services/disbursementApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/disbursementApi')>(),
  fetchDisbursementWorkspace: vi.fn(), submitDisbursementAction: vi.fn(),
}));

const action = (code: string, label: string, fields: DisbursementWorkspaceRow['available_actions'][number]['fields']) => ({
  action_code: code, label, enabled: true, disabled_reason: null, required_permission: `finance.${code}`,
  action_url: `/api/v1/actions/${code}/`, method: 'POST' as const, fields,
});
const authorise = action('authorise_disbursement', 'Authorise payment', [{ name: 'comments', label: 'CFC comments', type: 'textarea', required: true }]);
const reject = action('reject_disbursement', 'Reject payment', [{ name: 'comments', label: 'CFC comments', type: 'textarea', required: true }]);
const transfer = action('mark_transfer_successful', 'Record transfer success', [
  { name: 'bank_reference_number', label: 'UTR / bank reference', type: 'text', required: true },
  { name: 'disbursed_at', label: 'Transfer date and time', type: 'datetime-local', required: true },
  { name: 'bank_transfer_evidence_document_id', label: 'Bank evidence document ID', type: 'text', required: true },
]);
const row: DisbursementWorkspaceRow = {
  workspace_id: 'disbursement-1', loan_account_id: 'account-1', disbursement_id: 'disbursement-1',
  loan_application_id: 'application-1', application_reference_number: 'LO-API-001', loan_account_number: 'LN-API-001',
  member: { member_id: 'member-1', display_name: 'Backend Borrower' }, sanctioned_amount: '400000.00', disbursement_amount: '350000.00',
  sap: { request_id: 'sap-1', status: 'completed', customer_code_masked: '******001' },
  readiness: { ready_for_disbursement: true, evaluated_at: '2026-07-19T03:00:00Z', checks: [] },
  beneficiary_bank: { account_holder_name: 'Backend Borrower', account_number_masked: '******1234', ifsc_code: 'RATN0000001', bank_name: 'Borrower Bank', branch_name: 'Nashik' },
  source_bank: { account_holder_name: 'SFPCL', account_number_masked: '******5678', bank_name: 'RBL Bank' },
  initiation_status: 'initiated', authorisation_status: 'pending', bank_transfer_status: 'pending', advice_status: 'not_started',
  bank_reference_masked: null, initiated_by: { user_id: 'maker-1', full_name: 'Finance Maker' }, initiated_at: '2026-07-19T03:00:00Z',
  authorised_at: null, disbursed_at: null, available_actions: [authorise, reject],
};
const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };

describe('009K CFC payment authorisation workspace', () => {
  beforeEach(() => { vi.mocked(fetchDisbursementWorkspace).mockResolvedValue({ items: [row], pagination }); vi.mocked(submitDisbursementAction).mockResolvedValue({ authorisation_status: 'approved' }); });
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('shows CFC actions only when the backend projects them and posts the decision reason', async () => {
    render(<PaymentAuthorisationHub onOpenApplication={vi.fn()} />);
    await userEvent.type(await screen.findByLabelText('CFC comments'), 'Independent review complete.');
    await userEvent.click(screen.getByRole('button', { name: 'Authorise payment' }));
    await waitFor(() => expect(submitDisbursementAction).toHaveBeenCalledWith(authorise, { decision: 'approved', comments: 'Independent review complete.' }, undefined));
    expect(screen.getByText('Backend Borrower')).toBeTruthy();
  });

  it('does not invent authorise controls for a Senior Finance projection', async () => {
    vi.mocked(fetchDisbursementWorkspace).mockResolvedValueOnce({ items: [{ ...row, available_actions: [transfer] }], pagination });
    render(<PaymentAuthorisationHub onOpenApplication={vi.fn()} />);
    await screen.findByText('Backend Borrower');
    expect(screen.queryByRole('button', { name: 'Authorise payment' })).toBeNull();
  });

  it('surfaces backend duplicate UTR and permission errors without optimistic success', async () => {
    vi.mocked(fetchDisbursementWorkspace).mockResolvedValueOnce({ items: [{ ...row, authorisation_status: 'approved', available_actions: [transfer] }], pagination });
    vi.mocked(submitDisbursementAction).mockRejectedValueOnce(new AuthSessionError('DUPLICATE_BANK_REFERENCE', 'This UTR is already recorded.', 409));
    render(<PaymentAuthorisationHub onOpenApplication={vi.fn()} />);
    await userEvent.type(await screen.findByLabelText('UTR / bank reference'), 'UTR-EXISTING');
    await userEvent.type(screen.getByLabelText('Transfer date and time'), '2026-07-19T10:00');
    await userEvent.type(screen.getByLabelText('Bank evidence document ID'), '11111111-1111-4111-8111-111111111111');
    await userEvent.click(screen.getByRole('button', { name: 'Record transfer success' }));
    expect(await screen.findByText('This UTR is already recorded.')).toBeTruthy();
    expect(screen.queryByText('Transfer recorded successfully.')).toBeNull();

    cleanup();
    vi.mocked(fetchDisbursementWorkspace).mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'CFC scope denied.', 403));
    render(<PaymentAuthorisationHub onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('CFC scope denied.')).toBeTruthy();
  });

  it('owns no mock data or client-side role authority', () => {
    expect(pageSource).not.toContain('mockData'); expect(pageSource).not.toContain("currentUser.role"); expect(pageSource).not.toContain('isCfc');
  });
});
