import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import {
  createRecoveryDecision,
  fetchDefaultCase,
  fetchDefaultCases,
  fetchRecoveryApprovalCase,
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

const ok = (data: unknown, pagination?: unknown) => ({
  ok: true,
  status: 200,
  json: async () => ({
    success: true,
    data,
    ...(pagination ? { pagination } : {}),
  }),
}) as Response;
