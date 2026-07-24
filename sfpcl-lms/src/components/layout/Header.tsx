import React, { useCallback, useEffect, useState } from 'react';
import { Search, Bell, HelpCircle, ChevronDown, User, ChevronRight, LogOut } from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError, DEMO_AUTH_ENABLED } from '../../services/authSession';
import { fetchNotifications, markNotificationRead, type NotificationListItem } from '../../services/notificationsApi';

const DemoRoleSwitcher = DEMO_AUTH_ENABLED
  ? React.lazy(() => import('../../demo/DemoRoleSwitcher'))
  : null;

interface HeaderProps {
  activePage?: string;
  onNavigate?: (page: string, entityId?: string) => void;
  onSearch?: (query: string) => void;
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({ activePage, onNavigate, onSearch, onLogout }) => {
  const { currentUser, setDemoUser, can } = useRole();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [notifications, setNotifications] = useState<NotificationListItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notificationStatus, setNotificationStatus] = useState<'loading' | 'success' | 'unauthorized' | 'error'>('loading');

  const refreshNotificationSummary = useCallback(async () => {
    setNotificationStatus('loading');
    try {
      const result = await fetchNotifications({ readStatus: 'unread', pageSize: 4 });
      setNotifications(result.items);
      setUnreadCount(result.pagination.total_count);
      setNotificationStatus('success');
    } catch (error) {
      setNotifications([]);
      setUnreadCount(0);
      setNotificationStatus(error instanceof AuthSessionError && error.status === 401 ? 'unauthorized' : 'error');
    }
  }, []);

  useEffect(() => {
    void refreshNotificationSummary();
  }, [refreshNotificationSummary]);

  const handleMarkNotificationRead = async (notification: NotificationListItem) => {
    try {
      await markNotificationRead(notification.notification_id, notification.read_state_version);
      await refreshNotificationSummary();
    } catch (error) {
      if (error instanceof AuthSessionError && error.status === 409 && error.code === 'STALE_WRITE') {
        await refreshNotificationSummary();
        return;
      }
      setNotificationStatus(error instanceof AuthSessionError && error.status === 401 ? 'unauthorized' : 'error');
    }
  };

  const closeAll = () => {
    setShowNotifications(false);
    setShowProfile(false);
  };

  return (
    <header className="h-[72px] bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm shadow-slate-200/60 flex items-center px-5 lg:px-6 gap-4 flex-shrink-0 z-20">
      {/* Search */}
      <div className="flex-1 max-w-2xl min-w-0">
        <div className="relative">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && searchQuery.trim()) {
                onSearch?.(searchQuery.trim());
                setSearchQuery('');
                closeAll();
              }
            }}
            placeholder="Search: borrower name, app no., loan no., folio, PAN, Aadhaar last 4, SAP code, mobile, cheque no…"
            autoComplete="off"
            className="w-full h-10 pl-10 pr-4 rounded-lg border border-slate-200 text-sm bg-slate-50/80 shadow-inner shadow-slate-100 focus:bg-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-1 flex-shrink-0 ml-auto">
        {/* Help */}
        <button className="h-10 w-10 flex items-center justify-center text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors" title="Help & SOP Reference">
          <HelpCircle size={18} />
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-slate-200 mx-1" />

        {DemoRoleSwitcher && (
          <React.Suspense fallback={null}>
            <DemoRoleSwitcher
              currentUser={currentUser}
              onSwitch={setDemoUser}
              onOpen={() => {
                setShowNotifications(false);
                setShowProfile(false);
              }}
            />
          </React.Suspense>
        )}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setShowNotifications(!showNotifications); setShowProfile(false); }}
            aria-label={`Notifications, ${unreadCount} unread`}
            className="h-10 w-10 flex items-center justify-center text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors relative"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 bg-red-500 rounded-full ring-2 ring-white text-[10px] leading-4 text-white font-semibold">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-xl shadow-slate-200/80 z-50 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
                <span className="text-sm font-semibold text-slate-900">Notifications</span>
                {notificationStatus === 'success' && unreadCount > 0 && (
                  <span className="text-xs text-slate-500 font-medium">{unreadCount} unread</span>
                )}
              </div>
              {notificationStatus === 'loading' && (
                <div className="px-4 py-6 text-center text-sm text-slate-500">Loading notifications…</div>
              )}
              {notificationStatus === 'success' && notifications.length === 0 && (
                <div className="px-4 py-6 text-center text-sm text-slate-500">You have no unread notifications.</div>
              )}
              {notificationStatus === 'error' && (
                <div className="px-4 py-6 text-center text-sm text-red-600">Notifications could not be loaded.</div>
              )}
              {notificationStatus === 'unauthorized' && (
                <div className="px-4 py-6 text-center text-sm text-amber-700">Please sign in to view notifications.</div>
              )}
              {notificationStatus === 'success' && notifications.map(notification => (
                <div key={notification.notification_id} className={`px-4 py-3 border-b border-slate-50 hover:bg-slate-50 flex gap-3 ${notification.severity === 'urgent' || notification.severity === 'warning' ? 'bg-amber-50/50' : ''}`}>
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${notification.severity === 'urgent' || notification.severity === 'warning' ? 'bg-amber-500' : 'bg-slate-300'}`} />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-700">{notification.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{notification.message}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{formatNotificationTime(notification.created_at)}</p>
                    <button
                      type="button"
                      aria-label={`Mark ${notification.title} as read`}
                      onClick={() => { void handleMarkNotificationRead(notification); }}
                      className="text-xs text-green-600 font-medium mt-1 hover:text-green-700"
                    >
                      Mark as read
                    </button>
                  </div>
                </div>
              ))}
              <button
                type="button"
                onClick={() => {
                  onNavigate?.('notifications');
                  closeAll();
                }}
                className="w-full px-4 py-3 text-center text-sm text-green-600 font-medium hover:bg-green-50 transition-colors"
              >
                View all notifications
              </button>
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="w-px h-6 bg-slate-200 mx-1" />

        {/* Profile */}
        <div className="relative">
          <button
            onClick={() => { setShowProfile(!showProfile); setShowNotifications(false); }}
            className="h-10 flex items-center gap-2 pl-2.5 pr-2 rounded-lg border border-transparent hover:border-slate-200 hover:bg-slate-50 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
              <User size={16} className="text-green-700" />
            </div>
              <div className="text-left hidden sm:block">
                <div className="text-sm font-medium text-slate-900 leading-tight">{currentUser.name}</div>
                <div className="text-xs text-slate-500 leading-tight">{currentUser.roleName}</div>
              </div>
            <ChevronDown size={14} className="text-slate-400" />
          </button>
          {showProfile && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-slate-200 rounded-lg shadow-xl shadow-slate-200/80 z-50 overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-100">
                <div className="text-sm font-semibold text-slate-900">{currentUser.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{currentUser.roleName}</div>
                {currentUser.teamName && <div className="text-xs text-slate-400">{currentUser.teamName}</div>}
                <div className="text-xs text-slate-400">{currentUser.email}</div>
              </div>
              <div className="p-2 space-y-0.5">
                <button onClick={() => { onNavigate?.('profile'); closeAll(); }} className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-lg">My Profile</button>
                {can('view_settings') && (
                  <button onClick={() => { onNavigate?.('settings'); closeAll(); }} className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 rounded-lg">Settings</button>
                )}
                <div className="h-px bg-slate-100 my-1" />
                <button
                  onClick={onLogout}
                  className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-2"
                >
                  <LogOut size={14} />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

const formatNotificationTime = (value: string): string => {
  const date = new Date(value);
  if (!value || Number.isNaN(date.getTime())) return 'Time not recorded';
  return date.toLocaleString('en-IN', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  });
};

export default Header;
