import React, { useState } from 'react';
import {
  ChevronLeft, User, Building2, AlertTriangle, CheckCircle2,
  FileText, Shield, CreditCard, Phone, Mail, MapPin,
  Calendar, Banknote, TrendingDown, Clock, RefreshCw,
  Download, MessageSquare, ArrowUpRight, Database,
  History, ShieldAlert, BookOpen, ExternalLink, Eye
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import Tabs from '../../components/ui/Tabs';
import { members, loanApplications, loanAccounts, repayments, currentUser, auditEvents } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface Borrower360Props {
  memberId: string;
  onBack: () => void;
  onOpenApplication?: (id: string) => void;
  onOpenLoanAccount?: (id: string) => void;
}

const communicationsLog = [
  { date: '2026-06-15', type: 'SMS', direction: 'Outbound', message: 'Repayment reminder: ₹1,05,000 due on 30 Jun 2026. Please pay before due date to avoid overdue charges.', sentBy: 'System' },
  { date: '2026-06-01', type: 'Email', direction: 'Outbound', message: 'Loan sanction approval notification with sanction letter attached.', sentBy: 'Priya Kulkarni' },
  { date: '2026-05-22', type: 'Call', direction: 'Inbound', message: 'Borrower called to query about interest calculation. Clarified principal-first allocation.', sentBy: 'Priya Kulkarni' },
  { date: '2026-04-10', type: 'Letter', direction: 'Outbound', message: 'Hard copy of Loan Agreement dispatched by registered post. Tracking: RM123456789IN.', sentBy: 'Aarti Desai' },
];

const riskExceptions = [
  { type: 'Amount Exception', description: 'LO00000042: Requested ₹4,50,000 exceeds eligible limit ₹90,000.', severity: 'high', status: 'pending', date: '2026-06-14', linkedId: 'LO00000042' },
  { type: 'KYC Re-verification', description: 'Annual KYC re-verification due — Borrower needs updated documents', severity: 'medium', status: 'open', date: '2026-06-01' },
];

const Borrower360: React.FC<Borrower360Props> = ({ memberId, onBack, onOpenApplication, onOpenLoanAccount }) => {
  const member = members.find(m => m.id === memberId) || members[0];
  const memberApps = loanApplications.filter(a => a.memberId === member.id);
  const memberLoans = loanAccounts.filter(l => l.memberId === member.id);
  const memberRepayments = repayments.filter(r => memberLoans.some(l => l.id === r.loanAccountId));
  const memberAuditEvents = auditEvents.filter(e => 
    (e.entityType === 'member' && e.entityId === member.id) ||
    (e.entityType === 'application' && memberApps.some(a => a.id === e.entityId)) ||
    (e.entityType === 'loan_account' && memberLoans.some(l => l.id === e.entityId))
  ).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  const [activeTab, setActiveTab] = useState(0);

  const isFPC = member.memberType === 'fpc';
  const totalOutstanding = memberLoans.reduce((s, l) => s + l.outstandingPrincipal, 0);
  const totalAccruedInterest = memberLoans.reduce((s, l) => s + l.accruedInterest, 0);
  const overdueLoan = memberLoans.find(l => l.status === 'overdue');
  const hasOverdue = !!overdueLoan;

  const activeLoansCount = memberLoans.filter(l => ['active', 'overdue', 'grace_period', 'recovery_in_progress'].includes(l.status)).length;
  const overdueLoansCount = memberLoans.filter(l => ['overdue', 'grace_period', 'recovery_in_progress'].includes(l.status)).length;
  const openAppsCount = memberApps.filter(a => !['rejected_credit', 'rejected_by_credit_manager', 'rejected_sanction', 'rejected_by_sanction_committee', 'disbursed', 'closed'].includes(a.status)).length;
  const maxDpd = Math.max(0, ...memberLoans.map(l => l.dpd || 0));

  const kycBadgeText = (member.kycStatus === 'verified' && riskExceptions.some(e => e.type === 'KYC Re-verification' && e.status === 'open'))
    ? 'Verified · Re-KYC due'
    : member.kycStatus === 'rekyc_due' ? 'Re-KYC Due' : member.kycStatus;

  const defaultBadgeText = member.defaultStatus === 'no_default' && maxDpd > 0
    ? `No formal default · DPD ${maxDpd} overdue`
    : member.defaultStatus === 'no_default' ? undefined : (maxDpd > 0 ? `${member.defaultStatus.replace(/_/g, ' ')} · DPD ${maxDpd}` : member.defaultStatus.replace(/_/g, ' '));

  const canAddComm = ['credit_manager', 'accounts', 'sales_support', 'admin', 'field_officer', 'collection_officer'].includes(currentUser.role);
  const canExport = ['credit_manager', 'accounts', 'admin', 'cfo', 'report_viewer'].includes(currentUser.role);
  const canApproveException = ['cfo', 'director', 'sanction_committee', 'admin'].includes(currentUser.role);

  const TABS = [
    { id: 'summary',     label: 'Member Summary' },
    { id: 'applications', label: 'Applications', badge: memberApps.length || undefined },
    { id: 'loans',       label: 'Loan Accounts', badge: activeLoansCount || undefined },
    { id: 'repayments',  label: 'Repayment History' },
    { id: 'security',    label: 'Security Instruments' },
    { id: 'docs',        label: 'Documentation' },
    { id: 'nominee',     label: 'Nominee' },
    { id: 'comms',       label: 'Communications' },
    { id: 'risk',        label: 'Risk & Exceptions', badge: riskExceptions.length || undefined },
    { id: 'audit',       label: 'Audit Trail' },
  ];

  return (
    <div className="p-6 space-y-4">
      {/* Back + Header */}
      <div className="flex items-start gap-3">
        <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700 flex-shrink-0">
          <ChevronLeft size={20} />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${isFPC ? 'bg-blue-100' : 'bg-green-100'}`}>
              {isFPC ? <Building2 size={22} className="text-blue-700" /> : <User size={22} className="text-green-700" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-bold text-slate-900">{member.name}</h1>
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">Member 360</span>
                {isFPC && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">FPC</span>}
                <StatusBadge label={member.activeStatus} size="sm" />
                <StatusBadge label={kycBadgeText} size="sm" />
                {defaultBadgeText && <span className="text-xs font-semibold bg-amber-100 text-amber-700 px-2 py-0.5 rounded uppercase">{defaultBadgeText}</span>}
              </div>
              <p className="text-sm text-slate-500 mt-0.5">
                Folio: <span className="font-semibold text-slate-900 num">{member.folioNumber}</span>
                {' · '}{isFPC ? 'FPC' : 'Individual Farmer'}
                {member.sapCustomerCode && <> · SAP: <span className="font-mono font-semibold">{member.sapCustomerCode}</span></>}
              </p>
            </div>
          </div>
        </div>

        {/* Quick stats header row */}
        <div className="hidden lg:flex items-center gap-4 flex-shrink-0">
          <div className="text-right">
            <p className="text-xs text-slate-400">Total Outstanding</p>
            <p className="text-lg font-bold text-slate-900 num">{fmt(totalOutstanding)}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Open Applications</p>
            <p className="text-lg font-bold text-slate-900">{memberApps.filter(a => !['rejected_credit', 'rejected_by_credit_manager', 'rejected_sanction', 'rejected_by_sanction_committee'].includes(a.status)).length}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Accrued Interest</p>
            <p className="text-lg font-bold text-amber-700 num">{fmt(totalAccruedInterest)}</p>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {hasOverdue && overdueLoan && (
        <AlertBanner type="error" title="Overdue Loan — Reminder Due"
          message={`${overdueLoan.accountNumber} is overdue by ${overdueLoan.dpd} days. Next action: repayment reminder by Credit/Accounts.`} />
      )}
      {member.kycStatus === 'rekyc_due' && (
        <AlertBanner type="warning" title="Re-KYC Required"
          message="Annual KYC re-verification due. No new loans can be sanctioned until KYC is updated." />
      )}

      {/* Quick-stat chips */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        {[
          { label: 'Active Loan Accounts', value: String(activeLoansCount), color: 'bg-slate-50 text-slate-900' },
          { label: 'Overdue Loan Accounts', value: String(overdueLoansCount), color: overdueLoansCount > 0 ? 'bg-red-50 text-red-900' : 'bg-slate-50 text-slate-900' },
          { label: 'Open Application', value: String(openAppsCount), color: 'bg-slate-50 text-slate-900' },
          { label: 'KYC / Re-KYC', value: member.kycStatus === 'rekyc_due' ? 'Re-KYC Due' : (member.kycStatus === 'verified' && riskExceptions.some(e => e.type === 'KYC Re-verification' && e.status === 'open') ? 'Re-KYC Due' : kycBadgeText), color: (member.kycStatus === 'rekyc_due' || riskExceptions.some(e => e.type === 'KYC Re-verification' && e.status === 'open')) ? 'bg-amber-50 text-amber-800' : 'bg-green-50 text-green-800' },
          { label: 'Shareholding', value: `${member.sharesHeld} ${member.shareMode}`, color: 'bg-slate-50 text-slate-900' },
          { label: 'Open Exceptions', value: String(riskExceptions.filter(e => e.status === 'open' || e.status === 'pending').length), color: 'bg-slate-50 text-slate-900' },
        ].map(chip => (
          <div key={chip.label} className={`rounded-xl p-3 border border-slate-100 ${chip.color}`}>
            <p className="text-lg font-bold">{chip.value}</p>
            <p className="text-xs opacity-70 mt-0.5">{chip.label}</p>
          </div>
        ))}
      </div>

      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>

        {/* ── Tab 0: Borrower Summary ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="card space-y-3">
            <h3 className="font-semibold text-slate-800">Member Profile</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                ['Member ID', member.id.toUpperCase()],
                ['Date of Membership', member.registeredOn ? new Date(member.registeredOn).toLocaleDateString('en-IN') : '—'],
                ['Active Member Basis', 'Regular Trading / Supply'],
                ['Active Status', member.activeStatus],
                ['Active Status Reason', member.activeStatus === 'active' ? 'Meets supply criteria' : 'N/A'],
                ['Shareholding Mode', member.shareMode],
                ['Share Valuation Applied', '₹100 per share'],
                ['Current DPD / Default', defaultBadgeText || 'No default'],
              ].map(([k, v]) => (
                <div key={k} className="bg-slate-50 rounded-lg p-2">
                  <p className="text-xs text-slate-400">{k}</p>
                  <p className="text-sm font-semibold text-slate-800 mt-0.5">{v}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="card space-y-3">
            <h3 className="font-semibold text-slate-800">Loan Exposure Summary</h3>
            <div className="space-y-2">
              {memberLoans.length === 0 ? (
                <p className="text-sm text-slate-400">No loan accounts.</p>
              ) : memberLoans.map(loan => (
                <div key={loan.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-slate-900 num">{loan.accountNumber}</p>
                    <p className="text-xs text-slate-500">OS: {fmt(loan.outstandingPrincipal)} · DPD: {loan.dpd}</p>
                  </div>
                  <StatusBadge label={loan.status} size="sm" />
                  <button onClick={() => onOpenLoanAccount?.(loan.id)} className="text-xs text-green-600 hover:underline flex items-center gap-0.5">
                    <ExternalLink size={10} /> Open
                  </button>
                </div>
              ))}
            </div>
            <div className="flex gap-3 mt-2">
              {canExport && <button className="btn-secondary text-xs flex-1">Generate Statement</button>}
              {canAddComm && <button className="btn-secondary text-xs flex-1">Add Communication</button>}
            </div>
          </div>
        </div>

        {/* ── Tab 1: Applications ── */}
        <div className="space-y-3">
          {memberApps.length === 0 ? (
            <div className="card text-center py-8 text-slate-400 text-sm">No applications found.</div>
          ) : memberApps.map(app => (
            <div key={app.id} className="card">
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-slate-900 num">{app.applicationNumber}</span>
                    <StatusBadge label={app.status} size="sm" />
                    {app.isException && <span className="text-xs bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded">Exception</span>}
                    {app.specialCase && <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded">Special Case</span>}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-sm">
                    {[
                      ['Requested', fmt(app.requestedAmount)],
                      ['Eligible', fmt(app.eligibleAmount)],
                      ['Purpose', app.purpose.replace(/_/g, ' ')],
                      ['TAT Days', `${app.tatDaysRemaining ?? '—'} days left`],
                    ].map(([k, v]) => (
                      <div key={k}>
                        <p className="text-xs text-slate-400">{k}</p>
                        <p className="text-sm font-semibold text-slate-800">{v}</p>
                      </div>
                    ))}
                  </div>
                  {app.isException && app.exceptionReason && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-violet-700 bg-violet-50 rounded-lg px-3 py-2">
                      <ShieldAlert size={12} /> {app.exceptionReason}
                    </div>
                  )}
                </div>
                <button onClick={() => onOpenApplication?.(app.id)}
                  className="flex-shrink-0 flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors">
                  <ArrowUpRight size={12} /> Open
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* ── Tab 2: Loan Accounts ── */}
        <div className="space-y-3">
          {memberLoans.length === 0 ? (
            <div className="card text-center py-8 text-slate-400 text-sm">No loan accounts found.</div>
          ) : memberLoans.map(loan => (
            <div key={loan.id} className="card">
              <div className="flex items-start gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-bold text-slate-900 num">{loan.accountNumber}</span>
                    <StatusBadge label={loan.status} size="sm" />
                    {loan.dpd > 0 && (
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${loan.dpd > 90 ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                        DPD: {loan.dpd}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-sm">
                    {[
                      ['Sanctioned', fmt(loan.sanctionedAmount)],
                      ['Outstanding', fmt(loan.outstandingPrincipal)],
                      ['Accrued Interest', fmt(loan.accruedInterest)],
                      ['Rate', `${loan.interestRate}% p.a.`],
                    ].map(([k, v]) => (
                      <div key={k}>
                        <p className="text-xs text-slate-400">{k}</p>
                        <p className="text-sm font-semibold text-slate-800">{v}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <button onClick={() => onOpenLoanAccount?.(loan.id)}
                  className="flex-shrink-0 flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors">
                  <ArrowUpRight size={12} /> Open
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* ── Tab 3: Repayment History ── */}
        <div className="card overflow-hidden p-0">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Repayment History ({memberRepayments.length})</h3>
            {canExport && (
              <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
                <Download size={12} /> Export
              </button>
            )}
          </div>
          {memberRepayments.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-sm">No repayments recorded.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    {['Date', 'Loan Account', 'Amount', 'Principal', 'Interest', 'Channel', 'UTR / Ref', 'SAP Status'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {memberRepayments.map(r => (
                    <tr key={r.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-slate-700">{new Date(r.receiptDate).toLocaleDateString('en-IN')}</td>
                      <td className="px-4 py-3 text-slate-700 font-mono text-xs">{memberLoans.find(l => l.id === r.loanAccountId)?.accountNumber || r.loanAccountId}</td>
                      <td className="px-4 py-3 font-semibold text-slate-900">{fmt(r.amount)}</td>
                      <td className="px-4 py-3 text-slate-700">{fmt(r.principalAllocation)}</td>
                      <td className="px-4 py-3 text-slate-700">{fmt(r.interestAllocation)}</td>
                      <td className="px-4 py-3 text-xs text-slate-600">{r.channel.replace(/_/g, ' ')}</td>
                      <td className="px-4 py-3 text-xs font-mono text-slate-500">{r.bankReference}</td>
                      <td className="px-4 py-3"><StatusBadge label={r.sapEntryStatus} size="sm" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ── Tab 4: Security Instruments ── */}
        <div className="card space-y-4">
          <h3 className="font-semibold text-slate-800">Security Instruments Held</h3>
          {[
            { type: 'Power of Attorney (PoA)', status: 'notarised', custodian: 'Aarti Desai (CS)', date: '2024-09-18', invocable: true },
            { type: member.shareMode !== 'demat' ? 'SH-4 (Physical Share Transfer)' : 'CDSL Pledge', status: member.shareMode !== 'demat' ? 'held' : 'pledged', custodian: member.shareMode !== 'demat' ? 'Company Secretary' : 'CDSL DP', date: '2024-09-15', invocable: true },
            { type: 'Blank-Dated Cheque', status: 'held', custodian: 'Aarti Desai (CS)', date: '2024-09-15', invocable: true },
            { type: 'Tri-Party Agreement', status: 'executed', custodian: 'Company Secretary', date: '2024-09-18', invocable: false },
          ].map((sec, i) => (
            <div key={i} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-100">
              <div className="w-9 h-9 rounded-lg bg-green-50 flex items-center justify-center flex-shrink-0">
                <Shield size={16} className="text-green-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-800">{sec.type}</p>
                <p className="text-xs text-slate-500">Custodian: {sec.custodian} · Date: {new Date(sec.date).toLocaleDateString('en-IN')}</p>
              </div>
              <StatusBadge label={sec.status} size="sm" />
              {sec.invocable && (
                <span className="text-xs text-slate-600 font-medium bg-slate-100 border border-slate-200 px-2 py-1 rounded-lg flex-shrink-0">Locked — approval required</span>
              )}
            </div>
          ))}
        </div>

        {/* ── Tab 5: Documentation ── */}
        <div className="card space-y-3">
          <h3 className="font-semibold text-slate-800">KYC & Documentation Status</h3>
          <p className="text-xs text-slate-500 mt-1 mb-3">Linked records: {memberApps.map(a => a.applicationNumber).join(' · ')} {memberLoans.length > 0 ? '· ' + memberLoans.map(l => l.accountNumber).join(' · ') : ''}</p>
          {[
            { doc: 'Loan Application Form', status: 'complete', signed: true },
            { doc: 'PAN Copy (Borrower)', status: 'verified', signed: false },
            { doc: 'Aadhaar Copy (Borrower)', status: 'verified', signed: false },
            { doc: 'Nominee PAN & Aadhaar', status: 'verified', signed: false },
            { doc: '7/12 Extract', status: 'verified', signed: false },
            { doc: 'Crop Plan', status: 'verified', signed: false },
            { doc: '6-Month Bank Statement', status: 'verified', signed: false },
            { doc: 'Loan Agreement', status: 'notarised', signed: true },
            { doc: 'Term Sheet', status: 'signed', signed: true },
            { doc: 'Sanction Letter', status: 'complete', signed: false },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${['complete','verified','notarised','signed'].includes(item.status) ? 'bg-green-100' : 'bg-amber-100'}`}>
                {['complete','verified','notarised','signed'].includes(item.status)
                  ? <CheckCircle2 size={13} className="text-green-600" />
                  : <Clock size={13} className="text-amber-600" />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-800">{item.doc}</p>
              </div>
              <StatusBadge label={item.status} size="sm" />
              {item.signed && <span className="text-xs text-slate-400">Signed</span>}
            </div>
          ))}
        </div>

        {/* ── Tab 6: Nominee ── */}
        <div className="space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <User size={16} className="text-green-600" /> Nominee Details
              </h3>
              <StatusBadge label="Pending Signature" size="sm" type="warning" />
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { label: 'Full Name', value: 'Sudha Patil' },
                { label: 'Date of Birth', value: '15 Mar 1980' },
                { label: 'Age at Application', value: '45 years' },
                { label: 'Gender', value: 'Female' },
                { label: 'Relationship', value: 'Spouse' },
                { label: 'Mobile', value: '9900112233' },
                { label: 'Address', value: 'Sr. No. 88, Igatpuri, Nashik' },
                { label: 'PAN Document', value: 'Pending' },
                { label: 'Aadhaar Document', value: 'Uploaded' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                  <p className={`text-sm font-semibold mt-0.5 ${value === 'Pending' ? 'text-amber-700' : 'text-slate-900'}`}>{value}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Identity & Verification</h3>
            <div className="space-y-2">
              {[
                { label: 'Nominee PAN', value: '••••••••••', status: 'Pending', note: 'Reveal requires authorised access' },
                { label: 'Nominee Aadhaar (last 4)', value: '••••', status: 'Uploaded', note: 'Aadhaar copy uploaded, not yet verified' },
                { label: 'Minor age check', value: '≥ 18 years confirmed', status: 'Passed', note: '' },
                { label: 'Nominee signature', value: 'Not yet obtained', status: 'Pending', note: 'Required before disbursement' },
              ].map(({ label, value, status, note }) => (
                <div key={label} className="flex items-start justify-between gap-4 py-2 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-slate-700">{label}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{value}{note ? ` — ${note}` : ''}</p>
                  </div>
                  <StatusBadge label={status} size="sm" type={status === 'Passed' ? 'success' : status === 'Uploaded' ? 'info' : 'warning'} />
                </div>
              ))}
            </div>
          </div>
          {memberApps.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-700 font-medium">
                Nominee details are linked to application {memberApps[0].applicationNumber}. View full nominee panel in ApplicationDetail → Nominee tab.
              </p>
            </div>
          )}
        </div>

        {/* ── Tab 7: Communications ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Communications Log</h3>
            {canAddComm && (
              <button className="flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors">
                <MessageSquare size={12} /> Add Entry
              </button>
            )}
          </div>
          <div className="divide-y divide-slate-50">
            {communicationsLog.map((c, i) => (
              <div key={i} className="flex gap-4 px-6 py-4 hover:bg-slate-50">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${c.type === 'SMS' ? 'bg-blue-50' : c.type === 'Email' ? 'bg-green-50' : c.type === 'Call' ? 'bg-amber-50' : 'bg-slate-100'}`}>
                  <MessageSquare size={14} className="text-slate-500" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">{c.type}</span>
                    <span className="text-xs text-slate-400">{c.direction}</span>
                  </div>
                  <p className="text-sm text-slate-700 mt-1">{c.message}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{c.sentBy} · {new Date(c.date).toLocaleDateString('en-IN')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Tab 8: Risk & Exceptions ── */}
        <div className="space-y-3">
          {riskExceptions.length === 0 ? (
            <div className="card text-center py-8 text-slate-400 text-sm">
              <CheckCircle2 size={20} className="mx-auto mb-2 text-green-400" />
              No open risk flags or exceptions.
            </div>
          ) : riskExceptions.map((ex, i) => (
            <div key={i} className={`card border-l-4 ${ex.severity === 'high' ? 'border-l-red-500' : 'border-l-amber-400'}`}>
              <div className="flex items-start gap-3">
                <ShieldAlert size={18} className={`flex-shrink-0 mt-0.5 ${ex.severity === 'high' ? 'text-red-500' : 'text-amber-500'}`} />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-slate-900">{ex.type}</p>
                    {ex.linkedId && <span className="text-xs font-mono text-slate-500">{ex.linkedId}</span>}
                    <StatusBadge label={ex.status} size="sm" />
                    <span className={`text-xs font-semibold uppercase px-1.5 py-0.5 rounded ${ex.severity === 'high' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                      {ex.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{ex.description}</p>
                  <p className="text-xs text-slate-400 mt-1">Flagged: {new Date(ex.date).toLocaleDateString('en-IN')}</p>
                  {canApproveException && ex.status === 'pending' && (
                    <div className="flex gap-2 mt-2">
                      <button className="text-xs bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded">Approve</button>
                      <button className="text-xs bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded">Reject</button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        {/* ── Tab 9: Audit Trail ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="font-semibold text-slate-800">Audit Trail</h3>
          </div>
          <div className="divide-y divide-slate-50">
            {memberAuditEvents.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">No audit records found.</div>
            ) : memberAuditEvents.map((e, i) => (
              <div key={i} className="flex gap-4 px-6 py-4 hover:bg-slate-50">
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                  <History size={14} className="text-slate-500" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-800">{e.eventType}</p>
                  <p className="text-sm text-slate-600 mt-0.5">
                    {e.actorName} ({e.actorRole.replace(/_/g, ' ')})
                    {e.previousState && e.newState && ` changed state from ${e.previousState} to ${e.newState}`}
                  </p>
                  {e.comment && <p className="text-xs text-slate-500 mt-1">{e.comment}</p>}
                  {e.reason && <p className="text-xs text-red-500 mt-1">{e.reason}</p>}
                  <p className="text-xs text-slate-400 mt-1">{new Date(e.timestamp).toLocaleString('en-IN')}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Tabs>
    </div>
  );
};

export default Borrower360;
