import React, { useEffect, useState } from 'react';
import { ArrowLeft, Calendar, FileText, IndianRupee } from 'lucide-react';
import AlertBanner from '../../../../components/ui/AlertBanner';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { fetchPortalInterestInvoices, fetchPortalLoanAccount, fetchPortalLoanSchedule, fetchPortalRepaymentHistory, PortalInterestInvoiceSummary, PortalLoanAccountDetail, PortalLoanScheduleItem, PortalRepaymentHistoryItem } from '../../../../services/portalApi';
import { date, money, portalLoanError } from './MP15_MyLoans';

const MP16_LoanAccountDetail: React.FC<{ loanAccountId: string | null; onBack: () => void; onViewRepayments: () => void }> = ({ loanAccountId, onBack, onViewRepayments }) => {
  const [detail, setDetail] = useState<PortalLoanAccountDetail | null>(null);
  const [schedule, setSchedule] = useState<PortalLoanScheduleItem[]>([]);
  const [repayments, setRepayments] = useState<PortalRepaymentHistoryItem[]>([]);
  const [invoices, setInvoices] = useState<PortalInterestInvoiceSummary[]>([]);
  const [loading, setLoading] = useState(Boolean(loanAccountId));
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let current = true;
    if (!loanAccountId) { setLoading(false); return; }
    Promise.all([fetchPortalLoanAccount(loanAccountId), fetchPortalLoanSchedule(loanAccountId), fetchPortalRepaymentHistory(loanAccountId), fetchPortalInterestInvoices(loanAccountId)])
      .then(([account, scheduleRows, history, invoiceRows]) => { if (current) { setDetail(account); setSchedule(scheduleRows); setRepayments(history); setInvoices(invoiceRows); } })
      .catch(reason => { if (current) setError(portalLoanError(reason)); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [loanAccountId]);
  if (!loanAccountId) return <AlertBanner type="info" title="Select a loan from My Loans to view its account details." />;
  if (loading) return <AlertBanner type="info" title="Loading loan account details…" />;
  if (error || !detail) return <AlertBanner type="error" title={error ?? 'Loan account details are unavailable.'} />;
  return (
    <div className="space-y-6">
      <button type="button" onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"><ArrowLeft size={16} />Back to My Loans</button>
      <div className="bg-white rounded-xl border border-green-200 overflow-hidden">
        <div className="bg-green-50 px-6 py-5 border-b border-green-100 flex items-center justify-between gap-4"><div><p className="text-xs text-green-700">Loan Account Detail</p><h2 className="text-xl font-bold text-green-950">{detail.loan_account_number}</h2></div><StatusBadge label={detail.status} size="sm" /></div>
        <div className="p-6 grid grid-cols-1 sm:grid-cols-3 gap-4">{[['Disbursed Amount', money(detail.disbursed_amount)], ['Outstanding Principal', money(detail.principal_outstanding)], ['Total Outstanding', money(detail.total_outstanding)], ['Interest Due', money(detail.interest_outstanding)], ['Next Repayment', detail.next_due_date ? date(detail.next_due_date) : 'No upcoming due'], ['Repayment Route', detail.repayment_route.replace(/_/g, ' ')], ['Closure Status', detail.closure_status]].map(([label, value]) => <div key={label} className="bg-slate-50 rounded-lg p-3"><p className="text-xs text-slate-500">{label}</p><p className="text-sm font-semibold text-slate-900 mt-0.5 capitalize">{value}</p></div>)}</div>
      </div>
      <Section title="Repayment Schedule" icon={<Calendar size={16} className="text-green-600" />} empty="No repayment schedule is available."><ScheduleTable rows={schedule} /></Section>
      <Section title="Confirmed Repayment History" icon={<IndianRupee size={16} className="text-green-600" />} empty="No confirmed repayments yet.">{repayments.length > 0 && <div className="space-y-2">{repayments.map(row => <div key={row.repayment_id} className="bg-slate-50 rounded-lg p-3 flex justify-between gap-4"><div><p className="text-sm font-medium text-slate-900">{money(row.amount_received)} · {row.payment_mode.toUpperCase()}</p><p className="text-xs text-slate-500 mt-0.5">{date(row.receipt_date)} · Ref {row.reference}</p></div><StatusBadge label="confirmed" size="sm" /></div>)}</div>}</Section>
      <Section title="Interest Invoices and Notices" icon={<FileText size={16} className="text-green-600" />} empty="No issued interest invoices.">{invoices.length > 0 && <div className="space-y-2">{invoices.map(row => <div key={row.invoice_id} className="bg-slate-50 rounded-lg p-3"><p className="text-sm font-medium text-slate-900">{row.invoice_number} · {money(row.interest_amount)}</p><p className="text-xs text-slate-500 mt-0.5">{row.financial_year} · {date(row.invoice_date)}</p></div>)}</div>}</Section>
      <button type="button" onClick={onViewRepayments} className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium">View Full Repayment History</button>
    </div>
  );
};

const Section = ({ title, icon, empty, children }: { title: string; icon: React.ReactNode; empty: string; children?: React.ReactNode }) => <div className="bg-white rounded-xl border border-slate-100 p-5"><h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">{icon}{title}</h3>{children || <p className="text-sm text-slate-500">{empty}</p>}</div>;
export const ScheduleTable = ({ rows }: { rows: PortalLoanScheduleItem[] }) => rows.length === 0 ? null : <div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="border-b border-slate-100">{['Due Date', 'Principal', 'Interest', 'Paid', 'Status'].map(label => <th key={label} className="px-3 py-2 text-left text-xs font-semibold text-slate-500">{label}</th>)}</tr></thead><tbody className="divide-y divide-slate-50">{rows.map(row => <tr key={row.schedule_id}><td className="px-3 py-3 whitespace-nowrap">{date(row.due_date)}</td><td className="px-3 py-3 whitespace-nowrap">{money(row.principal_due)}</td><td className="px-3 py-3 whitespace-nowrap">{money(row.interest_due)}</td><td className="px-3 py-3 whitespace-nowrap">{money(row.paid_amount)}</td><td className="px-3 py-3"><StatusBadge label={row.status} size="sm" /></td></tr>)}</tbody></table></div>;
export default MP16_LoanAccountDetail;
