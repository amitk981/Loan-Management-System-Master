import React from 'react';
import { AlertTriangle, TrendingDown, Bell, FileBarChart2 } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanAccounts } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const DPD_BUCKETS = [
  { key: '0', label: 'Current (DPD 0)', min: 0, max: 0, color: 'green' },
  { key: '1_30', label: '1–30 days', min: 1, max: 30, color: 'amber' },
  { key: '31_90', label: '31–90 days', min: 31, max: 90, color: 'orange' },
  { key: '91_365', label: '91 days–1 year', min: 91, max: 365, color: 'red' },
  { key: '1yr_plus', label: '1+ year', min: 366, max: 9999, color: 'red' },
];

interface MonitoringDashboardProps {
  onOpenLoan: (id: string) => void;
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({ onOpenLoan }) => {
  const atRisk = loanAccounts.filter(l => l.dpd > 0 || l.status === 'grace_period');
  const overdue = loanAccounts.filter(l => l.status === 'overdue' || l.status === 'default_review');

  const bucketCounts = DPD_BUCKETS.map(b => ({
    ...b,
    loans: loanAccounts.filter(l => l.dpd >= b.min && l.dpd <= b.max),
    amount: loanAccounts
      .filter(l => l.dpd >= b.min && l.dpd <= b.max)
      .reduce((s, l) => s + l.outstandingPrincipal, 0),
  }));

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Monitoring Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">DPD tracking, reminders, and portfolio health</p>
      </div>

      {/* Alerts */}
      {overdue.length > 0 && (
        <AlertBanner
          type="error"
          title={`${overdue.length} loan${overdue.length > 1 ? 's' : ''} overdue — immediate action required`}
          message={overdue.map(l => `${l.accountNumber} (DPD: ${l.dpd})`).join(' · ')}
        />
      )}

      {/* DPD Bucket Analysis */}
      <div>
        <h2 className="section-title mb-3">DPD Bucket Analysis</h2>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          {bucketCounts.map(b => (
            <div
              key={b.key}
              className={`rounded-lg border p-4 text-center ${
                b.color === 'green' ? 'bg-green-50 border-green-200' :
                b.color === 'amber' ? 'bg-amber-50 border-amber-200' :
                b.color === 'orange' ? 'bg-orange-50 border-orange-200' : 'bg-red-50 border-red-200'
              }`}
            >
              <div className={`text-2xl font-bold num ${
                b.color === 'green' ? 'text-green-900' :
                b.color === 'amber' ? 'text-amber-900' :
                b.color === 'orange' ? 'text-orange-900' : 'text-red-900'
              }`}>{b.loans.length}</div>
              <div className={`text-xs font-medium mt-0.5 ${
                b.color === 'green' ? 'text-green-700' :
                b.color === 'amber' ? 'text-amber-700' :
                b.color === 'orange' ? 'text-orange-700' : 'text-red-700'
              }`}>{b.label}</div>
              {b.amount > 0 && (
                <div className="text-xs text-slate-500 mt-1 num">{fmt(b.amount)}</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* At-risk loans */}
      <div>
        <h2 className="section-title mb-3 flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-500" />
          At-Risk Loans ({atRisk.length})
        </h2>
        {atRisk.length === 0 ? (
          <div className="card text-center py-8 text-slate-400 text-sm">No at-risk loans.</div>
        ) : (
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Account No.</th>
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-right">Outstanding</th>
                  <th className="table-header text-right">Accrued Interest</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Due Date</th>
                  <th className="table-header text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {atRisk.map(l => (
                  <tr key={l.id} className="hover:bg-slate-50 transition-colors">
                    <td className="table-cell">
                      <button onClick={() => onOpenLoan(l.id)} className="font-semibold text-green-700 num hover:underline">
                        {l.accountNumber}
                      </button>
                    </td>
                    <td className="table-cell font-medium text-slate-900">{l.memberName}</td>
                    <td className="table-cell text-right num font-semibold text-amber-700">{fmt(l.outstandingPrincipal)}</td>
                    <td className="table-cell text-right num text-red-700">{fmt(l.accruedInterest)}</td>
                    <td className="table-cell"><StatusBadge label={l.status} size="sm" /></td>
                    <td className="table-cell text-right">
                      <span className={`font-bold num ${l.dpd > 90 ? 'text-red-600' : 'text-amber-600'}`}>{l.dpd}</span>
                    </td>
                    <td className="table-cell text-sm text-slate-600">{new Date(l.repaymentDueDate).toLocaleDateString('en-IN')}</td>
                    <td className="table-cell">
                      <div className="flex gap-1">
                        <button className="text-xs px-2 py-1 bg-amber-50 border border-amber-200 rounded text-amber-700 hover:bg-amber-100">
                          <Bell size={10} className="inline mr-0.5" /> Remind
                        </button>
                        {l.dpd > 90 && (
                          <button className="text-xs px-2 py-1 bg-red-50 border border-red-200 rounded text-red-700 hover:bg-red-100">
                            <TrendingDown size={10} className="inline mr-0.5" /> Recovery
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* MIS Summary */}
      <div>
        <h2 className="section-title mb-3 flex items-center gap-2">
          <FileBarChart2 size={16} /> MIS Summary
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Loan Accounts', value: loanAccounts.length },
            { label: 'Total Portfolio (OS)', value: fmt(loanAccounts.reduce((s, l) => s + l.outstandingPrincipal, 0)) },
            { label: 'Accrued Interest (Total)', value: fmt(loanAccounts.reduce((s, l) => s + l.accruedInterest, 0)) },
            { label: 'Loans with DPD > 0', value: loanAccounts.filter(l => l.dpd > 0).length },
          ].map(({ label, value }) => (
            <div key={label} className="card">
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">{label}</p>
              <p className="text-xl font-bold text-slate-900 num mt-1">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MonitoringDashboard;
