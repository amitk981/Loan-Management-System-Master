import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from './authSession';
import { fetchDefaultCase, fetchDefaultCases } from './recoveryApi';

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

const ok = (data: unknown, pagination?: unknown) => ({
  ok: true,
  status: 200,
  json: async () => ({
    success: true,
    data,
    ...(pagination ? { pagination } : {}),
  }),
}) as Response;
