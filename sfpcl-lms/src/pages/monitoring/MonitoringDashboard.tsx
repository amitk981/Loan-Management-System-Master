import React, { useState } from 'react';
import { AlertTriangle, TrendingDown, Bell, FileBarChart2, Eye, Calendar, Phone, MessageSquare, CheckCircle2, Clock, X as XIcon } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { loanAccounts } from '../../data/mockData';
import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
};

const DPD_BUCKETS = [
  { key: '0', label: 'Current', min: 0, max: 0, color: 'green' },
  { key: '1_30', label: '1–30 days', min: 1, max: 30, color: 'amber' },
  { key: '31_90', label: '31–90 days', min: 31, max: 90, color: 'orange' },
  { key: '91_365', label: '91 days–1 year', min: 91, max: 365, color: 'red' },
  { key: '1_2_yrs', label: '1–2 years', min: 366, max: 730, color: 'red' },
  { key: '2_3_yrs', label: '2–3 years', min: 731, max: 1095, color: 'red' },
  { key: '3_plus', label: '3+ years', min: 1096, max: 9999, color: 'red' },
];

interface MonitoringDashboardProps {
  onOpenLoan: (id: string) => void;
  onOpenDefault?: () => void;
}

const REMINDER_LOG = [
  { id: 'r1', accountNumber: 'LN-2025-000028', memberName: 'Sunita Bhosale', type: 'SMS', date: '2026-06-24', by: 'System Auto', status: 'delivered', dpd: 47, response: 'No response' },
  { id: 'r2', accountNumber: 'LN-2025-000028', memberName: 'Sunita Bhosale', type: 'Call', date: '2026-06-20', by: 'Ramesh Jadhav (FO)', status: 'connected', dpd: 43, response: 'Promised payment by 30 Jun' },
  { id: 'r3', accountNumber: 'LN-2024-000019', memberName: 'Vijay Deshmukh', type: 'SMS', date: '2026-06-22', by: 'System Auto', status: 'delivered', dpd: 12, response: 'No response' },
  { id: 'r4', accountNumber: 'LN-2024-000015', memberName: 'Manoj Jadhav', type: 'Call', date: '2026-06-18', by: 'Priya Kulkarni (CM)', status: 'not_reached', dpd: 95, response: 'Phone switched off' },
  { id: 'r5', accountNumber: 'LN-2024-000015', memberName: 'Manoj Jadhav', type: 'Notice', date: '2026-06-10', by: 'Priya Kulkarni (CM)', status: 'sent', dpd: 87, response: 'Notice delivered via registered post' },
];

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({ onOpenLoan, onOpenDefault }) => {
  const { currentUser } = useRole();
  const role = currentUser.role;
  const [showReminderLog, setShowReminderLog] = useState(false);

  // Role permissions
  const isAllowed = ['admin', 'credit_manager', 'senior_manager_finance', 'deputy_manager_finance', 'accounts_team', 'cfo', 'auditor', 'sales', 'field_officer', 'compliance_team'].includes(role);
  const canActOnReminder = ['credit_manager'].includes(role);

  if (!isAllowed) {
    return (
      <div className="p-6">
        <AlertBanner type="error" title="Access Denied" message="You do not have permission to view the Monitoring Dashboard." />
      </div>
    );
  }

  // Filter out closed loans for active monitoring counts
  const activeLoans = loanAccounts.filter(l => l.status !== 'closed');
  
  const atRisk = activeLoans.filter(l => l.dpd > 0 || l.status === 'grace_period');
  const overdue = activeLoans.filter(l => l.status === 'overdue' || l.status === 'default_review' || l.status === 'recovery_review');

  const bucketCounts = DPD_BUCKETS.map(b => ({
    ...b,
    loans: activeLoans.filter(l => l.dpd >= b.min && l.dpd <= b.max),
    amount: activeLoans
      .filter(l => l.dpd >= b.min && l.dpd <= b.max)
      .reduce((s, l) => s + l.outstandingPrincipal, 0),
  }));

  // Limit to first 5 cards for horizontal space
  const displayBuckets = bucketCounts.slice(0, 5);

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
          title={`${overdue.length} newly overdue loan${overdue.length > 1 ? 's' : ''} needs review`}
          message={overdue.map(l => `${l.accountNumber} · DPD ${l.dpd}`).join(', ')}
        />
      )}

      {/* DPD Bucket Analysis */}
      <div>
        <h2 className="section-title mb-3">DPD Bucket Analysis</h2>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {displayBuckets.map(b => (
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
          At-Risk / Default Watch ({atRisk.length})
        </h2>
        {atRisk.length === 0 ? (
          <div className="card text-center py-8 text-slate-400 text-sm">No at-risk loans.</div>
        ) : (
          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Account No.</th>
                    <th className="table-header text-left">Borrower / Member</th>
                    <th className="table-header text-right">Outstanding Principal</th>
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
                      <td className="table-cell">
                        <StatusBadge label={l.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} size="sm" type={l.status.includes('recovery') ? 'error' : l.status === 'grace_period' ? 'warning' : 'slate'}/>
                      </td>
                      <td className="table-cell text-right">
                        <span className={`font-bold num ${l.dpd > 90 ? 'text-red-600' : 'text-amber-600'}`}>{l.dpd}</span>
                      </td>
                      <td className="table-cell text-sm text-slate-600">{formatDate(l.repaymentDueDate)}</td>
                      <td className="table-cell">
                        <div className="flex flex-col gap-1.5 items-start">
                          {l.status === 'grace_period' ? (
                            canActOnReminder ? (
                              <button onClick={onOpenDefault} className="text-xs px-2 py-1 bg-amber-50 border border-amber-200 rounded text-amber-700 hover:bg-amber-100 flex items-center">
                                <Eye size={10} className="mr-1" /> View Grace Case
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400">View Only</span>
                            )
                          ) : l.status.includes('recovery') || l.status === 'default_review' ? (
                            canActOnReminder ? (
                              <button onClick={onOpenDefault} className="text-xs px-2 py-1 bg-red-50 border border-red-200 rounded text-red-700 hover:bg-red-100 flex items-center">
                                <TrendingDown size={10} className="mr-1" /> View Recovery Case
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400">View Only</span>
                            )
                          ) : l.dpd > 0 && l.dpd <= 30 ? (
                            canActOnReminder ? (
                              <button className="text-xs px-2 py-1 bg-blue-50 border border-blue-200 rounded text-blue-700 hover:bg-blue-100 flex items-center">
                                <Bell size={10} className="mr-1" /> Send Reminder
                              </button>
                            ) : (
                              <span className="text-xs text-slate-400">View Only</span>
                            )
                          ) : (
                            <span className="text-xs text-slate-400">—</span>
                          )}
                          <div className="text-[10px] text-slate-400 mt-0.5 leading-tight">
                            <div>Sent: 2 (Call)</div>
                            <div>Last: {formatDate(new Date(Date.now() - 3*24*60*60*1000).toISOString())}</div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Reminder Log */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="section-title flex items-center gap-2">
            <MessageSquare size={16} className="text-blue-500" />
            Reminder Log
          </h2>
          <button
            onClick={() => setShowReminderLog(!showReminderLog)}
            className="text-xs px-3 py-1.5 bg-blue-50 border border-blue-200 rounded text-blue-700 hover:bg-blue-100 flex items-center gap-1"
          >
            <Bell size={12} /> {showReminderLog ? 'Hide' : 'View All'} ({REMINDER_LOG.length})
          </button>
        </div>
        {showReminderLog && (
          <div className="card p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="table-header text-left">Account</th>
                  <th className="table-header text-left">Member</th>
                  <th className="table-header text-left">Type</th>
                  <th className="table-header text-left">Date</th>
                  <th className="table-header text-left">By</th>
                  <th className="table-header text-right">DPD</th>
                  <th className="table-header text-left">Status</th>
                  <th className="table-header text-left">Response</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {REMINDER_LOG.map(r => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="table-cell">
                      <button onClick={() => onOpenLoan(r.id)} className="font-semibold text-green-700 num hover:underline text-xs">{r.accountNumber}</button>
                    </td>
                    <td className="table-cell font-medium text-slate-800">{r.memberName}</td>
                    <td className="table-cell">
                      <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                        r.type === 'Call' ? 'bg-blue-50 text-blue-700' :
                        r.type === 'SMS' ? 'bg-slate-100 text-slate-600' :
                        'bg-amber-50 text-amber-700'
                      }`}>{r.type}</span>
                    </td>
                    <td className="table-cell text-slate-500 text-xs">{new Date(r.date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}</td>
                    <td className="table-cell text-slate-500 text-xs">{r.by}</td>
                    <td className="table-cell text-right">
                      <span className={`font-bold num text-xs ${r.dpd > 90 ? 'text-red-600' : r.dpd > 30 ? 'text-amber-600' : 'text-slate-600'}`}>{r.dpd}</span>
                    </td>
                    <td className="table-cell">
                      {r.status === 'connected' ? (
                        <span className="flex items-center gap-1 text-xs text-green-700"><CheckCircle2 size={11} /> Connected</span>
                      ) : r.status === 'delivered' ? (
                        <span className="flex items-center gap-1 text-xs text-blue-600"><CheckCircle2 size={11} /> Delivered</span>
                      ) : r.status === 'sent' ? (
                        <span className="flex items-center gap-1 text-xs text-slate-600"><Clock size={11} /> Sent</span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs text-red-600"><XIcon size={11} /> Not reached</span>
                      )}
                    </td>
                    <td className="table-cell text-slate-500 text-xs">{r.response}</td>
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
            { label: 'Monitored Loan Accounts', value: activeLoans.length },
            { label: 'Outstanding Principal', value: fmt(activeLoans.reduce((s, l) => s + l.outstandingPrincipal, 0)) },
            { label: 'Outstanding Interest', value: fmt(activeLoans.reduce((s, l) => s + l.accruedInterest, 0)) },
            { label: 'Loans with DPD > 0', value: activeLoans.filter(l => l.dpd > 0).length },
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
