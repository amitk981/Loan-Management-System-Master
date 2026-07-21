import React, { useState } from 'react';
import { Search, Bell, HelpCircle, ChevronDown, User, ChevronRight, LogOut, RefreshCw } from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { Role } from '../../types';
import { DEMO_AUTH_ENABLED } from '../../services/authSession';

// Internal roles only — Borrower logs in separately via Login screen
const ALL_ROLES: { role: Role; label: string; group?: string }[] = [
  { role: 'field_officer',          label: 'Field Officer',               group: 'Intake' },
  { role: 'credit_manager',         label: 'Credit Manager',              group: 'Credit Assessment' },
  { role: 'deputy_manager_finance', label: 'Deputy Manager – Finance',    group: 'Credit Assessment' },
  { role: 'compliance_team',        label: 'Compliance Team',             group: 'Compliance' },
  { role: 'company_secretary',      label: 'Company Secretary',           group: 'Compliance' },
  { role: 'sanction_committee',     label: 'Sanction Committee',          group: 'Sanction' },
  { role: 'cfo',                    label: 'CFO',                         group: 'Sanction' },
  { role: 'director',               label: 'Director',                    group: 'Sanction' },
  { role: 'senior_manager_finance', label: 'Senior Manager – Finance',    group: 'Finance' },
  { role: 'cfc',                    label: 'Chief Financial Controller',  group: 'Finance' },
  { role: 'accounts',               label: 'Accounts',                    group: 'Finance' },
  { role: 'sales_team_user',        label: 'Sales Team User',             group: 'Sales' },
  { role: 'auditor',                label: 'Auditor',                     group: 'Audit' },
  { role: 'admin',                  label: 'Administrator',               group: 'IT' },
  // Note: 'borrower' role is NOT listed here — borrowers use the login screen
];

const notifications = [
  { id: 1, type: 'approval', message: 'LO00000042 — Sanction approval required', time: '10 min ago', urgent: true },
  { id: 2, type: 'tat',      message: 'LO00000043 — Appraisal TAT will breach in 4 hours', time: '1 hr ago', urgent: true },
  { id: 3, type: 'doc',      message: 'LO00000039 — PoA pending notarisation', time: '2 hr ago', urgent: false },
  { id: 4, type: 'kyc',      message: 'Re-KYC due for 2 borrowers', time: '3 hr ago', urgent: false },
];

interface HeaderProps {
  activePage?: string;
  onNavigate?: (page: string, entityId?: string) => void;
  onSearch?: (query: string) => void;
  onLogout?: () => void;
}

const Header: React.FC<HeaderProps> = ({ activePage, onNavigate, onSearch, onLogout }) => {
  const { currentUser, setRole, can } = useRole();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showRolePicker, setShowRolePicker] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const closeAll = () => {
    setShowNotifications(false);
    setShowProfile(false);
    setShowRolePicker(false);
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

        {DEMO_AUTH_ENABLED && (
          <div className="relative">
            <button
              onClick={() => { setShowRolePicker(!showRolePicker); setShowNotifications(false); setShowProfile(false); }}
              className="h-10 flex items-center gap-1.5 text-xs font-semibold px-3 border border-slate-200 rounded-lg text-slate-600 bg-white hover:bg-slate-50 hover:border-slate-300 transition-colors"
              title="Switch demo role"
            >
              <RefreshCw size={12} />
              <span className="hidden sm:inline">Switch Role</span>
            </button>
            {showRolePicker && (
              <div className="absolute right-0 top-full mt-2 w-72 bg-white border border-slate-200 rounded-lg shadow-xl shadow-slate-200/80 z-50 overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-100">
                  <span className="text-sm font-semibold text-slate-900">Switch Demo Role</span>
                  <p className="text-xs text-slate-400 mt-0.5">Currently: <span className="text-green-700 font-medium">{currentUser.roleName}</span></p>
                  <p className="text-xs text-amber-600 mt-1">Internal roles only. Borrower uses separate login.</p>
                </div>
                <div className="max-h-80 overflow-y-auto py-1">
                  {(() => {
                    let lastGroup = '';
                    return ALL_ROLES.map(({ role, label, group }) => {
                      const showGroup = group !== lastGroup;
                      lastGroup = group || '';
                      return (
                        <React.Fragment key={role}>
                          {showGroup && group && (
                            <div className="px-4 py-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wide bg-slate-50 border-t border-slate-100 first:border-0">
                              {group}
                            </div>
                          )}
                          <button
                            onClick={() => { setRole(role); closeAll(); }}
                            className={`w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-slate-50 ${
                              currentUser.role === role ? 'text-green-700 bg-green-50 font-medium' : 'text-slate-700'
                            }`}
                          >
                            <span>{label}</span>
                            {currentUser.role === role && <ChevronRight size={14} className="text-green-500" />}
                          </button>
                        </React.Fragment>
                      );
                    });
                  })()}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setShowNotifications(!showNotifications); setShowProfile(false); setShowRolePicker(false); }}
            className="h-10 w-10 flex items-center justify-center text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors relative"
          >
            <Bell size={18} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
          </button>
          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-slate-200 rounded-lg shadow-xl shadow-slate-200/80 z-50 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
                <span className="text-sm font-semibold text-slate-900">Notifications</span>
                <span className="text-xs text-green-600 font-medium cursor-pointer">Mark all read</span>
              </div>
              {notifications.map(n => (
                <div key={n.id} className={`px-4 py-3 border-b border-slate-50 hover:bg-slate-50 cursor-pointer flex gap-3 ${n.urgent ? 'bg-amber-50/50' : ''}`}>
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${n.urgent ? 'bg-amber-500' : 'bg-slate-300'}`} />
                  <div>
                    <p className="text-sm text-slate-700">{n.message}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{n.time}</p>
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
            onClick={() => { setShowProfile(!showProfile); setShowNotifications(false); setShowRolePicker(false); }}
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

export default Header;
