import React, { useEffect, useState } from 'react';
import { AlertTriangle, Bell, MessageSquare } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import { fetchDpdPortfolio, fetchReminders, type DpdPortfolioProjection, type ReminderProjection } from '../../services/servicingApi';
import { formatMoney } from '../../utils/formatMoney';

interface Props { onOpenLoan: (id: string) => void; onOpenDefault?: () => void }
const bucketLabels = { current: 'Current', one_to_two_years: '1–2 years', two_to_three_years: '2–3 years', more_than_three_years: '>3 years' } as const;
const label = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());
const date = (value: string | null) => value ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';

const MonitoringDashboard: React.FC<Props> = ({ onOpenLoan }) => {
  const { currentUser } = useRole();
  const [portfolio, setPortfolio] = useState<DpdPortfolioProjection | null>(null);
  const [reminders, setReminders] = useState<ReminderProjection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReminders, setShowReminders] = useState(false);
  const [error, setError] = useState<{ title: string; message: string } | null>(null);

  useEffect(() => {
    let active = true; setLoading(true); setError(null); setPortfolio(null); setReminders([]);
    void fetchDpdPortfolio().then(async projection => {
      const reminderRows = await fetchReminders();
      if (active) { setPortfolio(projection); setReminders(reminderRows); }
    }).catch(reason => {
      if (!active) return;
      const unauthorized = reason instanceof AuthSessionError && [401, 403].includes(reason.status || 0);
      setError({ title: unauthorized ? 'Access Denied' : 'Monitoring Unavailable', message: reason instanceof Error ? reason.message : 'Monitoring records could not be loaded.' });
    }).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  if (!currentUser.permissions.includes('monitoring.dpd.read')) return <div className="p-6"><AlertBanner type="error" title="Access Denied" message="Monitoring DPD read permission is required." /></div>;
  if (loading) return <div className="p-6"><div className="card text-sm text-slate-500">Loading canonical DPD and reminder records…</div></div>;
  if (error || !portfolio) return <div className="p-6"><AlertBanner type="error" title={error?.title ?? 'Monitoring Unavailable'} message={error?.message ?? 'The complete monitoring projection is unavailable.'} /></div>;
  return <div className="p-6 space-y-6">
    <div><h1 className="text-xl font-bold text-slate-900">Monitoring Dashboard</h1><p className="text-sm text-slate-500 mt-0.5">Backend-owned DPD buckets and retained reminder evidence</p></div>
    <section><h2 className="section-title mb-3">DPD Bucket Analysis</h2><div className="grid grid-cols-2 sm:grid-cols-5 gap-3">{Object.entries(portfolio.sop_bucket_counts).map(([key, count]) => <div key={key} className={`${key === 'current' ? 'bg-green-50 border-green-200 text-green-900' : 'bg-red-50 border-red-200 text-red-900'} rounded-lg border p-4 text-center`}><div className="text-2xl font-bold num">{count}</div><div className="text-xs font-medium mt-0.5">{bucketLabels[key as keyof typeof bucketLabels]}</div></div>)}</div></section>
    <section><h2 className="section-title mb-3 flex items-center gap-2"><AlertTriangle size={16} className="text-amber-500" />Current DPD Rows ({portfolio.total_count})</h2><div className="card p-0 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Account', 'Member', 'Principal O/S', 'Overdue', 'DPD', 'SOP Bucket', 'Operational Bucket', 'As of'].map(value => <th key={value} className="table-header text-left">{value}</th>)}</tr></thead><tbody>{portfolio.rows.length === 0 && <tr><td colSpan={8} className="table-cell py-10 text-center text-slate-400">No current DPD snapshots are available in your scope.</td></tr>}{portfolio.rows.map(row => <tr key={row.dpd_status_id}><td className="table-cell"><button onClick={() => onOpenLoan(row.loan_account_id)} className="font-semibold text-green-700 hover:underline num">{row.loan_account_number}</button></td><td className="table-cell font-medium">{row.member_display_name}</td><td className="table-cell num">{formatMoney(row.principal_outstanding)}</td><td className="table-cell num">{formatMoney(row.total_overdue_amount)}</td><td className="table-cell num font-bold">{row.days_past_due}</td><td className="table-cell"><StatusBadge label={bucketLabels[row.sop_bucket as keyof typeof bucketLabels] ?? label(row.sop_bucket)} size="sm" /></td><td className="table-cell"><StatusBadge label={label(row.standard_bucket ?? 'not configured')} size="sm" /></td><td className="table-cell">{date(row.as_of_date)}</td></tr>)}</tbody></table></div></section>
    <section><div className="flex items-center justify-between mb-3"><h2 className="section-title flex items-center gap-2"><MessageSquare size={16} className="text-blue-500" />Reminder Log ({reminders.length})</h2><button onClick={() => setShowReminders(value => !value)} className="text-xs px-3 py-1.5 bg-blue-50 border border-blue-200 rounded text-blue-700"><Bell size={12} className="inline mr-1" />{showReminders ? 'Hide' : 'View All'}</button></div>{showReminders && <div className="card p-0 overflow-hidden"><table className="w-full text-sm"><thead><tr className="bg-slate-50 border-b border-slate-200">{['Account', 'Channel', 'Quarter End', 'Eligibility', 'Delivery', 'Follow-up', 'Outcome', 'Recorded By'].map(value => <th key={value} className="table-header text-left">{value}</th>)}</tr></thead><tbody>{reminders.length === 0 && <tr><td colSpan={8} className="table-cell py-10 text-center text-slate-400">No retained reminders are available for the current scoped DPD rows.</td></tr>}{reminders.map(row => <tr key={row.reminder_id}><td className="table-cell"><button onClick={() => onOpenLoan(row.loan_account_id)} className="font-semibold text-green-700 hover:underline"><Bell size={12} className="inline mr-1" />{portfolio.rows.find(item => item.loan_account_id === row.loan_account_id)?.loan_account_number ?? row.loan_account_id}</button></td><td className="table-cell"><StatusBadge label={label(row.channel)} size="sm" /></td><td className="table-cell">{date(row.quarter_end_date)}</td><td className="table-cell">{label(row.eligibility_decision.reason)}</td><td className="table-cell"><StatusBadge label={label(row.delivery_status)} size="sm" /></td><td className="table-cell">{date(row.next_follow_up_date)}</td><td className="table-cell">{row.call_outcome ?? row.status_reason ?? '—'}</td><td className="table-cell">{row.created_by.display_name}</td></tr>)}</tbody></table></div>}</section>
  </div>;
};

export default MonitoringDashboard;
