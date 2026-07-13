import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  fetchApprovalMatrixRules,
  fetchCreditSanctionRegister,
  fetchExceptionRegister,
  supersedeApprovalMatrixRule,
} from './approvalRegistersApi';
import approvalRegistersSource from './approvalRegistersApi.ts?raw';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'register-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('approval registers API client', () => {
  it('leaves authenticated envelope transport to the shared client', () => {
    expect(approvalRegistersSource).toContain('authenticatedPaginatedRequest');
    expect(approvalRegistersSource).toContain('authenticatedRequest');
    expect(approvalRegistersSource).not.toMatch(/\bfetch\s*\(|loadStoredAuthSession|Authorization|ApiEnvelope|listRequest|envelopeRequest/);
  });

  it('keeps sanction and exception filters on their independent scoped endpoints', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([sanctionRow], { ...pagination, page: 2, total_count: 21, total_pages: 2, has_previous: true }))
      .mockResolvedValueOnce(ok([exceptionRow], pagination));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchCreditSanctionRegister({ financialYear: 'FY2026-27', decision: 'sanctioned', page: 2, pageSize: 10 }))
      .resolves.toMatchObject({ items: [{ borrower_name: 'Frozen Borrower' }], pagination: { page: 2, total_count: 21 } });
    await expect(fetchExceptionRegister({ status: 'pending', exceptionType: 'stage_bypass', page: 1, pageSize: 20 }))
      .resolves.toMatchObject({ items: [{ business_reason: 'Frozen exception reason' }], pagination: { total_count: 1 } });

    expect(fetchMock).toHaveBeenNthCalledWith(1,
      'http://127.0.0.1:8000/api/v1/credit-sanction-register/?financial_year=FY2026-27&decision=sanctioned&page=2&page_size=10',
      request(),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(2,
      'http://127.0.0.1:8000/api/v1/exception-register/?status=pending&exception_type=stage_bypass&page=1&page_size=20',
      request(),
    );
  });

  it('reads versioned matrix rules and submits a complete replacement as a governed proposal', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([matrixRule], pagination))
      .mockResolvedValueOnce(ok(proposal));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchApprovalMatrixRules({ page: 1, pageSize: 100 }))
      .resolves.toMatchObject({ items: [{ version_number: 'AM-2026-01' }] });
    await expect(supersedeApprovalMatrixRule('rule-1', replacement))
      .resolves.toMatchObject({ status: 'pending', proposal_type: 'rule_supersede' });

    expect(fetchMock).toHaveBeenNthCalledWith(1,
      'http://127.0.0.1:8000/api/v1/approval-matrix-rules/?page=1&page_size=100',
      request(),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(2,
      'http://127.0.0.1:8000/api/v1/approval-matrix-rules/rule-1/',
      request('PATCH', replacement),
    );
  });

  it('surfaces denied register reads without fallback rows', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'FORBIDDEN')));
    await expect(fetchCreditSanctionRegister()).rejects.toMatchObject({ code: 'FORBIDDEN', status: 403 });
  });

  it('surfaces a direct matrix replacement denial for a non-manager', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(403, 'FORBIDDEN')));
    await expect(supersedeApprovalMatrixRule('rule-1', replacement))
      .rejects.toMatchObject({ code: 'FORBIDDEN', status: 403 });
  });
});

const pagination = { page: 1, page_size: 20, total_count: 1, total_pages: 1, has_next: false, has_previous: false };

const sanctionRow = {
  credit_sanction_register_entry_id: 'register-1', approval_case_id: 'case-1', loan_application_id: 'application-1',
  sanction_decision_id: 'decision-1', workflow_event_id: 'event-1', application_number: 'LO00000042',
  borrower_name: 'Frozen Borrower', borrower_type: 'individual_farmer', requested_amount: '500000.00',
  eligible_amount: '450000.00', recommended_amount: '440000.00', sanctioned_amount: '440000.00',
  approval_authority: 'CFO + one Director', approver_names: ['CFO One', 'Director One'], approval_date: '2026-07-13',
  decision: 'sanctioned', reasons: 'Frozen sanction reason', exception_reference: null,
  conflict_abstention_details: [], general_meeting_approval_reference: null, recorded_at: '2026-07-13T10:00:00Z',
};

const exceptionRow = {
  exception_register_entry_id: 'exception-1', loan_application_id: 'application-1', loan_account_id: null,
  approval_case_id: 'case-1', cycle_number: 1, exception_type: 'stage_bypass', description: 'Frozen description',
  business_reason: 'Frozen exception reason', risk_assessment: 'Low', status: 'pending', case_status: 'pending',
  conflict_block_reason: null, authority_applied_summary: 'CFO: CFO One (pending)', route_approvers: [],
  required_approvers: [], approval_actions: [], created_at: '2026-07-13T10:00:00Z', closed_at: null,
};

const matrixRule = {
  approval_matrix_rule_id: 'rule-1', decision_type: 'loan_sanction', amount_min: '0.00', amount_max: '500000.00',
  condition_code: null, required_approver_roles: ['cfo', 'director'], required_director_count: 1,
  joint_approval_required_flag: true, register_required: 'credit_sanction_register', effective_from: '2026-04-01',
  effective_to: null, status: 'active', version_number: 'AM-2026-01', authority_summary: 'CFO + one Director',
  minimum_approver_count: 2,
};

const replacement = {
  decision_type: 'loan_sanction', amount_min: '0.00', amount_max: '500000.00', condition_code: null,
  required_approver_roles: ['cfo', 'director'], required_director_count: 1, joint_approval_required_flag: true,
  register_required: 'credit_sanction_register', effective_from: '2026-08-01', effective_to: null,
  version_number: 'AM-2026-02', reason: 'Board-approved successor version.',
};

const proposal = {
  approval_configuration_proposal_id: 'proposal-1', proposal_type: 'rule_supersede', target_entity_id: 'rule-1',
  payload: replacement, reason: replacement.reason, status: 'pending', version: 1, made_by_user_id: 'admin-1',
  decided_by_user_id: null, decided_at: null, rejection_reason: null, available_actions: [],
};

function request(method = 'GET', body?: unknown): RequestInit {
  return {
    method,
    headers: expect.objectContaining({
      Accept: 'application/json',
      Authorization: 'Bearer register-token',
      'X-Request-ID': expect.any(String),
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
    }) as unknown as HeadersInit,
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  };
}

function ok(data: unknown, page?: typeof pagination): Response {
  return { ok: true, status: 200, json: async () => ({ success: true, data, ...(page ? { pagination: page } : {}) }) } as Response;
}

function error(status: number, code: string): Response {
  return { ok: false, status, json: async () => ({ success: false, error: { code, message: 'Denied.' } }) } as Response;
}
