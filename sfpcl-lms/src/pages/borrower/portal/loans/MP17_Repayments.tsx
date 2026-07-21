import React, { useEffect, useState } from 'react';
import { ArrowLeft, IndianRupee } from 'lucide-react';
import AlertBanner from '../../../../components/ui/AlertBanner';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { fetchPortalLoanAccount, fetchPortalRepaymentHistory, PortalLoanAccountDetail, PortalRepaymentHistoryItem } from '../../../../services/portalApi';
import { date, money, portalLoanError } from './MP15_MyLoans';

const MP17_Repayments: React.FC<{ loanAccountId: string | null; onBack: () => void }> = ({ loanAccountId, onBack }) => {
  const [account, setAccount] = useState<PortalLoanAccountDetail | null>(null);
  const [rows, setRows] = useState<PortalRepaymentHistoryItem[]>([]);
  const [loading, setLoading] = useState(Boolean(loanAccountId));
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let current = true;
    if (!loanAccountId) { setLoading(false); return; }
    Promise.all([fetchPortalLoanAccount(loanAccountId), fetchPortalRepaymentHistory(loanAccountId)])
      .then(([detail, history]) => { if (current) { setAccount(detail); setRows(history); } })
      .catch(reason => { if (current) setError(portalLoanError(reason)); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [loanAccountId]);
  return <div className="space-y-6"><div><h2 className="text-xl font-bold text-slate-900">Repayments</h2><p className="text-sm text-slate-500 mt-1">Only repayments verified and posted by SFPCL are shown as confirmed.</p></div>{loanAccountId && <button type="button" onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-slate-600"><ArrowLeft size={16} />Back to My Loans</button>}{!loanAccountId && <AlertBanner type="info" title="Select a loan from My Loans to view confirmed repayments." />}{loading && <AlertBanner type="info" title="Loading confirmed repayments…" />}{!loading && error && <AlertBanner type="error" title={error} />}{!loading && !error && account && <><div className="bg-white rounded-xl border border-slate-100 p-5 grid grid-cols-1 sm:grid-cols-2 gap-4"><div><p className="text-xs text-slate-500">Loan Account</p><p className="text-sm font-bold text-slate-900 mt-1">{account.loan_account_number}</p></div><div><p className="text-xs text-slate-500">Outstanding Balance</p><p className="text-lg font-bold text-slate-900 mt-1">{money(account.total_outstanding)}</p></div></div>{rows.length === 0 ? <AlertBanner type="info" title="No confirmed repayments yet." /> : <div className="bg-white rounded-xl border border-slate-100 overflow-hidden"><div className="overflow-x-auto"><table className="w-full text-sm"><thead><tr className="border-b border-slate-100">{['Receipt Date', 'Amount', 'Principal', 'Interest', 'Mode / Reference', 'Status'].map(label => <th key={label} className="px-4 py-3 text-left text-xs font-semibold text-slate-500">{label}</th>)}</tr></thead><tbody className="divide-y divide-slate-50">{rows.map(row => <tr key={row.repayment_id}><td className="px-4 py-3 whitespace-nowrap">{date(row.receipt_date)}</td><td className="px-4 py-3 font-semibold whitespace-nowrap"><IndianRupee size={13} className="inline" />{money(row.amount_received).replace(/^₹/, '')}</td><td className="px-4 py-3 whitespace-nowrap">{money(row.allocated_to_principal)}</td><td className="px-4 py-3 whitespace-nowrap">{money(row.allocated_to_interest)}</td><td className="px-4 py-3"><p className="uppercase">{row.payment_mode}</p><p className="text-xs text-slate-500">{row.reference}</p></td><td className="px-4 py-3"><StatusBadge label="confirmed" size="sm" /></td></tr>)}</tbody></table></div></div>}</>}</div>;
};
export default MP17_Repayments;
