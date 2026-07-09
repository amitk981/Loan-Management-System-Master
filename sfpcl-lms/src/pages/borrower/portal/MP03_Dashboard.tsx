import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  CreditCard,
  FileCheck,
  IndianRupee,
  Leaf,
  MessageSquare,
  Shield,
} from 'lucide-react';
import StatusBadge from '../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../services/authSession';
import { fetchPortalDashboard, type PortalDashboard } from '../../../services/portalApi';
import { BorrowerTab } from './MemberPortalLayout';

interface DashboardProps {
  onNavigate: (tab: BorrowerTab) => void;
}

const MP03_Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<PortalDashboard | null>(null);
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Loading your member dashboard...');

  useEffect(() => {
    let mounted = true;
    fetchPortalDashboard()
      .then(data => {
        if (!mounted) return;
        setSummary(data);
        setStatus('success');
      })
      .catch((error: AuthSessionError) => {
        if (!mounted) return;
        setMessage(error.message || 'Member dashboard could not be loaded.');
        setStatus('error');
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (status !== 'success' || !summary) {
    return <PortalPanel title="Member dashboard unavailable" message={message} tone={status === 'loading' ? 'loading' : 'error'} />;
  }

  return <MP03DashboardView summary={summary} onNavigate={onNavigate} />;
};

export const MP03DashboardView: React.FC<{ summary: PortalDashboard; onNavigate: (tab: BorrowerTab) => void }> = ({ summary, onNavigate }) => {
  const { member, application_counts, loan_counts, pending_actions } = summary;
  const openDeficiencies = pending_actions.open_deficiencies ?? 0;
  const hasActions = Object.values(pending_actions).some(count => Number(count) > 0);

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl p-5 sm:p-6 text-white">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <p className="text-green-100 text-sm mb-1">Welcome back</p>
            <h2 className="text-2xl font-bold">{member.display_name}</h2>
            <p className="text-green-100 text-sm mt-1">
              Folio: {member.folio_number} · Shares: {member.share_summary?.number_of_shares ?? 0}
            </p>
            <div className="mt-2 inline-flex items-center gap-1.5 bg-white/20 text-white text-xs font-semibold px-2.5 py-1 rounded-full">
              <CheckCircle2 size={11} /> {formatLabel(member.active_member_status?.status || member.membership_status)}
            </div>
          </div>
          <div className="sm:text-right">
            <p className="text-green-100 text-xs mb-1">Active Loans</p>
            <p className="text-2xl font-bold">{loan_counts.active ?? 0}</p>
            <p className="text-green-100 text-xs mt-1">Own account summary</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Applications', value: String(application_counts.total ?? 0), icon: <ClipboardList size={16} />, color: 'text-green-600' },
          { label: 'Returned', value: String(application_counts.incomplete_returned ?? 0), icon: <AlertTriangle size={16} />, color: 'text-amber-600' },
          { label: 'Open deficiencies', value: String(openDeficiencies), icon: <AlertCircle size={16} />, color: openDeficiencies ? 'text-red-500' : 'text-green-600' },
          { label: 'Active loans', value: String(loan_counts.active ?? 0), icon: <CreditCard size={16} />, color: 'text-slate-600' },
        ].map(item => (
          <div key={item.label} className="bg-white rounded-xl p-4 border border-slate-100">
            <div className={`${item.color} mb-2`}>{item.icon}</div>
            <div className="text-lg font-bold text-slate-900">{item.value}</div>
            <div className="text-xs text-slate-500">{item.label}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-100 p-6">
        <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <AlertCircle size={16} className="text-amber-500" />
          Pending Actions
        </h3>
        {hasActions ? (
          <div className="space-y-3">
            {openDeficiencies > 0 && (
              <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
                <AlertTriangle size={15} className="text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-amber-800">Open deficiencies</p>
                  <p className="text-xs text-amber-700 mt-0.5">{openDeficiencies} returned application action pending with you.</p>
                </div>
                <button onClick={() => onNavigate('application')} className="flex-shrink-0 text-xs bg-amber-600 text-white px-3 py-1.5 rounded-lg hover:bg-amber-700 transition-colors">Respond</button>
              </div>
            )}
            {Object.entries(pending_actions).filter(([code, count]) => code !== 'open_deficiencies' && Number(count) > 0).map(([code, count]) => (
              <div key={code} className="flex items-start gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
                <AlertCircle size={15} className="text-slate-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-700">{formatLabel(code)}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{count} action pending.</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Your application is with SFPCL for review. No action is required from you right now.</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <InfoCard title="Member & Eligibility" icon={<Shield size={16} className="text-green-600" />} rows={[
          ['Member Type', formatLabel(member.member_type)],
          ['Folio Number', member.folio_number],
          ['Shares Held', `${member.share_summary?.number_of_shares ?? 0} shares (${member.share_summary?.holding_mode ?? 'not recorded'})`],
          ['KYC Status', formatLabel(member.kyc_status)],
          ['Default Status', formatLabel(member.default_status)],
        ]} />
        <InfoCard title="Application Summary" icon={<Leaf size={16} className="text-green-600" />} rows={[
          ['Draft', String(application_counts.draft ?? 0)],
          ['Submitted', String(application_counts.submitted ?? 0)],
          ['Returned incomplete', String(application_counts.incomplete_returned ?? 0)],
          ['Reference generated', String(application_counts.reference_generated ?? 0)],
          ['Notices', String(summary.notices.length)],
        ]} />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'New Loan Application', icon: <ClipboardList size={20} />, style: 'bg-green-600 hover:bg-green-700 text-white shadow-sm shadow-green-200', tab: 'newApplication' },
          { label: 'Repayment Schedule', icon: <IndianRupee size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'repayments' },
          { label: 'My Documents', icon: <FileCheck size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'documents' },
          { label: 'Raise Grievance', icon: <MessageSquare size={20} />, style: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200', tab: 'grievance' },
        ].map(action => (
          <button key={action.label} onClick={() => onNavigate(action.tab as BorrowerTab)} className={`flex flex-col items-center justify-center gap-2 rounded-xl p-4 text-sm font-medium transition-colors ${action.style}`}>
            {action.icon}
            <span className="text-center leading-tight">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

const InfoCard: React.FC<{ title: string; icon: React.ReactNode; rows: [string, string][] }> = ({ title, icon, rows }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-6">
    <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">{icon}{title}</h3>
    <div className="space-y-2.5">
      {rows.map(([label, value]) => (
        <div key={label} className="flex items-center justify-between text-sm border-b border-slate-50 pb-2 last:border-0 last:pb-0">
          <span className="text-slate-500">{label}</span>
          <span className="font-medium text-slate-900 text-right">{value}</span>
        </div>
      ))}
    </div>
  </div>
);

const PortalPanel: React.FC<{ title: string; message: string; tone: 'loading' | 'error' }> = ({ title, message, tone }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-6">
    <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
      {tone === 'loading' ? <StatusBadge label="loading" size="sm" /> : <AlertTriangle size={16} className="text-amber-600" />}
      {title}
    </h3>
    <p className="text-sm text-slate-500">{message}</p>
  </div>
);

const formatLabel = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());

export default MP03_Dashboard;
