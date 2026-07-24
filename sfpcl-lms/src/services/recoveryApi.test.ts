import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  archiveLoanFile,
  closeLoan,
  createRecoveryDecision,
  downloadArchiveManifest,
  fetchArchiveRecord,
  fetchArchiveRecords,
  fetchComplianceDashboard,
  fetchClosureReadiness,
  fetchDefaultCase,
  fetchDefaultCases,
  fetchGrievances,
  fetchNoc,
  fetchRecoveryApprovalCase,
  issueNoc,
  recordSecurityReturn,
  resolveGrievance,
  reviewComplianceEvidence,
  reviewNbfcPrincipalTest,
  reviewSection186Tracker,
} from './recoveryApi';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'defaults-read-token', refreshToken: 'refresh-token' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('011PA default case read contracts', () => {
  it('uses the list and selected-detail endpoints and preserves frozen note facts', async () => {
    const projection = {
      default_case_id: 'case-1',
      non_payment_note: {
        frozen_case_facts: {
          original_due_date: '2025-04-15',
          prepared_by_name: 'Backend Assessor',
        },
      },
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([projection], {
        page: 1,
        page_size: 100,
        total_count: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      }))
      .mockResolvedValueOnce(ok(projection));
    vi.stubGlobal('fetch', fetchMock);

    const list = await fetchDefaultCases();
    const detail = await fetchDefaultCase('case-1');

    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/default-cases/?page_size=100',
      'http://127.0.0.1:8000/api/v1/default-cases/case-1/',
    ]);
    expect(list.items[0].non_payment_note?.frozen_case_facts).toEqual({
      original_due_date: '2025-04-15',
      prepared_by_name: 'Backend Assessor',
    });
    expect(detail.non_payment_note?.frozen_case_facts).toEqual(
      list.items[0].non_payment_note?.frozen_case_facts,
    );
  });
});

describe('011PB recovery decision contracts', () => {
  it('reads the note-linked approval and posts only its identifier, action, and mandatory reason', async () => {
    const approval = {
      approval_case_id: 'approval-1',
      approval_type: 'recovery',
      related_entity_type: 'non_payment_note',
      related_entity_id: 'note-1',
      current_status: 'approved',
      reason_for_approval: 'invoke_sh4',
    };
    const decision = {
      recovery_decision_id: 'decision-1',
      approval_case_id: 'approval-1',
      decision: 'invoke_sh4',
      decision_reason: 'Approved after reviewing frozen evidence.',
      status: 'approved',
      available_actions: [],
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(approval))
      .mockResolvedValueOnce(ok(decision));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchRecoveryApprovalCase('approval-1')).resolves.toMatchObject(approval);
    await expect(createRecoveryDecision('case-1', {
      approval_case_id: 'approval-1',
      decision: 'invoke_sh4',
      decision_reason: 'Approved after reviewing frozen evidence.',
    })).resolves.toMatchObject(decision);

    expect(fetchMock.mock.calls.map(([url, options]) => [
      url,
      (options as RequestInit | undefined)?.method ?? 'GET',
      (options as RequestInit | undefined)?.body,
    ])).toEqual([
      ['http://127.0.0.1:8000/api/v1/approval-cases/approval-1/', 'GET', undefined],
      [
        'http://127.0.0.1:8000/api/v1/default-cases/case-1/recovery-decision/',
        'POST',
        JSON.stringify({
          approval_case_id: 'approval-1',
          decision: 'invoke_sh4',
          decision_reason: 'Approved after reviewing frozen evidence.',
        }),
      ],
    ]);
  });
});

describe('011PC closure staff contracts', () => {
  it('reads readiness and posts financial closure with a stable idempotency identity', async () => {
    const readiness = {
      loan_account_id: 'loan-1',
      ready_for_closure: true,
      checks: [{ code: 'principal_paid', status: 'pass' }],
      principal_outstanding: '0.00',
      interest_outstanding: '0.00',
      charges_outstanding: '0.00',
      total_outstanding: '0.00',
      interest_adjustment_applied: false,
      security_return_required: false,
      physical_share_return_required: false,
      demat_unpledge_required: false,
      blank_cheque_return_required: false,
      poa_release_required: false,
    };
    const closure = {
      loan_closure_id: 'closure-1',
      loan_account_id: 'loan-1',
      loan_account_status: 'closed',
      closure_stage: 'financially_closed',
      closure_type: 'full_repayment',
      closed_at: '2026-07-25T10:00:00Z',
      noc_required: true,
      security_return_required: false,
      archive_required: true,
      requirements: { noc: 'pending', security_return: 'not_applicable', archive: 'pending' },
      idempotency_replayed: false,
      available_actions: ['closure.noc.issue', 'closure.archive.create'],
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(readiness))
      .mockResolvedValueOnce(ok(closure));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchClosureReadiness('loan-1')).resolves.toEqual(readiness);
    await expect(closeLoan('loan-1', {
      closure_notes: 'Canonical balances and blockers reviewed.',
      idempotency_key: 'closure-attempt-1',
    })).resolves.toEqual(closure);

    expect(fetchMock.mock.calls.map(([url, options]) => [
      url,
      (options as RequestInit | undefined)?.method ?? 'GET',
      (options as RequestInit | undefined)?.body,
      (options as RequestInit | undefined)?.headers,
    ])).toEqual([
      [
        'http://127.0.0.1:8000/api/v1/loan-accounts/loan-1/closure-readiness/',
        'GET',
        undefined,
        expect.any(Object),
      ],
      [
        'http://127.0.0.1:8000/api/v1/loan-accounts/loan-1/closure/',
        'POST',
        JSON.stringify({
          closure_type: 'full_repayment',
          closure_notes: 'Canonical balances and blockers reviewed.',
        }),
        expect.objectContaining({ 'Idempotency-Key': 'closure-attempt-1' }),
      ],
    ]);
  });

  it('issues NOC, records security return, and archives through exact owner endpoints', async () => {
    const noc = { noc_id: 'noc-1', loan_closure_id: 'closure-1', delivery_status: 'queued' };
    const security = {
      security_return_id: 'return-1',
      loan_closure_id: 'closure-1',
      security_package_id: null,
      status: 'completed',
      version: 1,
      completed_at: '2026-07-25T10:30:00Z',
      items: [],
      idempotency_replayed: false,
      available_actions: [],
    };
    const archive = {
      archive_record_id: 'archive-1',
      loan_closure_id: 'closure-1',
      retention_start_date: '2026-07-25',
      retention_until_date: '2034-07-25',
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(noc))
      .mockResolvedValueOnce(ok(noc))
      .mockResolvedValueOnce(ok(security))
      .mockResolvedValueOnce(ok(archive))
      .mockResolvedValueOnce(ok(archive));
    vi.stubGlobal('fetch', fetchMock);

    await issueNoc('closure-1', {
      document_id: 'document-1',
      delivery_mode: 'email',
      recipient_email: 'member@example.test',
      signatory_user_id: 'signatory-1',
      idempotency_key: 'noc-attempt-1',
    });
    await fetchNoc('closure-1');
    await recordSecurityReturn('closure-1', {
      payload: {},
      idempotency_key: 'return-attempt-1',
    });
    await archiveLoanFile('closure-1', {
      file_location_physical: 'Archive Room / Rack A / Box 12',
      file_location_digital: '',
      idempotency_key: 'archive-attempt-1',
    });
    await fetchArchiveRecord('closure-1');

    expect(fetchMock.mock.calls.map(([url, options]) => [
      new URL(String(url)).pathname,
      (options as RequestInit | undefined)?.method ?? 'GET',
      (options as RequestInit | undefined)?.body,
      ((options as RequestInit | undefined)?.headers as Record<string, string> | undefined)?.['Idempotency-Key'],
    ])).toEqual([
      ['/api/v1/loan-closures/closure-1/noc/', 'POST', JSON.stringify({
        document_id: 'document-1',
        delivery_mode: 'email',
        recipient_email: 'member@example.test',
        signatory_user_id: 'signatory-1',
      }), 'noc-attempt-1'],
      ['/api/v1/loan-closures/closure-1/noc/', 'GET', undefined, undefined],
      ['/api/v1/loan-closures/closure-1/security-return/', 'POST', JSON.stringify({}), 'return-attempt-1'],
      ['/api/v1/loan-closures/closure-1/archive/', 'POST', JSON.stringify({
        file_location_physical: 'Archive Room / Rack A / Box 12',
        file_location_digital: '',
      }), 'archive-attempt-1'],
      ['/api/v1/loan-closures/closure-1/archive/', 'GET', undefined, undefined],
    ]);
  });
});

describe('011PD compliance staff contracts', () => {
  it('loads every S62-S67 projection through its canonical read endpoint', async () => {
    const pages = [
      [{ compliance_control_id: 'control-1' }],
      [{ compliance_task_id: 'task-1' }],
      [{ section_186_tracker_id: 'section-1' }],
      [{ nbfc_principal_test_id: 'nbfc-1' }],
      [{ kyc_review_id: 'kyc-1' }],
      [{ money_lending_law_review_id: 'money-1' }],
      [{ stamp_duty_record_id: 'stamp-1' }],
    ];
    const fetchMock = vi.fn()
      .mockImplementation((_url: string, _options?: RequestInit) => (
        Promise.resolve(ok(pages.shift(), {
          page: 1,
          page_size: 100,
          total_count: 1,
          total_pages: 1,
          has_next: false,
          has_previous: false,
        }))
      ));
    vi.stubGlobal('fetch', fetchMock);

    const projection = await fetchComplianceDashboard();

    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/compliance-controls/?page_size=100',
      'http://127.0.0.1:8000/api/v1/compliance-tasks/?page_size=100',
      'http://127.0.0.1:8000/api/v1/compliance/section-186-trackers/',
      'http://127.0.0.1:8000/api/v1/compliance/nbfc-principal-tests/',
      'http://127.0.0.1:8000/api/v1/kyc-reviews/?page_size=100',
      'http://127.0.0.1:8000/api/v1/reports/money-lending-review/?page_size=100',
      'http://127.0.0.1:8000/api/v1/reports/stamp-duty/?page_size=100',
    ]);
    expect(projection.controls[0]).toMatchObject({ compliance_control_id: 'control-1' });
    expect(projection.section186[0]).toMatchObject({ section_186_tracker_id: 'section-1' });
    expect(projection.stampDuty[0]).toMatchObject({ stamp_duty_record_id: 'stamp-1' });
  });

  it('posts only the projected evidence and statutory review fields', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValue(ok({ compliance_task_id: 'task-1' }))
      .mockResolvedValue(ok({ section_186_tracker_id: 'section-1' }))
      .mockResolvedValue(ok({ nbfc_principal_test_id: 'nbfc-1' }));
    vi.stubGlobal('fetch', fetchMock);

    await reviewComplianceEvidence('evidence-1', {
      review_status: 'accepted',
      review_comments: 'Evidence reconciles to the governed source.',
    });
    await reviewSection186Tracker('section-1', {
      decision: 'accepted',
      comments: 'Quarterly threshold evidence reviewed.',
      presented_to_board_flag: false,
      board_document_id: null,
    });
    await reviewNbfcPrincipalTest('nbfc-1', {
      decision: 'rejected',
      comments: 'Ratio evidence needs correction.',
      presented_to_board_flag: false,
      board_document_id: null,
    });

    expect(fetchMock.mock.calls.map(([url, options]) => [
      url,
      (options as RequestInit).method,
      (options as RequestInit).body,
    ])).toEqual([
      [
        'http://127.0.0.1:8000/api/v1/compliance-evidence/evidence-1/review/',
        'POST',
        JSON.stringify({
          review_status: 'accepted',
          review_comments: 'Evidence reconciles to the governed source.',
        }),
      ],
      [
        'http://127.0.0.1:8000/api/v1/compliance/section-186-trackers/section-1/review/',
        'POST',
        JSON.stringify({
          decision: 'accepted',
          comments: 'Quarterly threshold evidence reviewed.',
          presented_to_board_flag: false,
          board_document_id: null,
        }),
      ],
      [
        'http://127.0.0.1:8000/api/v1/compliance/nbfc-principal-tests/nbfc-1/review/',
        'POST',
        JSON.stringify({
          decision: 'rejected',
          comments: 'Ratio evidence needs correction.',
          presented_to_board_flag: false,
          board_document_id: null,
        }),
      ],
    ]);
  });
});

describe('011PE grievance and archive staff contracts', () => {
  it('loads every grievance page, resolves through the projected action, and preserves idempotency', async () => {
    const grievance = {
      grievance_id: 'grievance-1',
      grievance_reference: 'GRV-2026-001',
      status: 'open',
      available_actions: ['resolve'],
    };
    const resolved = {
      ...grievance,
      status: 'resolved',
      resolution_summary: 'Canonical resolution retained.',
      available_actions: [],
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([grievance], {
        page: 1,
        page_size: 100,
        total_count: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      }))
      .mockResolvedValueOnce(ok(resolved));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchGrievances()).resolves.toMatchObject({
      items: [grievance],
      totalCount: 1,
    });
    await expect(resolveGrievance('grievance-1', {
      status: 'resolved',
      reason: 'Canonical resolution retained.',
      idempotency_key: 'grievance-resolution-1',
    })).resolves.toEqual(resolved);

    expect(fetchMock.mock.calls.map(([url, options]) => [
      url,
      (options as RequestInit | undefined)?.method ?? 'GET',
      (options as RequestInit | undefined)?.body,
      ((options as RequestInit | undefined)?.headers as Record<string, string> | undefined)?.['Idempotency-Key'],
    ])).toEqual([
      [
        'http://127.0.0.1:8000/api/v1/grievances/?page=1&page_size=100',
        'GET',
        undefined,
        undefined,
      ],
      [
        'http://127.0.0.1:8000/api/v1/grievances/grievance-1/resolve/',
        'POST',
        JSON.stringify({ resolution_summary: 'Canonical resolution retained.' }),
        'grievance-resolution-1',
      ],
    ]);
  });

  it('loads archive manifests and creates a download only after an audited canonical detail read', async () => {
    const archive = {
      archive_record_id: 'archive-1',
      loan_closure_id: 'closure-1',
      loan_account_id: 'loan-1',
      file_location_physical: 'Archive Room / Rack A / Box 12',
      file_location_digital: 'governed://loan-archive/manifest-25',
      retention_start_date: '2026-07-25',
      retention_until_date: '2034-07-25',
      archived_by_user_id: 'archivist-1',
      archived_by_role_code: 'company_secretary',
      archived_at: '2026-07-25T10:00:00Z',
      destruction_eligible: false,
      destruction_certificate_id: null,
      idempotency_replayed: false,
      available_actions: [],
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok([archive], {
        page: 1,
        page_size: 100,
        total_count: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      }))
      .mockResolvedValueOnce(ok(archive));
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchArchiveRecords('loan-1')).resolves.toMatchObject({
      items: [archive],
      totalCount: 1,
    });
    const manifest = await downloadArchiveManifest(archive);

    expect(manifest.fileName).toBe('archive-manifest-archive-1.json');
    expect(JSON.parse(await manifest.content.text())).toEqual(archive);
    expect(fetchMock.mock.calls.map(call => call[0])).toEqual([
      'http://127.0.0.1:8000/api/v1/archive-records/?page=1&page_size=100&search=loan-1',
      'http://127.0.0.1:8000/api/v1/loan-closures/closure-1/archive/',
    ]);
  });
});

const ok = (data: unknown, pagination?: unknown) => ({
  ok: true,
  status: 200,
  json: async () => ({
    success: true,
    data,
    ...(pagination ? { pagination } : {}),
  }),
}) as Response;
