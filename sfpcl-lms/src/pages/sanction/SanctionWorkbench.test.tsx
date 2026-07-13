// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import SanctionWorkbench from './SanctionWorkbench';
import { AuthSessionError, authenticatedRequest, storedAuthSession } from '../../services/authSession';
import workbenchSource from './SanctionWorkbench.tsx?raw';
import panelSource from '../../components/loan/ApprovalPanel.tsx?raw';
import appSource from '../../App.tsx?raw';

let userPermissions = ['approvals.case.read', 'approvals.case.approve', 'approvals.case.reject', 'approvals.case.return', 'approvals.sanction.read'];
let userRoleCodes = ['cfo'];
let userId = 'cfo-1';

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({
    currentUser: {
      id: userId, roleCodes: userRoleCodes,
      permissions: userPermissions,
    },
  }),
}));
vi.mock('../../services/authSession', async importOriginal => {
  const actual = await importOriginal<typeof import('../../services/authSession')>();
  return { ...actual, authenticatedRequest: vi.fn() };
});

const action = (action_code: string) => ({
  action_code, label: action_code, enabled: true, disabled_reason: null,
  required_permission: `approvals.case.${action_code === 'return' ? 'return' : action_code}`,
});

const approvalCase = {
  approval_case_id: 'case-1', cycle_number: 1, approval_type: 'sanction',
  related_entity_type: 'loan_application', related_entity_id: 'application-1', loan_application_id: 'application-1',
  application_reference_number: 'LO000001', amount: '450000.00', current_status: 'pending', decision_date: '2026-07-13', version: 4,
  approval_matrix_rule_id: 'rule-1', approval_matrix_rule_version: 3, sanction_committee_id: 'committee-1', sanction_committee_version: 2,
  route_approvers: [{ role_code: 'cfo', user_id: 'cfo-1', full_name: 'API CFO' }, { role_code: 'director', user_id: 'director-1', full_name: 'API Director' }],
  required_approvers: [{ role_code: 'cfo', user_id: 'cfo-1', full_name: 'API CFO', decision: null, acted_at: null }, { role_code: 'director', user_id: 'director-1', full_name: 'API Director', decision: null, acted_at: null }],
  approval_actions: [], excluded_approvers: [], general_meeting_evidence_required: false, general_meeting_approval: null, conflict_block_reason: null,
  reason_for_approval: 'Reviewed package is suitable.', exception_condition_code: null, exception_reason: null,
  matrix_projection: { authority_summary: 'CFO + one Director' }, committee_projection: {}, loan_limit_provenance: { policy_name: 'Board policy 2026' },
  review_facts: {
    eligibility: { overall_result: 'eligible' },
    loan_amounts: { requested_amount: '440000.00', eligible_amount: '475000.00', recommended_amount: '450000.00' },
    purpose: { category: 'crop_production', description: 'Kharif crop production' },
    compliance_checks: { member_active_check: 'pass', default_check: 'no_default', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned' },
    borrowing_history: 'No prior defaults; repayments timely.',
    risk: { overall_risk_rating: 'medium', risk_mitigation_notes: 'Crop insurance verified.' },
    documentation_completeness: { status: 'complete', document_check: 'complete' },
    source_references: {}, maker_checker: {},
  },
  available_actions: [action('approve'), action('reject'), action('return'), action('abstain')],
};

describe('SanctionWorkbench authenticated container', () => {
  afterEach(() => { cleanup(); vi.clearAllMocks(); vi.unstubAllGlobals(); localStorage.clear(); userPermissions = ['approvals.case.read', 'approvals.case.approve', 'approvals.case.reject', 'approvals.case.return', 'approvals.sanction.read']; userRoleCodes = ['cfo']; userId = 'cfo-1'; });

  it('loads frozen case truth and approves through the exact case boundary before canonical refresh', async () => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/?assigned_to_me=true&page_size=100') return [approvalCase] as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) return approvalCase as never;
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') return { ...approvalCase, version: 5 } as never;
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);

    expect(await screen.findAllByText('LO000001')).toHaveLength(2);
    expect(screen.getByText('No prior defaults; repayments timely.')).toBeTruthy();
    expect(screen.getAllByText('CFO + one Director')).toHaveLength(2);
    await userEvent.click(screen.getByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved after committee review.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));

    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(
      '/api/v1/approval-cases/case-1/approve/',
      { method: 'POST', body: { version: 4, comments: 'Approved after committee review.' } },
    ));
    expect(vi.mocked(authenticatedRequest).mock.calls.filter(([path]) => path === '/api/v1/approval-cases/case-1/')).toHaveLength(2);
  });

  it.each([
    ['Reject', 'reject', '/api/v1/approval-cases/case-1/reject/'],
    ['Return for Clarification', 'return', '/api/v1/approval-cases/case-1/return-for-clarification/'],
  ])('requires a reason and sends the exact %s request', async (button, actionCode, path) => {
    vi.mocked(authenticatedRequest).mockImplementation(async (requestPath, options) => {
      if (requestPath.includes('?assigned_to_me=')) return [approvalCase] as never;
      if (requestPath === '/api/v1/approval-cases/case-1/' && !options?.method) return approvalCase as never;
      if (requestPath === path && options?.method === 'POST') return { ...approvalCase, version: 5 } as never;
      throw new Error(`Unexpected request ${requestPath}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.click(screen.getByText(button, { selector: 'span' }));
    expect((screen.getByRole('button', { name: 'Confirm Decision' }) as HTMLButtonElement).disabled).toBe(true);
    await userEvent.type(screen.getByLabelText('Decision reason *'), 'Committee requires a documented response.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(path, {
      method: 'POST', body: { version: 4, comments: 'Committee requires a documented response.' },
    }));
    expect(actionCode).toBeTruthy();
  });

  it.each([
    ['CFO', ['cfo'], ['approvals.case.read', 'approvals.case.approve'], true],
    ['Director', ['director'], ['approvals.case.read', 'approvals.case.approve'], true],
    ['Credit Manager', ['credit_manager'], ['approvals.case.read'], false],
  ])('applies the $0 resource/permission usability matrix', async (_label, roles, permissions, actionable) => {
    userRoleCodes = roles;
    userPermissions = permissions;
    userId = roles[0] === 'director' ? 'director-1' : 'cfo-1';
    const projected = actionable ? { ...approvalCase, required_approvers: approvalCase.required_approvers.map(item => item.role_code === roles[0] ? { ...item, user_id: userId } : item) } : { ...approvalCase, available_actions: [] };
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('?assigned_to_me=') ? [projected] as never : projected as never);
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await screen.findAllByText('LO000001');
    expect(Boolean(screen.queryByRole('button', { name: 'Record My Decision' }))).toBe(actionable);
  });

  it('blocks an unauthorized role at the case collection boundary', async () => {
    userRoleCodes = ['sales_team_user']; userPermissions = []; userId = 'sales-1';
    vi.mocked(authenticatedRequest).mockRejectedValue(new AuthSessionError('FORBIDDEN', 'You do not have approval case read permission.', 403));
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Sanction access denied')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Record My Decision' })).toBeNull();
  });

  it('does not union global permission into absent or disabled resource authority', async () => {
    const readOnly = { ...approvalCase, available_actions: [] };
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('?assigned_to_me=') ? [readOnly] as never : readOnly as never);
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await screen.findAllByText('LO000001');
    expect(screen.queryByRole('button', { name: 'Record My Decision' })).toBeNull();
    expect(screen.getByText(/Read-only — no case action/)).toBeTruthy();
  });

  it.each([
    ['CONFLICTED_APPROVER_NOT_ALLOWED', 'This user is marked as conflicted.'],
    ['GENERAL_MEETING_EVIDENCE_REQUIRED', 'Approved general meeting evidence is required.'],
    ['GENERAL_MEETING_APPROVAL_PENDING', 'The current general meeting approval is pending.'],
    ['GENERAL_MEETING_APPROVAL_REJECTED', 'The current general meeting approval was rejected.'],
  ])('surfaces %s without fabricating completion or refetching', async (code, errorMessage) => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.includes('?assigned_to_me=')) return [approvalCase] as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) return approvalCase as never;
      if (path.endsWith('/approve/')) throw new AuthSessionError(code, errorMessage, 409);
      throw new Error(`Unexpected request ${path}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    expect(await screen.findByText(new RegExp(code))).toBeTruthy();
    expect(vi.mocked(authenticatedRequest).mock.calls.filter(([path]) => path === '/api/v1/approval-cases/case-1/')).toHaveLength(1);
  });

  it('keeps returned and corrected cycles isolated while navigating', async () => {
    const oldCycle = { ...approvalCase, approval_case_id: 'case-old', application_reference_number: 'LO-OLD', cycle_number: 1, current_status: 'returned_for_clarification', version: 5, review_facts: { ...approvalCase.review_facts, borrowing_history: 'Cycle one history.', loan_amounts: { ...approvalCase.review_facts.loan_amounts, recommended_amount: '400000.00' } }, loan_limit_provenance: { policy_name: 'Frozen old policy' }, available_actions: [] };
    const newCycle = { ...approvalCase, approval_case_id: 'case-new', application_reference_number: 'LO-NEW', cycle_number: 2, review_facts: { ...approvalCase.review_facts, borrowing_history: 'Cycle two corrected history.' }, loan_limit_provenance: { policy_name: 'Frozen corrected policy' } };
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path.includes('?assigned_to_me=')) return [oldCycle, newCycle] as never;
      if (path === '/api/v1/approval-cases/case-old/') return oldCycle as never;
      if (path === '/api/v1/approval-cases/case-new/') return newCycle as never;
      throw new Error(`Unexpected request ${path}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Cycle one history.')).toBeTruthy();
    expect(screen.getByText(/Frozen old policy/)).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: /LO-NEW/ }));
    expect(await screen.findByText('Cycle two corrected history.')).toBeTruthy();
    expect(screen.getByText(/Frozen corrected policy/)).toBeTruthy();
    expect(screen.queryByText('Cycle one history.')).toBeNull();
  });

  it('reads terminal sanction terms only with the independent sanction permission', async () => {
    const approved = { ...approvalCase, current_status: 'approved', available_actions: [] };
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path.includes('?assigned_to_me=')) return [approved] as never;
      if (path === '/api/v1/approval-cases/case-1/') return approved as never;
      if (path.endsWith('/sanction-decision/')) return { sanction_decision_id: 'sanction-1', decision: 'sanctioned', sanctioned_amount: '450000.00', sanctioned_tenure_months: null, interest_rate_type: null, interest_rate_value: null, repayment_date: null, penal_interest_rate: null, charges: {}, security_required_summary: null, conditions_precedent: null, decision_reason: 'Approved by frozen cycle authority.' } as never;
      throw new Error(`Unexpected request ${path}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('Approved by frozen cycle authority.')).toBeTruthy();
    expect(authenticatedRequest).toHaveBeenCalledWith('/api/v1/loan-applications/application-1/sanction-decision/');
  });

  it('uploads three application-scoped legal files before recording bounded special-case evidence', async () => {
    userPermissions = ['approvals.case.read', 'approvals.general_meeting.record', 'documents.file.download', 'documents.file.upload'];
    storedAuthSession({ accessToken: 'special-token', refreshToken: 'refresh' });
    const special = { ...approvalCase, general_meeting_evidence_required: true, available_actions: [{ action_code: 'record_general_meeting_approval', label: 'Record General Meeting Approval', enabled: true, disabled_reason: null, required_permission: 'approvals.general_meeting.record' }] };
    const ids = ['notice-id', 'minutes-id', 'resolution-id'];
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async () => ({
      ok: true, status: 200, json: async () => ({ success: true, data: { document_id: ids.shift() } }),
    })));
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.includes('?assigned_to_me=')) return [special] as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) return special as never;
      if (path.endsWith('/general-meeting-approval/') && options?.method === 'POST') return { general_meeting_approval_id: 'meeting-1' } as never;
      throw new Error(`Unexpected request ${path}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record general meeting evidence' }));
    await userEvent.selectOptions(screen.getByLabelText('Special case type'), 'director_relative');
    await userEvent.type(screen.getByLabelText('Relationship description *'), 'Borrower is a relative of a Director.');
    await userEvent.type(screen.getByLabelText('General meeting date *'), '2026-07-15');
    await userEvent.upload(screen.getByLabelText('Notice document *'), new File(['notice'], 'notice.pdf', { type: 'application/pdf' }));
    await userEvent.upload(screen.getByLabelText('Minutes document *'), new File(['minutes'], 'minutes.pdf', { type: 'application/pdf' }));
    await userEvent.upload(screen.getByLabelText('Resolution document *'), new File(['resolution'], 'resolution.pdf', { type: 'application/pdf' }));
    await userEvent.click(screen.getByRole('button', { name: 'Record Evidence' }));
    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(
      '/api/v1/loan-applications/application-1/general-meeting-approval/',
      { method: 'POST', body: {
        related_party_type: 'director_relative', related_party_user_id: null,
        relationship_description: 'Borrower is a relative of a Director.', meeting_date: '2026-07-15',
        notice_document_id: 'notice-id', minutes_document_id: 'minutes-id', resolution_document_id: 'resolution-id', approval_status: 'approved',
      } },
    ));
    const uploads = vi.mocked(fetch).mock.calls;
    expect(uploads).toHaveLength(3);
    uploads.forEach(([, options]) => {
      const form = options?.body as FormData;
      expect(form.get('document_category')).toBe('legal');
      expect(form.get('sensitivity_level')).toBe('restricted');
      expect(form.get('related_entity_type')).toBe('application');
      expect(form.get('related_entity_id')).toBe('application-1');
    });
  });

  it.each([
    [new AuthSessionError('AUTH_REQUIRED', 'Please sign in.', 401), 'Sign-in required'],
    [new AuthSessionError('OBJECT_ACCESS_DENIED', 'You cannot access this case.', 403), 'Sanction access denied'],
  ])('renders nondisclosing access state for $code', async (error, heading) => {
    vi.mocked(authenticatedRequest).mockRejectedValue(error);
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(await screen.findByText(heading)).toBeTruthy();
    expect(screen.queryByText('LO000001')).toBeNull();
  });

  it('renders loading then the honest empty assigned queue', async () => {
    let release: ((value: never[]) => void) | undefined;
    vi.mocked(authenticatedRequest).mockImplementation(() => new Promise(resolve => { release = resolve; }) as never);
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(screen.getByText('Loading sanction workbench')).toBeTruthy();
    release?.([]);
    expect(await screen.findByText('Sanction queue is clear')).toBeTruthy();
    expect(screen.getByText('No approval cases match this server filter.')).toBeTruthy();
  });

  it.each([
    [new AuthSessionError('VALIDATION_ERROR', 'Action failed validation.', 400, { comments: 'This field is required.' }), /comments: This field is required/],
    [new AuthSessionError('STALE_VERSION', 'The approval case has changed.', 409), /STALE_VERSION/],
  ])('surfaces action error state $code without retry', async (error, expected) => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.includes('?assigned_to_me=')) return [approvalCase] as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) return approvalCase as never;
      if (path.endsWith('/approve/')) throw error;
      throw new Error(`Unexpected request ${path}`);
    });
    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    expect((await screen.findAllByText(expected)).length).toBeGreaterThan(0);
    expect(vi.mocked(authenticatedRequest).mock.calls.filter(([path]) => path.endsWith('/approve/'))).toHaveLength(1);
  });

  it('leaves no mock or client authority path in the shell and owned files', () => {
    expect(workbenchSource).not.toContain('data/mockData');
    expect(workbenchSource).not.toContain('requestedAmount > 500000');
    expect(panelSource).not.toContain("can('approve_sanction')");
    expect(panelSource).not.toContain('requestedAmount <= 500000');
    expect(panelSource).not.toContain('currentUser.role');
    expect(appSource).not.toContain('applications={[]}');
  });
});
