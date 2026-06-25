import React, { useState } from 'react';
import { Banknote, Plus, CheckCircle2, Clock, XCircle } from 'lucide-react';
import RepaymentLedger from '../../components/loan/RepaymentLedger';
import StatusBadge from '../../components/ui/StatusBadge';
import { loanAccounts, repaymentRecords } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const SAP_ICONS = {
  posted: <CheckCircle2 size={14} className="text-green-600" />,
  pending: <Clock size={14} className="text-amber-500" />,
  failed: <XCircle size={14} className="text-red-500" />,
};

const RepaymentsHub: React.FC = () => {
  const [selectedLoan, setSelectedLoan] = useState<string>(loanAccounts[0]?.id || '');
  const [showPostModal, setShowPostModal] = useState(false);
  const [postAmount, setPostAmount] = useState('');
  const [postChannel, setPostChannel] = useState('direct_rtgs');
  const [postRef, setPostRef] = useState('');
  const [posted, setPosted] = useState(false);

  const loan = loanAccounts.find(l => l.id === selectedLoan);

  const totalPending = repaymentRecords.filter(r => r.sapEntryStatus === 'pending').length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Repayments Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {totalPending > 0 && (
              <span className="text-amber-700 font-medium">{totalPending} SAP entries pending · </span>
            )}
            {loanAccounts.length} active accounts
          </p>
        </div>
        <button onClick={() => setShowPostModal(true)} className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          Post Repayment
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Account selector */}
        <div className="card p-0 overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Loan Accounts</p>
          </div>
          <div className="divide-y divide-slate-100">
            {loanAccounts.map(l => (
              <button
                key={l.id}
                onClick={() => setSelectedLoan(l.id)}
                className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selectedLoan === l.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
              >
                <Banknote size={16} className="text-green-600 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-900 num text-sm">{l.accountNumber}</div>
                  <div className="text-xs text-slate-500 truncate">{l.memberName}</div>
                  <div className="text-xs text-slate-400 num">OS: {fmt(l.outstandingPrincipal)}</div>
                </div>
                <StatusBadge label={l.status} size="sm" />
              </button>
            ))}
          </div>
        </div>

        {/* Repayment ledger */}
        {loan && (
          <div className="lg:col-span-2 card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-slate-900 num">{loan.accountNumber}</h2>
                <p className="text-sm text-slate-500">{loan.memberName}</p>
              </div>
              <StatusBadge label={loan.status} size="sm" />
            </div>
            <RepaymentLedger
              loanAccountId={loan.id}
              outstandingPrincipal={loan.outstandingPrincipal}
              disbursedAmount={loan.disbursedAmount}
            />
          </div>
        )}
      </div>

      {/* Post Repayment Modal */}
      {showPostModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="p-5 border-b border-slate-200">
              <h3 className="text-lg font-bold text-slate-900">Post Repayment</h3>
              <p className="text-sm text-slate-500 mt-0.5">Record a new repayment receipt</p>
            </div>
            <div className="p-5 space-y-4">
              {posted ? (
                <div className="flex items-center gap-2 text-green-700 bg-green-50 rounded-lg p-4">
                  <CheckCircle2 size={20} /> Repayment posted successfully. SAP entry queued.
                </div>
              ) : (
                <>
                  <div>
                    <label className="field-label">Loan Account</label>
                    <select
                      value={selectedLoan}
                      onChange={e => setSelectedLoan(e.target.value)}
                      className="field-select"
                    >
                      {loanAccounts.map(l => (
                        <option key={l.id} value={l.id}>{l.accountNumber} — {l.memberName}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="field-label">Amount (₹)</label>
                    <input
                      type="number"
                      value={postAmount}
                      onChange={e => setPostAmount(e.target.value)}
                      className="field-input"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="field-label">Payment Channel</label>
                    <select
                      value={postChannel}
                      onChange={e => setPostChannel(e.target.value)}
                      className="field-select"
                    >
                      <option value="direct_rtgs">RTGS</option>
                      <option value="direct_neft">NEFT</option>
                      <option value="subsidiary_deduction">Subsidiary Deduction</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="field-label">Bank Reference / UTR</label>
                    <input
                      type="text"
                      value={postRef}
                      onChange={e => setPostRef(e.target.value)}
                      className="field-input"
                      placeholder="e.g. UTR20260624123456"
                    />
                  </div>
                </>
              )}
            </div>
            <div className="p-5 border-t border-slate-200 flex justify-end gap-3">
              <button onClick={() => { setShowPostModal(false); setPosted(false); setPostAmount(''); setPostRef(''); }} className="btn-secondary">
                {posted ? 'Close' : 'Cancel'}
              </button>
              {!posted && (
                <button
                  className="btn-primary disabled:opacity-50"
                  disabled={!postAmount || !postRef}
                  onClick={() => setPosted(true)}
                >
                  Post Entry
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RepaymentsHub;
