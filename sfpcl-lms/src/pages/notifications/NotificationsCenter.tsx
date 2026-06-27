import React, { useMemo, useState } from 'react';
import { ArrowRight, Bell, CheckCircle2, Clock, FileWarning, ShieldAlert } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { loanApplications, loanAccounts } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';
import type { Page } from '../../App';

interface NotificationsCenterProps {
  onNavigate: (page: Page, id?: string) => void;
}

type NotificationSeverity = 'urgent' | 'warning' | 'info';

interface InternalNotification {
  id: string;
  severity: NotificationSeverity;
  title: string;
  message: string;
  owner: string;
  age: string;
  status: string;
  route: Page;
  entityId?: string;
  source: string;
}

const severityIcon: Record<NotificationSeverity, React.ReactNode> = {
  urgent: <ShieldAlert size={16} className="text-red-600" />,
  warning: <FileWarning size={16} className="text-amber-600" />,
  info: <Bell size={16} className="text-slate-500" />,
};

const NotificationsCenter: React.FC<NotificationsCenterProps> = ({ onNavigate }) => {
  const { currentUser, can } = useRole();
  const [filter, setFilter] = useState<NotificationSeverity | 'all'>('all');

  const notifications = useMemo<InternalNotification[]>(() => {
    const tatItems = can('view_applications') ? loanApplications
      .filter(app => (app.tatDaysRemaining ?? 99) <= 1)
      .map(app => ({
        id: `tat-${app.id}`,
        severity: 'urgent' as const,
        title: `${app.applicationNumber} TAT requires action`,
        message: `${app.memberName} is at or near TAT breach. Current owner: ${app.currentOwner}.`,
        owner: app.currentOwner,
        age: app.tatDaysRemaining === 0 ? 'Due today' : `${app.tatDaysRemaining} day left`,
        status: app.status,
        route: 'applications/detail' as Page,
        entityId: app.id,
        source: 'Application SLA',
      })) : [];

    const sanctionItems = can('view_sanction') ? loanApplications
      .filter(app => ['pending_sanction_committee_approval', 'pending_sanction', 'under_sanction_review', 'clarification_requested'].includes(app.status) || app.isException)
      .map(app => ({
        id: `sanction-${app.id}`,
        severity: app.isException ? 'urgent' as const : 'warning' as const,
        title: `${app.applicationNumber} sanction decision pending`,
        message: app.isException
          ? `${app.exceptionReason || 'Exception case'}; approval matrix and conflict checks required.`
          : `${app.memberName} awaits sanction committee decision.`,
        owner: app.currentOwner,
        age: 'Open',
        status: app.isException ? 'exception' : app.status,
        route: 'sanction' as Page,
        entityId: app.id,
        source: 'Sanction Workbench',
      })) : [];

    const documentationItems = can('view_documentation') ? loanApplications
      .filter(app => ['sanctioned', 'documentation_in_progress', 'documentation_deficiency_raised', 'pending_final_checklist_approvals'].includes(app.status) && app.documentationStatus !== 'complete')
      .map(app => ({
        id: `doc-${app.id}`,
        severity: 'warning' as const,
        title: `${app.applicationNumber} documentation blocker`,
        message: `${app.documentationStatus.replace(/_/g, ' ')} blocks SAP and disbursement.`,
        owner: app.currentOwner,
        age: 'Pending',
        status: app.documentationStatus,
        route: 'documentation' as Page,
        entityId: app.id,
        source: 'Documentation Gate',
      })) : [];

    const monitoringItems = (can('view_monitoring') || can('manage_defaults')) ? loanAccounts
      .filter(loan => loan.dpd > 0)
      .map(loan => ({
        id: `loan-${loan.id}`,
        severity: loan.dpd > 90 ? 'urgent' as const : 'warning' as const,
        title: `${loan.accountNumber} is overdue`,
        message: `${loan.memberName} is ${loan.dpd} DPD with outstanding principal Rs.${loan.outstandingPrincipal.toLocaleString('en-IN')}.`,
        owner: loan.dpd > 90 ? 'CFO / Recovery approval' : 'Credit monitoring',
        age: `${loan.dpd} DPD`,
        status: loan.status,
        route: loan.dpd > 90 ? 'defaults' as Page : 'loan-accounts/detail' as Page,
        entityId: loan.id,
        source: 'Monitoring SOP',
      })) : [];

    return [...tatItems, ...sanctionItems, ...documentationItems, ...monitoringItems];
  }, [can]);

  const visibleNotifications = notifications.filter(item => filter === 'all' || item.severity === filter);
  const urgentCount = notifications.filter(item => item.severity === 'urgent').length;

  return (
    <div className="p-6 space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Notifications and Alerts Center</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Role-aware operational alerts for {currentUser.name}; alerts are limited to modules available to this role.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 sm:w-80">
          <div className="rounded-lg border border-red-100 bg-red-50 px-4 py-3">
            <p className="text-xs text-red-600">Urgent</p>
            <p className="text-2xl font-bold text-red-700 num">{urgentCount}</p>
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
          Each alert links to its owning workspace and keeps audit/source context visible.
        </div>
        <select value={filter} onChange={e => setFilter(e.target.value as NotificationSeverity | 'all')} className="field-select sm:w-44">
          <option value="all">All severities</option>
          <option value="urgent">Urgent</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50">
          <h2 className="text-sm font-semibold text-slate-900">Alert Queue</h2>
          <p className="text-xs text-slate-500 mt-0.5">Reason, owner, source and next action are shown for audit context.</p>
        </div>

        {visibleNotifications.length === 0 ? (
          <div className="py-12 text-center">
            <Bell size={28} className="mx-auto text-slate-300 mb-3" />
            <p className="text-sm font-semibold text-slate-700">No alerts for this filter</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {visibleNotifications.map(item => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.route, item.entityId)}
                className={`w-full p-4 text-left transition-colors hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500 ${
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
                        <StatusBadge label={item.status} size="sm" />
                      </div>
                      <p className="text-sm text-slate-600 mt-1">{item.message}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2 lg:w-[430px]">
                    <div className="rounded-lg bg-white/80 border border-slate-100 px-3 py-2">
                      <p className="text-[11px] text-slate-400">Owner</p>
                      <p className="text-xs font-medium text-slate-700 truncate">{item.owner}</p>
                    </div>
                    <div className="rounded-lg bg-white/80 border border-slate-100 px-3 py-2">
                      <p className="text-[11px] text-slate-400">Age</p>
                      <p className="text-xs font-medium text-slate-700 flex items-center gap-1"><Clock size={11} /> {item.age}</p>
                    </div>
                    <div className="rounded-lg bg-white/80 border border-slate-100 px-3 py-2">
                      <p className="text-[11px] text-slate-400">Source</p>
                      <p className="text-xs font-medium text-slate-700 truncate">{item.source}</p>
                    </div>
                  </div>
                  <ArrowRight size={16} className="hidden lg:block text-slate-300 flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationsCenter;
