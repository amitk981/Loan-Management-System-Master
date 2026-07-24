import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  Clock,
  FileText,
  Gavel,
  RefreshCw,
  ShieldAlert,
  WalletCards,
} from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import AlertBanner from '../components/ui/AlertBanner';
import { useRole } from '../contexts/RoleContext';
import type { Page } from '../App';
import { AuthSessionError } from '../services/authSession';
import {
  fetchDashboardSummary,
  type DashboardCard,
  type DashboardRoleContext,
  type DashboardSummary,
  type DashboardTask,
} from '../services/dashboardApi';

export type { DashboardSummary } from '../services/dashboardApi';

interface DashboardProps {
  onNavigate: (page: Page, id?: string) => void;
}

type DashboardStatus = 'loading' | 'success' | 'unauthorized' | 'forbidden' | 'error';

interface DashboardSummaryViewProps {
  status: DashboardStatus;
  summary?: DashboardSummary;
  message?: string;
  onNavigate: (page: Page, id?: string) => void;
  onRefresh?: () => void;
}

const ROLE_CONTEXT_LABELS: Record<DashboardRoleContext, string> = {
  credit_manager: 'Credit Manager Dashboard',
  sanction_committee: 'Sanction Committee Dashboard',
  compliance: 'Compliance Dashboard',
  treasury: 'Treasury Dashboard',
  management: 'Management Dashboard',
};

const ROLE_CONTEXT_SUBTITLES: Record<DashboardRoleContext, string> = {
  credit_manager: 'Applications, appraisal, monitoring, and review queues',
  sanction_committee: 'Sanction decisions and approval queues',
  compliance: 'Compliance, documentation, and audit work queues',
  treasury: 'Disbursement, SAP, and payment queues',
  management: 'Portfolio, compliance, and executive summaries',
};

const CARD_ICONS: Record<string, typeof ClipboardList> = {
  applications_pending_completeness: ClipboardList,
  deficiencies_pending: AlertTriangle,
  appraisals_due_today: Clock,
  appraisals_breaching_tat: ShieldAlert,
  credit_manager_review_queue: FileText,
  rejected_applications: AlertTriangle,
  outstanding_beyond_one_year: BarChart3,
  dpd_buckets: BarChart3,
  reminder_queue: Clock,
  default_assessment_queue: ShieldAlert,
  deficiencies_pending_resolution: AlertTriangle,
  appraisals_breaching_two_day_tat: ShieldAlert,
  loans_outstanding_beyond_one_year: BarChart3,
  sanction_cases_pending: Gavel,
  committee_votes_pending: Gavel,
  cases_pending_review: Gavel,
  cases_returned_for_clarification: AlertTriangle,
  exceptions_pending_decision: ShieldAlert,
  sanctions_approved_today: CheckCircle2,
  compliance_tasks_due: ShieldAlert,
  documents_pending_generation: FileText,
  documents_pending_signature: FileText,
  security_items_pending_custody: ShieldAlert,
  section186_items_pending: BarChart3,
  nbfc_tests_due: ShieldAlert,
  sap_requests_pending: WalletCards,
  customer_codes_pending: WalletCards,
  disbursements_pending: WalletCards,
  disbursements_pending_readiness: WalletCards,
  payment_authorisations_pending: WalletCards,
  disbursements_pending_authorisation: WalletCards,
  repayments_pending_allocation: WalletCards,
  interest_invoices_due: FileText,
  portfolio_review_items: BarChart3,
  portfolio_outstanding: BarChart3,
  applications_pipeline: ClipboardList,
  dpd_summary: BarChart3,
  compliance_summary: ShieldAlert,
  approvals_summary: Gavel,
  treasury_summary: WalletCards,
};

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { currentUser } = useRole();
  const [summary, setSummary] = useState<DashboardSummary | undefined>();
  const [status, setStatus] = useState<DashboardStatus>('loading');
  const [message, setMessage] = useState<string | undefined>();
  const [requestVersion, setRequestVersion] = useState(0);
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening';

  useEffect(() => {
    let cancelled = false;
    setStatus('loading');
    setMessage(undefined);

    fetchDashboardSummary()
      .then(data => {
        if (cancelled) return;
        setSummary(data);
        setStatus('success');
      })
      .catch(error => {
        if (cancelled) return;
        setSummary(undefined);
        if (error instanceof AuthSessionError && error.status === 401) {
          setStatus('unauthorized');
          setMessage(error.message);
          return;
        }
        if (error instanceof AuthSessionError && error.status === 403) {
          setStatus('forbidden');
          setMessage(error.message);
          return;
        }
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Dashboard could not be loaded.');
      });

    return () => {
      cancelled = true;
    };
  }, [requestVersion]);

  return (
    <div className="p-6 space-y-5 max-w-none">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between px-1">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-slate-900">{greeting}, {currentUser.name.split(' ')[0]}</h1>
          <p className="text-sm text-slate-500 mt-1">
            SFPCL LMS · {currentUser.roleName} · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        {summary && (
          <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-slate-500 font-medium">Dashboard context</p>
            <p className="text-2xl font-bold text-slate-900 num leading-tight">{summary.cards.length}</p>
            <p className="text-xs text-slate-500">summary cards</p>
          </div>
        )}
      </div>

      <DashboardSummaryView
        status={status}
        summary={summary}
        message={message}
        onNavigate={onNavigate}
        onRefresh={() => setRequestVersion(version => version + 1)}
      />
    </div>
  );
};

export const DashboardSummaryView: React.FC<DashboardSummaryViewProps> = ({
  status,
  summary,
  message,
  onNavigate,
  onRefresh,
}) => {
  if (status === 'loading') {
    return (
      <div className="card bg-white">
        <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
          <Clock size={16} className="mr-2 text-green-500" /> Loading dashboard summary...
        </div>
      </div>
    );
  }

  if (status === 'unauthorized' || status === 'forbidden') {
    return (
      <AlertBanner
        type="error"
        title="Dashboard unavailable"
        message={message || 'You do not have permission to read dashboard summaries.'}
      />
    );
  }

  if (status === 'error' || !summary) {
    return (
      <div>
        <AlertBanner
          type="error"
          title="Dashboard could not be loaded"
          message={message || 'Dashboard could not be loaded.'}
        />
        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            className="btn-secondary mt-3 flex items-center gap-2"
          >
            <RefreshCw size={14} /> Refresh dashboard
          </button>
        )}
      </div>
    );
  }

  const roleTitle = ROLE_CONTEXT_LABELS[summary.role_context];
  const roleSubtitle = ROLE_CONTEXT_SUBTITLES[summary.role_context];

  return (
    <>
      <div>
        <h2 className="section-title mb-3">{roleTitle}</h2>
        <p className="text-xs text-slate-500 mb-3">{roleSubtitle}</p>
        {summary.cards.length === 0 ? (
          <div className="card bg-white">
            <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
              <CheckCircle2 size={16} className="mr-2 text-green-500" /> No dashboard summary cards available
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {summary.cards.map(card => (
              <DashboardKpiCard key={card.code || card.label} card={card} onNavigate={onNavigate} />
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card bg-white h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">My Task Queue</h2>
            <button onClick={() => onNavigate('tasks')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
              View all <ArrowRight size={12} />
            </button>
          </div>
          <DashboardTaskList tasks={summary.tasks} onNavigate={onNavigate} />
        </div>

        <div className="card bg-white">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="section-title">Dashboard Source</h2>
              <p className="text-xs text-slate-500 mt-0.5">Live role-context summary from the backend API</p>
            </div>
          </div>
          <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
            <CheckCircle2 size={16} className="mr-2 text-green-500" /> {summary.role_context.replace('_', ' ')} loaded
          </div>
        </div>
      </div>
    </>
  );
};

const DashboardKpiCard: React.FC<{ card: DashboardCard; onNavigate: (page: Page) => void }> = ({ card, onNavigate }) => {
  const target = pageFromDashboardLink(card.link);
  const Icon = CARD_ICONS[card.code] || ClipboardList;

  return (
    <KPICard
      title={card.label}
      value={String(card.count)}
      subtitle={target ? 'Open workspace' : 'Workspace pending'}
      icon={Icon}
      highlight={card.count > 0 ? 'warning' : 'normal'}
      onClick={target ? () => {
        window.history.pushState({}, '', card.link);
        onNavigate(target);
      } : undefined}
    />
  );
};

const DashboardTaskList: React.FC<{ tasks: DashboardTask[]; onNavigate: (page: Page, id?: string) => void }> = ({
  tasks,
  onNavigate,
}) => {
  if (tasks.length === 0) {
    return (
      <div className="py-8 text-center text-slate-400 text-sm">
        <CheckCircle2 size={20} className="mx-auto mb-2 text-green-400" />
        No pending tasks for your role.
      </div>
    );
  }

  return (
    <div className="space-y-2 flex-1">
      {tasks.slice(0, 4).map(task => (
        <button
          key={`${task.task_type}-${task.entity_id}`}
          onClick={() => onNavigate('tasks', task.entity_id)}
          className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-slate-900 num">{task.title}</span>
            </div>
            <div className="text-xs text-slate-500 truncate">{task.task_type}</div>
          </div>
          {task.due_at && (
            <span className="text-xs text-amber-600 flex items-center gap-0.5">
              <Clock size={10} /> {formatDueDate(task.due_at)}
            </span>
          )}
        </button>
      ))}
    </div>
  );
};

const pageFromDashboardLink = (link: string): Page | null => {
  const path = link.split('?')[0].replace(/\/$/, '');
  if (path === '/applications') return 'applications';
  if (path.startsWith('/applications/')) return 'applications';
  if (path === '/appraisal') return 'appraisal';
  if (path.startsWith('/credit/appraisals')) return 'appraisal';
  if (path.startsWith('/credit/review-queue')) return 'appraisal';
  if (path === '/sanction') return 'sanction';
  if (path === '/sanctions') return 'sanction';
  if (path.startsWith('/sanctions/')) return 'sanction';
  if (path === '/documentation') return 'documentation';
  if (path === '/documents') return 'documentation';
  if (path.startsWith('/documents/')) return 'documentation';
  if (path.startsWith('/security/')) return 'documentation';
  if (path === '/disbursement') return 'disbursement';
  if (path.startsWith('/finance/sap-requests')) return 'disbursement';
  if (path.startsWith('/finance/customer-codes')) return 'disbursement';
  if (path.startsWith('/finance/disbursements')) return 'disbursement';
  if (path.startsWith('/finance/repayments')) return 'repayments';
  if (path.startsWith('/finance/interest-invoices')) return 'interest';
  if (path === '/repayments') return 'repayments';
  if (path === '/interest') return 'interest';
  if (path === '/cfc') return 'cfc';
  if (path === '/loan-accounts') return 'loan-accounts';
  if (path === '/monitoring') return 'monitoring';
  if (path.startsWith('/monitoring/')) return 'monitoring';
  if (path === '/defaults') return 'defaults';
  if (path.startsWith('/defaults/')) return 'defaults';
  if (path.startsWith('/compliance/grievances')) return 'grievances';
  if (path.startsWith('/compliance/archive')) return 'audit';
  if (path === '/compliance') return 'compliance';
  if (path.startsWith('/compliance/')) return 'compliance';
  if (path === '/registers') return 'registers';
  if (path === '/reports') return 'reports';
  if (path.startsWith('/reports/')) return 'reports';
  if (path === '/tasks') return 'tasks';
  return null;
};

const formatDueDate = (dueAt: string): string => {
  const parsed = new Date(dueAt);
  if (Number.isNaN(parsed.getTime())) return dueAt;
  return parsed.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

export default Dashboard;
