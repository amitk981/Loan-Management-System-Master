import React, { useState } from 'react';
import {
  AlertTriangle, Clock, FileText, CheckCircle2, XCircle,
  ChevronRight, Calendar, IndianRupee, User, MessageSquare,
  Shield, Gavel, ArrowRight, BarChart2
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
}

const defaultCases: DefaultCase[] = [
  { id: 'dc001', loanNo: 'LO00000042', borrower: 'Ganesh Thorat',   outstanding: 350000, overdueDays: 45,  dpdBucket: '31_60',   status: 'grace_period',  lastAction: 'Reminder sent 10 Jun', nextAction: 'Grace period expires 15 Sep 2025' },
  { id: 'dc002', loanNo: 'LO00000038', borrower: 'Malti Shinde',    outstanding: 180000, overdueDays: 95,  dpdBucket: '91_365',  status: 'default_review',lastAction: 'Grace expired',        nextAction: 'Submit Non-Payment Note to SC' },
  { id: 'dc003', loanNo: 'LO00000035', borrower: 'Kisan FPC Ltd',   outstanding: 890000, overdueDays: 187, dpdBucket: '91_365',  status: 'recovery_approved', lastAction: 'SC approved recovery', nextAction: 'Invoke SH-4 / blank cheque' },
];

const DefaultRecoveryHub: React.FC = () => {
  const { currentUser, can } = useRole();
  const [activeTab, setActiveTab] = useState<DefaultTab>('cases');
  const [selectedCase, setSelectedCase] = useState<DefaultCase | null>(defaultCases[0]);
  const [extensionReason, setExtensionReason] = useState('');
  const [nonPaymentNote, setNonPaymentNote] = useState('');
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [recoveryApproved, setRecoveryApproved] = useState(false);

  const tabs: { id: DefaultTab; label: string; badge?: number }[] = [
    { id: 'cases',       label: 'Default Cases',        badge: defaultCases.length },
    { id: 'grace',       label: 'Grace Period / Extension' },
    { id: 'non_payment', label: 'Non-Payment Note' },
    { id: 'recovery',    label: 'Recovery Approval' },
    { id: 'security',    label: 'Security Invocation' },
  ];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Default & Recovery Management</h1>
        <p className="text-sm text-slate-500 mt-1">Manage overdue loans, grace periods, extension notes, recovery approvals and security invocation.</p>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Overdue (1–30 DPD)',   value: '2',         amount: '₹2.1L', color: 'text-amber-600',  bg: 'bg-amber-50',  border: 'border-amber-100' },
          { label: 'Grace Period',          value: '3',         amount: '₹5.4L', color: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-100' },
          { label: 'Default Review',        value: '2',         amount: '₹10.7L',color: 'text-red-600',   bg: 'bg-red-50',    border: 'border-red-100' },
          { label: 'Recovery Approved',     value: '1',         amount: '₹8.9L', color: 'text-violet-700', bg: 'bg-violet-50', border: 'border-violet-100' },
        ].map(kpi => (
          <div key={kpi.label} className={`${kpi.bg} ${kpi.border} border rounded-xl p-4`}>
            <div className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</div>
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
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
              {tab.badge !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${activeTab === tab.id ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Cases list + detail */}
      {activeTab === 'cases' && (
        <div className="flex gap-6">
          {/* List */}
          <div className="w-80 flex-shrink-0 space-y-2">
            {defaultCases.map(c => (
              <button
                key={c.id}
                onClick={() => setSelectedCase(c)}
                className={`w-full text-left border rounded-xl p-4 transition-all ${
                  selectedCase?.id === c.id
                    ? 'border-green-300 bg-green-50'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs font-mono font-medium text-slate-600">{c.loanNo}</span>
                  <StatusBadge label={c.status} size="sm" />
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
                      <StatusBadge label={selectedCase.status} />
                    </div>
                    <div className="text-slate-600 mt-0.5">{selectedCase.borrower}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-500">Outstanding</div>
                    <div className="text-2xl font-bold text-red-600">₹{selectedCase.outstanding.toLocaleString('en-IN')}</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  {[
                    ['DPD Bucket', selectedCase.dpdBucket.replace('_', '–') + ' days'],
                    ['Overdue Days', `${selectedCase.overdueDays} days`],
                    ['Last Action', selectedCase.lastAction],
                    ['Next Action', selectedCase.nextAction],
                  ].map(([k, v]) => (
                    <div key={k}>
                      <div className="text-xs text-slate-500">{k}</div>
                      <div className="font-medium text-slate-800 mt-0.5">{v}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Default workflow */}
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h3 className="font-semibold text-slate-800 mb-4">Default Resolution Workflow</h3>
                <div className="space-y-3">
                  {[
                    { step: '1', label: 'Reminder issued (call/SMS)',        done: true },
                    { step: '2', label: 'Grace period started (90 days)',    done: selectedCase.overdueDays > 30 },
                    { step: '3', label: 'Extension note (if applicable)',    done: false },
                    { step: '4', label: 'Non-payment note to Sanction Committee', done: selectedCase.status === 'recovery_approved' },
                    { step: '5', label: 'Recovery action approved',          done: selectedCase.status === 'recovery_approved' },
                    { step: '6', label: 'Security invocation / legal action',done: false },
                  ].map(s => (
                    <div key={s.step} className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                        s.done ? 'bg-green-600 text-white' : 'bg-slate-100 text-slate-500'
                      }`}>
                        {s.done ? <CheckCircle2 size={14} /> : s.step}
                      </div>
                      <span className={`text-sm ${s.done ? 'text-slate-700' : 'text-slate-400'}`}>{s.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {can('manage_defaults') && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium text-amber-900 text-sm">Action Required</div>
                    <div className="text-xs text-amber-700 mt-0.5">{selectedCase.nextAction}</div>
                  </div>
                  <button
                    onClick={() => setActiveTab('non_payment')}
                    className="flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Take Action <ArrowRight size={14} />
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
                  {defaultCases.map(c => (
                    <option key={c.id}>{c.loanNo} — {c.borrower}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Extension Type</label>
                <select className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option>90-day Grace Period</option>
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
              {can('manage_defaults') && (
                <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                  <FileText size={16} />
                  Submit Extension Note
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
              {(can('manage_defaults') || can('do_appraisal')) && (
                <button className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                  <MessageSquare size={16} />
                  Submit to Sanction Committee
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recovery Approval */}
      {activeTab === 'recovery' && (
        <div className="max-w-2xl space-y-5">
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
                <StatusBadge label="recovery_approved" />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle2 size={14} />
                  Non-payment note submitted by Credit Manager on 20 Apr 2025
                </div>
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle2 size={14} />
                  Sanction Committee reviewed on 25 Apr 2025
                </div>
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle2 size={14} />
                  CFO approved recovery action on 28 Apr 2025
                </div>
              </div>
            </div>

            {can('approve_recovery') && !recoveryApproved && (
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
                  <textarea rows={3} placeholder="CFO remarks on recovery decision…" className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" />
                </div>
                <button
                  onClick={() => { setRecoveryApproved(true); setShowApproveModal(false); }}
                  className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
                >
                  <Gavel size={16} />
                  Approve Recovery Action
                </button>
              </div>
            )}
            {recoveryApproved && (
              <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-xl p-4">
                <CheckCircle2 size={18} />
                <span className="text-sm font-medium">Recovery action approved. Security invocation has been notified to Company Secretary.</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Security Invocation */}
      {activeTab === 'security' && (
        <div className="max-w-2xl space-y-5">
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
                <div><div className="text-slate-500">Recovery Approval</div><div className="font-medium text-green-700">Approved 28 Apr 2025</div></div>
                <div><div className="text-slate-500">Securities Held</div><div className="font-medium">SH-4, Blank Cheque</div></div>
                <div><div className="text-slate-500">Outstanding</div><div className="font-medium text-red-600">₹8,90,000</div></div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Security to Invoke</label>
                <div className="space-y-2">
                  {['SH-4 (share transfer to company)', 'Blank cheque presentment', 'Both SH-4 and blank cheque'].map(opt => (
                    <label key={opt} className="flex items-center gap-3 text-sm cursor-pointer p-3 rounded-lg border border-slate-100 hover:bg-slate-50">
                      <input type="checkbox" className="accent-green-600" />
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
              {can('manage_compliance') && (
                <div className="flex gap-3">
                  <button className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                    <Shield size={16} />
                    Invoke Security
                  </button>
                  <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                    <FileText size={16} />
                    Download Invocation Notice
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DefaultRecoveryHub;
