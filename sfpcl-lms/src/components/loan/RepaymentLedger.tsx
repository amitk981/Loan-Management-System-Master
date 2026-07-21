import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import AlertBanner from '../ui/AlertBanner';
import type { Pagination } from '../../services/authSession';
import type { LoanLedgerRow } from '../../services/servicingApi';
import { formatMoney } from '../../utils/formatMoney';

const date = (value: string) => new Date(value).toLocaleDateString('en-GB', {
  day: 'numeric', month: 'short', year: 'numeric',
});
const label = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());

interface RepaymentLedgerProps {
  rows: LoanLedgerRow[];
  pagination: Pagination;
  loading?: boolean;
  error?: { message: string; unauthorized: boolean } | null;
  onPage: (page: number) => void;
}

const RepaymentLedger: React.FC<RepaymentLedgerProps> = ({
  rows, pagination, loading = false, error = null, onPage,
}) => {
  if (loading) return <div className="text-center py-8 text-slate-400 text-sm">Loading loan ledger…</div>;
  if (error) return <AlertBanner type="error" title={error.unauthorized ? 'Access Denied' : 'Loan Ledger Unavailable'} message={error.message} />;
  if (rows.length === 0) return <div className="text-center py-8 text-slate-400 text-sm">No financial movements are recorded for this loan.</div>;
  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="bg-slate-50 border-b border-slate-200">
            {['Date', 'Transaction', 'Reference', 'Debit', 'Credit', 'Principal Balance', 'Interest Balance', 'Total Outstanding', 'Posted By', 'SAP Status'].map(column => <th key={column} className={`table-header ${['Debit', 'Credit', 'Principal Balance', 'Interest Balance', 'Total Outstanding'].includes(column) ? 'text-right' : 'text-left'}`}>{column}</th>)}
          </tr></thead>
          <tbody className="divide-y divide-slate-100">{rows.map(row => (
            <tr key={`${row.owner_reference.entity_type}-${row.owner_reference.entity_id}`} className="hover:bg-slate-50 transition-colors">
              <td className="table-cell whitespace-nowrap">{date(row.transaction_date)}</td>
              <td className="table-cell"><div className="font-medium text-slate-800">{label(row.transaction_type)}</div><div className="text-xs text-slate-500">{row.remarks}</div></td>
              <td className="table-cell num">{row.reference}</td>
              <td className="table-cell text-right num">{formatMoney(row.debit)}</td>
              <td className="table-cell text-right num">{formatMoney(row.credit)}</td>
              <td className="table-cell text-right num">{formatMoney(row.principal_balance)}</td>
              <td className="table-cell text-right num">{formatMoney(row.interest_balance)}</td>
              <td className="table-cell text-right num font-semibold">{formatMoney(row.total_outstanding)}</td>
              <td className="table-cell">{row.actor.display_name}</td>
              <td className="table-cell"><span className="text-xs capitalize">{label(row.sap_status)}</span></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <PaginationControls pagination={pagination} onPage={onPage} />
    </div>
  );
};

export const PaginationControls: React.FC<{ pagination: Pagination; onPage: (page: number) => void }> = ({ pagination, onPage }) => (
  <div className="flex items-center justify-between gap-2 text-xs">
    <span className="text-slate-500">Page {pagination.page} of {pagination.total_pages}</span>
    <div className="flex gap-2">
      <button type="button" className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_previous} onClick={() => onPage(pagination.page - 1)}><ChevronLeft size={14} /> Previous</button>
      <button type="button" className="btn-secondary flex items-center gap-1 text-sm" disabled={!pagination.has_next} onClick={() => onPage(pagination.page + 1)}>Next <ChevronRight size={14} /></button>
    </div>
  </div>
);

export default RepaymentLedger;
