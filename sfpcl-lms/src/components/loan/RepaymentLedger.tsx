import React from 'react';
import { CheckCircle2, Clock, XCircle } from 'lucide-react';
import { repaymentRecords } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

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
  loanAccountId, outstandingPrincipal, disbursedAmount,
}) => {
  const records = repaymentRecords.filter(r => r.loanAccountId === loanAccountId);

  const totalPaid = records.reduce((s, r) => s + r.amount, 0);
  const totalPrincipal = records.reduce((s, r) => s + r.principalAllocation, 0);
  const totalInterest = records.reduce((s, r) => s + r.interestAllocation, 0);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
          <div className="text-xs text-slate-500 font-medium">Disbursed</div>
          <div className="text-lg font-bold text-slate-900 num mt-0.5">{fmt(disbursedAmount || 0)}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3 text-center">
          <div className="text-xs text-green-700 font-medium">Total Paid</div>
          <div className="text-lg font-bold text-green-900 num mt-0.5">{fmt(totalPaid)}</div>
        </div>
        <div className="bg-amber-50 rounded-lg border border-amber-200 p-3 text-center">
          <div className="text-xs text-amber-700 font-medium">Outstanding</div>
          <div className="text-lg font-bold text-amber-900 num mt-0.5">{fmt(outstandingPrincipal || 0)}</div>
        </div>
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
          <div className="text-xs text-slate-500 font-medium">Interest Collected</div>
          <div className="text-lg font-bold text-slate-900 num mt-0.5">{fmt(totalInterest)}</div>
        </div>
      </div>

      {/* Ledger table */}
      {records.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-sm">No repayment records yet.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="table-header text-left">Date</th>
                <th className="table-header text-right">Amount</th>
                <th className="table-header text-right">Principal</th>
                <th className="table-header text-right">Interest</th>
                <th className="table-header text-left">Channel</th>
                <th className="table-header text-left">Reference</th>
                <th className="table-header text-left">SAP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {records.map(r => (
                <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                  <td className="table-cell">{new Date(r.receiptDate).toLocaleDateString('en-IN')}</td>
                  <td className="table-cell text-right num font-semibold">{fmt(r.amount)}</td>
                  <td className="table-cell text-right num text-green-700">{fmt(r.principalAllocation)}</td>
                  <td className="table-cell text-right num text-amber-700">{fmt(r.interestAllocation)}</td>
                  <td className="table-cell">
                    <div>{CHANNEL_LABELS[r.channel]}</div>
                    {r.subsidiaryName && <div className="text-xs text-slate-400 truncate max-w-32">{r.subsidiaryName}</div>}
                  </td>
                  <td className="table-cell num text-xs text-slate-500">{r.bankReference}</td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1">
                      {SAP_ICONS[r.sapEntryStatus]}
                      <span className="text-xs capitalize">{r.sapEntryStatus}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="border-t-2 border-slate-200 bg-slate-50">
              <tr>
                <td className="table-cell font-semibold">Total</td>
                <td className="table-cell text-right num font-bold">{fmt(totalPaid)}</td>
                <td className="table-cell text-right num font-bold text-green-700">{fmt(totalPrincipal)}</td>
                <td className="table-cell text-right num font-bold text-amber-700">{fmt(totalInterest)}</td>
                <td colSpan={3} />
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
};

export default RepaymentLedger;
