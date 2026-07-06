import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  DashboardSummaryView,
  type DashboardSummary,
} from './Dashboard';
import { fetchDashboardSummary } from '../services/dashboardApi';
import { clearStoredAuthSession, storedAuthSession } from '../services/authSession';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('dashboard API client', () => {
  it('loads the 003G dashboard summary with the stored bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok(creditManagerSummary));
    vi.stubGlobal('fetch', fetchMock);

    const summary = await fetchDashboardSummary();

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/dashboard/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer access-token-1',
        }),
      }),
    );
    expect(summary.cards[0]).toMatchObject({
      code: 'applications_pending_completeness',
      label: 'Applications pending completeness',
      count: 7,
      link: '/applications?status=pending_completeness',
    });
    expect(summary.tasks).toEqual([]);
  });

  it.each([
    ['AUTH_REQUIRED', 401],
    ['PERMISSION_DENIED', 403],
  ])('surfaces %s responses without substituting mock dashboard data', async (code, status) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(status, code)));

    await expect(fetchDashboardSummary()).rejects.toMatchObject({ code, status });
  });

  it('surfaces malformed or server failures as request failures', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(500, 'SERVER_ERROR')));

    await expect(fetchDashboardSummary()).rejects.toMatchObject({ code: 'SERVER_ERROR', status: 500 });
  });

  it('surfaces network failures without falling back to mock dashboard data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new Error('Network unavailable')));

    await expect(fetchDashboardSummary()).rejects.toThrow('Network unavailable');
  });
});

describe('DashboardSummaryView', () => {
  it('renders API card labels/counts and the empty task state from the 003G response', () => {
    const html = renderSummary(creditManagerSummary);

    expect(html).toContain('Applications pending completeness');
    expect(html).toContain('7');
    expect(html).toContain('Credit Manager Dashboard');
    expect(html).toContain('No pending tasks for your role.');
    expect(html).not.toContain('New Applications');
  });

  it('renders API tasks when the backend starts returning them', () => {
    const html = renderSummary({
      ...creditManagerSummary,
      tasks: [
        {
          task_type: 'completeness_review',
          entity_id: 'loan-app-1',
          title: 'Review application APP-0001',
          due_at: '2026-07-08T10:00:00Z',
        },
      ],
    });

    expect(html).toContain('Review application APP-0001');
    expect(html).toContain('completeness_review');
    expect(html).toContain('8 Jul 2026');
  });

  it.each([
    ['credit_manager', 'Applications pending completeness'],
    ['sanction_committee', 'Cases awaiting sanction'],
    ['compliance', 'Compliance tasks due'],
    ['treasury', 'Disbursements pending'],
    ['management', 'Portfolio review items'],
  ] as const)('renders %s cards from the API response', (roleContext, label) => {
    const html = renderSummary({
      role_context: roleContext,
      cards: [{ code: `${roleContext}_card`, label, count: 0, link: '/dashboard/future' }],
      tasks: [],
    });

    expect(html).toContain(label);
    expect(html).toContain(roleContext.replace('_', ' '));
  });

  it('uses existing alert patterns for unauthorized and error states', () => {
    const unauthorized = renderToStaticMarkup(
      <DashboardSummaryView status="forbidden" message="You do not have permission to read dashboard summaries." onNavigate={vi.fn()} />,
    );
    const failed = renderToStaticMarkup(
      <DashboardSummaryView status="error" message="Dashboard could not be loaded." onNavigate={vi.fn()} />,
    );

    expect(unauthorized).toContain('Dashboard unavailable');
    expect(unauthorized).toContain('You do not have permission');
    expect(unauthorized).not.toContain('Applications pending completeness');
    expect(failed).toContain('Dashboard could not be loaded.');
  });
});

const renderSummary = (summary: DashboardSummary) => renderToStaticMarkup(
  <DashboardSummaryView status="success" summary={summary} onNavigate={vi.fn()} />,
);

const creditManagerSummary: DashboardSummary = {
  role_context: 'credit_manager',
  cards: [
    {
      code: 'applications_pending_completeness',
      label: 'Applications pending completeness',
      count: 7,
      link: '/applications?status=pending_completeness',
    },
  ],
  tasks: [],
};

function ok(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, meta: { api_version: 'v1' } }),
  } as Response;
}

function error(status: number, code: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({
      success: false,
      error: { code, message: code === 'PERMISSION_DENIED' ? 'You do not have permission.' : 'Request failed.' },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
