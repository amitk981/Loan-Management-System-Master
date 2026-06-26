const fs = require('fs');
const path = require('path');

const code = `import React, { useState } from 'react';
import {
  AlertTriangle, Clock, FileText, CheckCircle2, XCircle,
  ChevronRight, Calendar, IndianRupee, User, MessageSquare,
  Shield, Gavel, ArrowRight, BarChart2, Lock, Edit3, Eye
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';

type DefaultTab = 'cases' | 'grace' | 'non_payment' | 'recovery' | 'security';

interface DefaultCase {
  id: string;
  loanNo: string;
  borrower: string;
  outstanding: number;
  overdueDays: number;
  dpdBucket: string;
  status: string;
  lastAction: string;
  nextAction: string;
  graceStartDate?: string;
  graceEndDate?: string;
  daysRemaining?: number;
  reminderCount?: number;
  lastReminderDate?: string;
  repaymentDuringGrace?: number;
}

const defaultCases: DefaultCase[] = [
  { id: 'dc001', loanNo: 'LO00000042', borrower: 'Ganesh Thorat',   outstanding: 350000, overdueDays: 45,  dpdBucket: '31_60',   status: 'grace_period',  lastAction: 'Reminder sent 10 Jun', nextAction: 'Grace period expires 15 Sep 2025', graceStartDate: '15 Jun 2025', graceEndDate: '15 Sep 2025', daysRemaining: 45, reminderCount: 3, lastReminderDate: '10 Jun 2025', repaymentDuringGrace: 0 },
  { id: 'dc002', loanNo: 'LO00000038', borrower: 'Malti Shinde',    outstanding: 180000, overdueDays: 95,  dpdBucket: '91_365',  status: 'default_review',lastAction: 'Grace expired',        nextAction: 'Submit Non-Payment Note to SC' },
  { id: 'dc003', loanNo: 'LO00000035', borrower: 'Kisan FPC Ltd',   outstanding: 890000, overdueDays: 187, dpdBucket: '91_365',  status: 'recovery_approved', lastAction: 'SC approved recovery', nextAction: 'Invoke SH-4 / blank cheque' },
];

const DefaultRecoveryHub: React.FC = () => {
  const { currentUser } = useRole();
  const role = currentUser.role;

  // Permissions
  const canAccess = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'compliance_team', 'sanction_committee'].includes(role);
  const canCreditAct = ['credit_manager'].includes(role);
  const canApproveRecovery = ['cfo', 'sanction_committee'].includes(role);
  const canInvokeSecurity = ['compliance_team', 'company_secretary'].includes(role);
  
  const [activeTab, setActiveTab] = useState<DefaultTab>('cases');
  const [selectedCase, setSelectedCase] = useState<DefaultCase>(defaultCases[0]);
  const [extensionReason, setExtensionReason] = useState('');
  const [nonPaymentNote, setNonPaymentNote] = useState('');
  const [extensionSubmitted, setExtensionSubmitted] = useState(false);
  const [nonPaymentSubmitted, setNonPaymentSubmitted] = useState(false);
  const [localRecoveryApproved, setLocalRecoveryApproved] = useState(false);
  const [invokedSecurities, setInvokedSecurities] = useState<string[]>(['SH-4 (share transfer to company)']);
  const [recoveryLogged, setRecoveryLogged] = useState(false);
  const [borrowerNoticeSent, setBorrowerNoticeSent] = useState(false);

  if (!canAccess) {
    return <div className="p-6 text-red-600">Access Denied. You do not have permission to view this module.</div>;
  }

  const isGrace = selectedCase.status === 'grace_period';
  const isDefaultReview = selectedCase.status === 'default_review';
  const isRecoveryApproved = selectedCase.status === 'recovery_approved' || localRecoveryApproved;

  const tabs: { id: DefaultTab; label: string; badge?: number }[] = [
    { id: 'cases',       label: 'All Cases', badge: defaultCases.length },
    { id: 'grace',       label: 'Grace Period / Extension' },
    { id: 'non_payment', label: 'Non-Payment Note' },
    { id: 'recovery',    label: 'Recovery Approval' },
    { id: 'security',    label: 'Security Invocation' },
  ];

  const toggleInvocation = (item: string) => {
    setInvokedSecurities(current =>
      current.includes(item)
        ? current.filter(value => value !== item)
        : [...current, item]
    );
  };

  // Determine workflow impact strictly per case state
  let wfImpact = [];
  if (isGrace) {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: 'not_applicable', note: 'Not applicable during grace period.' },
      { label: 'Security Register', status: 'locked', note: 'Locked until recovery is approved.' },
      { label: 'Borrower Notice', status: 'reminder_sent', note: 'Reminder notice issued.' },
      { label: 'Audit Trail', status: 'updated', note: 'Grace period initiation and reminders logged.' },
    ];
  } else if (isDefaultReview) {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: 'pending_update', note: 'Log entry is staged after non-payment and invocation action.' },
      { label: 'Security Register', status: 'locked', note: 'Locked until recovery is approved.' },
      { label: 'Borrower Notice', status: 'final_notice_staged', note: 'Final notice generation pending approval.' },
      { label: 'Audit Trail', status: 'updated', note: 'Default review steps logged.' },
    ];
  } else {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: recoveryLogged ? 'updated' : 'ready', note: recoveryLogged ? 'Invocation action has a local recovery-log entry.' : 'Ready for invocation entry.' },
      { label: 'Security Register', status: recoveryLogged ? 'invocation_recorded' : invokedSecurities.length > 0 ? 'invocation_selected' : 'unlocked', note: invokedSecurities.length > 0 ? invokedSecurities.join(', ') : 'Ready for security selection.' },
      { label: 'Borrower Notice', status: borrowerNoticeSent ? 'sent' : 'ready_to_send', note: borrowerNoticeSent ? 'Borrower-facing recovery notice is staged for MP19.' : 'Notice appears after recovery action is recorded.' },
      { label: 'Audit Trail', status: 'updated', note: 'Recovery approval logged.' },
    ];
  }

  const getWorkflowStepper = () => {
    if (isGrace) {
      return [
        { step: '1', label: 'Reminder issued (call/SMS)', state: 'complete' },
        { step: '2', label: 'Grace period started (90 days)', state: 'active' },
        { step: '3', label: 'Reason assessment', state: 'locked' },
        { step: '4', label: 'Extension note', state: 'locked' },
        { step: '5', label: 'Non-payment note to Sanction Committee', state: 'locked' },
        { step: '6', label: 'Recovery action approval', state: 'locked' },
        { step: '7', label: 'Security invocation / legal action', state: 'locked' },
      ];
    } else if (isDefaultReview) {
      return [
        { step: '1', label: 'Reminder issued (call/SMS)', state: 'complete' },
        { step: '2', label: 'Grace period expired', state: 'complete' },
        { step: '3', label: 'Reason assessment', state: 'complete' },
        { step: '4', label: 'Extension note', state: 'complete' },
        { step: '5', label: 'Non-payment note to Sanction Committee', state: nonPaymentSubmitted ? 'complete' : 'active' },
        { step: '6', label: 'Recovery action approval', state: nonPaymentSubmitted ? 'active' : 'locked' },
        { step: '7', label: 'Security invocation / legal action', state: 'locked' },
      ];
    } else {
      return [
        { step: '1', label: 'Reminder issued (call/SMS)', state: 'complete' },
        { step: '2', label: 'Grace period expired', state: 'complete' },
        { step: '3', label: 'Reason assessment', state: 'complete' },
        { step: '4', label: 'Extension note', state: 'complete' },
        { step: '5', label: 'Non-payment note to Sanction Committee', state: 'complete' },
        { step: '6', label: 'Recovery action approval', state: 'complete' },
        { step: '7', label: 'Security invocation / legal action', state: recoveryLogged ? 'complete' : 'active' },
      ];
    }
  };

  const currentStepper = getWorkflowStepper();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Default & Recovery Management</h1>
        <p className="text-sm text-slate-500 mt-1">Manage overdue loans, grace periods, extension notes, recovery approvals and security invocation.</p>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Grace Period',          value: '1',         amount: '₹3.5L', color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-100' },
          { label: 'Default Review',        value: '1',         amount: '₹1.8L', color: 'text-red-600',   bg: 'bg-red-50',    border: 'border-red-100' },
          { label: 'Recovery Approved',     value: '1',         amount: '₹8.9L', color: 'text-violet-700', bg: 'bg-violet-50', border: 'border-violet-100' },
        ].map(kpi => (
          <div key={kpi.label} className={\`\${kpi.bg} \${kpi.border} border rounded-xl p-4\`}>
            <div className={\`text-2xl font-bold \${kpi.color}\`}>{kpi.value}</div>
            <div className="text-xs text-slate-600 mt-0.5">{kpi.label}</div>
            <div className="text-sm font-semibold text-slate-700 mt-1">{kpi.amount}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={\`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors \${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }\`}
            >
              {tab.label}
              {tab.badge !== undefined && (
                <span className={\`text-xs px-1.5 py-0.5 rounded-full font-semibold \${activeTab === tab.id ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}\`}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between gap-3 mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Workflow Status</h3>
            <p className="text-xs text-slate-500 mt-0.5">Current status across monitoring, recovery log, notices and audit.</p>
          </div>
          <StatusBadge label={isGrace ? 'Grace Period Active' : isRecoveryApproved ? 'recovery_approved' : 'default_review'} size="sm" type={isGrace ? 'warning' : 'error'}/>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {wfImpact.map(item => (
            <div key={item.label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-semibold text-slate-700">{item.label}</p>
                <StatusBadge label={item.status} size="sm" type={item.status === 'locked' ? 'slate' : 'default'} />
              </div>
              <p className="text-xs text-slate-500 mt-2">{item.note}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Cases list + detail */}
      {activeTab === 'cases' && (
        <div className="flex flex-col lg:flex-row gap-6">
          {/* List */}
          <div className="w-full lg:w-80 flex-shrink-0 space-y-2">
            {defaultCases.map(c => (
              <button
                key={c.id}
                onClick={() => setSelectedCase(c)}
                className={\`w-full text-left border rounded-xl p-4 transition-all \${
                  selectedCase?.id === c.id
                    ? 'border-green-300 bg-green-50'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }\`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs font-mono font-medium text-slate-600">{c.loanNo}</span>
                  <StatusBadge label={c.status} size="sm" type={c.status === 'grace_period' ? 'warning' : 'error'} />
                </div>
                <div className="font-medium text-slate-900 text-sm">{c.borrower}</div>
                <div className="text-xs text-slate-500 mt-1">₹{c.outstanding.toLocaleString('en-IN')} outstanding · {c.overdueDays} DPD</div>
              </button>
            ))}
          </div>

          {/* Detail */}
          {selectedCase && (
            <div className="flex-1 space-y-4">
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-900">{selectedCase.loanNo}</h2>
                      <StatusBadge label={selectedCase.status} type={selectedCase.status === 'grace_period' ? 'warning' : 'error'} />
                    </div>
                    <div className="text-slate-600 mt-0.5">{selectedCase.borrower}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-500">Amount Due</div>
                    <div className="text-2xl font-bold text-red-600">₹{selectedCase.outstanding.toLocaleString('en-IN')}</div>
                  </div>
                </div>

                {isGrace ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-6">
                    <div>
                      <div className="text-xs text-slate-500">Grace Start Date</div>
                      <div className="font-medium text-slate-800 mt-0.5">{selectedCase.graceStartDate}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Grace End Date</div>
                      <div className="font-medium text-slate-800 mt-0.5">{selectedCase.graceEndDate}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Days Remaining</div>
                      <div className="font-medium text-amber-600 mt-0.5">{selectedCase.daysRemaining} days</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Amount Due</div>
                      <div className="font-medium text-slate-800 mt-0.5">₹{selectedCase.outstanding.toLocaleString('en-IN')}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Reminder Count</div>
                      <div className="font-medium text-slate-800 mt-0.5">{selectedCase.reminderCount}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Last Reminder</div>
                      <div className="font-medium text-slate-800 mt-0.5">{selectedCase.lastReminderDate}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Repayment During Grace</div>
                      <div className="font-medium text-slate-800 mt-0.5">₹{selectedCase.repaymentDuringGrace}</div>
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-6">
                    {[
                      ['DPD Bucket', selectedCase.dpdBucket.replace('_', '–') + ' days'],
                      ['Overdue Days', \`\${selectedCase.overdueDays} days\`],
                      ['Last Action', selectedCase.lastAction],
                      ['Next Action', selectedCase.nextAction],
                    ].map(([k, v]) => (
                      <div key={k}>
                        <div className="text-xs text-slate-500">{k}</div>
                        <div className="font-medium text-slate-800 mt-0.5">{v}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Default workflow */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-800 mb-4">Default Resolution Workflow</h3>
                <div className="space-y-3">
                  {currentStepper.map(s => (
                    <div key={s.step} className="flex items-center gap-3">
                      <div className={\`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold \${
                        s.state === 'complete' ? 'bg-green-600 text-white' : 
                        s.state === 'active' ? 'bg-blue-600 text-white' : 
                        'bg-slate-100 text-slate-500'
                      }\`}>
                        {s.state === 'complete' ? <CheckCircle2 size={14} /> : s.state === 'locked' ? <Lock size={12}/> : s.step}
                      </div>
                      <span className={\`text-sm \${s.state === 'complete' ? 'text-slate-900 font-medium' : s.state === 'active' ? 'text-blue-900 font-semibold' : 'text-slate-400'}\`}>{s.label}</span>
                      {s.state === 'active' && <span className="text-[10px] uppercase font-bold tracking-wider text-blue-600 ml-2 bg-blue-50 px-2 py-0.5 rounded">Active</span>}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Bar */}
              {canCreditAct && isGrace && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="font-medium text-amber-900 text-sm">Action Required</div>
                    <div className="text-xs text-amber-700 mt-0.5">Grace period requires active follow up before expiry.</div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="flex items-center gap-2 bg-white border border-amber-300 text-amber-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:bg-amber-100"
                    >
                      <Edit3 size={14} /> Log Follow-up
                    </button>
                    <button
                      className="flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      Mark Grace Outcome <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              )}
              {canCreditAct && isDefaultReview && !nonPaymentSubmitted && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="font-medium text-red-900 text-sm">Action Required</div>
                    <div className="text-xs text-red-700 mt-0.5">Grace period expired. Non-payment note required for Sanction Committee.</div>
                  </div>
                  <button
                    onClick={() => setActiveTab('non_payment')}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Prepare Non-Payment Note <ArrowRight size={14} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Grace Period / Extension */}
      {activeTab === 'grace' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-1">Grace Period Rules</h3>
            <p className="text-xs text-slate-500 mb-4">Per SOP Section 11.3 — three-month grace period automatically triggers on first missed repayment.</p>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Clock size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                <div><strong>Grace Period:</strong> 90 days from missed repayment. Reminder calls and SMS issued weekly. No additional interest during grace.</div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
                <Calendar size={16} className="text-amber-600 mt-0.5 flex-shrink-0" />
                <div><strong>Extension (non-intentional default):</strong> CFO may approve one-year extension with Sanction Committee concurrence. Extension Note mandatory.</div>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Prepare Extension Note</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Account</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  {defaultCases.filter(c => c.status === 'grace_period').map(c => (
                    <option key={c.id}>{c.loanNo} — {c.borrower}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Extension Type</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option>1-Year Non-Intentional Default Extension</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Reason for Extension (mandatory)</label>
                <textarea
                  value={extensionReason}
                  onChange={e => setExtensionReason(e.target.value)}
                  rows={4}
                  placeholder="Document the reason for non-payment (crop failure, natural disaster, illness, etc.)…"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Supporting Evidence</label>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center text-sm text-slate-400 cursor-pointer hover:border-green-300 hover:text-green-600 transition-colors">
                  Click to attach crop survey report, insurance claim, or other evidence
                </div>
              </div>
              {canCreditAct && (
                <button
                  onClick={() => setExtensionSubmitted(true)}
                  disabled={!extensionReason}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  <FileText size={16} />
                  {extensionSubmitted ? 'Extension Note Submitted' : 'Submit Extension Note'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Non-Payment Note */}
      {activeTab === 'non_payment' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle size={18} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-amber-800">
              <strong>SOP Requirement:</strong> If borrower fails to repay within the grace period, the Credit Assessment Team must submit a note for non-payment to the Sanction Committee explaining reasons and recommending recovery action.
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Note for Non-Payment</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Account</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  {defaultCases.filter(c => c.status === 'default_review').map(c => (
                    <option key={c.id}>{c.loanNo} — {c.borrower}</option>
                  ))}
                  {defaultCases.filter(c => c.status === 'default_review').length === 0 && (
                    <option disabled>No accounts eligible for non-payment note</option>
                  )}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4">
                <div><div className="text-slate-500">Grace Period Expired</div><div className="font-medium text-slate-900">15 March 2025</div></div>
                <div><div className="text-slate-500">Total Outstanding</div><div className="font-medium text-slate-900">₹1,80,000</div></div>
                <div><div className="text-slate-500">Days Past Due</div><div className="font-medium text-red-600">95 days</div></div>
                <div><div className="text-slate-500">Reminders Sent</div><div className="font-medium text-slate-900">8 calls, 12 SMS</div></div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Reason Analysis</label>
                <textarea
                  value={nonPaymentNote}
                  onChange={e => setNonPaymentNote(e.target.value)}
                  rows={5}
                  placeholder="Summarise reason for non-payment, actions taken, borrower's response, and recommended recovery action…"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Recommended Action</label>
                <div className="space-y-2">
                  {['Further extension (exceptional case)', 'Partial write-off and settlement', 'Legal recovery action', 'Security invocation (SH-4/cheque)'].map(opt => (
                    <label key={opt} className="flex items-center gap-3 text-sm cursor-pointer p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                      <input type="radio" name="recovery_action" className="accent-green-600" />
                      {opt}
                    </label>
                  ))}
                </div>
              </div>
              {canCreditAct && (
                <button
                  onClick={() => {
                    setNonPaymentSubmitted(true);
                  }}
                  disabled={!nonPaymentNote}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  <MessageSquare size={16} />
                  {nonPaymentSubmitted ? 'Submitted to Sanction Committee' : 'Submit to Sanction Committee'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recovery Approval */}
      {activeTab === 'recovery' && (
        <div className="max-w-2xl space-y-5">
          {defaultCases.filter(c => c.status !== 'grace_period').length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <Lock size={32} className="mx-auto text-slate-300 mb-3" />
              <div className="font-semibold text-slate-700">No Eligible Cases</div>
              <div className="text-sm text-slate-500 mt-1">Recovery approval requires a submitted Non-Payment Note.</div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Gavel size={16} className="text-red-600" />
                Recovery Action Approval
              </h3>
              <p className="text-xs text-slate-500 mb-4">Requires CFO approval and Sanction Committee concurrence. All decisions are logged in the audit trail.</p>

              <div className="border border-slate-200 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-medium text-slate-900">LO00000035 — Kisan FPC Ltd</div>
                    <div className="text-xs text-slate-500">Outstanding: ₹8,90,000 · DPD: 187 days</div>
                  </div>
                  <StatusBadge label={localRecoveryApproved || selectedCase.id === 'dc003' ? 'recovery_approved' : 'default_review'} />
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-green-700">
                    <CheckCircle2 size={14} />
                    Non-payment note submitted by Credit Manager
                  </div>
                  <div className="flex items-center gap-2 text-green-700">
                    <CheckCircle2 size={14} />
                    Reason assessment recorded and required evidence attached
                  </div>
                </div>
              </div>

              {canApproveRecovery && (!localRecoveryApproved && selectedCase.id !== 'dc003') && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Recovery Decision</label>
                    <div className="space-y-2">
                      {['Approve legal recovery action', 'Approve security invocation (SH-4/cheque)', 'Approve write-off (exceptional, with board approval)', 'Return for further negotiation'].map(opt => (
                        <label key={opt} className="flex items-center gap-3 text-sm cursor-pointer p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                          <input type="radio" name="rec_decision" className="accent-green-600" />
                          {opt}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Remarks (mandatory for recovery approval)</label>
                    <textarea rows={3} placeholder="Sanction Committee / CFO remarks on recovery decision…" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" />
                  </div>
                  <button
                    onClick={() => setLocalRecoveryApproved(true)}
                    className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
                  >
                    <Gavel size={16} />
                    Approve Recovery Action
                  </button>
                </div>
              )}
              {(localRecoveryApproved || selectedCase.id === 'dc003') && (
                <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-xl p-4">
                  <CheckCircle2 size={18} />
                  <span className="text-sm font-medium">Recovery action approved. Security invocation has been notified to Company Secretary.</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Security Invocation */}
      {activeTab === 'security' && (
        <div className="max-w-2xl space-y-5">
          {(!localRecoveryApproved && selectedCase.id !== 'dc003') ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <Lock size={32} className="mx-auto text-slate-300 mb-3" />
              <div className="font-semibold text-slate-700">Security Invocation Locked</div>
              <div className="text-sm text-slate-500 mt-1">Security invocation locked until recovery approval is recorded.</div>
            </div>
          ) : (
            <>
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
                <Shield size={18} className="text-red-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-800">
                  <strong>SOP Section 12:</strong> Security invocation (SH-4 transfer / cheque presentment) is permitted only after CFO-approved recovery action. All invocations are recorded in the Security Register.
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-900 mb-4">Security Invocation</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4">
                    <div><div className="text-slate-500">Loan</div><div className="font-medium">LO00000035 — Kisan FPC Ltd</div></div>
                    <div><div className="text-slate-500">Recovery Approval</div><div className="font-medium text-green-700">Approved</div></div>
                    <div><div className="text-slate-500">Securities Held</div><div className="font-medium">SH-4, Blank Cheque</div></div>
                    <div><div className="text-slate-500">Outstanding</div><div className="font-medium text-red-600">₹8,90,000</div></div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Approved Security to Invoke</label>
                    <div className="space-y-2">
                      {['SH-4 invocation', 'CDSL pledge invocation', 'Blank-dated cheque presentation'].map(opt => (
                        <label key={opt} className="flex items-center gap-3 text-sm cursor-pointer p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                          <input
                            type="checkbox"
                            checked={invokedSecurities.includes(opt)}
                            onChange={() => toggleInvocation(opt)}
                            className="accent-green-600"
                          />
                          {opt}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Invocation Date</label>
                    <input type="date" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Remarks</label>
                    <textarea rows={3} placeholder="Record invocation details, amounts recovered, reference numbers…" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" />
                  </div>
                  {canInvokeSecurity && (
                    <div className="flex gap-3">
                      <button
                        onClick={() => {
                          setRecoveryLogged(true);
                          setBorrowerNoticeSent(true);
                        }}
                        disabled={invokedSecurities.length === 0}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                      >
                        <Shield size={16} />
                        {recoveryLogged ? 'Invocation Recorded' : 'Invoke Security'}
                      </button>
                      <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                        <FileText size={16} />
                        Download Invocation Notice
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default DefaultRecoveryHub;
`;

fs.writeFileSync(path.join(__dirname, 'src/pages/defaults/DefaultRecoveryHub.tsx'), code);
console.log('Update successful');
