import React from 'react';
import {
  FileText, Users, Scale, Gavel, FolderOpen, Banknote,
  AlertTriangle, TrendingDown, TrendingUp, ShieldAlert, RefreshCw, CheckCircle2,
  ArrowRight, Clock, CreditCard, BarChart3, Receipt, Settings,
  BadgeCheck, Database, Percent, Shield, FileCheck, Book,
  Building2, UserCheck, Bell, Archive, ClipboardList
} from 'lucide-react';
import KPICard from '../components/ui/KPICard';
import StatusBadge from '../components/ui/StatusBadge';
import AlertBanner from '../components/ui/AlertBanner';
import { dashboardStats, loanApplications, loanAccounts } from '../data/mockData';
import { useRole, ROLE_LABELS } from '../contexts/RoleContext';
import type { Page } from '../App';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface DashboardProps {
  onNavigate: (page: Page, id?: string) => void;
}

// ─── Role-specific KPI card sets ─────────────────────────────────────────────

const CreditManagerCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <>
    <div>
      <h2 className="section-title mb-3">Application Pipeline</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard title="New Applications" value={String(dashboardStats.newApplications)} subtitle="last 7 days" icon={FileText} trend="up" onClick={() => onNavigate('applications')} />
        <KPICard title="Completeness Check" value={String(dashboardStats.pendingCompleteness)} subtitle="pending review" icon={CheckCircle2} highlight={dashboardStats.pendingCompleteness > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('applications')} />
        <KPICard title="Pending Appraisal" value={String(dashboardStats.pendingAppraisal)} subtitle="awaiting note" icon={Scale} highlight={dashboardStats.pendingAppraisal > 2 ? 'warning' : 'normal'} onClick={() => onNavigate('appraisal')} />
        <KPICard title="Pending Sanction" value={String(dashboardStats.pendingSanction)} subtitle="at committee" icon={Gavel} highlight="warning" onClick={() => onNavigate('sanction')} />
        <KPICard title="Documentation" value={String(dashboardStats.documentationPending)} subtitle="in progress" icon={FolderOpen} onClick={() => onNavigate('documentation')} />
        <KPICard title="Ready to Disburse" value={String(dashboardStats.readyForDisbursement)} subtitle="cleared for payment" icon={Banknote} highlight={dashboardStats.readyForDisbursement > 0 ? 'success' : 'normal'} onClick={() => onNavigate('disbursement')} />
      </div>
    </div>
    <div>
      <h2 className="section-title mb-3">Portfolio Health</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KPICard title="Active Loans" value={String(dashboardStats.activeLoans)} subtitle={fmt(dashboardStats.totalPortfolio) + ' portfolio'} icon={TrendingUp} onClick={() => onNavigate('loan-accounts')} />
        <KPICard title="Overdue Loans" value={String(dashboardStats.overdueLoans)} subtitle="DPD > 0" icon={TrendingDown} highlight={dashboardStats.overdueLoans > 0 ? 'danger' : 'normal'} trend="up" onClick={() => onNavigate('monitoring')} />
        <KPICard title="Open Exceptions" value={String(dashboardStats.openExceptions)} subtitle="pending Board approval" icon={ShieldAlert} highlight={dashboardStats.openExceptions > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
        <KPICard title="Re-KYC Due" value={String(dashboardStats.reKycDue)} subtitle="members need re-verification" icon={RefreshCw} highlight={dashboardStats.reKycDue > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('members')} />
      </div>
    </div>
  </>
);

const DeputyManagerCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">My Workload — Completeness & Appraisal</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Completeness Check" value={String(dashboardStats.pendingCompleteness)} subtitle="applications to review" icon={ClipboardList} highlight={dashboardStats.pendingCompleteness > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('applications')} />
      <KPICard title="Appraisal Notes" value={String(dashboardStats.pendingAppraisal)} subtitle="to prepare" icon={Scale} highlight={dashboardStats.pendingAppraisal > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('appraisal')} />
      <KPICard title="Docs Pending" value={String(dashboardStats.documentationPending)} subtitle="in preparation" icon={FolderOpen} onClick={() => onNavigate('documentation')} />
      <KPICard title="Active Loans (view)" value={String(dashboardStats.activeLoans)} subtitle="portfolio reference" icon={Banknote} onClick={() => onNavigate('loan-accounts')} />
    </div>
  </div>
);

const ComplianceTeamCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Documentation Workspace</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Docs In Preparation" value={String(dashboardStats.documentationPending)} subtitle="active files" icon={FolderOpen} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="KYC Compliance" value={String(dashboardStats.reKycDue)} subtitle="re-KYC overdue" icon={UserCheck} highlight={dashboardStats.reKycDue > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
      <KPICard title="Open Exceptions" value={String(dashboardStats.openExceptions)} subtitle="requiring attention" icon={ShieldAlert} highlight={dashboardStats.openExceptions > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
      <KPICard title="Ready to Disburse" value={String(dashboardStats.readyForDisbursement)} subtitle="docs complete" icon={BadgeCheck} highlight={dashboardStats.readyForDisbursement > 0 ? 'success' : 'normal'} onClick={() => onNavigate('disbursement')} />
    </div>
  </div>
);

const CompanySecretaryCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Company Secretary — Active Items</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Docs Pending Stamp" value="3" subtitle="stamp duty to record" icon={FileCheck} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="PoA Notarisation" value="1" subtitle="pending notary" icon={Shield} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="SH-4 Custody" value="2" subtitle="physical shares to hold" icon={Archive} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="NOC Pending" value="1" subtitle="closures awaiting NOC" icon={FileCheck} highlight="warning" onClick={() => onNavigate('closure')} />
    </div>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
      <KPICard title="CDSL Pledge" value="2" subtitle="pledge pending confirmation" icon={Database} onClick={() => onNavigate('documentation')} />
      <KPICard title="Security Return" value="1" subtitle="pending security return" icon={BadgeCheck} onClick={() => onNavigate('closure')} />
      <KPICard title="Compliance Review" value="2" subtitle="upcoming deadlines" icon={ShieldAlert} onClick={() => onNavigate('compliance')} />
      <KPICard title="Open Exceptions" value={String(dashboardStats.openExceptions)} subtitle="exception register" icon={AlertTriangle} highlight={dashboardStats.openExceptions > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
    </div>
  </div>
);

const SanctionCommitteeCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Sanction Committee — Pending Decisions</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Cases Awaiting Approval" value={String(dashboardStats.pendingSanction)} subtitle="my vote pending" icon={Gavel} highlight={dashboardStats.pendingSanction > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('sanction')} />
      <KPICard title="Above Rs.5 Lakh" value="2" subtitle="CFO + 2 Directors required" icon={AlertTriangle} highlight="danger" onClick={() => onNavigate('sanction')} />
      <KPICard title="Director / Relative Cases" value="1" subtitle="special case approval" icon={Users} highlight="danger" onClick={() => onNavigate('sanction')} />
      <KPICard title="Rejected – Pending Comm." value="1" subtitle="rejection note to send" icon={FileText} highlight="warning" onClick={() => onNavigate('applications')} />
    </div>
  </div>
);

const CFOCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">CFO — Portfolio & Compliance Overview</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Portfolio Outstanding" value={fmt(dashboardStats.totalPortfolio)} subtitle="total deployed" icon={BarChart3} onClick={() => onNavigate('reports')} />
      <KPICard title="Overdue Loans" value={String(dashboardStats.overdueLoans)} subtitle="DPD > 0" icon={TrendingDown} highlight={dashboardStats.overdueLoans > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('monitoring')} />
      <KPICard title="Open Exceptions" value={String(dashboardStats.openExceptions)} subtitle="my review required" icon={ShieldAlert} highlight={dashboardStats.openExceptions > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
      <KPICard title="Recovery Approvals" value="2" subtitle="pending CFO decision" icon={Scale} highlight="warning" onClick={() => onNavigate('defaults')} />
    </div>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
      <KPICard title="Section 186 Util." value={`${dashboardStats.sectionUtilisation}%`} subtitle="of lending limit used" icon={Percent} highlight={dashboardStats.sectionUtilisation > 80 ? 'danger' : dashboardStats.sectionUtilisation > 60 ? 'warning' : 'normal'} onClick={() => onNavigate('compliance')} />
      <KPICard title="Sanctions Pending" value={String(dashboardStats.pendingSanction)} subtitle="await CFO vote" icon={Gavel} onClick={() => onNavigate('sanction')} />
      <KPICard title="Above Rs.5L Cases" value="2" subtitle="CFO approval required" icon={AlertTriangle} highlight="warning" onClick={() => onNavigate('sanction')} />
      <KPICard title="Quarterly MIS" value="Due Jul 15" subtitle="next CFO MIS deadline" icon={Receipt} highlight="warning" onClick={() => onNavigate('reports')} />
    </div>
  </div>
);

const SMFinanceCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Senior Manager Finance — SAP & Disbursement Queue</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="SAP Code Requests" value="2" subtitle="pending creation" icon={Database} highlight="warning" onClick={() => onNavigate('disbursement')} />
      <KPICard title="SAP Confirmation" value="1" subtitle="code created; to confirm" icon={BadgeCheck} highlight="warning" onClick={() => onNavigate('disbursement')} />
      <KPICard title="Disbursement Ready" value={String(dashboardStats.readyForDisbursement)} subtitle="payment initiation pending" icon={Banknote} highlight={dashboardStats.readyForDisbursement > 0 ? 'success' : 'normal'} onClick={() => onNavigate('disbursement')} />
      <KPICard title="Failed Bank Transfers" value="0" subtitle="last 30 days" icon={AlertTriangle} highlight="normal" onClick={() => onNavigate('disbursement')} />
    </div>
  </div>
);

const CFCCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Chief Financial Controller — Payment Authorisation</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Bank Transfers Pending" value={String(dashboardStats.readyForDisbursement)} subtitle="awaiting CFC auth" icon={BadgeCheck} highlight={dashboardStats.readyForDisbursement > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('cfc')} />
      <KPICard title="High-Value Payments" value="1" subtitle="above Rs.5 lakh" icon={AlertTriangle} highlight="warning" onClick={() => onNavigate('cfc')} />
      <KPICard title="Returned Requests" value="0" subtitle="returned to SM Finance" icon={TrendingDown} onClick={() => onNavigate('cfc')} />
      <KPICard title="Disbursed Today" value="1" subtitle="bank transfer complete" icon={CheckCircle2} highlight="success" onClick={() => onNavigate('loan-accounts')} />
    </div>
  </div>
);

const AccountsCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Accounts — Repayment & Interest Work Queue</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="SAP Postings Pending" value="3" subtitle="repayment SAP entries" icon={Database} highlight="warning" onClick={() => onNavigate('repayments')} />
      <KPICard title="Interest Accrual Due" value="Q2" subtitle="quarterly accrual pending" icon={Percent} highlight="warning" onClick={() => onNavigate('interest')} />
      <KPICard title="Invoices to Generate" value="18" subtitle="year-end interest invoices" icon={FileText} onClick={() => onNavigate('interest')} />
      <KPICard title="Overdue Loans" value={String(dashboardStats.overdueLoans)} subtitle="DPD tracking" icon={TrendingDown} highlight={dashboardStats.overdueLoans > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('monitoring')} />
    </div>
  </div>
);

const AuditorCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Internal Auditor — Read-Only Access</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Active Loans" value={String(dashboardStats.activeLoans)} subtitle={fmt(dashboardStats.totalPortfolio)} icon={BarChart3} onClick={() => onNavigate('loan-accounts')} />
      <KPICard title="Compliance Records" value="8" subtitle="compliance register" icon={ShieldAlert} onClick={() => onNavigate('compliance')} />
      <KPICard title="Open Exceptions" value={String(dashboardStats.openExceptions)} subtitle="exception register" icon={AlertTriangle} highlight={dashboardStats.openExceptions > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('registers')} />
      <KPICard title="Audit Events (30d)" value="142" subtitle="audit log entries" icon={Book} onClick={() => onNavigate('audit')} />
    </div>
  </div>
);

const AdminCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Administrator — System Overview</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Total Users" value="13" subtitle="active system users" icon={Users} onClick={() => onNavigate('settings')} />
      <KPICard title="Active Roles" value="13" subtitle="role configurations" icon={Shield} onClick={() => onNavigate('settings')} />
      <KPICard title="Compliance Records" value="8" subtitle="monitoring items" icon={ShieldAlert} onClick={() => onNavigate('compliance')} />
      <KPICard title="Settings" value="Config" subtitle="policy & approval matrix" icon={Settings} onClick={() => onNavigate('settings')} />
    </div>
  </div>
);

const DirectorCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Director — Sanction Committee</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Cases Awaiting Vote" value={String(dashboardStats.pendingSanction)} subtitle="my vote pending" icon={Gavel} highlight={dashboardStats.pendingSanction > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('sanction')} />
      <KPICard title="Above Rs.5 Lakh" value="2" subtitle="CFO + 2 Directors" icon={AlertTriangle} highlight="danger" onClick={() => onNavigate('sanction')} />
      <KPICard title="Special Cases" value="1" subtitle="director/relative loans" icon={ShieldAlert} highlight="warning" onClick={() => onNavigate('sanction')} />
      <KPICard title="Rejected Cases" value="1" subtitle="pending communication" icon={FileText} onClick={() => onNavigate('applications')} />
    </div>
  </div>
);

// ─── Main Dashboard ───────────────────────────────────────────────────────────

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { currentUser, can } = useRole();

  const urgentApps = loanApplications.filter(a => (a.tatDaysRemaining ?? 99) <= 1);
  const overdueLoans = loanAccounts.filter(l => l.status === 'overdue' || l.status === 'grace_period');
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening';

  const renderRoleCards = () => {
    switch (currentUser.role) {
      case 'credit_manager':     return <CreditManagerCards onNavigate={onNavigate} />;
      case 'deputy_manager_finance': return <DeputyManagerCards onNavigate={onNavigate} />;
      case 'compliance_team':    return <ComplianceTeamCards onNavigate={onNavigate} />;
      case 'company_secretary':  return <CompanySecretaryCards onNavigate={onNavigate} />;
      case 'sanction_committee': return <SanctionCommitteeCards onNavigate={onNavigate} />;
      case 'cfo':                return <CFOCards onNavigate={onNavigate} />;
      case 'director':           return <DirectorCards onNavigate={onNavigate} />;
      case 'senior_manager_finance': return <SMFinanceCards onNavigate={onNavigate} />;
      case 'cfc':                return <CFCCards onNavigate={onNavigate} />;
      case 'accounts':           return <AccountsCards onNavigate={onNavigate} />;
      case 'auditor':            return <AuditorCards onNavigate={onNavigate} />;
      case 'admin':              return <AdminCards onNavigate={onNavigate} />;
      default:                   return <CreditManagerCards onNavigate={onNavigate} />;
    }
  };

  return (
    <div className="p-6 space-y-5 max-w-none">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between px-1">
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-slate-900">{greeting}, {currentUser.name.split(' ')[0]}</h1>
          <p className="text-sm text-slate-500 mt-1">
            SFPCL LMS · {ROLE_LABELS[currentUser.role]} · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
          <p className="text-xs text-slate-500">Section 186 utilisation</p>
          <p className="text-2xl font-bold text-slate-900 num leading-tight">{dashboardStats.sectionUtilisation}%</p>
          <p className="text-xs text-slate-500">of lending limit</p>
        </div>
      </div>

      {/* Alerts */}
      {dashboardStats.openExceptions > 0 && (
        <AlertBanner
          type="exception"
          title={`${dashboardStats.openExceptions} open exception${dashboardStats.openExceptions > 1 ? 's' : ''} require CFO + Director review`}
          message="Exception register entries pending approval. Disbursement blocked until resolved."
          actions={
            <button onClick={() => onNavigate('sanction')} className="text-xs font-semibold underline">
              View exceptions
            </button>
          }
        />
      )}
      {urgentApps.length > 0 && (
        <AlertBanner
          type="warning"
          title={`${urgentApps.length} application${urgentApps.length > 1 ? 's' : ''} at TAT deadline`}
          message={urgentApps.map(a => `${a.applicationNumber} (${a.memberName})`).join(' · ')}
        />
      )}

      {/* Role-specific KPI rows */}
      {renderRoleCards()}

      {/* Task queue + Overdue side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* My Task Queue */}
        <div className="card bg-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">My Task Queue</h2>
            <button onClick={() => onNavigate('tasks')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {loanApplications.slice(0, 4).map(app => (
              <button
                key={app.id}
                onClick={() => onNavigate('applications/detail', app.id)}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-slate-900 num">{app.applicationNumber}</span>
                    {app.isException && (
                      <span className="text-xs bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded font-medium">Exception</span>
                    )}
                    {app.specialCase && (
                      <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-medium">Special Case</span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 truncate">{app.memberName} · {fmt(app.requestedAmount)}</div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <StatusBadge label={app.status} size="sm" />
                  {(app.tatDaysRemaining ?? 99) <= 1 && (
                    <span className="text-xs text-red-600 flex items-center gap-0.5">
                      <Clock size={10} /> TAT due
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
          {loanApplications.length === 0 && (
            <div className="py-8 text-center text-slate-400 text-sm">
              <CheckCircle2 size={20} className="mx-auto mb-2 text-green-400" />
              No pending tasks for your role.
            </div>
          )}
        </div>

        {/* Overdue / At-risk loans */}
        <div className="card bg-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">Overdue & At-Risk Loans</h2>
            <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
              Monitoring <ArrowRight size={12} />
            </button>
          </div>
          {overdueLoans.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
              <CheckCircle2 size={16} className="mr-2 text-green-500" /> No overdue loans
            </div>
          ) : (
            <div className="space-y-2">
              {overdueLoans.map(loan => (
                <button
                  key={loan.id}
                  onClick={() => onNavigate('loan-accounts/detail', loan.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-slate-900 num">{loan.accountNumber}</div>
                    <div className="text-xs text-slate-500">{loan.memberName} · OS: {fmt(loan.outstandingPrincipal)}</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StatusBadge label={loan.status} size="sm" />
                    <span className={`text-xs font-semibold ${loan.dpd > 90 ? 'text-red-600' : 'text-amber-600'}`}>
                      DPD: {loan.dpd}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Section 186 usage bar — show for roles that can view compliance */}
      {can('view_compliance') && (
        <div className="card bg-white">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="section-title">Section 186 — Aggregate Lending Limit</h2>
              <p className="text-xs text-slate-500 mt-0.5">Total portfolio must not exceed 60% of paid-up capital + free reserves</p>
            </div>
            <button onClick={() => onNavigate('compliance')} className="text-xs text-green-600 hover:underline flex items-center gap-1">
              Full compliance report <ArrowRight size={12} />
            </button>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Current utilisation</span>
                <span className="font-semibold text-slate-900">{dashboardStats.sectionUtilisation}%</span>
              </div>
              <div className="bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all ${
                    dashboardStats.sectionUtilisation > 80 ? 'bg-red-500' :
                    dashboardStats.sectionUtilisation > 60 ? 'bg-amber-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${dashboardStats.sectionUtilisation}%` }}
                />
              </div>
              <div className="flex justify-between text-xs mt-1">
                <span className="text-green-700">{fmt(dashboardStats.totalPortfolio)} deployed</span>
                <span className="text-slate-400">Threshold: 60%</span>
              </div>
            </div>
            <div className={`text-xs font-semibold px-3 py-1.5 rounded-full ${
              dashboardStats.sectionUtilisation > 80 ? 'bg-red-100 text-red-700' :
              dashboardStats.sectionUtilisation > 60 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
            }`}>
              {dashboardStats.sectionUtilisation > 80 ? 'Near limit' : dashboardStats.sectionUtilisation > 60 ? 'Caution' : 'Healthy'}
            </div>
          </div>
        </div>
      )}

      {/* Auditor read-only notice */}
      {currentUser.role === 'auditor' && (
        <div className="card border-amber-200 bg-amber-50">
          <div className="flex items-center gap-3">
            <Shield size={18} className="text-amber-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-amber-900">Read-Only Access — Internal Auditor</p>
              <p className="text-xs text-amber-700 mt-0.5">You have view-only access to all records. No create, edit, approve or disburse actions are available.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
