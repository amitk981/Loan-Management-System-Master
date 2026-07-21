import React from 'react';
import { Bell, HelpCircle, LogOut } from 'lucide-react';
import Sidebar from '../../../components/layout/Sidebar';
import { useRole } from '../../../contexts/RoleContext';

export type BorrowerTab =
  | 'overview' | 'myProfile'
  | 'newApplication' | 'myApplications' | 'application' | 'sanctionOutcome'
  | 'documentationActions' | 'disbursementStatus'
  | 'repayments' | 'directRepayment' | 'documents' | 'notices'
  | 'loanHistory' | 'loanDetail' | 'closureNoc' | 'notifications' | 'supply'
  | 'grievance' | 'securitySettings';

interface MemberPortalLayoutProps {
  children: React.ReactNode;
  activeTab: BorrowerTab;
  activeSectionLabel: string;
  onNavigate: (tab: BorrowerTab) => void;
  onLogout?: () => void;
}

const MemberPortalLayout: React.FC<MemberPortalLayoutProps> = ({ children, activeTab, activeSectionLabel, onNavigate, onLogout }) => {
  const { currentUser } = useRole();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar
        activePage={activeTab}
        onNavigate={(page) => onNavigate(page as BorrowerTab)}
      />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 gap-4 flex-shrink-0 z-10">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-slate-500">Member Portal</div>
            <h1 className="text-lg font-bold text-slate-900 truncate">{activeSectionLabel}</h1>
          </div>
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            <button
              onClick={() => onNavigate('notifications')}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors relative"
              title="Notifications"
            >
              <Bell size={18} />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            <button
              onClick={() => onNavigate('grievance')}
              className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              title="Help"
            >
              <HelpCircle size={18} />
            </button>
            <div className="flex items-center gap-2 pl-3 pr-2 py-1.5 rounded-lg bg-slate-50 border border-slate-100">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-semibold text-sm">
                {currentUser.name.charAt(0)}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-sm font-medium text-slate-900 leading-tight">{currentUser.name}</div>
                <div className="text-xs text-slate-500 leading-tight">Member · Folio M-00042</div>
              </div>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                className="flex items-center gap-1 text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors"
              >
                <LogOut size={15} />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            )}
          </div>
        </header>
        <main className="flex-1 overflow-y-auto">
          <div className="w-full px-4 sm:px-6 py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default MemberPortalLayout;
