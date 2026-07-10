import React, { useEffect, useState } from 'react';
import { ClipboardList, Plus, ChevronRight, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import { fetchPortalApplications, type PortalApplication } from '../../../../services/portalApi';

interface MP09_MyApplicationsProps {
  onNavigateToApplication: (id: string) => void;
  onNavigateToNew: () => void;
}

const MP09_MyApplications: React.FC<MP09_MyApplicationsProps> = ({ onNavigateToApplication, onNavigateToNew }) => {
  const [applications, setApplications] = useState<PortalApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchPortalApplications()
      .then(result => {
        if (!mounted) return;
        setApplications(result.items);
        setError(null);
      })
      .catch(err => {
        if (!mounted) return;
        setError(err instanceof AuthSessionError ? err.message : 'Applications could not be loaded.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <MP09ApplicationsView
      applications={applications}
      loading={loading}
      error={error}
      onNavigateToApplication={onNavigateToApplication}
      onNavigateToNew={onNavigateToNew}
    />
  );
};

export const MP09ApplicationsView: React.FC<MP09_MyApplicationsProps & {
  applications: PortalApplication[];
  loading: boolean;
  error: string | null;
}> = ({ applications, loading, error, onNavigateToApplication, onNavigateToNew }) => (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">My Applications</h2>
          <p className="text-sm text-slate-500 mt-1">Track your loan applications and their current status.</p>
        </div>
        <button
          onClick={onNavigateToNew}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm"
        >
          <Plus size={16} />
          New Loan Application
        </button>
      </div>

      {loading && (
        <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">
          Loading applications...
        </div>
      )}

      {error && (
        <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
          {error}
        </div>
      )}

      {!loading && !error && applications.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-100 p-6 text-sm text-slate-500">
          No loan applications have been started yet.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {applications.map(app => (
          <div
            key={app.loan_application_id}
            onClick={() => onNavigateToApplication(app.loan_application_id)}
            className="bg-white rounded-xl border border-slate-100 p-5 hover:border-green-200 hover:shadow-md transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${app.application_status === 'reference_generated' ? 'bg-green-100 text-green-600' : app.application_status === 'incomplete_returned' ? 'bg-amber-50 text-amber-600' : 'bg-slate-50 text-slate-600'}`}>
                  {app.application_status === 'reference_generated' ? <CheckCircle2 size={20} /> : <Clock size={20} />}
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 group-hover:text-green-700 transition-colors">{app.purpose_category ? app.purpose_category.replace(/_/g, ' ') : 'Loan Application'}</h3>
                  <div className="text-xs text-slate-500 mt-0.5">{app.display_reference}</div>
                </div>
              </div>
              <StatusBadge label={app.application_status === 'incomplete_returned' ? 'Action needed' : app.application_status.replace(/_/g, ' ')} size="sm" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-slate-500">Requested Amount</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{formatCurrency(app.required_loan_amount)}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">Applied On</p>
                <p className="text-sm font-medium text-slate-900 mt-0.5">{formatDate(app.application_date)}</p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">Current Stage</p>
                <p className="text-sm font-medium text-slate-700 mt-0.5 flex items-center gap-1.5">
                  <ClipboardList size={14} className="text-slate-400" />
                  {app.pending_with === 'Borrower' ? app.borrower_action : app.current_stage.replace(/_/g, ' ')}
                </p>
              </div>
              <ChevronRight size={18} className="text-slate-300 group-hover:text-green-500 transition-colors" />
            </div>
          </div>
        ))}
      </div>
    </div>
);

const formatCurrency = (value: string | null) => {
  if (!value) return 'Not entered';
  return `₹${Number(value).toLocaleString('en-IN')}`;
};

const formatDate = (value: string | null) => {
  if (!value) return 'Not submitted';
  return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));
};

export default MP09_MyApplications;
