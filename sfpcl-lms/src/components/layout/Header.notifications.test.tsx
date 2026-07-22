// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import type { NotificationListItem } from '../../services/notificationsApi';
import Header from './Header';
import headerSource from './Header.tsx?raw';

const fetchNotifications = vi.fn();
const markNotificationRead = vi.fn();

vi.mock('../../services/notificationsApi', () => ({
  fetchNotifications: (...args: unknown[]) => fetchNotifications(...args),
  markNotificationRead: (...args: unknown[]) => markNotificationRead(...args),
}));

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({
    currentUser: {
      id: 'user-1', name: 'Notification User', email: 'notification@example.com',
      role: 'cfo', roleName: 'CFO', roleCodes: ['cfo'], teamCodes: [],
      permissions: [], availableActions: [], prototypePermissions: [],
    },
    setRole: vi.fn(),
    can: vi.fn(() => true),
  }),
}));

beforeEach(() => {
  fetchNotifications.mockReset();
  markNotificationRead.mockReset();
});

afterEach(cleanup);

describe('010O Header notification summary', () => {
  it('renders the bounded backend unread summary and real unread count', async () => {
    fetchNotifications.mockResolvedValueOnce({
      items: [notification],
      pagination: { page: 1, page_size: 4, total_count: 3, total_pages: 1, has_next: false, has_previous: false },
    });

    render(<Header />);

    await waitFor(() => expect(fetchNotifications).toHaveBeenCalledWith({ readStatus: 'unread', pageSize: 4 }));
    expect(screen.getByRole('button', { name: 'Notifications, 3 unread' })).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 3 unread' }));
    expect(screen.getByText('Review LA-2026-0001')).toBeTruthy();
    expect(screen.getByText('LA-2026-0001 requires credit review.')).toBeTruthy();
  });

  it('shows the existing loading pattern while the summary request is pending', async () => {
    fetchNotifications.mockReturnValueOnce(new Promise(() => undefined));

    render(<Header />);
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 0 unread' }));

    expect(screen.getByText('Loading notifications…')).toBeTruthy();
  });

  it('shows a truthful empty state when the backend has no unread notifications', async () => {
    fetchNotifications.mockResolvedValueOnce({
      items: [],
      pagination: { page: 1, page_size: 4, total_count: 0, total_pages: 1, has_next: false, has_previous: false },
    });

    render(<Header />);
    await waitFor(() => expect(fetchNotifications).toHaveBeenCalled());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 0 unread' }));

    expect(screen.getByText('You have no unread notifications.')).toBeTruthy();
  });

  it('shows an error state without substituting notification fixtures', async () => {
    fetchNotifications.mockRejectedValueOnce(new Error('Network unavailable'));

    render(<Header />);
    await waitFor(() => expect(fetchNotifications).toHaveBeenCalled());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 0 unread' }));

    expect(screen.getByText('Notifications could not be loaded.')).toBeTruthy();
    expect(screen.queryByText('Sanction approval required')).toBeNull();
  });

  it('shows the unauthorized state returned by the authenticated API seam', async () => {
    fetchNotifications.mockRejectedValueOnce(new AuthSessionError('AUTH_REQUIRED', 'Please sign in.', 401));

    render(<Header />);
    await waitFor(() => expect(fetchNotifications).toHaveBeenCalled());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 0 unread' }));

    expect(screen.getByText('Please sign in to view notifications.')).toBeTruthy();
  });

  it('marks a row read with its exact version and refreshes the unread summary', async () => {
    fetchNotifications
      .mockResolvedValueOnce({
        items: [notification],
        pagination: { page: 1, page_size: 4, total_count: 1, total_pages: 1, has_next: false, has_previous: false },
      })
      .mockResolvedValueOnce({
        items: [],
        pagination: { page: 1, page_size: 4, total_count: 0, total_pages: 1, has_next: false, has_previous: false },
      });
    markNotificationRead.mockResolvedValueOnce({ ...notification, read: true, read_state_version: 2 });

    render(<Header />);
    await waitFor(() => expect(screen.getByRole('button', { name: 'Notifications, 1 unread' })).toBeTruthy());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 1 unread' }));
    await userEvent.click(screen.getByRole('button', { name: 'Mark Review LA-2026-0001 as read' }));

    expect(markNotificationRead).toHaveBeenCalledWith('notif-1', 1);
    await waitFor(() => expect(fetchNotifications).toHaveBeenCalledTimes(2));
    expect(screen.getByRole('button', { name: 'Notifications, 0 unread' })).toBeTruthy();
  });

  it('refreshes backend truth after a 409 STALE_WRITE instead of retaining stale rows', async () => {
    fetchNotifications
      .mockResolvedValueOnce({
        items: [notification],
        pagination: { page: 1, page_size: 4, total_count: 1, total_pages: 1, has_next: false, has_previous: false },
      })
      .mockResolvedValueOnce({
        items: [],
        pagination: { page: 1, page_size: 4, total_count: 0, total_pages: 1, has_next: false, has_previous: false },
      });
    markNotificationRead.mockRejectedValueOnce(new AuthSessionError('STALE_WRITE', 'Notification changed.', 409));

    render(<Header />);
    await waitFor(() => expect(screen.getByRole('button', { name: 'Notifications, 1 unread' })).toBeTruthy());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 1 unread' }));
    await userEvent.click(screen.getByRole('button', { name: 'Mark Review LA-2026-0001 as read' }));

    await waitFor(() => expect(fetchNotifications).toHaveBeenCalledTimes(2));
    expect(screen.getByText('You have no unread notifications.')).toBeTruthy();
  });

  it('routes View all to the existing Notifications Center', async () => {
    fetchNotifications.mockResolvedValueOnce({
      items: [],
      pagination: { page: 1, page_size: 4, total_count: 0, total_pages: 1, has_next: false, has_previous: false },
    });
    const onNavigate = vi.fn();

    render(<Header onNavigate={onNavigate} />);
    await waitFor(() => expect(fetchNotifications).toHaveBeenCalled());
    await userEvent.click(screen.getByRole('button', { name: 'Notifications, 0 unread' }));
    await userEvent.click(screen.getByRole('button', { name: 'View all notifications' }));

    expect(onNavigate).toHaveBeenCalledWith('notifications');
  });

  it('owns the final Header mock-surface removal', () => {
    expect(headerSource).not.toContain('mockData');
    expect(headerSource).not.toContain('const notifications = [');
    expect(headerSource).not.toContain('Sanction approval required');
    expect(headerSource).not.toContain('Appraisal TAT will breach');
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
  recipient: { type: 'user', user_id: 'user-1', full_name: 'Notification User' },
  read: false,
  read_at: null,
  read_by_user_id: null,
  read_state_version: 1,
  created_at: '2026-07-22T08:00:00Z',
};
