// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SettingsHub from './SettingsHub';
import { fetchApprovalMatrixRules, supersedeApprovalMatrixRule } from '../../services/approvalRegistersApi';
import { createLoanPolicyVersion, fetchLoanPolicyVersions } from '../../services/loanPolicyApi';
import settingsSource from './SettingsHub.tsx?raw';
import policyPanelSource from './LoanPolicySettingsPanel.tsx?raw';

let permissions = ['approvals.matrix.read'];

vi.mock('../../contexts/RoleContext', () => ({
  ROLE_LABELS: {},
  useRole: () => ({
    currentUser: { id: 'staff-1', role: 'admin', roleCodes: ['system_admin'], permissions, isBackendSession: true },
    can: (permission: string) => (
      (permission === 'view_approval_matrix' && permissions.some(value => value.startsWith('approvals.matrix.')))
      || (permission === 'view_settings' && permissions.includes('config.loan_policy.read'))
      || (permission === 'manage_settings' && permissions.includes('config.loan_policy.manage'))
    ),
  }),
}));

vi.mock('../../services/approvalRegistersApi', async importOriginal => {
  const actual = await importOriginal<typeof import('../../services/approvalRegistersApi')>();
  return { ...actual, fetchApprovalMatrixRules: vi.fn(), supersedeApprovalMatrixRule: vi.fn() };
});

vi.mock('../../services/loanPolicyApi', () => ({
  fetchLoanPolicyVersions: vi.fn(),
  createLoanPolicyVersion: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  permissions = ['approvals.matrix.read'];
});

describe('SettingsHub Approval Matrix panel', () => {
  it('renders active and retained historical rules from the versioned API without local fixtures', async () => {
    vi.mocked(fetchApprovalMatrixRules).mockResolvedValue({ items: [activeRule, historicalRule], pagination });
    render(<SettingsHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Approval Matrix' }));

    expect(await screen.findByText('AM-2026-02')).toBeTruthy();
    expect(screen.getByText('AM-2026-01')).toBeTruthy();
    expect(screen.getByText('CFO + 2 Directors')).toBeTruthy();
    expect(screen.getByText('Superseded')).toBeTruthy();
    expect(fetchApprovalMatrixRules).toHaveBeenCalledWith({ page: 1, pageSize: 100 });
    expect(screen.queryByRole('button', { name: /Edit AM-2026-02/ })).toBeNull();
  });

  it('permits a canonical manager to submit a complete successor version as a pending proposal', async () => {
    permissions = ['approvals.matrix.read', 'approvals.matrix.manage'];
    vi.mocked(fetchApprovalMatrixRules).mockResolvedValue({ items: [activeRule], pagination: { ...pagination, total_count: 1 } });
    vi.mocked(supersedeApprovalMatrixRule).mockResolvedValue(proposal);
    render(<SettingsHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Approval Matrix' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Edit AM-2026-02' }));

    await userEvent.clear(screen.getByLabelText('Successor version'));
    await userEvent.type(screen.getByLabelText('Successor version'), 'AM-2026-03');
    await userEvent.clear(screen.getByLabelText('Effective from'));
    await userEvent.type(screen.getByLabelText('Effective from'), '2026-09-01');
    await userEvent.type(screen.getByLabelText('Change reason'), 'Board-approved threshold governance update.');
    await userEvent.click(screen.getByRole('button', { name: 'Submit for Approval' }));

    await waitFor(() => expect(supersedeApprovalMatrixRule).toHaveBeenCalledWith('rule-active', {
      decision_type: 'loan_sanction', amount_min: '500000.01', amount_max: null, condition_code: null,
      required_approver_roles: ['cfo', 'director'], required_director_count: 2,
      joint_approval_required_flag: true, register_required: 'credit_sanction_register',
      effective_from: '2026-09-01', effective_to: null, version_number: 'AM-2026-03',
      reason: 'Board-approved threshold governance update.',
    }));
    expect(await screen.findByText('Configuration proposal pending approval')).toBeTruthy();
    expect(screen.getByText('proposal-1')).toBeTruthy();
    expect(screen.getByText(/distinct CFO or Company Secretary/)).toBeTruthy();
  });

  it('shows denied/error states without falling back to the inline prototype matrix', async () => {
    vi.mocked(fetchApprovalMatrixRules).mockRejectedValueOnce(new Error('You do not have approval matrix permission.'));
    render(<SettingsHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Approval Matrix' }));
    expect(await screen.findByText('Approval matrix unavailable')).toBeTruthy();
    expect(screen.queryByText('Disbursement initiation')).toBeNull();
  });

  it('clears matrix rows when the actor loses canonical read permission', async () => {
    vi.mocked(fetchApprovalMatrixRules).mockResolvedValue({ items: [activeRule], pagination });
    const view = render(<SettingsHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Approval Matrix' }));
    expect(await screen.findByText('AM-2026-02')).toBeTruthy();

    permissions = [];
    view.rerender(<SettingsHub />);
    expect(screen.queryByText('AM-2026-02')).toBeNull();
    expect(screen.getByText('Access Restricted')).toBeTruthy();
  });

  it('removes inline business fixtures from the owned S71 panel source', () => {
    const panel = settingsSource.slice(settingsSource.indexOf('OWNED S71 START'), settingsSource.indexOf('OWNED S71 END'));
    expect(panel).not.toMatch(/Standard sanction|High-value sanction|Disbursement initiation|AM-2026-01/);
  });
});

describe('SettingsHub remaining panels', () => {
  it('loads retained policy versions from the authenticated configuration boundary without exposing edits to a reader', async () => {
    permissions = ['config.loan_policy.read'];
    vi.mocked(fetchLoanPolicyVersions).mockResolvedValue([activePolicy, retiredPolicy]);

    render(<SettingsHub />);

    expect(await screen.findByText('Board Loan Policy 2026')).toBeTruthy();
    expect(screen.getByText('Board Loan Policy 2025')).toBeTruthy();
    expect(screen.getByText('LP-2026')).toBeTruthy();
    expect(screen.getByText('Read-only access')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Create new policy version' })).toBeNull();
    expect(fetchLoanPolicyVersions).toHaveBeenCalledWith({ page: 1, pageSize: 100 });
  });

  it('creates a complete successor as a separate audited draft for a canonical policy manager', async () => {
    permissions = ['config.loan_policy.read', 'config.loan_policy.manage'];
    vi.mocked(fetchLoanPolicyVersions)
      .mockResolvedValueOnce([activePolicy])
      .mockResolvedValueOnce([draftPolicy, activePolicy]);
    vi.mocked(createLoanPolicyVersion).mockResolvedValue(draftPolicy);

    render(<SettingsHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Create new policy version' }));
    await userEvent.clear(screen.getByLabelText('New version'));
    await userEvent.type(screen.getByLabelText('New version'), 'LP-2027');
    await userEvent.clear(screen.getByLabelText('Effective from'));
    await userEvent.type(screen.getByLabelText('Effective from'), '2027-04-01');
    await userEvent.clear(screen.getByLabelText('Board approval reference'));
    await userEvent.type(screen.getByLabelText('Board approval reference'), 'BOARD-2027-01');
    await userEvent.click(screen.getByRole('button', { name: 'Create draft version' }));

    await waitFor(() => expect(createLoanPolicyVersion).toHaveBeenCalledWith({
      policy_name: 'Board Loan Policy 2026', policy_version: 'LP-2027', effective_from: '2027-04-01',
      effective_to: null, short_term_duration_months: 12, min_secured_loan_months: 12,
      max_secured_loan_years: 3, approval_threshold_amount: '500000.00',
      default_scale_of_finance_per_acre_amount: '20000.00', share_limit_percentage: '10.0000',
      per_share_cap_amount: '200.00', interest_rate_type: 'floating', interest_benchmark: 'Board benchmark',
      penal_interest_rate: null, rekyc_frequency_months: 24, record_retention_years: 8,
      grace_period_months: 3, non_intentional_extension_months: 12,
      board_approval_reference: 'BOARD-2027-01',
    }));
    expect(await screen.findByText('Draft policy version created')).toBeTruthy();
    expect(screen.getByText('LP-2027')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /activate/i })).toBeNull();
  });

  it('renders unsupported settings as explicitly inert and contains no former live business fixtures', async () => {
    permissions = ['config.loan_policy.read'];
    vi.mocked(fetchLoanPolicyVersions).mockResolvedValue([activePolicy]);
    render(<SettingsHub />);

    await userEvent.click(screen.getByRole('button', { name: 'Template Management' }));
    expect(screen.getByText(/until slice 008A/)).toBeTruthy();
    expect(screen.queryByRole('button', { name: /upload|activate|retire/i })).toBeNull();
    expect(screen.queryByRole('button', { name: 'User & Role Management' })).toBeNull();

    expect(settingsSource).not.toMatch(/POL-2026-01|System Admin|Rajesh Sharma|Loan Application Form|Completeness Check|30% of share value|D-3, D\+1, D\+7/);
    expect(settingsSource).not.toMatch(/defaultValue=|handleSave|setSaved/);
    expect(policyPanelSource).not.toMatch(/POL-2026-01|1000000|2026-01-01|30% of share value|D-3, D\+1, D\+7|defaultValue=/);
  });

  it('keeps server errors visible inside the successor modal and does not label a draft current', async () => {
    permissions = ['config.loan_policy.read', 'config.loan_policy.manage'];
    vi.mocked(fetchLoanPolicyVersions).mockResolvedValue([draftPolicy, activePolicy]);
    vi.mocked(createLoanPolicyVersion).mockRejectedValue(new Error('A newer policy version already exists. Refresh and try again.'));
    render(<SettingsHub />);

    await userEvent.click(await screen.findByRole('button', { name: 'Create new policy version' }));
    await userEvent.click(screen.getByRole('button', { name: 'Create draft version' }));

    expect(await screen.findByText('A newer policy version already exists. Refresh and try again.')).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Create new policy version' })).toBeTruthy();
    expect(screen.getByLabelText('New version')).toBeTruthy();
    expect(screen.getByText(/2027-04-01 — Not set/)).toBeTruthy();
  });
});

const activeRule = {
  approval_matrix_rule_id: 'rule-active', decision_type: 'loan_sanction', amount_min: '500000.01', amount_max: null,
  condition_code: null, required_approver_roles: ['cfo', 'director'], required_director_count: 2,
  joint_approval_required_flag: true, register_required: 'credit_sanction_register', effective_from: '2026-08-01',
  effective_to: null, status: 'active' as const, version_number: 'AM-2026-02',
};

const historicalRule = {
  ...activeRule, approval_matrix_rule_id: 'rule-history', amount_min: '0.00', amount_max: '500000.00',
  required_director_count: 1, effective_from: '2026-04-01', effective_to: '2026-07-31',
  status: 'superseded' as const, version_number: 'AM-2026-01',
};

const pagination = { page: 1, page_size: 100, total_count: 2, total_pages: 1, has_next: false, has_previous: false };

const proposal = {
  approval_configuration_proposal_id: 'proposal-1', proposal_type: 'rule_supersede', target_entity_id: 'rule-active',
  payload: { ...activeRule, approval_matrix_rule_id: undefined, status: undefined, effective_from: '2026-09-01', version_number: 'AM-2026-03' },
  reason: 'Board-approved threshold governance update.', status: 'pending' as const, version: 1,
  made_by_user_id: 'staff-1', decided_by_user_id: null, decided_at: null, rejection_reason: null,
  available_actions: [{ action_code: 'approvals.configuration_proposal.approve', label: 'Approve', enabled: false, disabled_reason: 'Maker cannot approve or reject their own proposal.', required_permission: '', confirmation_required: true }],
};

const activePolicy = {
  loan_policy_config_id: 'policy-active', policy_name: 'Board Loan Policy 2026', policy_version: 'LP-2026',
  effective_from: '2026-04-01', effective_to: null, short_term_duration_months: 12,
  min_secured_loan_months: 12, max_secured_loan_years: 3, approval_threshold_amount: '500000.00',
  default_scale_of_finance_per_acre_amount: '20000.00', share_limit_percentage: '10.0000',
  per_share_cap_amount: '200.00', interest_rate_type: 'floating', interest_benchmark: 'Board benchmark',
  penal_interest_rate: null, rekyc_frequency_months: 24, record_retention_years: 8,
  grace_period_months: 3, non_intentional_extension_months: 12,
  board_approval_reference: 'BOARD-2026-01', status: 'active' as const,
};

const retiredPolicy = {
  ...activePolicy, loan_policy_config_id: 'policy-retired', policy_name: 'Board Loan Policy 2025',
  policy_version: 'LP-2025', effective_from: '2025-04-01', effective_to: '2026-03-31',
  board_approval_reference: 'BOARD-2025-01', status: 'retired' as const,
};

const draftPolicy = {
  ...activePolicy, loan_policy_config_id: 'policy-draft', policy_version: 'LP-2027',
  effective_from: '2027-04-01', board_approval_reference: 'BOARD-2027-01', status: 'draft' as const,
};
