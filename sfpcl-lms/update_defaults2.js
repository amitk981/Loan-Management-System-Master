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
  approvedRecoveryMode?: string;
}

const defaultCases: DefaultCase[] = [
  { id: 'dc001', loanNo: 'LO00000042', borrower: 'Ganesh Thorat',   outstanding: 350000, overdueDays: 45,  dpdBucket: '31_60',   status: 'grace_period',  lastAction: 'Reminder sent 10 Jun', nextAction: 'Grace period expires 15 Sep 2025', graceStartDate: '15 Jun 2025', graceEndDate: '15 Sep 2025', daysRemaining: 45, reminderCount: 3, lastReminderDate: '10 Jun 2025', repaymentDuringGrace: 0 },
  { id: 'dc002', loanNo: 'LO00000038', borrower: 'Malti Shinde',    outstanding: 180000, overdueDays: 95,  dpdBucket: '91_365',  status: 'default_review',lastAction: 'Grace expired',        nextAction: 'Submit Non-Payment Note to SC' },
  { id: 'dc003', loanNo: 'LO00000035', borrower: 'Kisan FPC Ltd',   outstanding: 890000, overdueDays: 187, dpdBucket: '91_365',  status: 'recovery_approved', lastAction: 'SC approved recovery', nextAction: 'Invoke SH-4 / blank cheque', approvedRecoveryMode: 'SH-4 invocation' },
];

const DefaultRecoveryHub: React.FC = () => {
  const { currentUser } = useRole();
  const role = currentUser.role;

  // Permissions
  const canAccess = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'compliance_team', 'company_secretary', 'sanction_committee'].includes(role);
  const canCreditAct = ['credit_manager'].includes(role);
  const canApproveRecovery = ['cfo', 'sanction_committee'].includes(role);
  const canInvokeSecurity = ['compliance_team', 'company_secretary'].includes(role);
  
  const [activeTab, setActiveTab] = useState<DefaultTab>('cases');
  const [selectedCase, setSelectedCase] = useState<DefaultCase>(defaultCases[0]);
  
  const [extensionReason, setExtensionReason] = useState('');
  const [extensionEvidence, setExtensionEvidence] = useState(false);
  const [extensionSubmitted, setExtensionSubmitted] = useState(false);

  const [nonPaymentNote, setNonPaymentNote] = useState('');
  const [nonPaymentEvidence, setNonPaymentEvidence] = useState(false);
  const [nonPaymentSubmitted, setNonPaymentSubmitted] = useState(false);

  const [localRecoveryApproved, setLocalRecoveryApproved] = useState(false);
  const [recoveryLogged, setRecoveryLogged] = useState(false);
  
  const [invocationDate, setInvocationDate] = useState('');
  const [invocationRemarks, setInvocationRemarks] = useState('');

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

  // Determine workflow impact strictly per case state
  let wfImpact = [];
  if (isGrace) {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: 'not_applicable', note: 'Not Started / Not Applicable' },
      { label: 'Security Register', status: 'locked', note: 'Locked' },
      { label: 'Borrower Notice', status: 'reminder_sent', note: 'Reminder sent, if reminder exists' },
      { label: 'Audit Trail', status: 'updated', note: 'Updated' },
    ];
  } else if (isDefaultReview) {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: 'pending_update', note: 'Log entry is staged after non-payment and invocation action.' },
      { label: 'Security Register', status: 'locked', note: 'Locked' },
      { label: 'Borrower Notice', status: 'final_notice_staged', note: 'Final notice generation pending approval.' },
      { label: 'Audit Trail', status: 'updated', note: 'Updated' },
    ];
  } else {
    wfImpact = [
      { label: 'DPD Monitoring', status: 'updated', note: 'Selected loan remains visible in overdue and DPD review queues.' },
      { label: 'Recovery Log', status: 'updated', note: 'Updated' },
      { label: 'Security Register', status: 'ready', note: 'Ready / Invocation Pending' },
      { label: 'Borrower Notice', status: recoveryLogged ? 'generated' : 'pending', note: recoveryLogged ? 'Generated' : 'Pending' },
      { label: 'Audit Trail', status: 'updated', note: 'Updated' },
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
            <p className="text-xs text-slate-500 mt-0.5">Current status across monitoring, notices, registers and audit.</p>
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
                <div><strong>Grace Period:</strong> 90 days from missed repayment. Reminder calls and SMS issued weekly. Interest treatment during grace follows configured policy.</div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
                <Calendar size={16} className="text-amber-600 mt-0.5 flex-shrink-0" />
                <div><strong>Extension (non-intentional default):</strong> One-year extension requires configured approval and Extension Note.</div>
              </div>
            </div>
          </div>

          {isGrace ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4">Grace Period Tracking</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
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
                <div>
                  <div className="text-xs text-slate-500">Grace Status</div>
                  <div className="font-medium text-slate-800 mt-0.5">Active</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4">Prepare One-Year Extension Note</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Account</label>
                  <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                    <option>{selectedCase.loanNo} — {selectedCase.borrower}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Reason Assessment</label>
                  <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                    <option>Non-Intentional</option>
                    <option>Intentional</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Extension Recommendation</label>
                  <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                    <option>Recommend 1-Year Extension</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Reason for non-payment</label>
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
                  <button onClick={() => setExtensionEvidence(!extensionEvidence)} className={\`w-full border-2 border-dashed rounded-xl p-4 text-center text-sm transition-colors \${extensionEvidence ? 'border-green-500 text-green-700 bg-green-50' : 'border-slate-200 text-slate-400 cursor-pointer hover:border-green-300 hover:text-green-600'}\`}>
                    {extensionEvidence ? 'Evidence Attached (crop_survey.pdf)' : 'Click to attach crop survey report, insurance claim, or other evidence'}
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Prepared By</label>
                    <input type="text" readOnly value={currentUser.name} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Submit To</label>
                    <input type="text" readOnly value="Sanction Committee / CFO" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                  </div>
                </div>
                {canCreditAct && (
                  <button
                    onClick={() => setExtensionSubmitted(true)}
                    disabled={!extensionReason || !extensionEvidence}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                  >
                    <FileText size={16} />
                    {extensionSubmitted ? 'Submitted for Extension Review' : 'Submit for Extension Review'}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Non-Payment Note */}
      {activeTab === 'non_payment' && (
        <div className="max-w-2xl space-y-5">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle size={18} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-amber-800">
              Prepare this note only after grace/extension outcome is recorded and unpaid principal remains.
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Note for Non-Payment</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Loan Account</label>
                  <input type="text" readOnly value={selectedCase.loanNo} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Borrower</label>
                  <input type="text" readOnly value={selectedCase.borrower} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4">
                <div><div className="text-slate-500">Original Due Date</div><div className="font-medium text-slate-900">15 Dec 2024</div></div>
                <div><div className="text-slate-500">Grace Period Outcome</div><div className="font-medium text-slate-900">Expired</div></div>
                <div><div className="text-slate-500">Extension Outcome</div><div className="font-medium text-slate-900">Not Applicable</div></div>
                <div><div className="text-slate-500">Amount Still Unpaid</div><div className="font-medium text-red-600">₹{selectedCase.outstanding.toLocaleString('en-IN')}</div></div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Intentional / Non-Intentional Assessment</label>
                  <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                    <option>Intentional Default</option>
                    <option>Non-Intentional</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">Evidence Reviewed</label>
                  <button onClick={() => setNonPaymentEvidence(!nonPaymentEvidence)} className={\`w-full border-2 border-dashed rounded-xl p-2.5 text-center text-sm transition-colors \${nonPaymentEvidence ? 'border-green-500 text-green-700 bg-green-50' : 'border-slate-200 text-slate-400 cursor-pointer hover:border-green-300 hover:text-green-600'}\`}>
                    {nonPaymentEvidence ? 'Evidence Attached' : 'Attach Evidence'}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Reason for non-payment</label>
                <textarea
                  value={nonPaymentNote}
                  onChange={e => setNonPaymentNote(e.target.value)}
                  rows={4}
                  placeholder="Summarise reason for non-payment, actions taken, borrower's response…"
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Credit Assessment Team Recommendation</label>
                <div className="space-y-2">
                  {['Recommend further extension review', 'Recommend write-off review', 'Recommend legal recovery review', 'Recommend security invocation review'].map(opt => (
                    <label key={opt} className="flex items-center gap-3 text-sm cursor-pointer p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                      <input type="radio" name="recovery_action" className="accent-green-600" />
                      {opt}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Prepared By</label>
                <input type="text" readOnly value={currentUser.name} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
              </div>

              {canCreditAct && (
                <button
                  onClick={() => {
                    setNonPaymentSubmitted(true);
                  }}
                  disabled={!nonPaymentNote || !nonPaymentEvidence}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                >
                  <MessageSquare size={16} />
                  {nonPaymentSubmitted ? 'Submitted to Sanction Committee' : 'Submit Note to Sanction Committee'}
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
              <p className="text-xs text-slate-500 mb-4">Requires assigned Sanction Committee / CFO approvals as per authority matrix.</p>

              <div className="border border-slate-200 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-medium text-slate-900">{selectedCase.loanNo} — {selectedCase.borrower}</div>
                    <div className="text-xs text-slate-500">Outstanding: ₹{selectedCase.outstanding.toLocaleString('en-IN')} · DPD: {selectedCase.overdueDays} days</div>
                  </div>
                  <StatusBadge label={(localRecoveryApproved || selectedCase.status === 'recovery_approved') ? 'Recovery Approved' : 'Awaiting Sanction Committee Decision'} type={(localRecoveryApproved || selectedCase.status === 'recovery_approved') ? 'success' : 'warning'} />
                </div>
                
                <h4 className="text-xs font-semibold text-slate-700 mb-2 mt-4 uppercase tracking-wider">Approval Package</h4>
                <div className="space-y-2 text-sm bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Note for Non-Payment
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Reason assessment
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Loan ledger
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Security instruments (SH-4 / CDSL pledge status)
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Blank cheque custody
                  </div>
                  <div className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 size={14} className="text-green-600" /> Borrower communication log
                  </div>
                </div>
              </div>

              {!canApproveRecovery ? (
                <div className="bg-slate-50 p-4 rounded-lg text-sm text-slate-600 text-center border border-slate-100">
                  You do not have permission to approve recovery action.
                </div>
              ) : (
                (!localRecoveryApproved && selectedCase.status !== 'recovery_approved') && (
                  <div className="space-y-4 mt-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Decision Action</label>
                      <div className="space-y-2">
                        {['Approve legal recovery action', 'Approve security invocation (SH-4)', 'Approve security invocation (Blank Cheque)', 'Approve write-off (exceptional, with board approval)', 'Return for further negotiation'].map(opt => (
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
                )
              )}
              
              {(localRecoveryApproved || selectedCase.status === 'recovery_approved') && (
                <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-xl p-4 mt-4">
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
          {(!localRecoveryApproved && selectedCase.status !== 'recovery_approved') ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <Lock size={32} className="mx-auto text-slate-300 mb-3" />
              <div className="font-semibold text-slate-700">Security Invocation Locked</div>
              <div className="text-sm text-slate-500 mt-1">Security invocation is permitted only after approved recovery decision.</div>
            </div>
          ) : (
            <>
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
                <Shield size={18} className="text-red-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-red-800">
                  Security invocation is permitted only after approved recovery decision. All invocations are recorded in the Security Register.
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-900 mb-4">Security Invocation</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4">
                    <div><div className="text-slate-500">Loan</div><div className="font-medium">{selectedCase.loanNo} — {selectedCase.borrower}</div></div>
                    <div><div className="text-slate-500">Recovery Approval</div><div className="font-medium text-green-700">Approved</div></div>
                    <div><div className="text-slate-500">Approved Recovery Action Ref.</div><div className="font-medium">RA-2025-098</div></div>
                    <div><div className="text-slate-500">Security Custody Ref.</div><div className="font-medium">SEC-1102</div></div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Approved Recovery Mode</label>
                    <div className="space-y-2">
                      <label className="flex items-center gap-3 text-sm p-3 rounded-lg border border-slate-200 bg-slate-50">
                        <input
                          type="checkbox"
                          checked={true}
                          readOnly
                          className="accent-green-600"
                        />
                        {selectedCase.approvedRecoveryMode || 'SH-4 invocation'}
                      </label>
                    </div>
                  </div>

                  {(!selectedCase.approvedRecoveryMode || selectedCase.approvedRecoveryMode.includes('SH-4')) && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Share Certificate Details</label>
                        <input type="text" placeholder="Cert #..." className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1.5">Number of Shares</label>
                        <input type="number" placeholder="Qty..." className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm" />
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Invocation Date (Transfer Init)</label>
                      <input 
                        type="date" 
                        value={invocationDate}
                        onChange={e => setInvocationDate(e.target.value)}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Execution Status</label>
                      <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                        <option>Initiated</option>
                        <option>Completed</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Borrower Notice Status</label>
                      <input type="text" readOnly value={recoveryLogged ? 'Notice Generated' : 'Pending Generation'} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1.5">Security Register Entry</label>
                      <input type="text" readOnly value={recoveryLogged ? 'Recorded' : 'Pending'} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1.5">Remarks / Proceeds Received</label>
                    <textarea 
                      value={invocationRemarks}
                      onChange={e => setInvocationRemarks(e.target.value)}
                      rows={3} 
                      placeholder="Record invocation details, amounts recovered, reference numbers…" 
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" 
                    />
                  </div>

                  {!canInvokeSecurity ? (
                    <div className="bg-slate-50 p-4 rounded-lg text-sm text-slate-600 text-center border border-slate-100">
                      Security invocation can be recorded only by authorised legal/compliance role after recovery approval.
                    </div>
                  ) : (
                    <div className="flex gap-3 mt-2">
                      <button
                        onClick={() => {
                          setRecoveryLogged(true);
                          setBorrowerNoticeSent(true);
                        }}
                        disabled={!invocationDate || !invocationRemarks}
                        className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
                      >
                        <Shield size={16} />
                        {recoveryLogged ? 'Security Invocation Recorded' : 'Record Security Invocation'}
                      </button>
                      <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                        <FileText size={16} />
                        {recoveryLogged ? 'Download Invocation Notice' : 'Preview Invocation Notice'}
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
