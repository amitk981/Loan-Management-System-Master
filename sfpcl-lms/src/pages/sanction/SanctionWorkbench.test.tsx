// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SanctionWorkbench from './SanctionWorkbench';
import { AuthSessionError, authenticatedMultipartRequest, authenticatedPaginatedRequest, authenticatedRequest } from '../../services/authSession';
import workbenchSource from './SanctionWorkbench.tsx?raw';
import panelSource from '../../components/loan/ApprovalPanel.tsx?raw';
import appSource from '../../App.tsx?raw';
import sanctionApiSource from '../../services/sanctionApi.ts?raw';

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
  return { ...actual, authenticatedRequest: vi.fn(), authenticatedPaginatedRequest: vi.fn(), authenticatedMultipartRequest: vi.fn() };
});

const pagination = (items: unknown[], overrides: Record<string, unknown> = {}) => ({
  items,
  pagination: { page: 1, page_size: 20, total_count: items.length, total_pages: 1, has_next: false, has_previous: false, ...overrides },
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
  workbench_summary: {
    borrower_name: 'Frozen Borrower', member_type: 'individual_farmer',
    requested_amount: '440000.00', recommended_amount: '450000.00', eligible_amount: '475000.00',
    approval_path: 'CFO + one Director', exception_flag: false, related_party_flag: false,
    risk_rating: 'medium', submitted_at: '2026-07-13T09:00:00Z', current_decision_status: 'pending',
    pending_age: { label: 'Elapsed pending time', elapsed_seconds: 9000, display: '2h 30m' },
  },
  available_actions: [action('approve'), action('reject'), action('return'), action('abstain')],
};

const fullPage = (first: typeof approvalCase, prefix: string) => Array.from({ length: 20 }, (_, index) => index === 0 ? first : {
  ...first,
  approval_case_id: `${prefix}-case-${index + 1}`,
  loan_application_id: `${prefix}-application-${index + 1}`,
  related_entity_id: `${prefix}-application-${index + 1}`,
  application_reference_number: `${prefix.toUpperCase()}-${String(index + 1).padStart(2, '0')}`,
});

describe('SanctionWorkbench authenticated container', () => {
  beforeEach(() => {
    vi.mocked(authenticatedPaginatedRequest).mockImplementation(async path => {
      const items = await authenticatedRequest(path) as unknown[];
      return pagination(items) as never;
    });
  });
  afterEach(() => { cleanup(); vi.clearAllMocks(); vi.unstubAllGlobals(); localStorage.clear(); userPermissions = ['approvals.case.read', 'approvals.case.approve', 'approvals.case.reject', 'approvals.case.return', 'approvals.sanction.read']; userRoleCodes = ['cfo']; userId = 'cfo-1'; });

  it('renders the authoritative total and replaces the queue from the next server page', async () => {
    const secondPageCase = { ...approvalCase, approval_case_id: 'case-21', application_reference_number: 'LO000021' };
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination(fullPage(approvalCase, 'page-one'), { total_count: 101, total_pages: 6, has_next: true }) as never)
      .mockResolvedValueOnce(pagination(fullPage(secondPageCase, 'page-two'), { page: 2, total_count: 101, total_pages: 6, has_next: true, has_previous: true }) as never)
      .mockResolvedValueOnce(pagination([], { total_count: 0 }) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path === '/api/v1/approval-cases/case-1/') return approvalCase as never;
      if (path === '/api/v1/approval-cases/case-21/') return secondPageCase as never;
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);

    expect(await screen.findByText('101 cases from the approval-case service')).toBeTruthy();
    expect(screen.getByText('Page 1 of 6')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(await screen.findAllByText('LO000021')).toHaveLength(2);
    expect(screen.queryByText('LO000001')).toBeNull();
    expect(authenticatedPaginatedRequest).toHaveBeenNthCalledWith(1, '/api/v1/approval-cases/?approval_type=sanction&current_status=pending&assigned_to_me=true&page=1&page_size=20');
    expect(authenticatedPaginatedRequest).toHaveBeenNthCalledWith(2, '/api/v1/approval-cases/?approval_type=sanction&current_status=pending&assigned_to_me=true&page=2&page_size=20');
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Sanction queue is clear')).toBeTruthy();
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
    expect(authenticatedPaginatedRequest).toHaveBeenNthCalledWith(3, '/api/v1/approval-cases/?approval_type=sanction&current_status=approved&page=1&page_size=20');
  });

  it.each([
    [new AuthSessionError('OBJECT_ACCESS_DENIED', 'Permission was removed.', 403), 'Sanction access denied'],
    [new AuthSessionError('MALFORMED_RESPONSE', 'The server returned an invalid paginated response.', 200), 'Sanction action could not be completed'],
  ])('clears prior rows and totals when a later collection fails with $code', async (error, heading) => {
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination(fullPage(approvalCase, 'failure-page'), { total_count: 101, total_pages: 6, has_next: true }) as never)
      .mockRejectedValueOnce(error);
    vi.mocked(authenticatedRequest).mockResolvedValue(approvalCase as never);

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    expect(await screen.findByText('101 cases from the approval-case service')).toBeTruthy();
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');

    expect(await screen.findByText(heading)).toBeTruthy();
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
    expect(screen.queryByText('LO000001')).toBeNull();
  });

  it('keeps the newest filter authoritative when an older list response arrives last', async () => {
    let releasePending: ((value: ReturnType<typeof pagination>) => void) | undefined;
    const approved = {
      ...approvalCase,
      approval_case_id: 'case-approved',
      application_reference_number: 'LO-APPROVED',
      current_status: 'approved',
      available_actions: [],
    };
    vi.mocked(authenticatedPaginatedRequest)
      .mockImplementationOnce(() => new Promise(resolve => { releasePending = resolve as typeof releasePending; }) as never)
      .mockResolvedValueOnce(pagination([approved]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path === '/api/v1/approval-cases/case-approved/') return approved as never;
      if (path === '/api/v1/approval-cases/case-1/') return approvalCase as never;
      if (path.endsWith('/sanction-decision/')) throw new AuthSessionError('NOT_FOUND', 'No sanction decision.', 404);
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect((await screen.findAllByText('LO-APPROVED')).length).toBeGreaterThan(0);

    releasePending?.(pagination([approvalCase]));
    await waitFor(() => expect(screen.queryByText('LO000001')).toBeNull());
    expect(screen.getByText('1 cases from the approval-case service')).toBeTruthy();
    expect(screen.queryByText('Sanction queue is clear')).toBeNull();
  });

  it('keeps the newest empty filter state when an older denial arrives last', async () => {
    let rejectPending: ((reason: unknown) => void) | undefined;
    vi.mocked(authenticatedPaginatedRequest)
      .mockImplementationOnce(() => new Promise((_resolve, reject) => { rejectPending = reject; }) as never)
      .mockResolvedValueOnce(pagination([]) as never);

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Sanction queue is clear')).toBeTruthy();

    rejectPending?.(new AuthSessionError('OBJECT_ACCESS_DENIED', 'Old request denied.', 403));
    await waitFor(() => expect(screen.queryByText('Sanction access denied')).toBeNull());
    expect(screen.getByText('Sanction queue is clear')).toBeTruthy();
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
  });

  it('keeps the newest filter detail when an older detail response arrives last', async () => {
    let releaseOldDetail: ((value: typeof approvalCase) => void) | undefined;
    const approved = {
      ...approvalCase,
      approval_case_id: 'case-approved',
      application_reference_number: 'LO-APPROVED',
      current_status: 'approved',
      review_facts: { ...approvalCase.review_facts, borrowing_history: 'Newest approved history.' },
      available_actions: [],
    };
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination([approvalCase]) as never)
      .mockResolvedValueOnce(pagination([approved]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path === '/api/v1/approval-cases/case-1/') {
        return new Promise(resolve => { releaseOldDetail = resolve; }) as never;
      }
      if (path === '/api/v1/approval-cases/case-approved/') return approved as never;
      if (path.endsWith('/sanction-decision/')) throw new AuthSessionError('NOT_FOUND', 'No sanction decision.', 404);
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith('/api/v1/approval-cases/case-1/'));
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Newest approved history.')).toBeTruthy();

    releaseOldDetail?.(approvalCase);
    await waitFor(() => expect(screen.queryByText('No prior defaults; repayments timely.')).toBeNull());
    expect(screen.getByText('Newest approved history.')).toBeTruthy();
  });

  it.each([
    ['denial', new AuthSessionError('OBJECT_ACCESS_DENIED', 'Newest request denied.', 403), 'Sanction access denied'],
    ['malformed response', new AuthSessionError('MALFORMED_RESPONSE', 'The server returned an invalid paginated response.', 200), 'Sanction action could not be completed'],
    ['empty result', null, 'Sanction queue is clear'],
  ])('keeps the newest %s state when an older list response arrives last', async (_label, newestError, heading) => {
    let releaseOldList: ((value: ReturnType<typeof pagination>) => void) | undefined;
    vi.mocked(authenticatedPaginatedRequest)
      .mockImplementationOnce(() => new Promise(resolve => { releaseOldList = resolve as typeof releaseOldList; }) as never);
    if (newestError) vi.mocked(authenticatedPaginatedRequest).mockRejectedValueOnce(newestError);
    else vi.mocked(authenticatedPaginatedRequest).mockResolvedValueOnce(pagination([]) as never);
    vi.mocked(authenticatedRequest).mockResolvedValue(approvalCase as never);

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText(heading)).toBeTruthy();

    releaseOldList?.(pagination([approvalCase]));
    await waitFor(() => expect(screen.queryByText('LO000001')).toBeNull());
    expect(screen.getByText(heading)).toBeTruthy();
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
  });

  it('keeps the newest empty state when an older detail response arrives last', async () => {
    let releaseOldDetail: ((value: typeof approvalCase) => void) | undefined;
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination([approvalCase]) as never)
      .mockResolvedValueOnce(pagination([]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async path => {
      if (path === '/api/v1/approval-cases/case-1/') return new Promise(resolve => { releaseOldDetail = resolve; }) as never;
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith('/api/v1/approval-cases/case-1/'));
    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Sanction queue is clear')).toBeTruthy();

    releaseOldDetail?.(approvalCase);
    await waitFor(() => expect(screen.queryByText('No prior defaults; repayments timely.')).toBeNull());
    expect(screen.getByText('Sanction queue is clear')).toBeTruthy();
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
  });

  it('keeps a newer filter authoritative while an action detail refresh finishes', async () => {
    let releaseActionDetail: ((value: typeof approvalCase) => void) | undefined;
    let caseOneReads = 0;
    const approved = {
      ...approvalCase,
      approval_case_id: 'case-approved',
      application_reference_number: 'LO-ACTION-NEWEST',
      current_status: 'approved',
      review_facts: { ...approvalCase.review_facts, borrowing_history: 'Newest post-action filter detail.' },
      available_actions: [],
    };
    const staleActionDetail = {
      ...approvalCase,
      current_status: 'approved',
      review_facts: { ...approvalCase.review_facts, borrowing_history: 'Stale action refresh detail.' },
      available_actions: [],
    };
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination([approvalCase]) as never)
      .mockResolvedValueOnce(pagination([approved]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') return staleActionDetail as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) {
        caseOneReads += 1;
        if (caseOneReads === 1) return approvalCase as never;
        return new Promise(resolve => { releaseActionDetail = resolve; }) as never;
      }
      if (path === '/api/v1/approval-cases/case-approved/') return approved as never;
      if (path.endsWith('/sanction-decision/')) throw new AuthSessionError('NOT_FOUND', 'No sanction decision.', 404);
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved before changing filter.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    await waitFor(() => expect(caseOneReads).toBe(2));

    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Newest post-action filter detail.')).toBeTruthy();
    releaseActionDetail?.(staleActionDetail);

    await waitFor(() => expect(screen.queryByText('Stale action refresh detail.')).toBeNull());
    expect(screen.getByText('Newest post-action filter detail.')).toBeTruthy();
    expect(screen.getAllByText('LO-ACTION-NEWEST')).toHaveLength(2);
    expect(screen.getByText('1 cases from the approval-case service')).toBeTruthy();
  });

  it('keeps a newer empty filter authoritative while action submission finishes', async () => {
    let releaseAction: ((value: typeof approvalCase) => void) | undefined;
    let caseReads = 0;
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination([approvalCase]) as never)
      .mockResolvedValueOnce(pagination([]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') {
        return new Promise(resolve => { releaseAction = resolve; }) as never;
      }
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) {
        caseReads += 1;
        return approvalCase as never;
      }
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved before empty filter.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    await waitFor(() => expect(releaseAction).toBeTypeOf('function'));

    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText('Sanction queue is clear')).toBeTruthy();
    releaseAction?.({ ...approvalCase, current_status: 'approved', available_actions: [] });

    await waitFor(() => expect(screen.getByText('Sanction queue is clear')).toBeTruthy());
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
    expect(caseReads).toBe(1);
  });

  it.each([
    ['denied', new AuthSessionError('OBJECT_ACCESS_DENIED', 'Newest action filter denied.', 403), 'Sanction access denied'],
    ['malformed', new AuthSessionError('MALFORMED_RESPONSE', 'Newest action filter malformed.', 200), 'Sanction action could not be completed'],
    ['empty', null, 'Sanction queue is clear'],
  ])('keeps a newer %s state authoritative when an action detail refresh fails later', async (_label, newestError, heading) => {
    let rejectActionDetail: ((reason: unknown) => void) | undefined;
    let caseReads = 0;
    vi.mocked(authenticatedPaginatedRequest).mockResolvedValueOnce(pagination([approvalCase]) as never);
    if (newestError) vi.mocked(authenticatedPaginatedRequest).mockRejectedValueOnce(newestError);
    else vi.mocked(authenticatedPaginatedRequest).mockResolvedValueOnce(pagination([]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') return { ...approvalCase, version: 5 } as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) {
        caseReads += 1;
        if (caseReads === 1) return approvalCase as never;
        return new Promise((_resolve, reject) => { rejectActionDetail = reject; }) as never;
      }
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved before newest state.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    await waitFor(() => expect(caseReads).toBe(2));

    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'approved');
    expect(await screen.findByText(heading)).toBeTruthy();
    rejectActionDetail?.(new AuthSessionError('OBJECT_ACCESS_DENIED', 'Stale action refresh denied.', 403));

    await waitFor(() => expect(screen.getByText(heading)).toBeTruthy());
    expect(screen.getByText('0 cases from the approval-case service')).toBeTruthy();
    expect(screen.queryByText(/Stale action refresh denied/)).toBeNull();
  });

  it('keeps a newer filter authoritative while an action decision refresh finishes', async () => {
    let releaseDecision: ((value: { decision_reason: string; sanctioned_amount: string }) => void) | undefined;
    let caseReads = 0;
    const actionApproved = { ...approvalCase, current_status: 'approved', available_actions: [] };
    const rejected = {
      ...approvalCase,
      approval_case_id: 'case-rejected-newest',
      application_reference_number: 'LO-DECISION-NEWEST',
      current_status: 'rejected',
      review_facts: { ...approvalCase.review_facts, borrowing_history: 'Newest decision-race detail.' },
      available_actions: [],
    };
    vi.mocked(authenticatedPaginatedRequest)
      .mockResolvedValueOnce(pagination([approvalCase]) as never)
      .mockResolvedValueOnce(pagination([rejected]) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') return actionApproved as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) {
        caseReads += 1;
        return (caseReads === 1 ? approvalCase : actionApproved) as never;
      }
      if (path === '/api/v1/loan-applications/application-1/sanction-decision/') {
        return new Promise(resolve => { releaseDecision = resolve as typeof releaseDecision; }) as never;
      }
      if (path === '/api/v1/approval-cases/case-rejected-newest/') return rejected as never;
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);
    await userEvent.click(await screen.findByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved before decision race.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));
    await waitFor(() => expect(releaseDecision).toBeTypeOf('function'));

    await userEvent.selectOptions(screen.getByLabelText('Sanction case status'), 'rejected');
    expect(await screen.findByText('Newest decision-race detail.')).toBeTruthy();
    releaseDecision?.({ decision_reason: 'Stale sanction decision reason.', sanctioned_amount: '450000.00' });

    await waitFor(() => expect(screen.queryByText('Stale sanction decision reason.')).toBeNull());
    expect(screen.getByText('Newest decision-race detail.')).toBeTruthy();
    expect(screen.queryByText('Sanction decision')).toBeNull();
  });

  it('loads frozen case truth and approves through the exact case boundary before canonical refresh', async () => {
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path === '/api/v1/approval-cases/?approval_type=sanction&current_status=pending&assigned_to_me=true&page=1&page_size=20') return [approvalCase] as never;
      if (path === '/api/v1/approval-cases/case-1/' && !options?.method) return approvalCase as never;
      if (path === '/api/v1/approval-cases/case-1/approve/' && options?.method === 'POST') return { ...approvalCase, version: 5 } as never;
      throw new Error(`Unexpected request ${path}`);
    });

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);

    expect(await screen.findAllByText('LO000001')).toHaveLength(2);
    expect(screen.getByText('Frozen Borrower')).toBeTruthy();
    expect(screen.getByText(/individual farmer/)).toBeTruthy();
    expect(screen.getByText(/2h 30m/)).toBeTruthy();
    expect(screen.getByText('No prior defaults; repayments timely.')).toBeTruthy();
    expect(screen.getAllByText('CFO + one Director')).toHaveLength(3);
    await userEvent.click(screen.getByRole('button', { name: 'Record My Decision' }));
    await userEvent.type(screen.getByLabelText('Decision reason'), 'Approved after committee review.');
    await userEvent.click(screen.getByRole('button', { name: 'Confirm Decision' }));

    await waitFor(() => expect(authenticatedRequest).toHaveBeenCalledWith(
      '/api/v1/approval-cases/case-1/approve/',
      { method: 'POST', body: { version: 4, comments: 'Approved after committee review.' } },
    ));
    expect(vi.mocked(authenticatedRequest).mock.calls.filter(([path]) => path === '/api/v1/approval-cases/case-1/')).toHaveLength(2);
  });

  it('renders immutable action actor, role, decision, comment, and acted-at confirmation', async () => {
    const withHistory = {
      ...approvalCase,
      approval_actions: [{
        approval_action_id: 'action-1', role_code: 'director', user_id: 'director-1',
        full_name: 'API Director', decision: 'abstained', comments: 'Related-party conflict declared.',
        acted_at: '2026-07-13T10:15:00Z',
      }],
    };
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('assigned_to_me=true') ? [withHistory] as never : withHistory as never);

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);

    expect(await screen.findByText('Related-party conflict declared.')).toBeTruthy();
    expect(screen.getByText('API Director · director')).toBeTruthy();
    expect(screen.getByText('Confirmed at 2026-07-13T10:15:00Z')).toBeTruthy();
    expect(screen.getByText('Abstained')).toBeTruthy();
  });

  it('renders unavailable frozen legacy approver names without a live identity lookup', async () => {
    const legacy = {
      ...approvalCase,
      required_approvers: approvalCase.required_approvers.map(item => ({ ...item, full_name: null })),
      approval_actions: [{
        approval_action_id: 'legacy-action', role_code: 'director', user_id: 'legacy-director',
        full_name: null, decision: 'approved', comments: 'Legacy immutable decision.',
        acted_at: '2026-07-13T10:15:00Z',
      }],
    };
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('assigned_to_me=true') ? [legacy] as never : legacy as never);

    render(<SanctionWorkbench onOpenApplication={vi.fn()} />);

    expect((await screen.findAllByText('Not recorded')).length).toBeGreaterThan(0);
    expect(screen.getByText('Not recorded · director')).toBeTruthy();
    expect(screen.getByText('Legacy immutable decision.')).toBeTruthy();
  });

  it.each([
    ['Reject', 'reject', '/api/v1/approval-cases/case-1/reject/'],
    ['Return for Clarification', 'return', '/api/v1/approval-cases/case-1/return-for-clarification/'],
  ])('requires a reason and sends the exact %s request', async (button, actionCode, path) => {
    vi.mocked(authenticatedRequest).mockImplementation(async (requestPath, options) => {
      if (requestPath.includes('assigned_to_me=true')) return [approvalCase] as never;
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
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('assigned_to_me=true') ? [projected] as never : projected as never);
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
    vi.mocked(authenticatedRequest).mockImplementation(async path => path.includes('assigned_to_me=true') ? [readOnly] as never : readOnly as never);
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
      if (path.includes('assigned_to_me=true')) return [approvalCase] as never;
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
      if (path.includes('assigned_to_me=true')) return [oldCycle, newCycle] as never;
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
      if (path.includes('assigned_to_me=true')) return [approved] as never;
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
    const special = {
      ...approvalCase,
      general_meeting_evidence_required: true,
      general_meeting_approval: {
        general_meeting_approval_id: 'old-meeting', loan_application_id: 'application-1',
        related_party_type: 'director_relative', related_party_user_id: null,
        relationship_description: 'Prior submission.', meeting_date: '2026-07-01',
        notice_document_id: 'old-notice', minutes_document_id: 'old-minutes', resolution_document_id: 'old-resolution',
        approval_status: 'approved', recorded_by_user_id: 'secretary-1', recorded_at: '2026-07-01T12:00:00Z',
        supersedes_general_meeting_approval_id: null,
      },
      available_actions: [{ action_code: 'record_general_meeting_approval', label: 'Record General Meeting Approval', enabled: true, disabled_reason: null, required_permission: 'approvals.general_meeting.record' }],
    };
    const ids = ['notice-id', 'minutes-id', 'resolution-id'];
    vi.mocked(authenticatedMultipartRequest).mockImplementation(async () => ({ document_id: ids.shift() }) as never);
    vi.mocked(authenticatedRequest).mockImplementation(async (path, options) => {
      if (path.includes('assigned_to_me=true')) return [special] as never;
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
    const uploads = vi.mocked(authenticatedMultipartRequest).mock.calls;
    expect(uploads).toHaveLength(3);
    uploads.forEach(([path, fields]) => {
      expect(path).toBe('/api/v1/document-files/');
      expect(fields.document_category).toBe('legal');
      expect(fields.sensitivity_level).toBe('restricted');
      expect(fields.related_entity_type).toBe('application');
      expect(fields.related_entity_id).toBe('application-1');
      expect(fields.file).toBeInstanceOf(File);
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
      if (path.includes('assigned_to_me=true')) return [approvalCase] as never;
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
    expect(workbenchSource).not.toContain('referenceable');
    expect(sanctionApiSource).not.toContain('loadStoredAuthSession');
    expect(sanctionApiSource).not.toContain('API_BASE_URL');
    expect(sanctionApiSource).not.toContain('fetch(');
  });
});
