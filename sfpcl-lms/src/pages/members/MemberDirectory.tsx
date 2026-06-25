import React, { useState } from 'react';
import { Search, Users, AlertTriangle, RefreshCw, Eye, BarChart2 } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { members } from '../../data/mockData';

const fmt = (n: number) => '\u20b9' + n.toLocaleString('en-IN');

interface MemberDirectoryProps {
  onSelect: (memberId: string) => void;
  onBorrower360?: (memberId: string) => void;
}

const MemberDirectory: React.FC<MemberDirectoryProps> = ({ onSelect, onBorrower360 }) => {
  const [search, setSearch] = useState('');
  const [kycFilter, setKycFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const filtered = members.filter(m => {
    const matchSearch =
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.folioNumber.toLowerCase().includes(search.toLowerCase());
    const matchKyc = kycFilter === 'all' || m.kycStatus === kycFilter;
    const matchType = typeFilter === 'all' || m.memberType === typeFilter;
    return matchSearch && matchKyc && matchType;
  });

  const reKycCount = members.filter(m => m.kycStatus === 'rekyc_due' || m.kycStatus === 'expired').length;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Member Directory</h1>
          <p className="text-sm text-slate-500 mt-0.5">{filtered.length} members</p>
        </div>
        {reKycCount > 0 && (
          <div className="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            <RefreshCw size={14} />
            {reKycCount} member{reKycCount > 1 ? 's' : ''} require Re-KYC
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name or folio…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="field-input pl-8 py-2 text-sm"
          />
        </div>
        <select
          value={kycFilter}
          onChange={e => setKycFilter(e.target.value)}
          className="field-select py-2 text-sm"
        >
          <option value="all">All KYC statuses</option>
          <option value="verified">Verified</option>
          <option value="rekyc_due">Re-KYC Due</option>
          <option value="expired">Expired</option>
          <option value="pending">Pending</option>
        </select>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="field-select py-2 text-sm"
        >
          <option value="all">All types</option>
          <option value="individual">Individual</option>
          <option value="fpc">FPC</option>
          <option value="producer_institution">Producer Institution</option>
        </select>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="table-header text-left">Member</th>
                <th className="table-header text-left">Folio / Type</th>
                <th className="table-header text-right">Shares</th>
                <th className="table-header text-left">KYC Status</th>
                <th className="table-header text-left">Active Status</th>
                <th className="table-header text-right">Current Exposure</th>
                <th className="table-header text-left">Default</th>
                <th className="table-header text-left">Supply Years</th>
                <th className="table-header text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="table-cell text-center text-slate-400 py-12">
                    No members found.
                  </td>
                </tr>
              ) : (
                filtered.map(m => (
                  <tr
                    key={m.id}
                    onClick={() => onSelect(m.id)}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                          <Users size={14} className="text-green-700" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900">{m.name}</div>
                          <div className="text-xs text-slate-400">{m.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="table-cell">
                      <div className="font-medium text-slate-700 num">{m.folioNumber}</div>
                      <div className="text-xs text-slate-400 capitalize">{m.memberType === 'fpc' ? 'FPC' : m.memberType}</div>
                    </td>
                    <td className="table-cell text-right num">
                      <div>{m.sharesHeld.toLocaleString('en-IN')}</div>
                      <div className="text-xs text-slate-400 capitalize">{m.shareMode}</div>
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={m.kycStatus} size="sm" />
                    </td>
                    <td className="table-cell">
                      <StatusBadge label={m.activeStatus} size="sm" />
                    </td>
                    <td className="table-cell text-right num">
                      {m.currentExposure > 0 ? (
                        <span className="text-amber-700 font-medium">{fmt(m.currentExposure)}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="table-cell">
                      {m.defaultStatus !== 'no_default' ? (
                        <span className="flex items-center gap-1 text-xs text-red-600">
                          <AlertTriangle size={12} />
                          {m.defaultStatus === 'current_default' ? 'Current' : 'Past'}
                        </span>
                      ) : (
                        <span className="text-xs text-green-600">None</span>
                      )}
                    </td>
                    <td className="table-cell">
                      <span className="text-sm text-slate-700">{m.supplyYears} yr{m.supplyYears !== 1 ? 's' : ''}</span>
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => onSelect(m.id)}
                          className="flex items-center gap-1 text-xs text-green-700 hover:text-green-900 px-2 py-1 rounded hover:bg-green-50 transition-colors"
                          title="Member Profile"
                        >
                          <Eye size={12} /> Profile
                        </button>
                        {onBorrower360 && (
                          <button
                            onClick={() => onBorrower360(m.id)}
                            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 px-2 py-1 rounded hover:bg-blue-50 transition-colors"
                            title="Borrower 360"
                          >
                            <BarChart2 size={12} /> 360
                          </button>
                        )}
                      </div>
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

export default MemberDirectory;
