import React, { useEffect, useRef, useState } from 'react';
import { ArrowRight, ChevronLeft, Lock } from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import RepaymentLedger, { PaginationControls } from '../../components/loan/RepaymentLedger';
import { AuthSessionError, type Pagination } from '../../services/authSession';
import {
  fetchLoanAccount,
  fetchLoanAccounts,
  type LoanAccountProjection,
} from '../../services/loanAccountsApi';
import {
  fetchLoanLedger,
  fetchRepaymentSchedule,
  type LoanLedgerRow,
  type RepaymentScheduleRow,
} from '../../services/servicingApi';
import { formatMoney } from '../../utils/formatMoney';

const fmtDecimal = formatMoney;

const formatDate = (dateStr: string | null | undefined) => dateStr
  ? new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
  : '—';

const formatTime = (dateStr: string | null | undefined) => {
  if (!dateStr) return '—';
  const value = new Date(dateStr);
  return `${value.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} at ${value.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;
};

const label = (value: string) => value
  .replace(/_/g, ' ')
  .replace(/\b\w/g, character => character.toUpperCase());

const ACCOUNT_TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'ledger', label: 'Loan Ledger' },
  { id: 'schedule', label: 'Repayment Schedule' },
  { id: 'interest', label: 'Interest Invoices' },
  { id: 'documents', label: 'Documents' },
  { id: 'security', label: 'Security' },
  { id: 'monitoring', label: 'Monitoring' },
  { id: 'defaults', label: 'Default History' },
  { id: 'communications', label: 'Communications' },
  { id: 'closure', label: 'Closure' },
  { id: 'audit', label: 'Audit Trail' },
];

interface LoanAccount360Props {
  loanAccountId: string | null;
  onSelect: (id: string) => void;
  onBack?: () => void;
}

const LoanAccount360: React.FC<LoanAccount360Props> = ({ loanAccountId, onSelect, onBack }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [accounts, setAccounts] = useState<LoanAccountProjection[]>([]);
  const [account, setAccount] = useState<LoanAccountProjection | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<{ message: string; unauthorized: boolean } | null>(null);
  const [ledger, setLedger] = useState<LoanLedgerRow[]>([]);
  const [schedule, setSchedule] = useState<RepaymentScheduleRow[]>([]);
  const [ledgerPage, setLedgerPage] = useState(1);
  const [schedulePage, setSchedulePage] = useState(1);
  const [servicingLoading, setServicingLoading] = useState(false);
  const [servicingError, setServicingError] = useState<{ message: string; unauthorized: boolean } | null>(null);
  const emptyPagination: Pagination = { page: 1, page_size: 20, total_count: 0, total_pages: 1, has_next: false, has_previous: false };
  const [ledgerPagination, setLedgerPagination] = useState<Pagination>(emptyPagination);
  const [schedulePagination, setSchedulePagination] = useState<Pagination>(emptyPagination);
  const servicingLoan = useRef<string | null>(null);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setLoadError(null);
    setAccount(null);
    const request = loanAccountId
      ? fetchLoanAccount(loanAccountId).then(value => { if (current) setAccount(value); })
      : fetchLoanAccounts(1, 20).then(result => { if (current) setAccounts(result.items); });
    void request.catch(error => {
      if (!current) return;
      setLoadError({
        message: error instanceof Error ? error.message : 'Loan accounts could not be loaded.',
        unauthorized: error instanceof AuthSessionError && [401, 403].includes(error.status || 0),
      });
    }).finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [loanAccountId]);

  useEffect(() => {
    if (!loanAccountId || ![1, 2].includes(activeTab)) return;
    if (servicingLoan.current !== loanAccountId) {
      servicingLoan.current = loanAccountId;
      if (ledgerPage !== 1) setLedgerPage(1);
      if (schedulePage !== 1) setSchedulePage(1);
      if (ledgerPage !== 1 || schedulePage !== 1) return;
    }
    let current = true;
    const ledgerActive = activeTab === 1;
    setServicingLoading(true);
    setServicingError(null);
    const request = ledgerActive
      ? fetchLoanLedger(loanAccountId, ledgerPage, 20).then(result => {
        if (current) { setLedger(result.items); setLedgerPagination(result.pagination); }
      })
      : fetchRepaymentSchedule(loanAccountId, schedulePage, 20).then(result => {
        if (current) { setSchedule(result.items); setSchedulePagination(result.pagination); }
      });
    void request.catch(error => {
      if (!current) return;
      setServicingError({
        message: error instanceof Error ? error.message : 'Servicing records could not be loaded.',
        unauthorized: error instanceof AuthSessionError && [401, 403].includes(error.status || 0),
      });
    }).finally(() => { if (current) setServicingLoading(false); });
    return () => { current = false; };
  }, [activeTab, ledgerPage, loanAccountId, schedulePage]);

  if (loading) return <div className="p-6"><div className="card text-sm text-slate-500">{loanAccountId ? 'Loading loan account summary…' : 'Loading loan accounts…'}</div></div>;
  if (loadError) return <div className="p-6"><AlertBanner type="error" title={loadError.unauthorized ? 'Access Denied' : 'Loan Accounts Unavailable'} message={loadError.message} /></div>;

  if (!loanAccountId) {
    return (
      <div className="p-6 space-y-4">
        <h1 className="text-xl font-bold text-slate-900">Loan Accounts</h1>
        <div className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="bg-slate-50 border-b border-slate-200">
              <th className="table-header text-left">Account No.</th>
              <th className="table-header text-left">Borrower / Member</th>
              <th className="table-header text-right">Disbursed</th>
              <th className="table-header text-right">Principal O/S</th>
              <th className="table-header text-right">Interest Rate</th>
              <th className="table-header text-left">Status</th>
              <th className="table-header text-left">DPD</th>
              <th className="table-header text-left">Due Date</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {accounts.length === 0 && <tr><td colSpan={8} className="table-cell py-12 text-center text-slate-400">No loan accounts are available in your scope.</td></tr>}
              {accounts.map(row => <tr key={row.loan_account_id} onClick={() => onSelect(row.loan_account_id)} className="hover:bg-slate-50 cursor-pointer transition-colors">
                <td className="table-cell"><div className="font-semibold text-green-700 hover:underline num">{row.loan_account_number}</div><div className="text-xs text-slate-400 num">{row.application_reference_number || '—'}</div><div className="text-xs text-slate-400 num mt-0.5">SAP: {row.sap_customer_code || 'Pending'}</div></td>
                <td className="table-cell font-medium text-slate-900">{row.member.display_name}</td>
                <td className="table-cell text-right num">{fmtDecimal(row.disbursed_amount)}</td>
                <td className="table-cell text-right"><div className="num font-semibold">{fmtDecimal(row.principal_outstanding)}</div><div className="text-xs text-slate-500 num mt-0.5">Interest: {fmtDecimal(row.interest_outstanding)}</div></td>
                <td className="table-cell text-right">{row.current_interest_rate}%</td>
                <td className="table-cell"><StatusBadge label={label(row.loan_account_status)} size="sm" /></td>
                <td className="table-cell"><span className="font-semibold text-slate-400">—</span><div className="text-xs text-slate-400">Not available</div></td>
                <td className="table-cell text-sm text-slate-600">{formatDate(row.repayment_date)}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (!account) return <div className="p-6"><AlertBanner type="error" title="Loan Account Unavailable" message="The loan account was not found or is inaccessible." /></div>;

  const facts = [
    ['Account Number', account.loan_account_number],
    ['Application Number', account.application_reference_number || '—'],
    ['Member', account.member.display_name],
    ['Loan Type', label(account.loan_type)],
    ['Facility Type', label(account.facility_type)],
    ['Interest Rate', `${account.current_interest_rate}% ${label(account.interest_rate_type)}`],
    ['Tenure', `${account.tenure_months} months`],
    ['Tenure Start', formatDate(account.tenure_start_date)],
    ['Tenure End', formatDate(account.tenure_end_date)],
    ['Repayment Due', formatDate(account.repayment_date)],
    ['SAP Customer Code', account.sap_customer_code || 'Pending'],
    ['Created', formatTime(account.created_at)],
    ['Activated', account.activated_at ? formatTime(account.activated_at) : 'Not activated'],
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start gap-3">
        {onBack && <button type="button" onClick={onBack} className="mt-1 text-slate-500 hover:text-slate-700"><ChevronLeft size={20} /></button>}
        <div className="flex-1"><div className="flex items-center gap-2 flex-wrap"><h1 className="text-xl font-bold text-slate-900 num">{account.loan_account_number}</h1><StatusBadge label={label(account.loan_account_status)} size="md" /></div><div className="flex items-center gap-3 mt-0.5 text-sm text-slate-500"><span>{account.member.display_name}</span><span>·</span><span className="num">{fmtDecimal(account.disbursed_amount)} disbursed</span><span>·</span><span>SAP: <span className="num font-medium text-slate-900">{account.sap_customer_code || 'Pending'}</span></span></div></div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          ['Sanctioned', account.sanctioned_amount],
          ['Disbursed', account.disbursed_amount],
          ['Outstanding Principal', account.principal_outstanding],
          ['Outstanding Interest', account.interest_outstanding],
          ['Total Outstanding', account.total_outstanding],
        ].map(([key, value]) => <div key={key} className="rounded-lg border p-3 bg-slate-50 border-slate-200"><p className="text-xs text-slate-500 font-medium">{key}</p><p className="text-lg font-bold num mt-0.5 text-slate-900">{fmtDecimal(value)}</p></div>)}
      </div>
      <Tabs tabs={ACCOUNT_TABS} activeIndex={activeTab} onChange={setActiveTab}>
        <div className="card space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">{facts.map(([key, value]) => <div key={key} className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{key}</p><p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p></div>)}</div>
          <div className="border-t pt-4"><div className="flex items-center justify-between text-sm"><span className="text-slate-500">Linked Application:</span><span className="text-green-600 flex items-center gap-1 font-medium num">{account.application_reference_number || account.loan_application_id} <ArrowRight size={12} /></span></div></div>
        </div>
        <div className="card"><RepaymentLedger rows={ledger} pagination={ledgerPagination} loading={servicingLoading} error={servicingError} onPage={setLedgerPage} /></div>
        <div className="card space-y-4">
          {servicingLoading && <div className="text-center py-8 text-slate-400 text-sm">Loading repayment schedule…</div>}
          {!servicingLoading && servicingError && <AlertBanner type="error" title={servicingError.unauthorized ? 'Access Denied' : 'Repayment Schedule Unavailable'} message={servicingError.message} />}
          {!servicingLoading && !servicingError && schedule.length === 0 && <div className="text-center py-8 text-slate-400 text-sm">No repayment schedule items are recorded for this loan.</div>}
          {!servicingLoading && !servicingError && schedule.length > 0 && <><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Instalment', 'Due Date', 'Principal Due', 'Interest Due', 'Charges Due', 'Total Due', 'Amount Received', 'Status'].map(column => <th key={column} className={`table-header ${column.includes('Due') || column === 'Amount Received' ? 'text-right' : 'text-left'}`}>{column}</th>)}</tr></thead><tbody className="divide-y divide-slate-100">{schedule.map(row => <tr key={row.repayment_schedule_id}><td className="table-cell num">{row.installment_number}</td><td className="table-cell">{formatDate(row.due_date)}</td><td className="table-cell text-right num">{fmtDecimal(row.principal_due)}</td><td className="table-cell text-right num">{fmtDecimal(row.interest_due)}</td><td className="table-cell text-right num">{fmtDecimal(row.charges_due)}</td><td className="table-cell text-right num font-semibold">{fmtDecimal(row.total_due)}</td><td className="table-cell text-right num">{fmtDecimal(row.amount_received)}</td><td className="table-cell"><StatusBadge label={label(row.schedule_status)} size="sm" /></td></tr>)}</tbody></table></div><PaginationControls pagination={schedulePagination} onPage={setSchedulePage} /></>}
        </div>
        {ACCOUNT_TABS.slice(3).map(tab => (
          <div key={tab.id} className="card flex items-start gap-3">
            <Lock size={16} className="text-slate-400 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-slate-700">{tab.label} is not available yet.</p>
              <p className="text-xs text-slate-500 mt-0.5">This view will appear after its governed Epic 010 owner is connected.</p>
            </div>
          </div>
        ))}
      </Tabs>
    </div>
  );
};

export default LoanAccount360;
