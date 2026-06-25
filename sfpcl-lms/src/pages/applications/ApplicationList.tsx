import React, { useState } from 'react';
import { Plus, Search, Filter, ChevronDown } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { loanApplications } from '../../data/mockData';
import type { ApplicationStatus } from '../../types';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

interface ApplicationListProps {
  onNew: () => void;
  onSelect: (id: string) => void;
}

const STATUS_OPTIONS: Array<ApplicationStatus | 'all'> = [
  'all', 'draft', 'submitted', 'reference_generated', 'appraisal_pending',
  'credit_review', 'pending_sanction', 'sanctioned', 'rejected_credit', 'rejected_sanction',
];

const STATUS_LABELS: Record<string, string> = {
  all: 'All statuses',
  draft: 'Draft', submitted: 'Submitted', reference_generated: 'Reference Generated',
  appraisal_pending: 'Appraisal Pending', credit_review: 'Credit Review',
  pending_sanction: 'Pending Sanction', sanctioned: 'Sanctioned',
  rejected_credit: 'Rejected (Credit)', rejected_sanction: 'Rejected (Sanction)',
};

const ApplicationList: React.FC<ApplicationListProps> = ({ onNew, onSelect }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'all'>('all');
  const [exceptionOnly, setExceptionOnly] = useState(false);

  const filtered = loanApplications.filter(app => {
    const matchSearch =
      app.applicationNumber.toLowerCase().includes(search.toLowerCase()) ||
      app.memberName.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || app.status === statusFilter;
    const matchException = !exceptionOnly || app.isException;
    return matchSearch && matchStatus && matchException;
  });

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Loan Applications</h1>
          <p className="text-sm text-slate-500 mt-0.5">{filtered.length} application{filtered.length !== 1 ? 's' : ''}</p>
        </div>
        <button onClick={onNew} className="btn-primary flex items-center gap-2">
          <Plus size={16} />
          New Application
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by number or member…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="field-input pl-8 text-sm py-2"
          />
        </div>

        <div className="relative">
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value as ApplicationStatus | 'all')}
            className="field-select text-sm py-2 pr-8 appearance-none"
          >
            {STATUS_OPTIONS.map(s => (
              <option key={s} value={s}>{STATUS_LABELS[s]}</option>
            ))}
          </select>
          <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
        </div>

        <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
          <input
            type="checkbox"
            checked={exceptionOnly}
            onChange={e => setExceptionOnly(e.target.checked)}
            className="rounded border-slate-300 text-green-600"
          />
          Exceptions only
        </label>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="table-header text-left">Application No.</th>
                <th className="table-header text-left">Member</th>
                <th className="table-header text-left">Type</th>
                <th className="table-header text-right">Requested</th>
                <th className="table-header text-right">Eligible</th>
                <th className="table-header text-left">Status</th>
                <th className="table-header text-left">Current Owner</th>
                <th className="table-header text-left">TAT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="table-cell text-center text-slate-400 py-12">
                    No applications match your filters.
                  </td>
                </tr>
              ) : (
                filtered.map(app => (
                  <tr
                    key={app.id}
                    onClick={() => onSelect(app.id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-green-700 num">{app.applicationNumber}</span>
                        {app.isException && (
                          <span className="text-xs bg-violet-100 text-violet-700 px-1 py-0.5 rounded font-medium">EX</span>
                        )}
                      </div>
                      <div className="text-xs text-slate-400">{app.applicationDate}</div>
                    </td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-900">{app.memberName}</div>
                    </td>
                    <td className="table-cell">
                      <span className="text-xs capitalize text-slate-600">{app.memberType === 'fpc' ? 'FPC' : app.memberType.replace('_', ' ')}</span>
                    </td>
                    <td className="table-cell text-right num">{fmt(app.requestedAmount)}</td>
                    <td className="table-cell text-right num">{fmt(app.eligibleAmount)}</td>
                    <td className="table-cell">
                      <StatusBadge label={app.status} size="sm" />
                    </td>
                    <td className="table-cell">
                      <div className="text-slate-700">{app.currentOwner}</div>
                    </td>
                    <td className="table-cell">
                      {app.tatDaysRemaining !== undefined && (
                        <span className={`text-xs font-semibold ${
                          app.tatDaysRemaining === 0 ? 'text-red-600' :
                          app.tatDaysRemaining <= 1 ? 'text-amber-600' : 'text-slate-500'
                        }`}>
                          {app.tatDaysRemaining === 0 ? 'Overdue' : `${app.tatDaysRemaining}d left`}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ApplicationList;
