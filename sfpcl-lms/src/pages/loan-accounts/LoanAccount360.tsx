import React, { useEffect, useState } from 'react';
import { ChevronLeft, ArrowRight, FileText, CheckCircle2, Banknote, Calendar, Check, AlertOctagon, Shield, Lock, Download, AlertTriangle } from 'lucide-react';
import Tabs from '../../components/ui/Tabs';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanAccounts, documents, securities, auditEvents, repaymentRecords } from '../../data/mockData';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchLoanAccount,
  fetchLoanAccounts,
  type LoanAccountProjection,
} from '../../services/loanAccountsApi';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');
const fmtDecimal = (value: string) => `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
};

const formatTime = (dateStr: string | undefined) => {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) +
    ' at ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
};

const DPD_BUCKET_LABELS: Record<string, string> = {
  '0_30': '1–30 days', '31_60': '31–60 days', '61_90': '31–90 days',
  '91_365': '91 days–1 year', '1_2_years': '1–2 years',
  '2_3_years': '2–3 years', '3plus_years': '3+ years',
};

const DOC_TYPE_LABELS: Record<string, string> = {
  pan: 'PAN Card', aadhaar: 'Aadhaar Card', nominee_pan: 'Nominee PAN', nominee_aadhaar: 'Nominee Aadhaar',
  witness_pan: 'Witness PAN', witness_aadhaar: 'Witness Aadhaar', share_certificate: 'Share Certificate',
  land_712: '7/12 Extract', crop_plan: 'Crop Plan', bank_statement: 'Bank Statement',
  poa: 'Power of Attorney', tri_party: 'Tri-Party Agreement', sh4: 'SH-4 Physical Shares',
  term_sheet: 'Term Sheet', loan_agreement: 'Loan Agreement', cancelled_cheque: 'Cancelled Cheque',
  blank_cheque: 'Blank Cheque', bank_verification_letter: 'Bank Verification Letter',
};

const SECURITY_TYPE_LABELS: Record<string, string> = {
  sh4: 'SH-4 Physical Share Certificate', poa: 'Power of Attorney', cdsl_pledge: 'CDSL Share Pledge',
  blank_cheque: 'Blank Cheque', tri_party: 'Tri-Party Agreement',
};

const mapStatus = (status: string) => {
  if (status === 'recovery_in_progress') return 'Recovery In Progress';
  if (status === 'default_review' || status === 'recovery_review') return 'Recovery Review';
  if (status === 'recovery_action_approved') return 'Recovery Action Approved';
  if (status === 'grace_period') return 'Grace Period';
  if (status === 'extended' || status === 'extension') return 'Extension Granted';
  if (status === 'overdue') return 'Overdue';
  if (status === 'active' || status === 'active_repayment') return 'Active Repayment';
  if (status === 'closure_review') return 'Closure Review';
  if (status === 'closed') return 'Closed';
  if (status === 'recovered') return 'Recovered';
  return status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const mapInitialStatus = (status: string) => status === 'active' ? 'Active' : mapStatus(status);

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
      const unauthorized = error instanceof AuthSessionError && [401, 403].includes(error.status || 0);
      setLoadError({
        message: error instanceof Error ? error.message : 'Loan accounts could not be loaded.',
        unauthorized,
      });
    }).finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [loanAccountId]);

  if (loading) return <div className="p-6"><div className="card text-sm text-slate-500">{loanAccountId ? 'Loading loan account summary…' : 'Loading loan accounts…'}</div></div>;
  if (loadError) return <div className="p-6"><AlertBanner type="error" title={loadError.unauthorized ? 'Access Denied' : 'Loan Accounts Unavailable'} message={loadError.message} /></div>;

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
              {accounts.length === 0 && <tr><td colSpan={8} className="table-cell py-12 text-center text-slate-400">No loan accounts are available in your scope.</td></tr>}
              {accounts.map(l => {
                return (
                  <tr key={l.loan_account_id} onClick={() => onSelect(l.loan_account_id)} className="hover:bg-slate-50 cursor-pointer transition-colors">
                    <td className="table-cell">
                      <div className="font-semibold text-green-700 hover:underline num">{l.loan_account_number}</div>
                      <div className="text-xs text-slate-400 num">{l.application_reference_number || '—'}</div>
                      <div className="text-xs text-slate-400 num mt-0.5">SAP: {l.sap_customer_code || 'Pending'}</div>
                    </td>
                    <td className="table-cell font-medium text-slate-900">{l.member.display_name}</td>
                    <td className="table-cell text-right num">{fmtDecimal(l.disbursed_amount)}</td>
                    <td className="table-cell text-right">
                       <div className="num font-semibold">{fmtDecimal(l.principal_outstanding)}</div>
                       <div className="text-xs text-slate-500 num mt-0.5">Interest: {fmtDecimal(l.interest_outstanding)}</div>
                    </td>
                    <td className="table-cell text-right">{l.current_interest_rate}%</td>
                    <td className="table-cell">
                       <StatusBadge label={mapInitialStatus(l.loan_account_status)} size="sm" />
                    </td>
                    <td className="table-cell">
                      <span className="font-semibold text-slate-400">—</span>
                      <div className="text-xs text-slate-400">Not available</div>
                    </td>
                    <td className="table-cell text-sm text-slate-600">{formatDate(l.repayment_date)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (!account) return <div className="p-6"><AlertBanner type="error" title="Loan Account Unavailable" message="The loan account was not found or is inaccessible." /></div>;

  const loan = loanAccounts.find(l => l.id === loanAccountId) || loanAccounts[0];
  const loanDocs = documents.filter(d => d.applicationId === loan.applicationId);
  const loanSecurities = securities.filter(s => s.applicationId === loan.applicationId);
  const loanAuditEvents = auditEvents.filter(e => e.entityId === loan.applicationNumber || e.entityId === loan.accountNumber);
  const loanRepayments = repaymentRecords.filter(r => r.loanAccountId === loan.id);

  let dpdLabelDetail = DPD_BUCKET_LABELS[loan.dpdBucket] || loan.dpdBucket;
  if (loan.status === 'closed' || loan.status === 'recovered') dpdLabelDetail = 'Closed';
  else if (loan.dpd === 0) dpdLabelDetail = 'Current';

  const TABS = [
    { id: 'summary', label: 'Summary' },
    { id: 'ledger', label: 'Loan Ledger' },
    { id: 'schedule', label: 'Repayment Schedule' },
    { id: 'interest', label: 'Interest Invoices' },
    { id: 'documents', label: 'Documents', badge: loanDocs.length > 0 ? loanDocs.length : undefined },
    { id: 'security', label: 'Security', badge: loanSecurities.length > 0 ? loanSecurities.length : undefined },
    { id: 'monitoring', label: 'DPD History' },
    { id: 'defaults', label: 'Default History' },
    { id: 'closure', label: 'Closure' },
    { id: 'audit', label: 'Audit Trail' },
  ];

  // Mock interest invoices for this loan
  const interestInvoices = [
    { id: `INV-${loan.applicationNumber}-001`, period: 'Apr 2026', principalOs: loan.disbursedAmount, rate: loan.interestRate, days: 30, interest: Math.round(loan.disbursedAmount * loan.interestRate / 100 / 12), status: 'generated', invoiceDate: '2026-05-01', sapStatus: 'posted' },
    { id: `INV-${loan.applicationNumber}-002`, period: 'May 2026', principalOs: loan.disbursedAmount, rate: loan.interestRate, days: 31, interest: Math.round(loan.disbursedAmount * loan.interestRate / 100 / 12), status: 'generated', invoiceDate: '2026-06-01', sapStatus: 'pending' },
    { id: `INV-${loan.applicationNumber}-003`, period: 'Jun 2026', principalOs: loan.outstandingPrincipal, rate: loan.interestRate, days: 30, interest: Math.round(loan.outstandingPrincipal * loan.interestRate / 100 / 12), status: 'draft', invoiceDate: '', sapStatus: '' },
  ];

  // Mock DPD history
  const dpdHistory = [
    { date: formatDate(loan.disbursementDate), dpd: 0, status: 'Current', action: 'Loan disbursed' },
    { date: '1 month after disbursement', dpd: 0, status: 'Current', action: 'First EMI period' },
    ...(loan.dpd > 0 ? [
      { date: formatDate(loan.repaymentDueDate), dpd: loan.dpd, status: loan.dpd > 90 ? 'Overdue (90+ DPD)' : 'Overdue', action: 'Repayment missed' },
    ] : []),
    ...(loan.status === 'grace_period' ? [{ date: formatDate(loan.gracePeriodEnd), dpd: loan.dpd, status: 'Grace Period Active', action: 'Grace period granted by Credit Manager' }] : []),
    ...(loan.status === 'extended' || loan.status === 'extension' ? [{ date: '10 Jan 2026', dpd: 0, status: 'Extended', action: 'Sanction Committee approved 6-month extension' }] : []),
    ...(loan.status === 'recovered' ? [{ date: formatDate(loan.lastRepaymentDate), dpd: 0, status: 'Recovered', action: 'SH-4 invoked · Full settlement received' }] : []),
  ];

  // Mock default history
  const defaultHistory = loan.dpd > 0 || ['grace_period', 'overdue', 'recovery_review', 'recovery_in_progress', 'recovered', 'extended', 'extension'].includes(loan.status)
    ? [
        { date: formatDate(loan.repaymentDueDate), event: 'First default registered', dpd: loan.dpd, action: 'Borrower notice sent via registered post', by: 'Credit Manager' },
        ...(loan.status === 'grace_period' ? [{ date: formatDate(loan.gracePeriodEnd), event: 'Grace period approved', dpd: loan.dpd, action: '90-day grace period granted', by: 'Credit Manager' }] : []),
        ...(loan.status === 'extended' || loan.status === 'extension' ? [
          { date: '10 Jan 2026', event: 'Extension approved by SC', dpd: 0, action: '6-month extension; next repayment 10 Jul 2026', by: 'Sanction Committee' },
        ] : []),
        ...(loan.status === 'recovered' ? [
          { date: formatDate(loan.lastRepaymentDate), event: 'SH-4 invoked — settlement', dpd: 0, action: 'Full recovery; NOC pending', by: 'Company Secretary' },
        ] : []),
      ]
    : [];

  // Closure readiness
  const closureItems = [
    { label: 'Outstanding principal', done: loan.outstandingPrincipal === 0, value: loan.outstandingPrincipal === 0 ? '₹0 — Fully repaid' : fmt(loan.outstandingPrincipal) + ' remaining' },
    { label: 'Accrued interest cleared', done: loan.accruedInterest === 0, value: loan.accruedInterest === 0 ? 'Nil' : fmt(loan.accruedInterest) + ' outstanding' },
    { label: 'SAP entries posted', done: loanRepayments.every(r => r.sapEntryStatus === 'posted'), value: 'All repayment entries posted' },
    { label: 'NOC generated', done: loan.status === 'closed', value: loan.status === 'closed' ? 'NOC issued' : 'Pending — outstanding balance clearance required' },
    { label: 'Security instruments returned', done: loanSecurities.some(s => s.status === 'returned'), value: loanSecurities.some(s => s.status === 'returned') ? 'SH-4 / PoA returned to borrower' : 'Pending — after NOC issuance' },
    { label: 'Account archived', done: loan.status === 'archived', value: loan.status === 'archived' ? 'Archived' : 'Pending — after security return' },
  ];
  const closureReadiness = Math.round(closureItems.filter(c => c.done).length / closureItems.length * 100);

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
            <h1 className="text-xl font-bold text-slate-900 num">{account.loan_account_number}</h1>
            <StatusBadge label={mapInitialStatus(account.loan_account_status)} size="md" />
          </div>
          <div className="flex items-center gap-3 mt-0.5 text-sm text-slate-500">
            <span>{account.member.display_name}</span>
            <span>·</span>
            <span className="num">{fmtDecimal(account.disbursed_amount)} disbursed</span>
            <span>·</span>
            <span>SAP: <span className="num font-medium text-slate-900">{account.sap_customer_code || 'Pending'}</span></span>
          </div>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { label: 'Sanctioned', value: fmtDecimal(account.sanctioned_amount), color: 'slate' },
          { label: 'Disbursed', value: fmtDecimal(account.disbursed_amount), color: account.loan_account_status === 'active' ? 'green' : 'slate' },
          { label: 'Outstanding Principal', value: fmtDecimal(account.principal_outstanding), color: 'slate' },
          { label: 'Outstanding Interest', value: fmtDecimal(account.interest_outstanding), color: 'slate' },
          { label: 'Total Outstanding', value: fmtDecimal(account.total_outstanding), color: 'slate' },
        ].map(({ label, value, color }) => (
          <div key={label} className={`rounded-lg border p-3 ${
            color === 'red' ? 'bg-red-50 border-red-200' :
            color === 'amber' ? 'bg-amber-50 border-amber-200' :
            color === 'green' ? 'bg-green-50 border-green-200' : 'bg-slate-50 border-slate-200'
          }`}>
            <p className="text-xs text-slate-500 font-medium">{label}</p>
            <p className={`text-lg font-bold num mt-0.5 ${
              color === 'red' ? 'text-red-900' : color === 'amber' ? 'text-amber-900' :
              color === 'green' ? 'text-green-900' : 'text-slate-900'
            }`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <Tabs tabs={TABS} activeIndex={activeTab} onChange={setActiveTab}>

        {/* Tab 0: Summary */}
        <div className="card space-y-5">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Account Number', value: account.loan_account_number },
              { label: 'Application Number', value: account.application_reference_number || '—' },
              { label: 'Member', value: account.member.display_name },
              { label: 'Loan Type', value: mapStatus(account.loan_type) },
              { label: 'Facility Type', value: mapStatus(account.facility_type) },
              { label: 'Interest Rate', value: `${account.current_interest_rate}% ${mapStatus(account.interest_rate_type)}` },
              { label: 'Tenure', value: `${account.tenure_months} months` },
              { label: 'Tenure Start', value: formatDate(account.tenure_start_date || undefined) },
              { label: 'Tenure End', value: formatDate(account.tenure_end_date || undefined) },
              { label: 'Repayment Due', value: formatDate(account.repayment_date) },
              { label: 'SAP Customer Code', value: account.sap_customer_code || 'Pending' },
              { label: 'Created', value: formatTime(account.created_at) },
              { label: 'Activated', value: account.activated_at ? formatTime(account.activated_at) : 'Not activated' },
            ].map(({ label, value }) => (
              <div key={label} className="bg-slate-50 rounded-lg p-3">
                <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
              </div>
            ))}
          </div>
          <div className="border-t pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Linked Application:</span>
              <span className="text-green-600 flex items-center gap-1 font-medium num">
                {account.application_reference_number || account.loan_application_id} <ArrowRight size={12} />
              </span>
            </div>
          </div>
        </div>

        {/* Tab 1: Loan Ledger */}
        <div className="card p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr className="border-b border-slate-200">
                  <th className="table-header text-left">Date</th>
                  <th className="table-header text-left">Type</th>
                  <th className="table-header text-left">Reference</th>
                  <th className="table-header text-right">Debit</th>
                  <th className="table-header text-right">Credit</th>
                  <th className="table-header text-right">Principal Bal.</th>
                  <th className="table-header text-right">Interest Bal.</th>
                  <th className="table-header text-left">SAP Status</th>
                  <th className="table-header text-left">Remarks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr className="hover:bg-slate-50 transition-colors">
                  <td className="table-cell">{formatDate(loan.disbursementDate)}</td>
                  <td className="table-cell font-medium text-slate-900">Disbursement</td>
                  <td className="table-cell font-mono text-xs text-slate-500">{loan.sapCustomerCode || 'SAP-Pending'}</td>
                  <td className="table-cell text-right num font-semibold">{fmt(loan.disbursedAmount)}</td>
                  <td className="table-cell text-right text-slate-400">—</td>
                  <td className="table-cell text-right num text-slate-700">{fmt(loan.disbursedAmount)}</td>
                  <td className="table-cell text-right num text-slate-700">₹0</td>
                  <td className="table-cell"><StatusBadge label="Posted" size="sm" /></td>
                  <td className="table-cell text-slate-500">Initial disbursement recorded</td>
                </tr>
                {loanRepayments.map(r => (
                  <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                    <td className="table-cell">{formatDate(r.receiptDate)}</td>
                    <td className="table-cell font-medium text-slate-900">Repayment</td>
                    <td className="table-cell font-mono text-xs text-slate-500">{r.bankReference}</td>
                    <td className="table-cell text-right text-slate-400">—</td>
                    <td className="table-cell text-right num font-semibold text-green-700">{fmt(r.amount)}</td>
                    <td className="table-cell text-right num text-slate-700">{fmt(loan.disbursedAmount - r.principalAllocation)}</td>
                    <td className="table-cell text-right num text-slate-700">{fmt(r.interestAllocation)}</td>
                    <td className="table-cell"><StatusBadge label={r.sapEntryStatus === 'posted' ? 'Posted' : 'Pending'} size="sm" /></td>
                    <td className="table-cell text-slate-500">{r.channel === 'subsidiary_deduction' ? `Subsidiary: ${r.subsidiaryName}` : r.channel.replace(/_/g, ' ')}</td>
                  </tr>
                ))}
                {loan.accruedInterest > 0 && (
                  <tr className="hover:bg-slate-50 transition-colors bg-amber-50/40">
                    <td className="table-cell">{formatDate(new Date(new Date(loan.disbursementDate).getTime() + 30*24*60*60*1000).toISOString())}</td>
                    <td className="table-cell font-medium text-slate-900">Interest Accrual</td>
                    <td className="table-cell font-mono text-xs text-slate-500">—</td>
                    <td className="table-cell text-right num font-semibold text-amber-700">{fmt(loan.accruedInterest)}</td>
                    <td className="table-cell text-right text-slate-400">—</td>
                    <td className="table-cell text-right num text-slate-700">{fmt(loan.outstandingPrincipal)}</td>
                    <td className="table-cell text-right num text-slate-700">{fmt(loan.accruedInterest)}</td>
                    <td className="table-cell"><StatusBadge label="Pending" size="sm" /></td>
                    <td className="table-cell text-slate-500">Monthly interest accrued</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 2: Repayment Schedule */}
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Indicative Repayment Schedule</h3>
          <p className="text-xs text-slate-400 mb-4">Based on configured rate and term sheet schedule.</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">#</th>
                  <th className="table-header text-left">Due Date</th>
                  <th className="table-header text-right">Opening Principal</th>
                  <th className="table-header text-right">Principal</th>
                  <th className="table-header text-right">Interest</th>
                  <th className="table-header text-right">Total Due</th>
                  <th className="table-header text-right">Amount Received</th>
                  <th className="table-header text-right">Closing Balance</th>
                  <th className="table-header text-left">Status</th>
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
                  const isPaid = loan.lastRepaymentDate && new Date(loan.lastRepaymentDate) >= dueDate;
                  return (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="table-cell text-slate-500">{i + 1}</td>
                      <td className="table-cell">{formatDate(dueDate.toISOString())}</td>
                      <td className="table-cell text-right num">{fmt(open)}</td>
                      <td className="table-cell text-right num text-green-700">{fmt(principal)}</td>
                      <td className="table-cell text-right num text-amber-700">{fmt(interest)}</td>
                      <td className="table-cell text-right num font-semibold">{fmt(emi)}</td>
                      <td className="table-cell text-right text-slate-400">{isPaid ? fmt(emi) : '—'}</td>
                      <td className="table-cell text-right num">{fmt(close)}</td>
                      <td className="table-cell"><StatusBadge label={isPaid ? 'Paid' : dueDate < new Date() ? 'Overdue' : 'Pending'} size="sm" /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Tab 3: Interest Invoices */}
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Interest Invoices — {loan.accountNumber}</h3>
            <span className="text-xs text-slate-400">{loan.interestRate}% p.a. · Principal-first</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Invoice ID</th>
                  <th className="table-header text-left">Period</th>
                  <th className="table-header text-right">Principal O/S</th>
                  <th className="table-header text-right">Rate</th>
                  <th className="table-header text-right">Days</th>
                  <th className="table-header text-right">Interest Amount</th>
                  <th className="table-header text-left">Invoice Date</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">SAP</th>
                  <th className="table-header"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {interestInvoices.map(inv => (
                  <tr key={inv.id} className="hover:bg-slate-50">
                    <td className="table-cell font-mono text-xs text-slate-600">{inv.id}</td>
                    <td className="table-cell font-medium">{inv.period}</td>
                    <td className="table-cell text-right num">{fmt(inv.principalOs)}</td>
                    <td className="table-cell text-right">{inv.rate}%</td>
                    <td className="table-cell text-right">{inv.days}</td>
                    <td className="table-cell text-right num font-semibold text-amber-700">{fmt(inv.interest)}</td>
                    <td className="table-cell text-slate-500">{inv.invoiceDate || '—'}</td>
                    <td className="table-cell">
                      <StatusBadge label={inv.status === 'generated' ? 'Generated' : 'Draft'} size="sm" />
                    </td>
                    <td className="table-cell">
                      {inv.sapStatus ? <StatusBadge label={inv.sapStatus === 'posted' ? 'Posted' : 'Pending'} size="sm" /> : <span className="text-slate-400 text-xs">—</span>}
                    </td>
                    <td className="table-cell">
                      {inv.status === 'generated' && (
                        <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
                          <Download size={10} /> PDF
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 text-xs text-amber-800">
            Total interest invoiced: <span className="font-semibold">{fmt(interestInvoices.filter(i => i.status === 'generated').reduce((s, i) => s + i.interest, 0))}</span>
            · Outstanding invoices: <span className="font-semibold">{interestInvoices.filter(i => i.sapStatus === 'pending').length}</span>
          </div>
        </div>

        {/* Tab 4: Documents */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-700">Loan Documents</h3>
          {loanDocs.length === 0 ? (
            <p className="text-sm text-slate-400">No document records linked to this loan application.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Document</th>
                    <th className="table-header text-left">Required</th>
                    <th className="table-header text-left">Status</th>
                    <th className="table-header text-left">Stamp</th>
                    <th className="table-header text-left">Notarisation</th>
                    <th className="table-header text-left">Verified By</th>
                    <th className="table-header"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loanDocs.map(doc => (
                    <tr key={doc.id} className="hover:bg-slate-50">
                      <td className="table-cell font-medium text-slate-900">{DOC_TYPE_LABELS[doc.documentType] || doc.documentType}</td>
                      <td className="table-cell"><StatusBadge label={doc.requiredFlag} size="sm" /></td>
                      <td className="table-cell"><StatusBadge label={doc.status} size="sm" /></td>
                      <td className="table-cell text-xs text-slate-500">{doc.stampStatus || '—'}</td>
                      <td className="table-cell text-xs text-slate-500">{doc.notarisationStatus || '—'}</td>
                      <td className="table-cell text-xs text-slate-500">{doc.verifiedBy || '—'}</td>
                      <td className="table-cell">
                        {doc.status !== 'not_started' && doc.status !== 'pending_upload' && (
                          <button className="flex items-center gap-1 text-xs text-green-700 hover:underline">
                            <Download size={10} /> View
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Tab 5: Security */}
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Security Instruments</h3>
            <span className="text-xs text-slate-400">{loanSecurities.length} instrument(s) registered</span>
          </div>
          {loanSecurities.length === 0 ? (
            <p className="text-sm text-slate-400">No security instruments recorded for this loan.</p>
          ) : (
            <div className="space-y-3">
              {loanSecurities.map(s => (
                <div key={s.id} className={`rounded-lg border p-4 ${s.status === 'invoked' ? 'bg-red-50 border-red-200' : s.status === 'released' || s.status === 'returned' ? 'bg-teal-50 border-teal-100' : 'bg-slate-50 border-slate-200'}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <Shield size={16} className={s.status === 'invoked' ? 'text-red-600' : 'text-green-600'} />
                      <span className="text-sm font-semibold text-slate-900">{SECURITY_TYPE_LABELS[s.securityType] || s.securityType}</span>
                    </div>
                    <StatusBadge label={s.status} size="sm" />
                  </div>
                  <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    {s.executionDate && <div><span className="text-slate-500">Execution: </span><span className="font-medium">{formatDate(s.executionDate)}</span></div>}
                    {s.custodian && <div><span className="text-slate-500">Custodian: </span><span className="font-medium">{s.custodian}</span></div>}
                    {s.stampDutyStatus && <div><span className="text-slate-500">Stamp: </span><StatusBadge label={s.stampDutyStatus} size="sm" /></div>}
                    {s.notarisationStatus && <div><span className="text-slate-500">Notarisation: </span><StatusBadge label={s.notarisationStatus} size="sm" /></div>}
                    {s.psnNumber && <div><span className="text-slate-500">PSN: </span><span className="font-mono font-medium">{s.psnNumber}</span></div>}
                    {s.invocationStatus && <div><span className="text-slate-500">Invocation: </span><span className="font-medium">{s.invocationStatus.replace(/_/g, ' ')}</span></div>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tab 6: DPD History */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-700">DPD History</h3>
          <div className="space-y-0">
            {dpdHistory.map((event, idx, arr) => (
              <div key={idx} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                    event.dpd > 90 ? 'bg-red-100 text-red-700' : event.dpd > 0 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {event.dpd > 0 ? <AlertTriangle size={13} /> : <CheckCircle2 size={13} />}
                  </div>
                  {idx !== arr.length - 1 && <div className="w-0.5 flex-1 bg-slate-200 my-1" />}
                </div>
                <div className={`flex-1 ${idx !== arr.length - 1 ? 'pb-4' : ''}`}>
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm font-semibold text-slate-900">{event.status}</span>
                    <span className="text-xs text-slate-400 flex-shrink-0">{event.date}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{event.action}</p>
                  {event.dpd > 0 && <span className="text-xs font-medium text-red-600">DPD: {event.dpd} days</span>}
                </div>
              </div>
            ))}
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-600">
            Current DPD: <span className={`font-semibold ${loan.dpd > 90 ? 'text-red-600' : loan.dpd > 0 ? 'text-amber-600' : 'text-green-600'}`}>{loan.dpd} days</span>
            · Bucket: <span className="font-semibold">{dpdLabelDetail}</span>
          </div>
        </div>

        {/* Tab 7: Default History */}
        <div className="card space-y-4">
          <h3 className="text-sm font-semibold text-slate-700">Default History</h3>
          {defaultHistory.length === 0 ? (
            <div className="bg-green-50 border border-green-100 rounded-lg p-4 text-sm text-green-800">
              <CheckCircle2 size={16} className="inline mr-1" />
              No defaults recorded — this loan is current.
            </div>
          ) : (
            <div className="space-y-3">
              {defaultHistory.map((event, idx) => (
                <div key={idx} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm font-semibold text-slate-900">{event.event}</span>
                    <span className="text-xs text-slate-400">{event.date}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{event.action}</p>
                  <p className="text-xs text-slate-400 mt-0.5">By: {event.by}</p>
                  {event.dpd > 0 && <span className="text-xs font-medium text-red-600">DPD at time: {event.dpd} days</span>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tab 8: Closure */}
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Closure Readiness</h3>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${closureReadiness === 100 ? 'bg-green-100 text-green-700' : closureReadiness > 50 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
              {closureReadiness}% ready
            </span>
          </div>
          <div className="space-y-2">
            {closureItems.map((item, idx) => (
              <div key={idx} className={`rounded-lg border p-3 flex items-center justify-between gap-3 ${item.done ? 'bg-green-50 border-green-100' : 'bg-slate-50 border-slate-200'}`}>
                <div className="flex items-center gap-2">
                  {item.done ? <CheckCircle2 size={15} className="text-green-600 flex-shrink-0" /> : <Lock size={15} className="text-slate-400 flex-shrink-0" />}
                  <span className="text-sm font-medium text-slate-900">{item.label}</span>
                </div>
                <span className={`text-xs ${item.done ? 'text-green-700' : 'text-slate-500'}`}>{item.value}</span>
              </div>
            ))}
          </div>
          {loan.status === 'closed' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-800">
                <CheckCircle2 size={16} />
                <span className="font-semibold">Loan Closed</span>
              </div>
              <p className="text-xs text-green-700 mt-1">NOC issued · Security instruments returned · Account archived in 8-year retention schedule.</p>
            </div>
          )}
        </div>

        {/* Tab 9: Audit Trail */}
        <div className="card">
          <div className="space-y-0 p-2">
            {(loanAuditEvents.length > 0 ? loanAuditEvents : [
              { id: 'a1', eventType: 'Loan account created', actorRole: 'system', actorName: 'System', timestamp: loan.disbursementDate, comment: undefined },
              { id: 'a2', eventType: 'SAP customer code confirmed', actorRole: 'accounts', actorName: 'Accounts', timestamp: loan.disbursementDate, comment: loan.sapCustomerCode },
              { id: 'a3', eventType: 'Disbursement recorded', actorRole: 'senior_manager_finance', actorName: 'Senior Manager – Finance', timestamp: loan.disbursementDate, comment: `${fmt(loan.disbursedAmount)} transferred` },
              { id: 'a4', eventType: 'Repayment schedule generated', actorRole: 'system', actorName: 'System', timestamp: loan.disbursementDate, comment: '12-month schedule created' },
            ] as any[]).map((event: any, idx: number, arr: any[]) => (
              <div key={idx} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 bg-blue-100 text-blue-700">
                    <FileText size={14} />
                  </div>
                  {idx !== arr.length - 1 && <div className="w-0.5 flex-1 bg-slate-200 my-1" />}
                </div>
                <div className={`flex-1 ${idx !== arr.length - 1 ? 'pb-4' : ''}`}>
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-sm font-semibold text-slate-900">{event.eventType}</span>
                    <span className="text-xs text-slate-400 flex-shrink-0">{formatTime(event.timestamp)}</span>
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">{event.actorName} · {String(event.actorRole).replace(/_/g, ' ')}</div>
                  {(event.comment || event.reason) && <p className="text-xs text-slate-400 mt-0.5">{event.comment || event.reason}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Tabs>
    </div>
  );
};

export default LoanAccount360;
