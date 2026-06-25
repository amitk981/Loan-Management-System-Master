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
import { members, loanApplications, loanAccounts, repayments } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface Borrower360Props {
  memberId: string;
  onBack: () => void;
  onOpenApplication?: (id: string) => void;
  onOpenLoanAccount?: (id: string) => void;
}

const communicationsLog = [
  { date: '2026-06-15', type: 'SMS', direction: 'Outbound', message: 'EMI reminder: ₹1,05,000 due on 30 Jun 2025. Pay on time to avoid penalty.', sentBy: 'System' },
  { date: '2026-06-01', type: 'Email', direction: 'Outbound', message: 'Loan sanction approval notification with sanction letter attached.', sentBy: 'Priya Kulkarni' },
  { date: '2026-05-22', type: 'Call', direction: 'Inbound', message: 'Borrower called to query about interest calculation. Clarified principal-first allocation.', sentBy: 'Priya Kulkarni' },
  { date: '2026-04-10', type: 'Letter', direction: 'Outbound', message: 'Hard copy of Loan Agreement dispatched by registered post. Tracking: RM123456789IN.', sentBy: 'Aarti Desai' },
];

const riskExceptions = [
  { type: 'Amount Exception', description: 'Requested ₹8,00,000 exceeds eligible limit ₹3,60,000', severity: 'high', status: 'pending', date: '2026-06-14' },
  { type: 'KYC Re-verification', description: 'Annual KYC re-verification due — FPC needs updated documents', severity: 'medium', status: 'open', date: '2026-06-01' },
];

const Borrower360: React.FC<Borrower360Props> = ({ memberId, onBack, onOpenApplication, onOpenLoanAccount }) => {
  const member = members.find(m => m.id === memberId) || members[0];
  const memberApps = loanApplications.filter(a => a.memberId === member.id);
  const memberLoans = loanAccounts.filter(l => l.memberId === member.id);
  const memberRepayments = repayments.filter(r => memberLoans.some(l => l.id === r.loanAccountId));
  const [activeTab, setActiveTab] = useState(0);

  const isFPC = member.memberType === 'fpc';
  const totalOutstanding = memberLoans.reduce((s, l) => s + l.outstandingPrincipal, 0);
  const totalAccruedInterest = memberLoans.reduce((s, l) => s + l.accruedInterest, 0);
  const hasOverdue = memberLoans.some(l => l.status === 'overdue' || l.status === 'grace_period');

  const TABS = [
    { id: 'summary',     label: 'Borrower Summary' },
    { id: 'applications', label: 'Applications', badge: memberApps.length || undefined },
    { id: 'loans',       label: 'Active Loans', badge: memberLoans.filter(l => l.status === 'active' || l.status === 'overdue').length || undefined },
    { id: 'repayments',  label: 'Repayment History' },
    { id: 'security',    label: 'Security Instruments' },
    { id: 'docs',        label: 'Documentation' },
    { id: 'comms',       label: 'Communications' },
    { id: 'risk',        label: 'Risk & Exceptions', badge: riskExceptions.length || undefined },
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
                <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">Borrower 360</span>
                {isFPC && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold">FPC</span>}
                <StatusBadge label={member.activeStatus} size="sm" />
                <StatusBadge label={member.kycStatus} size="sm" />
                {member.defaultStatus !== 'no_default' && <StatusBadge label={member.defaultStatus} size="sm" />}
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
            <p className="text-lg font-bold text-slate-900">{memberApps.filter(a => a.status !== 'rejected_credit' && a.status !== 'rejected_sanction').length}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400">Accrued Interest</p>
            <p className="text-lg font-bold text-amber-700 num">{fmt(totalAccruedInterest)}</p>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {hasOverdue && (
        <AlertBanner type="error" title="Overdue Loan — Recovery Risk"
          message="One or more loan accounts are overdue. DPD monitoring active. Reminder workflow should be initiated." />
      )}
      {member.kycStatus === 'rekyc_due' && (
        <AlertBanner type="warning" title="Re-KYC Required"
          message="Annual KYC re-verification due. No new loans can be sanctioned until KYC is updated." />
      )}

      {/* Quick-stat chips */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3">
        {[
          { label: 'Total Outstanding', value: fmt(totalOutstanding), color: 'bg-slate-50 text-slate-900' },
          { label: 'Accrued Interest', value: fmt(totalAccruedInterest), color: 'bg-amber-50 text-amber-900' },
          { label: 'Active Loans', value: String(memberLoans.filter(l => l.status === 'active').length), color: 'bg-green-50 text-green-900' },
          { label: 'Overdue Loans', value: String(memberLoans.filter(l => l.status === 'overdue').length), color: memberLoans.some(l => l.status === 'overdue') ? 'bg-red-50 text-red-900' : 'bg-slate-50 text-slate-900' },
          { label: 'Open Applications', value: String(memberApps.filter(a => !['rejected_credit','rejected_sanction'].includes(a.status)).length), color: 'bg-slate-50 text-slate-900' },
          { label: 'KYC Status', value: member.kycStatus.replace(/_/g, ' '), color: member.kycStatus === 'verified' ? 'bg-green-50 text-green-800' : 'bg-amber-50 text-amber-800' },
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
            <h3 className="font-semibold text-slate-800">Borrower Profile</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {[
                ['Member ID', member.id.toUpperCase()],
                ['Folio Number', member.folioNumber],
                ['Member Type', isFPC ? 'FPC' : 'Individual Farmer'],
                ['Shares Held', `${member.sharesHeld.toLocaleString('en-IN')} (${member.shareMode})`],
                ['Mobile', member.mobile],
                ['Email', member.email],
                ['Active Status', member.activeStatus],
                ['Default Status', member.defaultStatus.replace(/_/g, ' ')],
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
              <button className="btn-secondary text-xs flex-1">Generate Statement</button>
              <button className="btn-secondary text-xs flex-1">Add Communication</button>
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

        {/* ── Tab 2: Active Loans ── */}
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
            <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
              <Download size={12} /> Export
            </button>
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
                <span className="text-xs text-amber-600 font-medium bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">Invocable</span>
              )}
            </div>
          ))}
        </div>

        {/* ── Tab 5: Documentation ── */}
        <div className="card space-y-3">
          <h3 className="font-semibold text-slate-800">Documentation Status</h3>
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

        {/* ── Tab 6: Communications ── */}
        <div className="card p-0 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800">Communications Log</h3>
            <button className="flex items-center gap-1 text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg transition-colors">
              <MessageSquare size={12} /> Add Entry
            </button>
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

        {/* ── Tab 7: Risk & Exceptions ── */}
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
                    <StatusBadge label={ex.status} size="sm" />
                    <span className={`text-xs font-semibold uppercase px-1.5 py-0.5 rounded ${ex.severity === 'high' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>
                      {ex.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{ex.description}</p>
                  <p className="text-xs text-slate-400 mt-1">Flagged: {new Date(ex.date).toLocaleDateString('en-IN')}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Tabs>
    </div>
  );
};

export default Borrower360;
