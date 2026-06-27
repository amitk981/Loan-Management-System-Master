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
import { dashboardStats, loanApplications, loanAccounts, auditEvents } from '../data/mockData';
import { useRole, ROLE_LABELS } from '../contexts/RoleContext';
import type { Page } from '../App';
import { getApplicationReference } from '../utils/applicationDisplay';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface DashboardProps {
  onNavigate: (page: Page, id?: string) => void;
}

// ─── Role-specific KPI card sets ─────────────────────────────────────────────

const CreditManagerCards: React.FC<{ onNavigate: (p: Page) => void, readyToDisburse: number }> = ({ onNavigate, readyToDisburse }) => (
  <>
    <div>
      <h2 className="section-title mb-3">Application Pipeline</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <KPICard title="New Applications" value={String(dashboardStats.newApplications)} subtitle="last 7 days" icon={FileText} trend="up" onClick={() => onNavigate('applications')} />
        <KPICard title="Completeness Check" value={String(dashboardStats.pendingCompleteness)} subtitle="DM Finance review" icon={CheckCircle2} highlight={dashboardStats.pendingCompleteness > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('completeness')} />
        <KPICard title="Appraisal Review" value={String(dashboardStats.pendingAppraisal)} subtitle="Credit Manager action" icon={Scale} highlight={dashboardStats.pendingAppraisal > 2 ? 'warning' : 'normal'} onClick={() => onNavigate('appraisal')} />
        <KPICard title="Pending Sanction Committee" value={String(dashboardStats.pendingSanction)} subtitle="approval queue" icon={Gavel} highlight="warning" onClick={() => onNavigate('sanction')} />
        <KPICard title="Documentation" value={String(dashboardStats.documentationPending)} subtitle="in progress" icon={FolderOpen} onClick={() => onNavigate('documentation')} />
        <KPICard title="Disbursement Queue" value={String(readyToDisburse)} subtitle="finance action" icon={Banknote} highlight={readyToDisburse > 0 ? 'success' : 'normal'} onClick={() => onNavigate('disbursement')} />
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

const FieldOfficerCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Field Officer — Assisted Intake</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Draft Applications" value="1" subtitle="field-assisted intake" icon={ClipboardList} highlight="warning" onClick={() => onNavigate('applications')} />
      <KPICard title="Member Details Pending" value="3" subtitle="folio / KYC details to collect" icon={UserCheck} onClick={() => onNavigate('members')} />
      <KPICard title="Documents to Collect" value="4" subtitle="borrower upload support" icon={FileCheck} highlight="warning" onClick={() => onNavigate('applications')} />
      <KPICard title="Submitted Today" value="0" subtitle="ready for finance review" icon={CheckCircle2} onClick={() => onNavigate('applications')} />
    </div>
    <div className="card border-amber-200 bg-amber-50 mt-4">
      <div className="flex items-center gap-3">
        <Shield size={18} className="text-amber-600 flex-shrink-0" />
        <div>
          <p className="text-sm font-semibold text-amber-900">Intake-only role</p>
          <p className="text-xs text-amber-700 mt-0.5">Field Officers can assist with drafts and document collection, but cannot approve sanctions, appraisal outcomes, disbursement, recovery or closure.</p>
        </div>
      </div>
    </div>
  </div>
);

const DeputyManagerCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">My Workload — Completeness & Appraisal</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Completeness Check" value={String(dashboardStats.pendingCompleteness)} subtitle="applications to review" icon={ClipboardList} highlight={dashboardStats.pendingCompleteness > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('applications')} />
      <KPICard title="Appraisal Notes" value={String(dashboardStats.pendingAppraisal)} subtitle="to prepare" icon={Scale} highlight={dashboardStats.pendingAppraisal > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('appraisal')} />
      <KPICard title="Application Docs Pending" value={String(dashboardStats.documentationPending)} subtitle="deficiencies pending" icon={FolderOpen} onClick={() => onNavigate('documentation')} />
      <KPICard title="Returned for Correction" value="0" subtitle="returned appraisals" icon={RefreshCw} onClick={() => onNavigate('applications')} />
    </div>
  </div>
);

const ComplianceTeamCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Documentation Workspace</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Docs In Preparation" value={String(dashboardStats.documentationPending)} subtitle="active files" icon={FolderOpen} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="Stamp / Notary Pending" value="3" subtitle="legal execution" icon={Shield} highlight="warning" onClick={() => onNavigate('documentation')} />
      <KPICard title="KYC / Re-KYC Exceptions" value={String(dashboardStats.reKycDue)} subtitle="pending items" icon={UserCheck} highlight={dashboardStats.reKycDue > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('compliance')} />
      <KPICard title="Docs Cleared for CS / Finance" value={String(dashboardStats.readyForDisbursement)} subtitle="handoff ready" icon={BadgeCheck} highlight={dashboardStats.readyForDisbursement > 0 ? 'success' : 'normal'} onClick={() => onNavigate('documentation')} />
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
      <KPICard title="Legal Compliance Review" value="2" subtitle="upcoming deadlines" icon={ShieldAlert} onClick={() => onNavigate('compliance')} />
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
      <KPICard title="Rejected — Communication Pending" value="1" subtitle="rejection note to send" icon={FileText} highlight="warning" onClick={() => onNavigate('applications')} />
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
      <KPICard title="My CFO Votes Pending" value={String(dashboardStats.pendingSanction)} subtitle="await CFO decision" icon={Gavel} onClick={() => onNavigate('sanction')} />
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
      <KPICard title="SAP Code Confirmation" value="1" subtitle="code created; to confirm" icon={BadgeCheck} highlight="warning" onClick={() => onNavigate('disbursement')} />
      <KPICard title="Ready for Payment" value={String(dashboardStats.readyForDisbursement)} subtitle="payment package pending" icon={Banknote} highlight={dashboardStats.readyForDisbursement > 0 ? 'success' : 'normal'} onClick={() => onNavigate('disbursement')} />
      <KPICard title="Failed Bank Transfers" value="0" subtitle="last 30 days" icon={AlertTriangle} highlight="normal" onClick={() => onNavigate('disbursement')} />
    </div>
  </div>
);

const CFCCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Chief Financial Controller — Payment Authorisation</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Bank Transfers Pending" value={String(dashboardStats.readyForDisbursement)} subtitle="awaiting CFC authorisation" icon={BadgeCheck} highlight={dashboardStats.readyForDisbursement > 0 ? 'danger' : 'normal'} onClick={() => onNavigate('cfc')} />
      <KPICard title="High-Value Payments" value="1" subtitle="above ₹5 lakh" icon={AlertTriangle} highlight="warning" onClick={() => onNavigate('cfc')} />
      <KPICard title="Returned Requests" value="0" subtitle="returned to Senior Manager – Finance" icon={TrendingDown} onClick={() => onNavigate('cfc')} />
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

const SalesTeamCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Sales Team — Interest Invoice Support</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Invoices to Prepare" value="18" subtitle="borrower follow-up pending" icon={FileText} highlight="warning" onClick={() => onNavigate('interest')} />
      <KPICard title="Subsidiary Deduction Checks" value="6" subtitle="repayment linkage checks" icon={Receipt} onClick={() => onNavigate('loan-accounts')} />
      <KPICard title="Invoice Register: Open" value="View" subtitle="statutory evidence" icon={Book} onClick={() => onNavigate('registers')} />
      <KPICard title="MIS Extract Ready" value="Yes" subtitle="accounts coordination" icon={BarChart3} onClick={() => onNavigate('reports')} />
    </div>
  </div>
);

const AuditorCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Internal Auditor — Read-Only Access</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Active Loans" value={String(dashboardStats.activeLoans)} subtitle="portfolio records" icon={BarChart3} onClick={() => onNavigate('loan-accounts')} />
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
      <KPICard title="Policy Configs" value="Up to Date" subtitle="workflow & settings" icon={Settings} highlight="success" onClick={() => onNavigate('settings')} />
      <KPICard title="Approval Matrix" value="2" subtitle="pending changes" icon={ShieldAlert} highlight="warning" onClick={() => onNavigate('settings')} />
    </div>
  </div>
);

const DirectorCards: React.FC<{ onNavigate: (p: Page) => void }> = ({ onNavigate }) => (
  <div>
    <h2 className="section-title mb-3">Director — Sanction Committee</h2>
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <KPICard title="Cases Awaiting Vote" value={String(dashboardStats.pendingSanction)} subtitle="my vote pending" icon={Gavel} highlight={dashboardStats.pendingSanction > 0 ? 'warning' : 'normal'} onClick={() => onNavigate('sanction')} />
      <KPICard title="Above ₹5 Lakh" value="2" subtitle="CFO + 2 Directors" icon={AlertTriangle} highlight="danger" onClick={() => onNavigate('sanction')} />
      <KPICard title="Director / Relative Cases" value="1" subtitle="special case approval" icon={ShieldAlert} highlight="warning" onClick={() => onNavigate('sanction')} />
      <KPICard title="Rejected — Communication Pending" value="1" subtitle="pending communication" icon={FileText} onClick={() => onNavigate('applications')} />
    </div>
  </div>
);

// ─── Main Dashboard ───────────────────────────────────────────────────────────

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { currentUser, can } = useRole();

  const urgentApps = currentUser.role === 'admin'
    ? [
        { id: 'admin1', applicationNumber: 'Approval matrix change pending', memberName: 'Configuration' },
        { id: 'admin2', applicationNumber: 'Inactive user access review due', memberName: 'Security' }
      ] as any[]
    : loanApplications.filter(a => {
    if ((a.tatDaysRemaining ?? 99) > 1) return false;
    if (currentUser.role === 'deputy_manager_finance' || currentUser.role === 'compliance_team' || currentUser.role === 'company_secretary' || currentUser.role === 'sanction_committee' || currentUser.role === 'cfo' || currentUser.role === 'director' || currentUser.role === 'senior_manager_finance' || currentUser.role === 'cfc' || currentUser.role === 'accounts' || currentUser.role === 'sales_team') {
      return a.currentOwnerRole === currentUser.role;
    }
    return true; // auditor gets all exceptions for review
  });
  const overdueLoans = loanAccounts.filter(l => l.status === 'overdue' || l.status === 'grace_period');
  const docBlockers = loanApplications.filter(a =>
    ['in_progress', 'documentation_in_progress', 'documentation_deficiency_raised', 'pending_signature'].includes(a.documentationStatus)
  );
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening';

  const myTasks = currentUser.role === 'admin'
    ? [
        { id: 'admin1', applicationNumber: 'SYS-001', memberName: 'Role permission review due', status: 'pending', loanAmount: 0 },
        { id: 'admin2', applicationNumber: 'SYS-002', memberName: 'Approval matrix update pending', status: 'pending', loanAmount: 0 }
      ] as any[]
    : currentUser.role === 'field_officer'
    ? [
        { id: 'f1', applicationNumber: 'LO00000042', memberName: 'Ramesh Patil', rightStatus: 'Borrower follow-up due', statusBadge: 'Docs Pending', amount: 450000 },
        { id: 'f2', applicationNumber: 'LO00000043', memberName: 'Sunita Bhosale', rightStatus: 'TAT due', statusBadge: 'KYC Upload', amount: 350000, isTatDue: true },
        { id: 'f3', applicationNumber: 'LO00000044', memberName: 'Kisan Samruddhi FPC Ltd.', rightStatus: 'Collect details', statusBadge: 'Nominee / witness pending', amount: 800000 },
        { id: 'f4', applicationNumber: 'APP-INT-2026-000003', memberName: 'Vijay Deshmukh', rightStatus: 'Finance review · Read-only', statusBadge: 'Submitted', amount: 200000 },
      ] as any[]
    : currentUser.role === 'auditor'
    ? loanApplications.slice(0, 4)
    : (currentUser.role === 'credit_manager' || currentUser.role === 'deputy_manager_finance' || currentUser.role === 'compliance_team' || currentUser.role === 'company_secretary' || currentUser.role === 'sanction_committee' || currentUser.role === 'cfo' || currentUser.role === 'director' || currentUser.role === 'senior_manager_finance' || currentUser.role === 'cfc' || currentUser.role === 'accounts' || currentUser.role === 'sales_team')
    ? loanApplications.filter(app => app.currentOwnerRole === currentUser.role)
    : loanApplications.slice(0, 4);

  const safeReadyToDisburseCount = loanApplications.filter(a => 
    a.documentationStatus === 'complete' && 
    a.sapCustomerCode && 
    a.bankAccount &&
    !a.isException &&
    ['sanctioned', 'disbursement_ready', 'sap_customer_code_confirmed', 'payment_initiated'].includes(a.status)
  ).length;

  const renderRoleCards = () => {
    switch (currentUser.role) {
      case 'field_officer':      return <FieldOfficerCards onNavigate={onNavigate} />;
      case 'credit_manager':     return <CreditManagerCards onNavigate={onNavigate} readyToDisburse={safeReadyToDisburseCount} />;
      case 'deputy_manager_finance': return <DeputyManagerCards onNavigate={onNavigate} />;
      case 'compliance_team':    return <ComplianceTeamCards onNavigate={onNavigate} />;
      case 'company_secretary':  return <CompanySecretaryCards onNavigate={onNavigate} />;
      case 'sanction_committee': return <SanctionCommitteeCards onNavigate={onNavigate} />;
      case 'cfo':                return <CFOCards onNavigate={onNavigate} />;
      case 'director':           return <DirectorCards onNavigate={onNavigate} />;
      case 'senior_manager_finance': return <SMFinanceCards onNavigate={onNavigate} />;
      case 'cfc':                return <CFCCards onNavigate={onNavigate} />;
      case 'accounts':           return <AccountsCards onNavigate={onNavigate} />;
      case 'sales_team_user':    return <SalesTeamCards onNavigate={onNavigate} />;
      case 'auditor':            return <AuditorCards onNavigate={onNavigate} />;
      case 'admin':              return <AdminCards onNavigate={onNavigate} />;
      default:                   return <CreditManagerCards onNavigate={onNavigate} readyToDisburse={safeReadyToDisburseCount} />;
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
        {currentUser.role === 'credit_manager' ? (
          <div className="sm:text-right rounded-lg border border-red-100 bg-red-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-red-600 font-medium">DPD attention</p>
            <p className="text-2xl font-bold text-red-700 num leading-tight">{dashboardStats.overdueLoans}</p>
            <p className="text-xs text-red-600">overdue loans</p>
          </div>
        ) : currentUser.role === 'deputy_manager_finance' ? (
          <div className="sm:text-right rounded-lg border border-amber-100 bg-amber-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-amber-600 font-medium">Appraisal drafts</p>
            <p className="text-2xl font-bold text-amber-700 num leading-tight">{dashboardStats.pendingAppraisal}</p>
            <p className="text-xs text-amber-600">to prepare</p>
          </div>
        ) : currentUser.role === 'compliance_team' ? (
          <div className="sm:text-right rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-indigo-600 font-medium">Stamp / Notary pending</p>
            <p className="text-2xl font-bold text-indigo-700 num leading-tight">3</p>
            <p className="text-xs text-indigo-600">items</p>
          </div>
        ) : currentUser.role === 'company_secretary' ? null : currentUser.role === 'sanction_committee' ? (
          <div className="sm:text-right rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-blue-600 font-medium">My decisions pending</p>
            <p className="text-2xl font-bold text-blue-700 num leading-tight">{dashboardStats.pendingSanction}</p>
            <p className="text-xs text-blue-600">awaiting vote</p>
          </div>
        ) : currentUser.role === 'cfo' ? (
          <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-slate-500 font-medium">CFO approvals pending</p>
            <p className="text-2xl font-bold text-slate-900 num leading-tight">2</p>
            <p className="text-xs text-slate-500">awaiting vote</p>
          </div>
        ) : currentUser.role === 'director' ? (
          <div className="sm:text-right rounded-lg border border-purple-100 bg-purple-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-purple-600 font-medium">My votes pending</p>
            <p className="text-2xl font-bold text-purple-700 num leading-tight">{dashboardStats.pendingSanction}</p>
            <p className="text-xs text-purple-600">awaiting decision</p>
          </div>
        ) : currentUser.role === 'senior_manager_finance' ? (
          <div className="sm:text-right rounded-lg border border-teal-100 bg-teal-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-teal-600 font-medium">SAP pending</p>
            <p className="text-2xl font-bold text-teal-700 num leading-tight">2</p>
            <p className="text-xs text-teal-600">requests</p>
          </div>
        ) : currentUser.role === 'cfc' ? (
          <div className="sm:text-right rounded-lg border border-teal-100 bg-teal-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-teal-600 font-medium">Payment queue</p>
            <p className="text-2xl font-bold text-teal-700 num leading-tight">1</p>
            <p className="text-xs text-teal-600">pending authorisation</p>
          </div>
        ) : currentUser.role === 'accounts' ? (
          <div className="sm:text-right rounded-lg border border-orange-100 bg-orange-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-orange-600 font-medium">Posting queue</p>
            <p className="text-2xl font-bold text-orange-700 num leading-tight">3</p>
            <p className="text-xs text-orange-600">pending</p>
          </div>
        ) : currentUser.role === 'sales_team' ? (
          <div className="sm:text-right rounded-lg border border-sky-100 bg-sky-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-sky-600 font-medium">Invoices pending</p>
            <p className="text-2xl font-bold text-sky-700 num leading-tight">18</p>
            <p className="text-xs text-sky-600">support actions</p>
          </div>
        ) : currentUser.role === 'auditor' ? (
          <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-slate-500 font-medium">Audit events</p>
            <p className="text-2xl font-bold text-slate-900 num leading-tight">142</p>
            <p className="text-xs text-slate-500">in 30d</p>
          </div>
        ) : currentUser.role === 'admin' ? (
          <div className="sm:text-right rounded-lg border border-indigo-100 bg-indigo-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-indigo-600 font-medium">System status</p>
            <p className="text-2xl font-bold text-indigo-700 num leading-tight">Active</p>
            <p className="text-xs text-indigo-600">all systems operational</p>
          </div>
        ) : currentUser.role === 'field_officer' ? (
          <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-slate-500 font-medium">Assigned intake</p>
            <p className="text-2xl font-bold text-slate-900 num leading-tight">8</p>
            <p className="text-xs text-slate-500">open items</p>
          </div>
        ) : (
          <div className="sm:text-right rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 flex-shrink-0">
            <p className="text-xs text-slate-500">Section 186 utilisation</p>
            <p className="text-2xl font-bold text-slate-900 num leading-tight">{dashboardStats.sectionUtilisation}%</p>
            <p className="text-xs text-slate-500">of lending limit</p>
          </div>
        )}
      </div>

      {/* Alerts */}
      {dashboardStats.openExceptions > 0 && (
        <AlertBanner
          type="exception"
          title={
            currentUser.role === 'company_secretary'
              ? `${dashboardStats.openExceptions} exception${dashboardStats.openExceptions > 1 ? 's' : ''} awaiting CFO + Director approval.`
              : currentUser.role === 'sales_team'
              ? `${dashboardStats.openExceptions} case${dashboardStats.openExceptions > 1 ? 's' : ''} blocked for approval.`
              : currentUser.role === 'admin'
              ? `${dashboardStats.openExceptions} approval exception${dashboardStats.openExceptions > 1 ? 's' : ''} visible in system.`
              : currentUser.role === 'auditor'
              ? `${dashboardStats.openExceptions} exception${dashboardStats.openExceptions > 1 ? 's' : ''} awaiting CFO + Director approval.`
              : currentUser.role === 'field_officer'
              ? `${dashboardStats.openExceptions} assigned application${dashboardStats.openExceptions > 1 ? 's' : ''} have open exceptions.`
              : (currentUser.role === 'sanction_committee' || currentUser.role === 'cfo' || currentUser.role === 'director')
              ? `${dashboardStats.openExceptions} exception${dashboardStats.openExceptions > 1 ? 's' : ''} awaiting escalated approval.`
              : (currentUser.role === 'credit_manager' || currentUser.role === 'deputy_manager_finance' || currentUser.role === 'compliance_team' || currentUser.role === 'senior_manager_finance' || currentUser.role === 'cfc' || currentUser.role === 'accounts')
              ? `${dashboardStats.openExceptions} open exception${dashboardStats.openExceptions > 1 ? 's' : ''} awaiting CFO + Director approval.`
              : `${dashboardStats.openExceptions} open exception${dashboardStats.openExceptions > 1 ? 's' : ''} require CFO + Director review`
          }
          message={
            currentUser.role === 'credit_manager'
              ? "Credit Manager can view, prepare and route. Approval remains with CFO / Director."
              : currentUser.role === 'deputy_manager_finance'
              ? "Deputy Manager – Finance can view or prepare inputs. Approval remains with CFO / Director."
              : currentUser.role === 'compliance_team'
              ? "Compliance Team can prepare evidence and update register inputs. Approval remains with CFO / Director."
              : currentUser.role === 'company_secretary'
              ? "Exception Register update required before disbursement."
              : currentUser.role === 'senior_manager_finance'
              ? "Payment remains blocked until exception register is cleared."
              : currentUser.role === 'cfc'
              ? "Payment authorisation is blocked until exception register is cleared."
              : currentUser.role === 'accounts'
              ? "Accounting and disbursement actions remain blocked until exception register is cleared."
              : currentUser.role === 'sales_team'
              ? "No sales action until approval is complete."
              : currentUser.role === 'admin'
              ? "No administrator action required."
              : currentUser.role === 'auditor'
              ? "Available for audit review. No auditor action required."
              : currentUser.role === 'field_officer'
              ? "CFO / Director review pending. Intake is read-only until resolved."
              : (currentUser.role === 'sanction_committee' || currentUser.role === 'cfo' || currentUser.role === 'director')
              ? "Exception cases require escalated matrix (CFO + 2 Directors) and Register update."
              : "Exception register entries pending approval. Disbursement blocked until resolved."
          }
          actions={
            <button onClick={() => onNavigate(currentUser.role === 'field_officer' ? 'applications' : 'compliance')} className="text-xs font-semibold underline">
              {currentUser.role === 'field_officer' ? 'View assigned applications' : 'View exception register'}
            </button>
          }
        />
      )}
      {urgentApps.length > 0 && (
        <AlertBanner
          type="warning"
          title={currentUser.role === 'compliance_team' 
            ? `${urgentApps.length} documentation item${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'company_secretary'
            ? `${urgentApps.length} legal item${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'sanction_committee'
            ? `${urgentApps.length} sanction decision${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'cfo'
            ? `${urgentApps.length} CFO decision${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'director'
            ? `${urgentApps.length} director decision${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'senior_manager_finance'
            ? `${urgentApps.length} finance item${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'cfc'
            ? `${urgentApps.length} payment authorisation${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'accounts'
            ? `${urgentApps.length} accounting item${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'sales_team'
            ? `${urgentApps.length} invoice follow-up${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : currentUser.role === 'auditor'
            ? `${urgentApps.length} TAT exception${urgentApps.length > 1 ? 's' : ''} available for review`
            : currentUser.role === 'admin'
            ? `${urgentApps.length} system configuration item${urgentApps.length > 1 ? 's' : ''} need review`
            : currentUser.role === 'field_officer'
            ? `${urgentApps.length} intake follow-up${urgentApps.length > 1 ? 's' : ''} at TAT deadline`
            : `${urgentApps.length} application${urgentApps.length > 1 ? 's' : ''} at TAT deadline`}
          message={
            currentUser.role === 'field_officer'
              ? 'LO00000042: borrower documents pending · LO00000043: KYC upload pending'
              : urgentApps.map(a => `${getApplicationReference(a)} (${a.memberName})`).join(' · ')
          }
        />
      )}

      {/* Role-specific KPI rows */}
      {renderRoleCards()}

      {/* Task queue + Overdue side by side */}
      <div className={`grid grid-cols-1 gap-6 ${currentUser.role === 'credit_manager' ? 'lg:grid-cols-3' : 'lg:grid-cols-2'}`}>
        {/* My Task Queue */}
        <div className="card bg-white h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-title">
              {currentUser.role === 'auditor' ? 'Audit Review Queue' : currentUser.role === 'admin' ? 'Admin Task Queue' : currentUser.role === 'field_officer' ? 'My Intake Queue' : 'My Task Queue'}
            </h2>
            <button onClick={() => onNavigate('tasks')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="space-y-2 flex-1">
            {myTasks.length === 0 ? (
              <div className="py-8 text-center text-slate-400 text-sm">
                <CheckCircle2 size={20} className="mx-auto mb-2 text-green-400" />
                No pending tasks for your role.
              </div>
            ) : (
              myTasks.slice(0, 4).map(app => (
                <button
                  key={app.id}
                  onClick={() => onNavigate('applications/detail', app.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-slate-900 num">{'applicationNumber' in app && 'status' in app ? getApplicationReference(app as any) : app.applicationNumber}</span>
                      {app.isException && (
                        <span className="text-xs bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded font-medium">Exception</span>
                      )}
                      {app.specialCase && (
                        <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-medium">Special Case</span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 truncate">
                      {app.memberName}{currentUser.role !== 'admin' && ` · ${fmt(app.loanAmount || app.requestedAmount || app.amount || 0)}`}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    {currentUser.role === 'auditor' ? (
                      <span className="text-xs font-semibold text-amber-600">audit review pending</span>
                    ) : currentUser.role === 'admin' ? (
                      <span className="text-xs font-semibold text-amber-600">system review pending</span>
                    ) : currentUser.role === 'field_officer' ? (
                      <>
                        <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium border border-slate-200">{app.statusBadge}</span>
                        <span className={`text-xs font-semibold ${app.isTatDue ? 'text-red-600 flex items-center gap-0.5' : 'text-slate-500'}`}>
                          {app.isTatDue && <Clock size={10} />}
                          {app.rightStatus}
                        </span>
                      </>
                    ) : (
                      <StatusBadge label={app.status} size="sm" />
                    )}
                    {currentUser.role !== 'field_officer' && (app.tatDaysRemaining ?? 99) <= 1 && (
                      <span className="text-xs text-red-600 flex items-center gap-0.5">
                        <Clock size={10} /> TAT due
                      </span>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Overdue / At-risk loans or Doc Blockers */}
        {currentUser.role === 'compliance_team' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title">Documentation Blockers</h2>
              <button onClick={() => onNavigate('documentation')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                Workspace <ArrowRight size={12} />
              </button>
            </div>
            {docBlockers.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No blockers
              </div>
            ) : (
              <div className="space-y-2">
                {docBlockers.map(app => (
                  <button
                    key={app.id}
                    onClick={() => onNavigate('documentation')}
                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-slate-900 num">{getApplicationReference(app)}</div>
                      <div className="text-xs text-slate-500">{app.memberName}</div>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <StatusBadge label={app.documentationStatus} size="sm" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'company_secretary' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title">Recovery / Security Legal Watch</h2>
              <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                Monitoring <ArrowRight size={12} />
              </button>
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No items on watch
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
                        {loan.dpd > 90 ? 'Legal notice pending' : 'Recovery review pending'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (currentUser.role === 'sanction_committee' || currentUser.role === 'director') ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title">Decision Risk Watch</h2>
              {currentUser.role !== 'director' && (
                <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                  Monitoring <ArrowRight size={12} />
                </button>
              )}
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No high-risk items
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
                        {loan.dpd > 90 ? 'High DPD history' : 'Overdue exposure'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'cfo' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Overdue & At-Risk Loans</h2>
                <p className="text-xs text-slate-500 mt-0.5">Oversight and recovery approvals</p>
              </div>
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
                        DPD: {loan.dpd} · {loan.dpd > 90 ? 'CFO recovery approval req.' : 'Risk monitoring'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (currentUser.role === 'senior_manager_finance' || currentUser.role === 'cfc') ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">{currentUser.role === 'cfc' ? 'Payment Risk Holds' : 'Finance Risk Holds'}</h2>
                <p className="text-xs text-slate-500 mt-0.5">Read-only portfolio context</p>
              </div>
              <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                Monitoring <ArrowRight size={12} />
              </button>
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No {currentUser.role === 'cfc' ? 'payment' : 'finance'} holds
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
                        {loan.dpd > 90 ? 'Failed transfer hold' : 'Recovery payment pending'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'accounts' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Repayment & DPD Watch</h2>
                <p className="text-xs text-slate-500 mt-0.5">DPD tracking and posting status</p>
              </div>
              <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                Monitoring <ArrowRight size={12} />
              </button>
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No overdue items
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
                        DPD: {loan.dpd} · {loan.dpd > 90 ? 'Demand notice support' : 'Posting pending'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'sales_team' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Borrower Follow-up Watch</h2>
                <p className="text-xs text-slate-500 mt-0.5">Invoice and repayment support</p>
              </div>
              <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                Monitoring <ArrowRight size={12} />
              </button>
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No follow-ups needed
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
                        {loan.dpd > 90 ? 'DPD: ' + loan.dpd + ' · Contact pending' : 'Invoice confirmation pending'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'auditor' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Risk & Exception Snapshot</h2>
                <p className="text-xs text-slate-500 mt-0.5">Read-only portfolio context</p>
              </div>
              <button onClick={() => onNavigate('monitoring')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                View risk records <ArrowRight size={12} />
              </button>
            </div>
            {overdueLoans.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No risk records
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
                        {loan.dpd > 90 ? 'High risk review' : 'Account review'}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : currentUser.role === 'admin' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Access & Security Review</h2>
                <p className="text-xs text-slate-500 mt-0.5">System audit snapshot</p>
              </div>
              <button onClick={() => onNavigate('settings')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                View audit logs <ArrowRight size={12} />
              </button>
            </div>
            <div className="space-y-2">
              {[
                { id: 'a1', ref: 'SEC-044', title: 'Failed login attempt', type: 'locked account', status: 'warning' },
                { id: 'a2', ref: 'SEC-045', title: 'Approval matrix update', type: 'config change', status: 'success' },
                { id: 'a3', ref: 'SEC-046', title: 'Audit export request', type: 'export request', status: 'pending' },
              ].map(event => (
                <button
                  key={event.id}
                  onClick={() => onNavigate('settings')}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-slate-900 num">{event.ref}</div>
                    <div className="text-xs text-slate-500">{event.title}</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <StatusBadge label={event.type.replace(' ', '_')} size="sm" />
                    <span className={`text-xs font-semibold ${event.status === 'warning' ? 'text-red-600' : event.status === 'success' ? 'text-green-600' : 'text-amber-600'}`}>
                      {event.status === 'warning' ? 'Review required' : 'Processed'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : currentUser.role === 'field_officer' ? (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Assigned Borrower Follow-ups</h2>
                <p className="text-xs text-slate-500 mt-0.5">Intake support</p>
              </div>
              <button onClick={() => onNavigate('applications')} className="text-xs text-green-600 flex items-center gap-1 hover:underline">
                View follow-ups <ArrowRight size={12} />
              </button>
            </div>
            <div className="space-y-2">
              {[
                { id: 'fo1', accountNumber: 'LO00000042', memberName: 'Ramesh Patil', subtext: 'Witness PAN / Aadhaar pending', status: 'Document follow-up', rightText: 'Due today', isDue: false },
                { id: 'fo2', accountNumber: 'LO00000043', memberName: 'Sunita Bhosale', subtext: 'Borrower upload support required', status: 'KYC upload', rightText: 'TAT due', isDue: true },
              ].map(loan => (
                <button
                  key={loan.id}
                  onClick={() => onNavigate('applications/detail', loan.id)}
                  className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-slate-50 transition-colors text-left border border-transparent hover:border-slate-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-slate-900 num">{loan.accountNumber}</div>
                    <div className="text-xs text-slate-500">{loan.memberName} · {loan.subtext}</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium border border-slate-200">{loan.status}</span>
                    <span className={`text-xs font-semibold ${loan.isDue ? 'text-red-600' : 'text-amber-600'}`}>
                      {loan.rightText}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-title">Overdue & At-Risk Loans</h2>
                {currentUser.role === 'deputy_manager_finance' && (
                  <p className="text-xs text-slate-500 mt-0.5">Read-only portfolio context</p>
                )}
              </div>
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
        )}

        {/* Recent Activity Card - Credit Manager Only */}
        {currentUser.role === 'credit_manager' && (
          <div className="card bg-white">
            <div className="flex items-center justify-between mb-4">
              <h2 className="section-title">Recent Activity</h2>
            </div>
            {auditEvents.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                <CheckCircle2 size={16} className="mr-2 text-green-500" /> No recent activity
              </div>
            ) : (
              <div className="space-y-4">
                {auditEvents.slice(0, 5).map(event => (
                  <div key={event.id} className="flex gap-3 text-sm">
                    <div className="text-green-500 mt-0.5"><CheckCircle2 size={14} /></div>
                    <div>
                      <p className="text-slate-900 font-medium">{event.entityType === 'application' && (() => {
                        const app = loanApplications.find(a => a.id === event.entityId);
                        return app ? getApplicationReference(app) : undefined;
                      })()} {event.eventType.toLowerCase()}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{new Date(event.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })} · {event.actorName}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Section 186 usage bar — show for roles that can view compliance */}
      {can('view_compliance') && currentUser.role !== 'credit_manager' && currentUser.role !== 'deputy_manager_finance' && (
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
