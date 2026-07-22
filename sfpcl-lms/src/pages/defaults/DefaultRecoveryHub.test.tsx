// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import DefaultRecoveryHub from './DefaultRecoveryHub';
import { fetchRecoveryCases, initiateRecoveryAction, uploadRecoveryEvidence } from '../../services/recoveryApi';
vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({ currentUser: { role: 'company_secretary', name: 'Recovery CS' } }),
}));
vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchRecoveryCases: vi.fn(), uploadRecoveryEvidence: vi.fn(),
  initiateRecoveryAction: vi.fn(), completeRecoveryAction: vi.fn(),
}));
const row = {
  default_case_id: 'case-1', loan_account_id: 'loan-1', loan_account_number: 'LN-REC-001',
  borrower_name: 'Backend Borrower', total_outstanding: '345000.00', default_case_status: 'recovery_approved',
  recovery_decision: { recovery_decision_id: 'decision-1', decision: 'invoke_sh4', status: 'approved', available_actions: [{ action_code: 'execute_recovery' }] },
  recovery_action: null,
};
const pagination = { page: 1, page_size: 100, total_count: 1, total_pages: 1, has_next: false, has_previous: false };
describe('011F recovery execution surface', () => {
  beforeEach(() => {
    vi.mocked(fetchRecoveryCases).mockResolvedValue({ items: [row], pagination });
    vi.mocked(uploadRecoveryEvidence).mockResolvedValue('document-1');
    vi.mocked(initiateRecoveryAction).mockResolvedValue({ recovery_action_id: 'action-1', action_status: 'pending' } as never);
  });
  afterEach(() => { cleanup(); vi.clearAllMocks(); });
  it('uses the approved backend action and uploaded evidence to initiate S57', async () => {
    render(<DefaultRecoveryHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Security Invocation' }));
    expect(await screen.findByText(/Backend Borrower/)).toBeTruthy();
    await userEvent.upload(screen.getByLabelText('Recovery evidence'), new File(['proof'], 'proof.pdf', { type: 'application/pdf' }));
    await userEvent.type(screen.getByLabelText('Remarks / Proceeds Received'), 'Borrower contacted and approved SH-4 route initiated.');
    await userEvent.click(screen.getByRole('button', { name: 'Initiate Approved Recovery' }));
    await waitFor(() => expect(initiateRecoveryAction).toHaveBeenCalledTimes(1));
    expect(vi.mocked(initiateRecoveryAction).mock.calls[0][0]).toBe('decision-1');
    expect(vi.mocked(initiateRecoveryAction).mock.calls[0][1]).toMatchObject({ action_type: 'invoke_sh4', evidence_document_ids: ['document-1'] });
  });
});
