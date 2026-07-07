import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import { fetchMemberDirectory, type MemberDirectoryItem } from '../../services/memberDirectoryApi';
import { MemberDirectoryView } from './MemberDirectory';

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

describe('member directory API client', () => {
  it('loads members from the backend list endpoint with the stored bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok([member]));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchMemberDirectory({ search: 'Ramesh', kycStatus: 'verified' });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/?search=Ramesh&kyc_status=verified',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer access-token-1',
        }),
      }),
    );
    expect(result.items[0]).toMatchObject({
      member_id: 'member-1',
      member_number: 'MEM-00125',
      display_name: 'Ramesh Patil',
      mobile_number: '******7890',
    });
  });

  it.each([
    ['AUTH_REQUIRED', 401],
    ['PERMISSION_DENIED', 403],
  ])('surfaces %s without substituting mock members', async (code, status) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(status, code)));

    await expect(fetchMemberDirectory()).rejects.toMatchObject({ code, status });
  });

  it('surfaces network failures without falling back to mock member data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new Error('Network unavailable')));

    await expect(fetchMemberDirectory()).rejects.toThrow('Network unavailable');
  });
});

describe('MemberDirectoryView', () => {
  it('renders API-backed rows and state messages without mock-only directory fields', () => {
    const populated = renderView('success', [member]);
    const empty = renderView('success', []);
    const forbidden = renderView('forbidden', [], 'You do not have permission to read members.');
    const loading = renderView('loading', []);

    expect(populated).toContain('Ramesh Patil');
    expect(populated).toContain('MEM-00125');
    expect(populated).toContain('******7890');
    expect(populated).not.toContain('Current Exposure');
    expect(populated).not.toContain('Supply Years');
    expect(populated).not.toContain('Borrower 360');
    expect(populated).not.toContain('Ganesh Thorat');
    expect(empty).toContain('No members found.');
    expect(forbidden).toContain('Member directory unavailable');
    expect(forbidden).toContain('You do not have permission');
    expect(loading).toContain('Loading members');
  });
});

const member: MemberDirectoryItem = {
  member_id: 'member-1',
  member_number: 'MEM-00125',
  member_type: 'individual_farmer',
  legal_name: 'Ramesh Patil',
  display_name: 'Ramesh Patil',
  folio_number: 'FOL-456',
  membership_status: 'active',
  kyc_status: 'verified',
  rekyc_due_date: '2027-06-22',
  default_status: 'no_default',
  mobile_number: '******7890',
  email: 'ramesh@example.com',
  share_summary: {
    number_of_shares: 100,
    holding_mode: 'physical',
    available_share_count: 100,
  },
  active_member_status: {
    status: 'active',
    verified_at: '2026-06-22T10:30:00Z',
  },
};

const renderView = (
  status: React.ComponentProps<typeof MemberDirectoryView>['status'],
  members: MemberDirectoryItem[],
  message = '',
) => renderToStaticMarkup(
  <MemberDirectoryView
    status={status}
    message={message}
    members={members}
    search=""
    kycFilter="all"
    typeFilter="all"
    onSearchChange={vi.fn()}
    onKycFilterChange={vi.fn()}
    onTypeFilterChange={vi.fn()}
    onSelect={vi.fn()}
    canViewMembers
  />,
);

function ok(data: unknown[]): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      success: true,
      data,
      pagination: {
        page: 1,
        page_size: 20,
        total_count: data.length,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}

function error(status: number, code: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({
      success: false,
      error: {
        code,
        message: code === 'PERMISSION_DENIED' ? 'You do not have permission.' : 'Request failed.',
      },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
