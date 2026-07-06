import React, { useEffect, useMemo, useState } from 'react';
import { ArrowRight, Bell, CheckCircle2, Clock, FileWarning, ShieldAlert } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import type { Page } from '../../App';
import {
  AuthSessionError,
} from '../../services/authSession';
import {
  fetchNotifications,
  markNotificationRead,
  type NotificationListItem,
  type NotificationSeverity,
} from '../../services/notificationsApi';

interface NotificationsCenterProps {
  onNavigate: (page: Page, id?: string) => void;
}

type NotificationFilter = NotificationSeverity | 'all';
type NotificationStatus = 'loading' | 'success' | 'forbidden' | 'unauthorized' | 'error';

const severityIcon: Record<NotificationSeverity, React.ReactNode> = {
  urgent: <ShieldAlert size={16} className="text-red-600" />,
  warning: <FileWarning size={16} className="text-amber-600" />,
  info: <Bell size={16} className="text-slate-500" />,
};

const NotificationsCenter: React.FC<NotificationsCenterProps> = ({ onNavigate }) => {
  const { currentUser } = useRole();
  const [filter, setFilter] = useState<NotificationFilter>('all');
  const [status, setStatus] = useState<NotificationStatus>('loading');
  const [message, setMessage] = useState('');
  const [notifications, setNotifications] = useState<NotificationListItem[]>([]);

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage('');

    fetchNotifications()
      .then(result => {
        if (cancelled) return;
        setNotifications(result.items);
        setStatus('success');
      })
      .catch(error => {
        if (cancelled) return;
        const next = notificationErrorState(error);
        setStatus(next.status);
        setMessage(next.message);
        setNotifications([]);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleMarkRead = async (notification: NotificationListItem) => {
    try {
      const updated = await markNotificationRead(
        notification.notification_id,
        notification.read_state_version,
      );
      setNotifications(prev => prev.map(item =>
        item.notification_id === updated.notification_id ? updated : item,
      ));
    } catch (error) {
      const next = notificationErrorState(error);
      setStatus(next.status);
      setMessage(next.message);
    }
  };

  return (
    <NotificationsCenterView
      status={status}
      message={message}
      notifications={notifications}
      filter={filter}
      onFilterChange={setFilter}
      onNavigate={onNavigate}
      onMarkRead={handleMarkRead}
      currentUserName={currentUser.name}
    />
  );
};

interface NotificationsCenterViewProps {
  status: NotificationStatus;
  message?: string;
  notifications: NotificationListItem[];
  filter: NotificationFilter;
  onFilterChange: (filter: NotificationFilter) => void;
  onNavigate: (page: Page, id?: string) => void;
  onMarkRead: (notification: NotificationListItem) => void;
  currentUserName: string;
}

export const NotificationsCenterView: React.FC<NotificationsCenterViewProps> = ({
  status,
  message,
  notifications,
  filter,
  onFilterChange,
  onNavigate,
  onMarkRead,
  currentUserName,
}) => {
  const visibleNotifications = useMemo(
    () => notifications.filter(item => filter === 'all' || item.severity === filter),
    [filter, notifications],
  );
  const urgentCount = notifications.filter(item => item.severity === 'urgent').length;
  const unreadCount = notifications.filter(item => !item.read).length;

  return (
    <div className="p-6 space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Notifications and Alerts Center</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Current-user notifications for {currentUserName}; dashboard task summaries remain separate.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 sm:w-[30rem]">
          <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3">
            <p className="text-xs text-red-600">Urgent</p>
            <p className="text-2xl font-bold text-red-700 num">{urgentCount}</p>
          </div>
          <div className="rounded-lg border border-amber-100 bg-amber-50 px-4 py-3">
            <p className="text-xs text-amber-600">Unread</p>
            <p className="text-2xl font-bold text-amber-700 num">{unreadCount}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">
            <p className="text-xs text-slate-500">Total</p>
            <p className="text-2xl font-bold text-slate-900 num">{notifications.length}</p>
          </div>
        </div>
      </div>

      <div className="card flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <CheckCircle2 size={16} className="text-green-600" />
          Notifications are scoped to direct, role, and team recipients from the backend inbox.
        </div>
        <select
          value={filter}
          onChange={e => onFilterChange(e.target.value as NotificationFilter)}
          className="field-select sm:w-44"
        >
          <option value="all">All severities</option>
          <option value="urgent">Urgent</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50">
          <h2 className="text-sm font-semibold text-slate-900">Alert Queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">Title, linked record, severity, timestamp, sender, recipient and read state.</p>
        </div>

        {status === 'loading' ? (
          <NotificationMessage icon={<Clock size={28} />} title="Loading notifications" />
        ) : status !== 'success' ? (
          <NotificationMessage
            icon={<Bell size={28} />}
            title="Notifications unavailable"
            message={message || 'Notifications could not be loaded.'}
          />
        ) : visibleNotifications.length === 0 ? (
          <NotificationMessage icon={<Bell size={28} />} title="No notifications for this filter" />
        ) : (
          <div className="divide-y divide-slate-100">
            {visibleNotifications.map(item => (
              <div
                key={item.notification_id}
                className={`w-full p-4 text-left ${
                  item.severity === 'urgent' ? 'bg-red-50/40' : ''
                }`}
              >
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="mt-0.5 h-8 w-8 rounded-lg bg-white border border-slate-100 flex items-center justify-center flex-shrink-0">
                      {severityIcon[item.severity]}
                    </div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold text-slate-900">{item.title}</p>
                        <StatusBadge label={item.read ? 'Read' : 'Unread'} size="sm" />
                        <StatusBadge label={item.category} size="sm" />
                      </div>
                      <p className="text-sm text-slate-600 mt-1">{item.message}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 lg:w-[430px]">
                    <InfoTile label="Sender" value={item.sender?.full_name || 'System'} />
                    <InfoTile label="Time" value={formatDateTime(item.created_at)} />
                    <InfoTile label="Recipient" value={recipientLabel(item)} />
                  </div>
                  <div className="flex items-center gap-2 lg:w-48 lg:justify-end">
                    {!item.read && (
                      <button
                        type="button"
                        onClick={() => onMarkRead(item)}
                        className="btn-secondary text-xs px-3 py-2"
                      >
                        Mark as read
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => navigateNotification(item, onNavigate)}
                      className="btn-secondary text-xs px-3 py-2 flex items-center gap-1"
                    >
                      {item.action_label || 'Open related record'}
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const NotificationMessage: React.FC<{
  icon: React.ReactNode;
  title: string;
  message?: string;
}> = ({ icon, title, message }) => (
  <div className="py-12 text-center">
    <div className="mx-auto text-slate-300 mb-3 flex justify-center">{icon}</div>
    <p className="text-sm font-semibold text-slate-700">{title}</p>
    {message && <p className="text-sm text-slate-500 mt-1">{message}</p>}
  </div>
);

const InfoTile: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="rounded-lg bg-white/80 border border-slate-100 px-3 py-2">
    <p className="text-[11px] text-slate-400">{label}</p>
    <p className="text-xs font-medium text-slate-700 truncate">{value}</p>
  </div>
);

const navigateNotification = (
  notification: NotificationListItem,
  onNavigate: (page: Page, id?: string) => void,
) => {
  const page = pageFromActionUrl(notification.action_url);
  onNavigate(page, notification.related_entity_id ?? undefined);
};

const pageFromActionUrl = (actionUrl: string | null): Page => {
  if (actionUrl?.startsWith('/applications')) return 'applications/detail';
  if (actionUrl?.startsWith('/loan-accounts')) return 'loan-accounts/detail';
  if (actionUrl?.startsWith('/documentation')) return 'documentation';
  if (actionUrl?.startsWith('/compliance')) return 'compliance';
  return 'notifications';
};

const recipientLabel = (notification: NotificationListItem): string => {
  if (notification.recipient.type === 'user') return notification.recipient.full_name || 'User';
  if (notification.recipient.type === 'role') return notification.recipient.role_code || 'Role';
  if (notification.recipient.type === 'team') return notification.recipient.team_code || 'Team';
  return 'Recipient';
};

const formatDateTime = (value: string): string => {
  if (!value) return 'Not recorded';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const notificationErrorState = (error: unknown): { status: NotificationStatus; message: string } => {
  if (error instanceof AuthSessionError) {
    if (error.status === 401) {
      return { status: 'unauthorized', message: 'Please sign in to view notifications.' };
    }
    if (error.status === 403) {
      return { status: 'forbidden', message: error.message };
    }
    return { status: 'error', message: error.message };
  }
  return { status: 'error', message: 'Notifications could not be loaded.' };
};

export default NotificationsCenter;
