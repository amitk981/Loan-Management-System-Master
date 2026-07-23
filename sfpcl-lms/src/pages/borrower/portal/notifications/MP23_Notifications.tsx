import React, { useEffect, useState } from 'react';
import { Bell, CheckCircle2, Clock, FileWarning } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import {
  fetchPortalNotifications,
  markPortalNotificationRead,
  type PortalNotification,
} from '../../../../services/portalApi';

export const MP23NotificationsView: React.FC<{
  notifications: PortalNotification[];
  loading: boolean;
  error: string | null;
  onMarkRead: (notification: PortalNotification) => void;
}> = ({ notifications, loading, error, onMarkRead }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-xl font-bold text-slate-900">Notifications</h2>
      <p className="text-sm text-slate-500 mt-1">All borrower-facing alerts, reminders, and workflow updates.</p>
    </div>
    {error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
    <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-100 flex items-center gap-2">
        <Bell size={17} className="text-green-600" />
        <h3 className="font-semibold text-slate-900">Notification Center</h3>
      </div>
      {loading ? (
        <div className="p-8 text-center text-sm text-slate-500">Loading notifications…</div>
      ) : notifications.length === 0 ? (
        <div className="p-8 text-center text-sm text-slate-500">You have no portal notifications.</div>
      ) : (
        <div className="divide-y divide-slate-50">
          {notifications.map(item => {
            const Icon = item.severity === 'urgent' ? Clock : item.severity === 'warning' ? FileWarning : CheckCircle2;
            return (
              <button
                key={item.notification_id}
                className="w-full text-left px-6 py-4 flex items-start justify-between gap-4 hover:bg-slate-50 transition-colors"
                onClick={() => { if (!item.read) onMarkRead(item); }}
                aria-label={`${item.title}${item.read ? '' : ' — mark as read'}`}
              >
                <div className="flex items-start gap-3 min-w-0">
                  <div className="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0">
                    <Icon size={18} className={item.severity === 'urgent' ? 'text-red-600' : item.severity === 'warning' ? 'text-amber-600' : 'text-green-600'} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                    <p className="text-sm text-slate-600 mt-1">{item.message}</p>
                    <p className="text-xs text-slate-400 mt-1">{new Date(item.created_at).toLocaleString()}</p>
                  </div>
                </div>
                <StatusBadge label={item.read ? 'read' : 'unread'} size="sm" />
              </button>
            );
          })}
        </div>
      )}
    </div>
  </div>
);

const MP23_Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<PortalNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchPortalNotifications()
      .then(rows => { if (active) setNotifications(rows); })
      .catch(reason => {
        if (active) setError(reason instanceof AuthSessionError && reason.status === 403
          ? 'You are not authorised to view these notifications.'
          : 'Notifications could not be loaded. Please try again.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const markRead = async (notification: PortalNotification) => {
    setError(null);
    try {
      const updated = await markPortalNotificationRead(notification);
      setNotifications(rows => rows.map(row => row.notification_id === updated.notification_id ? updated : row));
    } catch {
      setError('Notification status changed. Refresh and try again.');
    }
  };

  return <MP23NotificationsView notifications={notifications} loading={loading} error={error} onMarkRead={markRead} />;
};

export default MP23_Notifications;
