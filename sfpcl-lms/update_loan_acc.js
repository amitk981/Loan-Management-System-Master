const fs = require('fs');
const path = require('path');

const code = `import React, { useState } from 'react';
import { ChevronLeft, ArrowRight } from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import RepaymentLedger from '../../components/loan/RepaymentLedger';
import AuditTimeline from '../../components/loan/AuditTimeline';
import { loanAccounts, loanApplications } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
};

const DPD_BUCKET_LABELS: Record<string, string> = {
  '0_30': '1–30 days', '31_60': '31–60 days', '61_90': '31–90 days',
  '91_365': '91 days–1 year', '1_2_years': '1–2 years',
  '2_3_years': '2–3 years', '3plus_years': '3+ years',
};

const mapStatus = (status: string) => {
  if (status === 'recovery_in_progress') return 'Recovery In Progress';
  if (status === 'default_review') return 'Recovery Review';
  if (status === 'grace_period') return 'Grace Period';
  if (status === 'overdue') return 'Overdue';
  if (status === 'active') return 'Active';
  if (status === 'closed') return 'Closed';
  return status.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
};

interface LoanAccount360Props {
  loanAccountId: string | null;
  onSelect: (id: string) => void;
  onBack?: () => void;
}

const LoanAccount360: React.FC<LoanAccount360Props> = ({ loanAccountId, onSelect, onBack }) => {
  const [activeTab, setActiveTab] = useState(0);
  const { currentUser } = useRole();
  const role = currentUser.role;

  // Basic permission check - only roles that should see loan accounts can enter this screen. 
  // Normally handled by App.tsx router, but adding defensive check here.
  const isAllowed = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'sales', 'field_officer', 'compliance_team'].includes(role);

  if (!isAllowed) {
    return (
      <div className="p-6">
        <AlertBanner type="error" title="Access Denied" message="You do not have permission to view Loan Accounts." />
      </div>
    );
  }

  if (!loanAccountId) {
    return (
      <div className="p-6 space-y-4">
        <h1 className="text-xl font-bold text-slate-900">Loan Accounts</h1>
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="table-header text-left">Account No.</th>
                <th className="table-header text-left">Borrower / Member</th>
                <th className="table-header text-right">Disbursed</th>
                <th className="table-header text-right">Principal O/S</th>
                <th className="table-header text-right">Interest Rate</th>
                <th className="table-header text-left">Status</th>
                <th className="table-header text-left">DPD</th>
                <th className="table-header text-left">Due Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loanAccounts.map(l => {
                const isClosed = l.status === 'closed';
                
                let dpdLabel = DPD_BUCKET_LABELS[l.dpdBucket] || l.dpdBucket;
                if (isClosed) {
                  dpdLabel = 'Closed';
                } else if (l.dpd === 0) {
                  dpdLabel = 'Current';
                }

                return (
                  <tr
                    key={l.id}
                    onClick={() => onSelect(l.id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell">
                      <div className="font-semibold text-green-700 hover:underline num">{l.accountNumber}</div>
                      <div className="text-xs text-slate-400 num">{l.applicationNumber}</div>
                      <div className="text-xs text-slate-400 num mt-0.5">SAP: {l.sapCustomerCode || 'Pending'}</div>
                    </td>
                    <td className="table-cell font-medium text-slate-900">{l.memberName}</td>
                    <td className="table-cell text-right num">{fmt(l.disbursedAmount)}</td>
                    <td className="table-cell text-right">
                       <div className="num font-semibold">{fmt(l.outstandingPrincipal)}</div>
                       <div className="text-xs text-slate-500 num mt-0.5">Interest: {fmt(l.accruedInterest)}</div>
                    </td>
                    <td className="table-cell text-right">{l.interestRate}%</td>
                    <td className="table-cell">
                       <StatusBadge label={mapStatus(l.status)} size="sm" 
                         type={isClosed ? 'slate' : l.status === 'overdue' ? 'error' : l.status.includes('recovery') ? 'error' : 'success'} 
                       />
                    </td>
                    <td className="table-cell">
                      <span className={\`font-semibold \${isClosed ? 'text-slate-400' : l.dpd > 90 ? 'text-red-600' : l.dpd > 0 ? 'text-amber-600' : 'text-green-600'}\`}>
                        {isClosed ? '—' : l.dpd}
                      </span>
                      <div className="text-xs text-slate-400">{dpdLabel}</div>
                    </td>
                    <td className="table-cell text-sm text-slate-600">
                      {isClosed ? (
                        <span className="text-slate-500 text-xs">Closed on {formatDate(l.lastRepaymentDate || l.repaymentDueDate)}</span>
                      ) : (
                        formatDate(l.repaymentDueDate)
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  const loan = loanAccounts.find(l => l.id === loanAccountId) || loanAccounts[0];
  const app = loanApplications.find(a => a.id === loan.applicationId);

  const TABS = [
    { id: 'summary', label: 'Summary' },
    { id: 'repayment', label: 'Repayment Ledger' },
    { id: 'schedule', label: 'Repayment Schedule' },
    { id: 'audit', label: 'Audit Trail' },
  ];

  const monthlyEMI = Math.round((loan.disbursedAmount * (loan.interestRate / 100 / 12)) /
    (1 - Math.pow(1 + loan.interestRate / 100 / 12, -12)));

  const isClosed = loan.status === 'closed';
  let dpdLabelDetail = DPD_BUCKET_LABELS[loan.dpdBucket] || loan.dpdBucket;
  if (isClosed) {
    dpdLabelDetail = 'Closed';
  } else if (loan.dpd === 0) {
    dpdLabelDetail = 'Current';
  }

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start gap-3">
        {onBack && (
          <button onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700">
            <ChevronLeft size={20} />
          </button>
        )}
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-slate-900 num">{loan.accountNumber}</h1>
            <StatusBadge label={mapStatus(loan.status)} size="md" 
              type={isClosed ? 'slate' : loan.status === 'overdue' ? 'error' : loan.status.includes('recovery') ? 'error' : 'success'}
            />
          </div>
          <div className="flex items-center gap-3 mt-0.5 text-sm text-slate-500">
            <span>{loan.memberName}</span>
            <span>·</span>
            <span className="num">{fmt(loan.disbursedAmount)} disbursed</span>
            <span>·</span>
            <span>SAP: <span className="num font-medium text-slate-900">{loan.sapCustomerCode || 'Pending'}</span></span>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {loan.status === 'overdue' && (
        <AlertBanner
          type="error"
          title={\`Loan Overdue — DPD: \${loan.dpd} days\`}
          message={\`Overdue since \${formatDate(loan.repaymentDueDate)}. Please initiate recovery communication.\`}
        />
      )}
      {loan.status === 'grace_period' && loan.gracePeriodEnd && (
        <AlertBanner
          type="warning"
          title={\`Grace Period Active — ends \${formatDate(loan.gracePeriodEnd)}\`}
          message="Repayment expected before grace period expiry to avoid default classification."
        />
      )}

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { label: 'Sanctioned', value: fmt(loan.sanctionedAmount), color: 'slate' },
          { label: 'Principal O/S', value: fmt(loan.outstandingPrincipal), color: loan.outstandingPrincipal > 0 ? 'amber' : 'green' },
          { label: 'Interest O/S', value: fmt(loan.accruedInterest), color: loan.accruedInterest > 0 ? 'amber' : 'slate' },
          { label: 'Interest Rate', value: \`\${loan.interestRate}% p.a.\`, color: 'slate' },
          { label: 'DPD', value: isClosed ? '—' : String(loan.dpd), color: isClosed ? 'slate' : loan.dpd > 90 ? 'red' : loan.dpd > 0 ? 'amber' : 'green' },
        ].map(({ label, value, color }) => (
          <div key={label} className={\`rounded-lg border p-3 \${
            color === 'red' ? 'bg-red-50 border-red-200' :
            color === 'amber' ? 'bg-amber-50 border-amber-200' :
            color === 'green' ? 'bg-green-50 border-green-200' : 'bg-slate-50 border-slate-200'
          }\`}>
            <p className="text-xs text-slate-500 font-medium">{label}</p>
            <p className={\`text-lg font-bold num mt-0.5 \${
              color === 'red' ? 'text-red-900' :
              color === 'amber' ? 'text-amber-900' :
              color === 'green' ? 'text-green-900' : 'text-slate-900'
            }\`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>
        {/* Tab 0: Summary */}
        <div className="card space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Account Number', value: loan.accountNumber },
              { label: 'Application Number', value: loan.applicationNumber },
              { label: 'Loan Type', value: loan.loanType === 'short_term' ? 'Short Term' : 'Long Term' },
              { label: 'Disbursement Date', value: formatDate(loan.disbursementDate) },
              { label: 'Repayment Due', value: formatDate(loan.repaymentDueDate) },
              { label: 'Monthly EMI (indicative)', value: fmt(monthlyEMI) },
              { label: 'Last Repayment', value: loan.lastRepaymentDate ? formatDate(loan.lastRepaymentDate) : 'None' },
              { label: 'Last Amount', value: loan.lastRepaymentAmount ? fmt(loan.lastRepaymentAmount) : '—' },
              { label: 'SAP Customer Code', value: loan.sapCustomerCode || 'Pending' },
              { label: 'DPD Bucket', value: dpdLabelDetail },
              ...(loan.gracePeriodEnd ? [{ label: 'Grace Period End', value: formatDate(loan.gracePeriodEnd) }] : []),
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
              </div>
            ))}
          </div>
          {app && (
            <div className="border-t pt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-500">Linked Application:</span>
                <button className="text-green-600 hover:underline flex items-center gap-1 font-medium num">
                  {app.applicationNumber} <ArrowRight size={12} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Tab 1: Repayment Ledger */}
        <div className="card">
          <RepaymentLedger
            loanAccountId={loan.id}
            outstandingPrincipal={loan.outstandingPrincipal}
            disbursedAmount={loan.disbursedAmount}
          />
        </div>

        {/* Tab 2: Schedule */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Indicative Repayment Schedule</h3>
          <p className="text-xs text-slate-400 mb-4">Based on flat interest rate @ {loan.interestRate}% p.a. · Monthly instalments</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">#</th>
                  <th className="table-header text-left">Due Date</th>
                  <th className="table-header text-right">Opening Principal</th>
                  <th className="table-header text-right">Principal</th>
                  <th className="table-header text-right">Interest</th>
                  <th className="table-header text-right">EMI</th>
                  <th className="table-header text-right">Closing Balance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {Array.from({ length: 12 }).map((_, i) => {
                  const rateMonth = loan.interestRate / 100 / 12;
                  const emi = Math.round((loan.disbursedAmount * rateMonth) / (1 - Math.pow(1 + rateMonth, -12)));
                  const open = Math.round(loan.disbursedAmount * Math.pow(1 + rateMonth, i) - emi * ((Math.pow(1 + rateMonth, i) - 1) / rateMonth));
                  const interest = Math.round(open * rateMonth);
                  const principal = emi - interest;
                  const close = Math.max(0, open - principal);
                  const dueDate = new Date(loan.disbursementDate);
                  dueDate.setMonth(dueDate.getMonth() + i + 1);
                  return (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="table-cell text-slate-500">{i + 1}</td>
                      <td className="table-cell">{formatDate(dueDate.toISOString())}</td>
                      <td className="table-cell text-right num">{fmt(open)}</td>
                      <td className="table-cell text-right num text-green-700">{fmt(principal)}</td>
                      <td className="table-cell text-right num text-amber-700">{fmt(interest)}</td>
                      <td className="table-cell text-right num font-semibold">{fmt(emi)}</td>
                      <td className="table-cell text-right num">{fmt(close)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 3: Audit Trail */}
        <div className="card">
          <AuditTimeline entityId={loan.applicationId} />
        </div>
      </Tabs>
    </div>
  );
};

export default LoanAccount360;
`;

fs.writeFileSync(path.join(__dirname, 'src/pages/loan-accounts/LoanAccount360.tsx'), code);
console.log('Update successful');
