import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  fetchNotifications,
  markNotificationRead,
  type NotificationListItem,
} from '../../services/notificationsApi';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import { NotificationsCenterView } from './NotificationsCenter';

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

describe('notification API client', () => {
  it('loads current-user notifications with the stored bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok([notification]));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchNotifications({ readStatus: 'unread' });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/notifications/?read_status=unread',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer access-token-1',
        }),
      }),
    );
    expect(result.items[0]).toMatchObject({
      notification_id: 'notif-1',
      title: 'Review LA-2026-0001',
      read: false,
    });
  });

  it('marks a notification read with optimistic read-state version', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok({ ...notification, read: true, read_state_version: 2 }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await markNotificationRead('notif-1', 1);

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/notifications/notif-1/mark-read/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ read_state_version: 1 }),
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(result.read).toBe(true);
    expect(result.read_state_version).toBe(2);
  });

  it.each([
    ['AUTH_REQUIRED', 401],
    ['PERMISSION_DENIED', 403],
  ])('surfaces %s without substituting mock notifications', async (code, status) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(status, code)));

    await expect(fetchNotifications()).rejects.toMatchObject({ code, status });
  });

  it('surfaces network failures without falling back to mock notification data', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new Error('Network unavailable')));

    await expect(fetchNotifications()).rejects.toThrow('Network unavailable');
  });
});

describe('NotificationsCenterView', () => {
  it('renders backend notifications and existing empty/error states without mock borrower data', () => {
    const populated = renderView('success', [notification]);
    const empty = renderView('success', []);
    const forbidden = renderView('forbidden', [], 'You do not have permission to read notifications.');

    expect(populated).toContain('Review LA-2026-0001');
    expect(populated).toContain('Unread');
    expect(populated).not.toContain('outstanding principal');
    expect(empty).toContain('No notifications for this filter');
    expect(forbidden).toContain('Notifications unavailable');
    expect(forbidden).toContain('You do not have permission');
  });
});

const notification: NotificationListItem = {
  notification_id: 'notif-1',
  communication_id: 'comm-1',
  notification_type: 'application',
  category: 'Application',
  severity: 'warning',
  title: 'Review LA-2026-0001',
  message: 'LA-2026-0001 requires credit review.',
  related_entity_type: 'loan_application',
  related_entity_id: 'loan-app-1',
  action_label: 'Open related record',
  action_url: '/applications/detail',
  sender: { user_id: 'sender-1', full_name: 'Compliance User' },
  recipient: { type: 'user', user_id: 'user-1', full_name: 'Credit Manager' },
  read: false,
  read_at: null,
  read_by_user_id: null,
  read_state_version: 1,
  created_at: '2026-07-06T10:00:00Z',
};

const renderView = (
  status: React.ComponentProps<typeof NotificationsCenterView>['status'],
  notifications: NotificationListItem[],
  message = '',
) => renderToStaticMarkup(
  <NotificationsCenterView
    status={status}
    message={message}
    notifications={notifications}
    filter="all"
    onFilterChange={vi.fn()}
    onNavigate={vi.fn()}
    onMarkRead={vi.fn()}
    currentUserName="Credit Manager"
  />,
);

function ok(data: unknown): Response {
  const isList = Array.isArray(data);
  return {
    ok: true,
    status: 200,
    json: async () => ({
      success: true,
      data,
      pagination: isList ? {
        page: 1,
        page_size: 20,
        total_count: data.length,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      } : undefined,
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
      error: { code, message: code === 'PERMISSION_DENIED' ? 'You do not have permission.' : 'Request failed.' },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
