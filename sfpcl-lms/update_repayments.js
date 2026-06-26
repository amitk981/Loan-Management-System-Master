const fs = require('fs');
const path = require('path');

const formatNumber = `const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');`;

const repaymentLedgerCode = `import React from 'react';
import { CheckCircle2, Clock, XCircle } from 'lucide-react';
import { repaymentRecords } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
};

const SAP_ICONS = {
  posted: <CheckCircle2 size={14} className="text-green-600" />,
  pending: <Clock size={14} className="text-amber-500" />,
  failed: <XCircle size={14} className="text-red-500" />,
};

const CHANNEL_LABELS: Record<string, string> = {
  direct_rtgs: 'RTGS',
  direct_neft: 'NEFT',
  subsidiary_deduction: 'Subsidiary Deduction',
  other: 'Other',
};

interface RepaymentLedgerProps {
  loanAccountId: string;
  outstandingPrincipal?: number;
  disbursedAmount?: number;
}

const RepaymentLedger: React.FC<RepaymentLedgerProps> = ({
  loanAccountId, disbursedAmount = 0,
}) => {
  const records = repaymentRecords.filter(r => r.loanAccountId === loanAccountId);

  const totalPaid = records.reduce((s, r) => s + r.amount, 0);
  const totalPrincipal = records.reduce((s, r) => s + r.principalAllocation, 0);
  const totalInterest = records.reduce((s, r) => s + r.interestAllocation, 0);
  
  // Principal O/S = Disbursed Principal - Principal Paid + capitalised principal adjustments, if any.
  // We'll ignore capitalisation for this basic ledger unless passed in, so:
  const calculatedOutstanding = disbursedAmount - totalPrincipal;

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
          <div className="text-xs text-slate-500 font-medium">Disbursed</div>
          <div className="text-lg font-bold text-slate-900 num mt-0.5">{fmt(disbursedAmount)}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3 text-center">
          <div className="text-xs text-green-700 font-medium">Total Paid</div>
          <div className="text-lg font-bold text-green-900 num mt-0.5">{fmt(totalPaid)}</div>
        </div>
        <div className="bg-amber-50 rounded-lg border border-amber-200 p-3 text-center">
          <div className="text-xs text-amber-700 font-medium">Principal O/S</div>
          <div className="text-lg font-bold text-amber-900 num mt-0.5">{fmt(calculatedOutstanding)}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
          <div className="text-xs text-slate-500 font-medium">Interest Collected</div>
          <div className="text-lg font-bold text-slate-900 num mt-0.5">{fmt(totalInterest)}</div>
        </div>
      </div>

      {/* Ledger table */}
      {records.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-sm">No repayment receipts recorded yet.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="table-header text-left">Receipt ID</th>
                <th className="table-header text-left">Date</th>
                <th className="table-header text-right">Amount</th>
                <th className="table-header text-right">Principal</th>
                <th className="table-header text-right">Interest</th>
                <th className="table-header text-left">Channel & Ref</th>
                <th className="table-header text-left">SAP Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map(r => (
                <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-cell font-mono text-xs text-slate-500">{r.id}</td>
                  <td className="table-cell">
                    <div>{formatDate(r.receiptDate)}</div>
                    <div className="text-[10px] text-slate-400">Val: {formatDate(r.receiptDate)}</div>
                  </td>
                  <td className="table-cell text-right num font-semibold">{fmt(r.amount)}</td>
                  <td className="table-cell text-right num text-green-700">{fmt(r.principalAllocation)}</td>
                  <td className="table-cell text-right num text-amber-700">{fmt(r.interestAllocation)}</td>
                  <td className="table-cell">
                    <div className="font-medium text-slate-800">{CHANNEL_LABELS[r.channel]}</div>
                    <div className="text-xs text-slate-500 num truncate max-w-[120px]" title={r.bankReference}>{r.bankReference}</div>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1">
                      {SAP_ICONS[r.sapEntryStatus]}
                      <span className="text-xs capitalize">{r.sapEntryStatus}</span>
                    </div>
                    {r.sapEntryStatus === 'posted' && (
                       <div className="text-[10px] text-slate-400 mt-0.5">By System on {formatDate(r.receiptDate)}</div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t-2 border-slate-200 bg-slate-50">
              <tr>
                <td colSpan={2} className="table-cell font-semibold">Total</td>
                <td className="table-cell text-right num font-bold">{fmt(totalPaid)}</td>
                <td className="table-cell text-right num font-bold text-green-700">{fmt(totalPrincipal)}</td>
                <td className="table-cell text-right num font-bold text-amber-700">{fmt(totalInterest)}</td>
                <td colSpan={2} />
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
};

export default RepaymentLedger;
`;


const repaymentsHubCode = `import React, { useState } from 'react';
import { Banknote, Plus, CheckCircle2, Clock, XCircle, FileText } from 'lucide-react';
import RepaymentLedger from '../../components/loan/RepaymentLedger';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanAccounts, repaymentRecords } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '';
  return new Date(dateStr).toISOString().split('T')[0];
};

const RepaymentsHub: React.FC = () => {
  const { currentUser } = useRole();
  const role = currentUser.role;

  // Active "Record Receipt" only to Accounts / Credit Manager
  const canRecordReceipt = ['admin', 'accounts_team', 'senior_manager_finance', 'deputy_manager_finance', 'credit_manager'].includes(role);
  // View-only allowed for auditor, cfo, etc.
  const isAllowed = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'sales', 'field_officer', 'compliance_team'].includes(role);

  const activeOrOverdueLoans = loanAccounts.filter(l => l.status === 'active' || l.status === 'overdue' || l.status === 'grace_period' || l.status.includes('recovery'));
  
  const [selectedLoan, setSelectedLoan] = useState<string>(activeOrOverdueLoans[0]?.id || '');
  const [showPostModal, setShowPostModal] = useState(false);
  const [postAmount, setPostAmount] = useState('');
  const [postChannel, setPostChannel] = useState('direct_rtgs');
  const [postRef, setPostRef] = useState('');
  const [postDate, setPostDate] = useState(formatDate(new Date().toISOString()));
  const [postBank, setPostBank] = useState('SFPCL HDFC A/c');
  const [posted, setPosted] = useState(false);

  if (!isAllowed) {
    return (
      <div className="p-6">
        <AlertBanner type="error" title="Access Denied" message="You do not have permission to view the Repayments Hub." />
      </div>
    );
  }

  const loan = loanAccounts.find(l => l.id === selectedLoan);
  const totalPending = repaymentRecords.filter(r => r.sapEntryStatus === 'pending').length;

  // Handle modal logic
  const selectedModalLoan = loanAccounts.find(l => l.id === selectedLoan);
  let allocationPreview = null;
  if (selectedModalLoan && postAmount && Number(postAmount) > 0) {
    const amt = Number(postAmount);
    // Principal OS = disbursed - paid
    const priorPrincipalPaid = repaymentRecords.filter(r => r.loanAccountId === selectedModalLoan.id).reduce((s, r) => s + r.principalAllocation, 0);
    const actualPrincipalOs = selectedModalLoan.disbursedAmount - priorPrincipalPaid;
    
    let allocatedPrincipal = 0;
    let allocatedInterest = 0;
    
    if (amt <= actualPrincipalOs) {
      allocatedPrincipal = amt;
      allocatedInterest = 0;
    } else {
      allocatedPrincipal = actualPrincipalOs;
      allocatedInterest = amt - actualPrincipalOs;
    }
    
    allocationPreview = {
      principal: allocatedPrincipal,
      interest: allocatedInterest,
      unallocated: 0,
      newPrincipalOs: actualPrincipalOs - allocatedPrincipal
    };
  }

  const isModalLoanClosed = selectedModalLoan?.status === 'closed';

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Repayments Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {totalPending > 0 && (
              <span className="text-amber-700 font-medium">{totalPending} SAP entries pending · </span>
            )}
            {loanAccounts.length} loan accounts shown
          </p>
        </div>
        {canRecordReceipt && (
          <button onClick={() => {
            setShowPostModal(true);
            setPosted(false);
            setPostAmount('');
            setPostRef('');
          }} className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            Record Receipt
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Account selector */}
        <div className="card p-0 overflow-hidden flex flex-col max-h-[80vh]">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Loan Accounts</p>
          </div>
          <div className="divide-y divide-slate-100 overflow-y-auto flex-1">
            {loanAccounts.map(l => {
               // Dynamic calculate Principal OS
               const priorPrincipalPaid = repaymentRecords.filter(r => r.loanAccountId === l.id).reduce((s, r) => s + r.principalAllocation, 0);
               const actualPrincipalOs = l.disbursedAmount - priorPrincipalPaid;
               return (
                <button
                  key={l.id}
                  onClick={() => setSelectedLoan(l.id)}
                  className={\`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left \${selectedLoan === l.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}\`}
                >
                  <Banknote size={16} className="text-green-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm">{l.accountNumber}</div>
                    <div className="text-xs text-slate-500 truncate">{l.memberName}</div>
                    <div className="text-xs text-slate-400 num">Principal O/S: {fmt(actualPrincipalOs)}</div>
                  </div>
                  <StatusBadge label={l.status === 'closed' ? 'Closed' : l.status.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase())} size="sm" type={l.status === 'closed' ? 'slate' : 'success'} />
                </button>
               );
            })}
          </div>
        </div>

        {/* Repayment ledger */}
        {loan && (
          <div className="lg:col-span-2 card flex flex-col max-h-[80vh]">
            <div className="flex items-center justify-between mb-4 flex-shrink-0">
              <div>
                <h2 className="text-base font-bold text-slate-900 num">{loan.accountNumber}</h2>
                <p className="text-sm text-slate-500">{loan.memberName}</p>
              </div>
              <StatusBadge label={loan.status === 'closed' ? 'Closed' : loan.status.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase())} size="sm" type={loan.status === 'closed' ? 'slate' : 'success'} />
            </div>
            <div className="overflow-y-auto flex-1 pr-2">
              <RepaymentLedger
                loanAccountId={loan.id}
                disbursedAmount={loan.disbursedAmount}
              />
            </div>
          </div>
        )}
      </div>

      {/* Post Repayment Modal */}
      {showPostModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="p-5 border-b border-slate-200">
              <h3 className="text-lg font-bold text-slate-900">Record Repayment Receipt</h3>
              <p className="text-sm text-slate-500 mt-0.5">Record direct repayment receipt and allocation.</p>
            </div>
            <div className="p-5 space-y-4">
              {posted ? (
                <div className="flex flex-col items-center gap-3 text-green-700 bg-green-50 border border-green-100 rounded-xl p-6 text-center">
                  <CheckCircle2 size={32} />
                  <div>
                    <div className="font-semibold text-green-900 text-lg">Receipt Recorded</div>
                    <div className="text-sm mt-1">SAP Entry Status: <span className="font-medium text-amber-600">Pending</span></div>
                    <div className="text-xs mt-1">Posting due next working day.</div>
                  </div>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <label className="field-label">Loan Account</label>
                      <select
                        value={selectedLoan}
                        onChange={e => setSelectedLoan(e.target.value)}
                        className="field-select"
                      >
                        {loanAccounts.map(l => (
                          <option key={l.id} value={l.id} disabled={l.status === 'closed'}>
                            {l.accountNumber} — {l.memberName} {l.status === 'closed' ? '(Closed)' : ''}
                          </option>
                        ))}
                      </select>
                      {isModalLoanClosed && (
                        <div className="text-xs text-red-600 mt-1 font-medium flex items-center gap-1">
                          <XCircle size={12} /> Closed loans cannot receive direct repayments.
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="field-label">Receipt Type</label>
                      <select
                        value={postChannel}
                        onChange={e => setPostChannel(e.target.value)}
                        className="field-select"
                        disabled={isModalLoanClosed}
                      >
                        <option value="direct_rtgs">Direct RTGS</option>
                        <option value="direct_neft">Direct NEFT</option>
                        <option value="subsidiary_deduction" disabled>Subsidiary Deduction (Use dedicated route)</option>
                      </select>
                    </div>

                    <div>
                      <label className="field-label">Payment Date</label>
                      <input
                        type="date"
                        value={postDate}
                        onChange={e => setPostDate(e.target.value)}
                        className="field-input"
                        disabled={isModalLoanClosed}
                      />
                    </div>

                    <div>
                      <label className="field-label">Amount Received (₹)</label>
                      <input
                        type="number"
                        min="1"
                        value={postAmount}
                        onChange={e => setPostAmount(e.target.value)}
                        className="field-input"
                        placeholder="0"
                        disabled={isModalLoanClosed}
                      />
                    </div>

                    <div>
                      <label className="field-label">Bank Reference / UTR</label>
                      <input
                        type="text"
                        value={postRef}
                        onChange={e => setPostRef(e.target.value)}
                        className="field-input"
                        placeholder="e.g. UTR20260624123456"
                        disabled={isModalLoanClosed}
                      />
                    </div>

                    <div className="col-span-2">
                      <label className="field-label">Bank Account Credited</label>
                      <select
                        value={postBank}
                        onChange={e => setPostBank(e.target.value)}
                        className="field-select"
                        disabled={isModalLoanClosed}
                      >
                        <option value="SFPCL HDFC A/c">SFPCL HDFC A/c - 50200000123456</option>
                        <option value="SFPCL SBI A/c">SFPCL SBI A/c - 33100000123456</option>
                      </select>
                    </div>
                  </div>

                  {allocationPreview && !isModalLoanClosed && (
                    <div className="mt-6 border border-slate-200 rounded-xl overflow-hidden">
                      <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
                        <span className="text-sm font-semibold text-slate-900">Allocation Preview</span>
                        <span className="text-[10px] text-slate-500 uppercase tracking-wide flex items-center gap-1"><FileText size={12}/> Principal-First</span>
                      </div>
                      <div className="p-4 grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-xs text-slate-500">Principal Allocation</div>
                          <div className="text-sm font-semibold text-green-700">{fmt(allocationPreview.principal)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Interest Allocation</div>
                          <div className="text-sm font-semibold text-amber-700">{fmt(allocationPreview.interest)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500">Unallocated</div>
                          <div className="text-sm font-semibold text-slate-700">{fmt(allocationPreview.unallocated)}</div>
                        </div>
                        <div className="pt-2 border-t border-slate-100 col-span-2 flex justify-between">
                          <span className="text-xs text-slate-700 font-medium">New Principal O/S:</span>
                          <span className="text-sm font-bold text-slate-900">{fmt(allocationPreview.newPrincipalOs)}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="p-5 border-t border-slate-200 flex justify-end gap-3 bg-slate-50 rounded-b-xl">
              <button onClick={() => { setShowPostModal(false); setPosted(false); setPostAmount(''); setPostRef(''); }} className="btn-secondary">
                {posted ? 'Close' : 'Cancel'}
              </button>
              {!posted && (
                <button
                  className="btn-primary disabled:opacity-50"
                  disabled={!postAmount || Number(postAmount) <= 0 || !postRef || !postDate || isModalLoanClosed}
                  onClick={() => setPosted(true)}
                >
                  Record Receipt
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
`;

fs.writeFileSync(path.join(__dirname, 'src/components/loan/RepaymentLedger.tsx'), repaymentLedgerCode);
fs.writeFileSync(path.join(__dirname, 'src/pages/repayments/RepaymentsHub.tsx'), repaymentsHubCode);
console.log('Update successful');
