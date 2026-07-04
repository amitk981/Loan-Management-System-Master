import React, { useState } from 'react';
import {
  LayoutDashboard, FileText, Users, ClipboardCheck, Gavel,
  FolderCheck, Database, Banknote, ReceiptIndianRupee, TimerReset,
  ShieldCheck, BarChart3, Settings, History, ChevronRight,
  Sprout, MessageSquareWarning, ChevronLeft, BadgeCheck, TrendingDown,
  Percent, Inbox, ClipboardList, FileCheck, Leaf, MessageSquare
} from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { Permission } from '../../contexts/RoleContext';
import { visibleStaffNavItems, type Page } from '../../services/navigationPermissions';

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
  requiredPermission?: Permission;
}

export interface StaffNavItem extends NavItem {
  id: Page;
}

export const allNavItems: StaffNavItem[] = [
  { id: 'dashboard',     label: 'Dashboard',             icon: <LayoutDashboard size={18} /> },
  { id: 'tasks',         label: 'Task Inbox',            icon: <Inbox size={18} />,           badge: 5, requiredPermission: 'view_applications' },
  { id: 'applications',  label: 'Applications',          icon: <FileText size={18} />,        badge: 3, requiredPermission: 'view_applications' },
  { id: 'completeness',  label: 'Completeness',          icon: <ClipboardList size={18} />,   badge: 3, requiredPermission: 'do_completeness_check' },
  { id: 'members',       label: 'Members & Borrowers',   icon: <Users size={18} />,           requiredPermission: 'view_members' },
  { id: 'appraisal',     label: 'Appraisal',             icon: <ClipboardCheck size={18} />,  badge: 2, requiredPermission: 'do_appraisal' },
  { id: 'sanction',      label: 'Sanction',              icon: <Gavel size={18} />,           badge: 1, requiredPermission: 'view_sanction' },
  { id: 'documentation', label: 'Documentation',         icon: <FolderCheck size={18} />,     badge: 1, requiredPermission: 'view_documentation' },
  { id: 'disbursement',  label: 'SAP & Disbursement',    icon: <Database size={18} />,        requiredPermission: 'initiate_disbursement' },
  { id: 'cfc',           label: 'Payment Authorisation', icon: <BadgeCheck size={18} />,      requiredPermission: 'authorise_disbursement' },
  { id: 'interest',      label: 'Interest Management',   icon: <Percent size={18} />,         requiredPermission: 'manage_interest' },
  { id: 'loan-accounts', label: 'Loan Accounts',         icon: <Banknote size={18} />,        requiredPermission: 'view_loan_accounts' },
  { id: 'repayments',    label: 'Repayments',            icon: <ReceiptIndianRupee size={18} />, requiredPermission: 'post_repayment' },
  { id: 'monitoring',    label: 'Monitoring',            icon: <TimerReset size={18} />,      badge: 3, requiredPermission: 'view_monitoring' },
  { id: 'defaults',      label: 'Default & Recovery',    icon: <TrendingDown size={18} />,    badge: 2, requiredPermission: 'manage_defaults' },
  { id: 'closure',       label: 'Closure & Archive',     icon: <BadgeCheck size={18} />,      requiredPermission: 'manage_closure' },
  { id: 'compliance',    label: 'Compliance',            icon: <ShieldCheck size={18} />,     requiredPermission: 'view_compliance' },
  { id: 'registers',     label: 'Registers',             icon: <Sprout size={18} />,          requiredPermission: 'view_registers' },
  { id: 'reports',       label: 'Reports & MIS',         icon: <BarChart3 size={18} />,       requiredPermission: 'view_reports' },
  { id: 'grievances',    label: 'Grievances',            icon: <MessageSquareWarning size={18} />, requiredPermission: 'view_compliance' },
  { id: 'audit',         label: 'Audit & Archive',       icon: <History size={18} />,         requiredPermission: 'view_audit' },
  { id: 'settings',      label: 'Settings',              icon: <Settings size={18} />,        requiredPermission: 'view_settings' },
  { id: 'admin-users',   label: 'Admin Users',           icon: <Users size={18} />,           requiredPermission: 'manage_users' },
  { id: 'tracer',        label: 'Tracer',                icon: <ClipboardCheck size={18} />,  requiredPermission: 'run_tracer' },
];

// Borrower portal nav
const borrowerNavItems: NavItem[] = [
  { id: 'overview',        label: 'Overview',            icon: <BarChart3 size={18} /> },
  { id: 'myProfile',       label: 'My Profile',          icon: <Users size={18} /> },
  { id: 'newApplication',  label: 'New Application',     icon: <ClipboardList size={18} /> },
  { id: 'myApplications',  label: 'My Applications',     icon: <FileText size={18} /> },
  { id: 'application',     label: 'Application Status',  icon: <FileText size={18} /> },
  { id: 'sanctionOutcome', label: 'Sanction Terms',      icon: <Gavel size={18} /> },
  { id: 'documentationActions', label: 'Documentation',  icon: <FolderCheck size={18} /> },
  { id: 'disbursementStatus', label: 'Disbursement',     icon: <Database size={18} /> },
  { id: 'loanHistory',     label: 'My Loans',            icon: <History size={18} /> },
  { id: 'repayments',      label: 'Repayments',          icon: <ReceiptIndianRupee size={18} /> },
  { id: 'directRepayment', label: 'Direct Repayment',    icon: <Banknote size={18} /> },
  { id: 'documents',       label: 'My Documents',        icon: <FileCheck size={18} /> },
  { id: 'notices',         label: 'Notices & Letters',   icon: <MessageSquareWarning size={18} /> },
  { id: 'closureNoc',      label: 'Closure & NOC',       icon: <BadgeCheck size={18} /> },
  { id: 'notifications',   label: 'Notifications',       icon: <Inbox size={18} /> },
  { id: 'supply',          label: 'Produce Supply',      icon: <Leaf size={18} /> },
  { id: 'grievance',       label: 'Raise Grievance',     icon: <MessageSquare size={18} /> },
  { id: 'securitySettings', label: 'Security Settings',  icon: <Settings size={18} /> },
];

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activePage, onNavigate }) => {
  const [collapsed, setCollapsed] = useState(false);
  const { currentUser, can } = useRole();

  const isBorrower = currentUser.role === 'borrower';
  const items = isBorrower
    ? borrowerNavItems
    : visibleStaffNavItems(allNavItems, can);

  return (
    <aside className={`flex flex-col bg-white border-r border-slate-200 transition-all duration-200 ${collapsed ? 'w-16' : 'w-60'} flex-shrink-0 h-full`}>
      {/* Logo */}
      <div className="flex items-center h-16 border-b border-slate-200 px-4 gap-3 flex-shrink-0">
        <img src="/logo.png" alt="Logo" className="w-8 h-8 object-contain flex-shrink-0" />
        {!collapsed && (
          <div className="min-w-0">
            <div className="text-sm font-bold text-slate-900 truncate">SFPCL</div>
            <div className="text-xs text-slate-500 truncate">
              {isBorrower ? 'Member Portal' : 'Credit Management'}
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {items.map(item => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group ${
                isActive
                  ? 'bg-green-50 text-green-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              } ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? item.label : undefined}
            >
              <span className={`flex-shrink-0 ${isActive ? 'text-green-600' : 'text-slate-500 group-hover:text-slate-700'}`}>
                {item.icon}
              </span>
              {!collapsed && (
                <>
                  <span className="flex-1 text-left truncate">{item.label}</span>
                  {item.badge !== undefined && (
                    <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold flex-shrink-0 ${
                      isActive ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                    }`}>{item.badge}</span>
                  )}
                  {isActive && <ChevronRight size={14} className="flex-shrink-0 text-green-500" />}
                </>
              )}
            </button>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-slate-200 p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-50 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
