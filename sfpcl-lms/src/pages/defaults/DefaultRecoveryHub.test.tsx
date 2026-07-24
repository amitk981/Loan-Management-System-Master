// @vitest-environment jsdom
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import {
  createRecoveryDecision,
  fetchDefaultCase,
  fetchDefaultCases,
  fetchRecoveryApprovalCase,
  type DefaultCaseProjection,
  type RecoveryApprovalProjection,
} from '../../services/recoveryApi';
import DefaultRecoveryHub from './DefaultRecoveryHub';
import defaultRecoverySource from './DefaultRecoveryHub.tsx?raw';

vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchDefaultCases: vi.fn(),
  fetchDefaultCase: vi.fn(),
  fetchRecoveryApprovalCase: vi.fn(),
  createRecoveryDecision: vi.fn(),
}));

const pagination = {
  page: 1,
  page_size: 100,
  total_count: 1,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const populatedCase: DefaultCaseProjection = {
  default_case_id: 'case-011pa',
  loan_account_id: 'loan-011pa',
  loan_account_number: 'LN-DEFAULT-011PA',
  member_id: 'member-011pa',
  borrower_name: 'Backend Default Member',
  principal_outstanding: '300000.00',
  interest_outstanding: '45000.00',
  total_outstanding: '345000.00',
  trigger_event: 'missed_principal_repayment',
  scheduled_due_date: '2025-04-15',
  repayment_schedule_id: 'schedule-011pa',
  default_case_status: 'non_payment_under_review',
  grace_period_start_date: '2025-04-15',
  grace_period_end_date: '2025-07-15',
  grace_state: 'expired',
  reason: 'Scheduled principal repayment remained unpaid.',
  current_assessment: {
    default_assessment_id: 'assessment-011pa',
    default_case_id: 'case-011pa',
    assessment_type: 'post_grace',
    payment_failure_classification: 'non_intentional',
    reason_summary: 'Crop loss delayed repayment.',
    evidence_document_ids: ['assessment-document'],
    borrower_interaction_summary: 'Borrower explained the crop loss.',
    recommended_action: 'grant_extension',
    assessed_by_user_id: 'assessor-011pa',
    assessed_at: '2025-07-16T10:00:00Z',
  },
  extension_note: {
    extension_note_id: 'extension-011pa',
    default_case_id: 'case-011pa',
    loan_account_id: 'loan-011pa',
    extension_reason: 'Non-intentional crop loss.',
    extension_start_date: '2025-07-16',
    extension_end_date: '2026-07-15',
    document_id: 'extension-document',
    prepared_by_user_id: 'manager-011pa',
    approved_by_user_id: 'approver-011pa',
    status: 'active',
  },
  non_payment_note: {
    non_payment_note_id: 'note-011pa',
    default_case_id: 'case-011pa',
    loan_account_id: 'loan-011pa',
    reason_for_non_payment: 'Frozen reason from the backend record.',
    intentionality_assessment: 'non_intentional',
    outstanding_principal_amount: '300000.00',
    outstanding_interest_amount: '45000.00',
    recommended_recovery_action: 'present_to_sanction_committee',
    evidence_document_ids: ['note-evidence'],
    frozen_case_facts: {
      borrower_name: 'Backend Default Member',
      original_due_date: '2025-04-15',
      grace_outcome_summary: 'Grace expired without full principal repayment.',
      extension_outcome_summary: 'Extension expired unpaid.',
      prepared_by_name: 'Backend Credit Assessor',
    },
    document_id: 'note-document',
    prepared_by_user_id: 'assessor-011pa',
    status: 'draft',
    approval_case_id: null,
    submitted_to_sanction_committee_at: null,
    available_actions: [],
  },
  recovery_decision: {
    recovery_decision_id: 'decision-011pa',
    approval_case_id: 'approval-011pb',
    decision: 'invoke_sh4',
    decision_reason: 'Approved after reviewing frozen evidence.',
    status: 'approved',
    available_actions: [{ action_code: 'execute_recovery' }],
  },
  recovery_decision_control: null,
  recovery_action: null,
  available_actions: [],
};

const approvalCase: RecoveryApprovalProjection = {
  approval_case_id: 'approval-011pb',
  approval_type: 'recovery',
  related_entity_type: 'non_payment_note',
  related_entity_id: 'note-011pa',
  current_status: 'approved',
  decision_date: '2026-07-20',
  reason_for_approval: 'invoke_sh4',
  conflict_block_reason: null,
  required_approvers: [
    { role_code: 'sanction_committee_member', user_id: 'approver-1', full_name: 'Committee Approver', decision: 'approved', acted_at: '2026-07-20T10:00:00Z' },
    { role_code: 'cfo', user_id: 'approver-2', full_name: 'CFO Approver', decision: 'approved', acted_at: '2026-07-20T10:05:00Z' },
  ],
  approval_actions: [
    { approval_action_id: 'action-1', role_code: 'sanction_committee_member', user_id: 'approver-1', full_name: 'Committee Approver', decision: 'approved', comments: 'Approved.', acted_at: '2026-07-20T10:00:00Z' },
    { approval_action_id: 'action-2', role_code: 'cfo', user_id: 'approver-2', full_name: 'CFO Approver', decision: 'approved', comments: 'Approved.', acted_at: '2026-07-20T10:05:00Z' },
  ],
  excluded_approvers: [],
  available_actions: [],
};

describe('011PA default case and frozen-note read surface', () => {
  beforeEach(() => {
    vi.mocked(fetchDefaultCases).mockResolvedValue({
      items: [populatedCase],
      pagination,
    });
    vi.mocked(fetchDefaultCase).mockResolvedValue(populatedCase);
    vi.mocked(fetchRecoveryApprovalCase).mockResolvedValue(approvalCase);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('renders list/detail, grace, extension, and frozen note from backend projections', async () => {
    render(<DefaultRecoveryHub />);

    expect((await screen.findAllByText('LN-DEFAULT-011PA')).length).toBeGreaterThan(0);
    expect(await screen.findByText('Scheduled principal repayment remained unpaid.')).toBeTruthy();
    expect(fetchDefaultCases).toHaveBeenCalledTimes(1);
    expect(fetchDefaultCase).toHaveBeenCalledWith('case-011pa');

    await userEvent.click(screen.getByRole('button', { name: 'Grace Period / Extension' }));
    expect(screen.getByText('Crop loss delayed repayment.')).toBeTruthy();
    expect(screen.getByText('Non-intentional crop loss.')).toBeTruthy();
    expect(screen.getByText('2026-07-15')).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Non-Payment Note' }));
    expect(screen.getByText('Frozen reason from the backend record.')).toBeTruthy();
    expect(screen.getByText('Grace expired without full principal repayment.')).toBeTruthy();
    expect(screen.getByText('Backend Credit Assessor')).toBeTruthy();
    expect(screen.queryByRole('textbox')).toBeNull();

    expect(screen.getByRole('button', { name: 'Recovery Approval' }).hasAttribute('disabled')).toBe(false);
    expect(screen.getByRole('button', { name: 'Security Invocation' }).hasAttribute('disabled')).toBe(false);
    expect(screen.queryByRole('button', { name: /execute|approve|submit note/i })).toBeNull();
  });

  it('renders the loading state until the list resolves', async () => {
    let resolveList: ((value: { items: DefaultCaseProjection[]; pagination: typeof pagination }) => void) | undefined;
    vi.mocked(fetchDefaultCases).mockReturnValue(new Promise(resolve => {
      resolveList = resolve;
    }));

    render(<DefaultRecoveryHub />);
    expect(screen.getByText('Loading default cases…')).toBeTruthy();

    resolveList?.({ items: [populatedCase], pagination });
    expect((await screen.findAllByText('LN-DEFAULT-011PA')).length).toBeGreaterThan(0);
  });

  it('renders the empty state without requesting a detail', async () => {
    vi.mocked(fetchDefaultCases).mockResolvedValue({
      items: [],
      pagination: { ...pagination, total_count: 0 },
    });

    render(<DefaultRecoveryHub />);
    expect(await screen.findByText('No default cases are available in your scope.')).toBeTruthy();
    expect(fetchDefaultCase).not.toHaveBeenCalled();
  });

  it('renders distinct unauthorized and general error states', async () => {
    vi.mocked(fetchDefaultCases).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Default case read permission is required.', 403),
    );
    const { unmount } = render(<DefaultRecoveryHub />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Default case read permission is required.')).toBeTruthy();
    unmount();

    vi.mocked(fetchDefaultCases).mockRejectedValueOnce(new Error('Default service unavailable.'));
    render(<DefaultRecoveryHub />);
    expect(await screen.findByText('Default Cases Unavailable')).toBeTruthy();
    expect(screen.getByText('Default service unavailable.')).toBeTruthy();
  });

  it('renders absent assessment, extension, and note as blocked server states', async () => {
    const blockedCase = {
      ...populatedCase,
      default_case_status: 'grace_period_active',
      grace_state: 'active',
      current_assessment: null,
      extension_note: null,
      non_payment_note: null,
      recovery_decision: null,
    } satisfies DefaultCaseProjection;
    vi.mocked(fetchDefaultCases).mockResolvedValue({
      items: [blockedCase],
      pagination,
    });
    vi.mocked(fetchDefaultCase).mockResolvedValue(blockedCase);

    render(<DefaultRecoveryHub />);
    await screen.findAllByText('LN-DEFAULT-011PA');
    await userEvent.click(screen.getByRole('button', { name: 'Grace Period / Extension' }));
    expect(screen.getByText('Reason assessment not recorded')).toBeTruthy();
    expect(screen.getByText('Extension note not recorded')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Non-Payment Note' }));
    expect(screen.getByText('Frozen non-payment note not available')).toBeTruthy();
  });

  it('keeps the latest selected case authoritative when an older detail resolves later', async () => {
    const secondCase = {
      ...populatedCase,
      default_case_id: 'case-011pa-second',
      loan_account_id: 'loan-011pa-second',
      loan_account_number: 'LN-DEFAULT-SECOND',
      borrower_name: 'Second Backend Member',
      reason: 'Second case reason.',
    } satisfies DefaultCaseProjection;
    vi.mocked(fetchDefaultCases).mockResolvedValue({
      items: [populatedCase, secondCase],
      pagination: { ...pagination, total_count: 2 },
    });
    vi.mocked(fetchDefaultCase).mockResolvedValueOnce(populatedCase);

    render(<DefaultRecoveryHub />);
    await screen.findByText('Scheduled principal repayment remained unpaid.');

    let resolveSecond: ((value: DefaultCaseProjection) => void) | undefined;
    let resolveFirstAgain: ((value: DefaultCaseProjection) => void) | undefined;
    vi.mocked(fetchDefaultCase)
      .mockReturnValueOnce(new Promise(resolve => { resolveSecond = resolve; }))
      .mockReturnValueOnce(new Promise(resolve => { resolveFirstAgain = resolve; }));

    await userEvent.click(screen.getByRole('button', { name: /LN-DEFAULT-SECOND/ }));
    await userEvent.click(screen.getByRole('button', { name: /LN-DEFAULT-011PA/ }));
    resolveFirstAgain?.(populatedCase);
    expect(await screen.findByText('Scheduled principal repayment remained unpaid.')).toBeTruthy();
    await act(async () => {
      resolveSecond?.(secondCase);
      await Promise.resolve();
    });
    expect(screen.getByText('Scheduled principal repayment remained unpaid.')).toBeTruthy();
    expect(screen.queryByText('Second case reason.')).toBeNull();
  });

  it('renders a detail-level authorization failure distinctly', async () => {
    vi.mocked(fetchDefaultCase).mockRejectedValue(
      new AuthSessionError('FORBIDDEN', 'Selected case scope was revoked.', 403),
    );

    render(<DefaultRecoveryHub />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Selected case scope was revoked.')).toBeTruthy();
  });

  it('shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls', async () => {
    for (const [projection, blocker] of [
      [{ ...approvalCase, current_status: 'pending' }, 'The approval case is not a matching terminal approval for this recovery action.'],
      [{ ...approvalCase, current_status: 'rejected' }, 'The approval case is not a matching terminal approval for this recovery action.'],
      [{ ...approvalCase, conflict_block_reason: 'Required CFO authority is unavailable after conflict exclusion.' }, 'Required CFO authority is unavailable after conflict exclusion.'],
      [{ ...approvalCase, related_entity_id: 'foreign-note' }, 'The approval case is not a matching terminal approval for this recovery action.'],
    ] as Array<[RecoveryApprovalProjection, string]>) {
      const submitted = {
        ...populatedCase,
        default_case_status: 'recovery_decision_pending',
        non_payment_note: {
          ...populatedCase.non_payment_note!,
          status: 'submitted',
          approval_case_id: approvalCase.approval_case_id,
          submitted_to_sanction_committee_at: '2026-07-19T10:00:00Z',
          recommended_recovery_action: 'invoke_sh4',
        },
        recovery_decision: null,
        recovery_decision_control: {
          action_code: 'record_recovery_decision',
          enabled: false,
          disabled_reason: blocker,
          approval_case_id: approvalCase.approval_case_id,
          decision: 'invoke_sh4',
        },
      } satisfies DefaultCaseProjection;
      vi.mocked(fetchDefaultCases).mockResolvedValueOnce({ items: [submitted], pagination });
      vi.mocked(fetchDefaultCase).mockResolvedValueOnce(submitted);
      vi.mocked(fetchRecoveryApprovalCase).mockResolvedValueOnce(projection);
      const { unmount } = render(<DefaultRecoveryHub />);
      await userEvent.click(await screen.findByRole('button', { name: 'Recovery Approval' }));
      expect(await screen.findByText(blocker)).toBeTruthy();
      expect(screen.queryByRole('button', { name: 'Record Recovery Decision' })).toBeNull();
      expect(screen.getByRole('button', { name: 'Security Invocation' }).hasAttribute('disabled')).toBe(true);
      unmount();
    }
  });

  it('enforces a reason, posts the server-fixed action, and refetches canonical terminal state', async () => {
    const submitted = {
      ...populatedCase,
      default_case_status: 'recovery_decision_pending',
      non_payment_note: {
        ...populatedCase.non_payment_note!,
        status: 'submitted',
        approval_case_id: approvalCase.approval_case_id,
        submitted_to_sanction_committee_at: '2026-07-19T10:00:00Z',
        recommended_recovery_action: 'invoke_sh4',
      },
      recovery_decision: null,
      recovery_decision_control: {
        action_code: 'record_recovery_decision',
        enabled: true,
        disabled_reason: null,
        approval_case_id: approvalCase.approval_case_id,
        decision: 'invoke_sh4',
      },
    } satisfies DefaultCaseProjection;
    const decided = {
      ...submitted,
      default_case_status: 'recovery_approved',
      recovery_decision: populatedCase.recovery_decision,
      recovery_decision_control: null,
    } satisfies DefaultCaseProjection;
    vi.mocked(fetchDefaultCases).mockResolvedValue({ items: [submitted], pagination });
    vi.mocked(fetchDefaultCase)
      .mockResolvedValueOnce(submitted)
      .mockResolvedValueOnce(decided);
    vi.mocked(createRecoveryDecision).mockResolvedValue(populatedCase.recovery_decision!);

    render(<DefaultRecoveryHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Recovery Approval' }));
    expect((await screen.findAllByText('Committee Approver')).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Invoke Sh4').length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole('button', { name: 'Record Recovery Decision' }));
    expect(screen.getByText('A decision reason is required.')).toBeTruthy();
    expect(createRecoveryDecision).not.toHaveBeenCalled();

    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved after reviewing frozen evidence.');
    await userEvent.click(screen.getByRole('button', { name: 'Record Recovery Decision' }));

    await waitFor(() => expect(createRecoveryDecision).toHaveBeenCalledWith('case-011pa', {
      approval_case_id: 'approval-011pb',
      decision: 'invoke_sh4',
      decision_reason: 'Approved after reviewing frozen evidence.',
    }));
    expect(fetchDefaultCase).toHaveBeenLastCalledWith('case-011pa');
    expect(await screen.findByText('Recovery decision recorded from canonical backend state.')).toBeTruthy();
    expect(screen.getByText('Approved after reviewing frozen evidence.')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Security Invocation' }).hasAttribute('disabled')).toBe(false);
    await userEvent.click(screen.getByRole('button', { name: 'Security Invocation' }));
    expect(screen.getByRole('button', { name: 'Initiate Approved Recovery' })).toBeTruthy();
  });

  it('keeps terminal approval read-only when the backend session omits decision permission', async () => {
    const submitted = {
      ...populatedCase,
      default_case_status: 'recovery_decision_pending',
      non_payment_note: {
        ...populatedCase.non_payment_note!,
        status: 'submitted',
        approval_case_id: approvalCase.approval_case_id,
        submitted_to_sanction_committee_at: '2026-07-19T10:00:00Z',
        recommended_recovery_action: 'invoke_sh4',
      },
      recovery_decision: null,
      recovery_decision_control: {
        action_code: 'record_recovery_decision',
        enabled: false,
        disabled_reason: 'Configured recovery decision authority is required.',
        approval_case_id: approvalCase.approval_case_id,
        decision: 'invoke_sh4',
      },
    } satisfies DefaultCaseProjection;
    vi.mocked(fetchDefaultCases).mockResolvedValue({ items: [submitted], pagination });
    vi.mocked(fetchDefaultCase).mockResolvedValue(submitted);

    render(<DefaultRecoveryHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Recovery Approval' }));
    expect(await screen.findByText('Configured recovery decision authority is required.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Record Recovery Decision' })).toBeNull();
  });

  it('is the final mock-removal owner and contains no runtime default/recovery fixtures', () => {
    expect(defaultRecoverySource).not.toMatch(/mockData|mockDefault|mockRecovery/);
    expect(defaultRecoverySource).not.toMatch(/const\s+(defaultCases|recoveryCases)\s*=/);
  });
});
