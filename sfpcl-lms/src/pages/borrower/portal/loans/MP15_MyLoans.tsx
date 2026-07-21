import React, { useEffect, useState } from 'react';
import { ArrowRight, Clock, History } from 'lucide-react';
import AlertBanner from '../../../../components/ui/AlertBanner';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import { fetchPortalLoanAccounts, PortalLoanAccountSummary } from '../../../../services/portalApi';

const MP15_MyLoans: React.FC<{ onSelectLoan: (id: string, destination: 'detail' | 'repayments' | 'instructions') => void }> = ({ onSelectLoan }) => {
  const [loans, setLoans] = useState<PortalLoanAccountSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');

  useEffect(() => {
    let current = true;
    fetchPortalLoanAccounts()
      .then(data => { if (current) setLoans(data); })
      .catch(reason => { if (current) setError(portalLoanError(reason)); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, []);

  const rows = loans.filter(loan => activeTab === 'active' ? loan.closure_status === 'active' : loan.closure_status === 'closed');
  return (
    <div className="space-y-6">
      <div><h2 className="text-xl font-bold text-slate-900">My Loans</h2><p className="text-sm text-slate-500 mt-1">View your active loan details and past loan history.</p></div>
      <div className="flex border-b border-slate-200">
        {([['active', 'Active Loans', Clock], ['history', 'Loan History', History]] as const).map(([id, label, Icon]) => (
          <button key={id} type="button" onClick={() => setActiveTab(id)} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === id ? 'border-green-600 text-green-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}><Icon size={16} />{label}</button>
        ))}
      </div>
      {loading && <AlertBanner type="info" title="Loading your loans…" />}
      {!loading && error && <AlertBanner type="error" title={error} />}
      {!loading && !error && rows.length === 0 && <AlertBanner type="info" title={activeTab === 'active' ? 'No active loan accounts.' : 'No closed loan accounts.'} />}
      {!loading && !error && rows.map(loan => (
        <div key={loan.loan_account_id} className="bg-white rounded-xl border border-slate-100 overflow-hidden">
          <div className="bg-green-50 px-6 py-5 border-b border-green-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div><p className="text-xs text-green-700">Loan Account</p><button type="button" onClick={() => onSelectLoan(loan.loan_account_id, 'detail')} className="text-lg font-bold text-green-950 hover:text-green-700">{loan.loan_account_number}</button><p className="text-xs text-green-700 mt-1">Application {loan.application_reference ?? '—'}</p></div>
            <StatusBadge label={loan.closure_status === 'closed' ? 'closed' : loan.status} size="sm" />
          </div>
          <div className="p-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[['Disbursed Amount', money(loan.disbursed_amount)], ['Outstanding Principal', money(loan.principal_outstanding)], ['Next Due', loan.next_due_date ? `${money(loan.next_due_amount)} on ${date(loan.next_due_date)}` : 'No upcoming due']].map(([label, value]) => <div key={label} className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">{label}</p><p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p></div>)}
          </div>
          <div className="px-6 pb-6 flex flex-col sm:flex-row gap-3">
            <Action label="View Loan" onClick={() => onSelectLoan(loan.loan_account_id, 'detail')} />
            <Action label="View Repayments" onClick={() => onSelectLoan(loan.loan_account_id, 'repayments')} />
            <Action label="Repayment Instructions" onClick={() => onSelectLoan(loan.loan_account_id, 'instructions')} />
          </div>
        </div>
      ))}
    </div>
  );
};

const Action = ({ label, onClick }: { label: string; onClick: () => void }) => <button type="button" onClick={onClick} className="flex-1 flex items-center justify-center gap-2 bg-white text-slate-700 hover:bg-slate-50 px-4 py-2.5 rounded-lg text-sm font-medium border border-slate-200">{label}<ArrowRight size={15} /></button>;
// eslint-disable-next-line react-refresh/only-export-components
export const portalLoanError = (error: unknown) => error instanceof AuthSessionError && (error.status === 401 || error.status === 403) ? 'You are not authorised to view these loan details.' : 'Loan information could not be loaded. Please try again.';
// eslint-disable-next-line react-refresh/only-export-components
export const money = (value: string | null) => value ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(value)) : '—';
// eslint-disable-next-line react-refresh/only-export-components
export const date = (value: string) => new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }).format(new Date(`${value}T00:00:00`));
export default MP15_MyLoans;
