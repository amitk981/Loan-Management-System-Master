import {
  API_BASE_URL,
  AuthSessionError,
  loadStoredAuthSession,
} from './authSession';

interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    field_errors?: Record<string, unknown>;
  };
  pagination?: Pagination;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export type NotificationSeverity = 'info' | 'warning' | 'urgent';
export type NotificationReadStatus = 'all' | 'read' | 'unread';

export interface NotificationListItem {
  notification_id: string;
  communication_id: string | null;
  notification_type: string;
  category: string;
  severity: NotificationSeverity;
  title: string;
  message: string;
  related_entity_type: string | null;
  related_entity_id: string | null;
  action_label: string | null;
  action_url: string | null;
  sender: { user_id: string; full_name: string } | null;
  recipient: Record<string, string>;
  read: boolean;
  read_at: string | null;
  read_by_user_id: string | null;
  read_state_version: number;
  created_at: string;
}

export interface NotificationList {
  items: NotificationListItem[];
  pagination: Pagination;
}

export const fetchNotifications = async (filters: {
  readStatus?: NotificationReadStatus;
  severity?: NotificationSeverity | 'all';
  category?: string;
} = {}): Promise<NotificationList> => {
  const params = new URLSearchParams();
  if (filters.readStatus && filters.readStatus !== 'all') {
    params.set('read_status', filters.readStatus);
  }
  if (filters.severity && filters.severity !== 'all') {
    params.set('severity', filters.severity);
  }
  if (filters.category) params.set('category', filters.category);
  const query = params.toString();
  const envelope = await request<NotificationListItem[]>(
    `/api/v1/notifications/${query ? `?${query}` : ''}`,
    { method: 'GET' },
  );
  return {
    items: normalizeNotifications(envelope.data ?? []),
    pagination: envelope.pagination ?? emptyPagination,
  };
};

export const markNotificationRead = async (
  notificationId: string,
  readStateVersion: number,
): Promise<NotificationListItem> => {
  const envelope = await request<NotificationListItem>(
    `/api/v1/notifications/${notificationId}/mark-read/`,
    {
      method: 'POST',
      body: JSON.stringify({ read_state_version: readStateVersion }),
    },
  );
  return normalizeNotification(envelope.data);
};

const request = async <T>(path: string, options: RequestInit): Promise<ApiEnvelope<T>> => {
  const session = loadStoredAuthSession();
  if (!session) {
    throw new AuthSessionError('AUTH_REQUIRED', 'Please sign in to continue.', 401);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session.accessToken}`,
      ...(options.headers || {}),
    },
  });
  const envelope = await response.json() as ApiEnvelope<T>;
  if (!response.ok || !envelope.success) {
    throw new AuthSessionError(
      envelope.error?.code ?? 'REQUEST_FAILED',
      envelope.error?.message ?? 'Request failed.',
      response.status,
    );
  }
  return envelope;
};

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const normalizeNotifications = (items: NotificationListItem[]): NotificationListItem[] =>
  Array.isArray(items) ? items.map(normalizeNotification) : [];

const normalizeNotification = (item: NotificationListItem | undefined): NotificationListItem => ({
  notification_id: String(item?.notification_id ?? ''),
  communication_id: item?.communication_id ? String(item.communication_id) : null,
  notification_type: String(item?.notification_type ?? ''),
  category: String(item?.category ?? 'System'),
  severity: normalizeSeverity(item?.severity),
  title: String(item?.title ?? ''),
  message: String(item?.message ?? ''),
  related_entity_type: item?.related_entity_type ? String(item.related_entity_type) : null,
  related_entity_id: item?.related_entity_id ? String(item.related_entity_id) : null,
  action_label: item?.action_label ? String(item.action_label) : null,
  action_url: item?.action_url ? String(item.action_url) : null,
  sender: item?.sender ?? null,
  recipient: item?.recipient ?? { type: 'unknown' },
  read: Boolean(item?.read),
  read_at: item?.read_at ?? null,
  read_by_user_id: item?.read_by_user_id ?? null,
  read_state_version: Number.isFinite(Number(item?.read_state_version)) ? Number(item?.read_state_version) : 1,
  created_at: String(item?.created_at ?? ''),
});

const normalizeSeverity = (severity: unknown): NotificationSeverity => {
  if (severity === 'urgent' || severity === 'warning' || severity === 'info') return severity;
  return 'info';
};
