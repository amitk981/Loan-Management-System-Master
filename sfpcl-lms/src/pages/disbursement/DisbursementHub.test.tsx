// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import DisbursementHub from './DisbursementHub';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchDisbursementWorkspace,
  submitDisbursementAction,
  type DisbursementWorkspaceRow,
} from '../../services/disbursementApi';
import pageSource from './DisbursementHub.tsx?raw';

vi.mock('../../services/disbursementApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/disbursementApi')>(),
  fetchDisbursementWorkspace: vi.fn(), submitDisbursementAction: vi.fn(),
}));

const action = (code: string, label: string, fields: DisbursementWorkspaceRow['available_actions'][number]['fields'] = []) => ({
  action_code: code, label, enabled: true, disabled_reason: null,
  required_permission: `finance.${code}`, action_url: `/api/v1/actions/${code}/`, method: 'POST' as const, fields,
});

const row: DisbursementWorkspaceRow = {
  workspace_id: 'account-1', loan_account_id: 'account-1', disbursement_id: null,
  loan_application_id: 'application-1', application_reference_number: 'LO-API-001', loan_account_number: 'LN-API-001',
  member: { member_id: 'member-1', display_name: 'Backend Borrower' },
  sanctioned_amount: '400000.00', disbursement_amount: '350000.00',
  sap: { request_id: 'sap-1', status: 'completed', customer_code_masked: '******001' },
  readiness: { ready_for_disbursement: false, evaluated_at: '2026-07-19T03:00:00Z', checks: [
    { code: 'documentation_complete', label: 'Documentation checklist complete', status: 'fail', reason: 'Credit Manager sign-off is pending.' },
    { code: 'sap_customer_code_present', label: 'SAP customer code present', status: 'pass' },
  ] },
  beneficiary_bank: { account_holder_name: 'Backend Borrower', account_number_masked: '******1234', ifsc_code: 'RATN0000001', bank_name: 'Borrower Bank', branch_name: 'Nashik' },
  source_bank: { account_holder_name: 'SFPCL', account_number_masked: '******5678', bank_name: 'RBL Bank' },
  initiation_status: null, authorisation_status: null, bank_transfer_status: null,
  advice_status: 'not_started', bank_reference_masked: null, initiated_by: null,
  initiated_at: null, authorised_at: null, disbursed_at: null,
  available_actions: [action('initiate_disbursement', 'Initiate payment', [
    { name: 'disbursement_amount', label: 'Disbursement amount', type: 'money', required: true, value: '350000.00' },
    { name: 'final_verification_comments', label: 'Final verification comments', type: 'textarea', required: true },
  ])],
};
const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };

describe('009K disbursement finance workspace', () => {
  beforeEach(() => {
    vi.mocked(fetchDisbursementWorkspace).mockResolvedValue({ items: [row], pagination });
    vi.mocked(submitDisbursementAction).mockResolvedValue({ disbursement_id: 'disbursement-1' });
  });
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('renders named backend blockers and disables initiation while readiness fails', async () => {
    render(<DisbursementHub onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Credit Manager sign-off is pending.')).toBeTruthy();
    expect(screen.getByText('Backend Borrower')).toBeTruthy();
    expect((screen.getByRole('button', { name: 'Initiate payment' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('submits Money fields with one stable key and treats replay as success', async () => {
    vi.mocked(fetchDisbursementWorkspace).mockResolvedValue({ items: [{ ...row, readiness: { ...row.readiness, ready_for_disbursement: true, checks: row.readiness.checks.map(check => ({ ...check, status: 'pass' as const, reason: undefined })) } }], pagination });
    vi.mocked(submitDisbursementAction).mockResolvedValue({ idempotency_replayed: true, original_response: { disbursement_id: 'disbursement-1' } });
    render(<DisbursementHub onOpenApplication={vi.fn()} />);
    await userEvent.type(await screen.findByLabelText('Final verification comments'), 'All evidence verified.');
    await userEvent.click(screen.getByRole('button', { name: 'Initiate payment' }));
    await waitFor(() => expect(submitDisbursementAction).toHaveBeenCalledTimes(1));
    expect(vi.mocked(submitDisbursementAction).mock.calls[0][1]).toMatchObject({ disbursement_amount: '350000.00', final_verification_comments: 'All evidence verified.' });
    expect(vi.mocked(submitDisbursementAction).mock.calls[0][2]).toMatch(/^initiate_disbursement-account-1-/);
    expect(await screen.findByText('The original payment initiation was returned; no duplicate was created.')).toBeTruthy();
  });

  it('shows unauthorized and empty states without mock fallback', async () => {
    vi.mocked(fetchDisbursementWorkspace).mockRejectedValueOnce(new AuthSessionError('FORBIDDEN', 'Finance scope denied.', 403));
    const denied = render(<DisbursementHub onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Finance scope denied.')).toBeTruthy(); denied.unmount();
    vi.mocked(fetchDisbursementWorkspace).mockResolvedValueOnce({ items: [], pagination: { ...pagination, total_count: 0 } });
    render(<DisbursementHub onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('No applications pending disbursement')).toBeTruthy();
  });

  it('owns no mock data or local business fixtures', () => {
    expect(pageSource).not.toContain('mockData');
    expect(pageSource).not.toContain('loanApplications');
    expect(pageSource).not.toContain('auditLog');
  });
});
