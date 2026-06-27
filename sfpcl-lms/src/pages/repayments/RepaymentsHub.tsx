import React, { useState } from 'react';
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

  const activeOrOverdueLoans = loanAccounts.filter(l => l.status !== 'closed' && l.status !== 'recovered');
  
  const [selectedLoan, setSelectedLoan] = useState<string>(activeOrOverdueLoans[0]?.id || '');
  const [showPostModal, setShowPostModal] = useState(false);
  const [postAmount, setPostAmount] = useState('');
  const [postChannel, setPostChannel] = useState('direct_rtgs');
  const [postRef, setPostRef] = useState('');
  const [postDate, setPostDate] = useState(formatDate(new Date().toISOString()));
  const [postBank, setPostBank] = useState('SFPCL HDFC A/c');
  const [subsidiaryName, setSubsidiaryName] = useState('Sahyadri Farms Post Harvest Care Ltd.');
  const [subsidiaryNarration, setSubsidiaryNarration] = useState('');
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
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selectedLoan === l.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                >
                  <Banknote size={16} className="text-green-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm">{l.accountNumber}</div>
                    <div className="text-xs text-slate-500 truncate">{l.memberName}</div>
                    <div className="text-xs text-slate-400 num">Principal O/S: {fmt(actualPrincipalOs)}</div>
                  </div>
                  <StatusBadge label={l.status === 'closed' ? 'Closed' : l.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} size="sm" type={l.status === 'closed' ? 'slate' : 'success'} />
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
              <StatusBadge label={loan.status === 'closed' ? 'Closed' : loan.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} size="sm" type={loan.status === 'closed' ? 'slate' : 'success'} />
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
                        <option value="subsidiary_deduction">Subsidiary Deduction</option>
                      </select>
                    </div>

                    {postChannel === 'subsidiary_deduction' && (
                      <>
                        <div>
                          <label className="field-label">Subsidiary Name</label>
                          <select
                            value={subsidiaryName}
                            onChange={e => setSubsidiaryName(e.target.value)}
                            className="field-select"
                            disabled={isModalLoanClosed}
                          >
                            <option>Sahyadri Farms Post Harvest Care Ltd.</option>
                            <option>Sahyadri Agro</option>
                            <option>Sahyadri Farms</option>
                            <option>Sahyadri Post Harvest</option>
                          </select>
                        </div>
                        <div>
                          <label className="field-label">Deduction Narration</label>
                          <input
                            type="text"
                            value={subsidiaryNarration}
                            onChange={e => setSubsidiaryNarration(e.target.value)}
                            className="field-input"
                            placeholder="e.g. Crop produce deduction FY 2025-26"
                            disabled={isModalLoanClosed}
                          />
                        </div>
                      </>
                    )}

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
                  disabled={!postAmount || Number(postAmount) <= 0 || !postDate || isModalLoanClosed || (postChannel !== 'subsidiary_deduction' && !postRef) || (postChannel === 'subsidiary_deduction' && !subsidiaryNarration)}
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
