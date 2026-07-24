import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertOctagon,
  MessageSquareWarning,
  Search,
  X as XIcon,
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchGrievances,
  resolveGrievance,
  type GrievanceProjection,
} from '../../services/recoveryApi';

const TABS = ['Open', 'Overdue', 'Recovery-related', 'Escalated', 'Resolved', 'Closed'] as const;
type GrievanceTab = typeof TABS[number];

const display = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, letter => letter.toUpperCase());
const date = (value: string | null) => value
  ? new Date(`${value.slice(0, 10)}T00:00:00Z`).toLocaleDateString('en-GB', { timeZone: 'UTC' })
  : '—';
const errorMessage = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

const GrievancesHub: React.FC = () => {
  const [grievances, setGrievances] = useState<GrievanceProjection[] | null>(null);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [activeTab, setActiveTab] = useState<GrievanceTab>('Open');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<GrievanceProjection | null>(null);
  const [resolutionStatus, setResolutionStatus] = useState('');
  const [resolutionReason, setResolutionReason] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [actionError, setActionError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      const result = await fetchGrievances();
      setGrievances(result.items);
    } catch (error) {
      setLoadError(error instanceof Error ? error : new Error('Grievances could not be loaded.'));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (grievances ?? []).filter(grievance => {
      const matchesTab =
        (activeTab === 'Open' && ['open', 'investigating'].includes(grievance.status))
        || (activeTab === 'Overdue' && grievance.is_overdue)
        || (activeTab === 'Recovery-related' && grievance.grievance_category === 'recovery_conduct_issue')
        || (activeTab === 'Escalated' && grievance.status === 'escalated')
        || (activeTab === 'Resolved' && grievance.status === 'resolved')
        || (activeTab === 'Closed' && grievance.status === 'closed');
      const matchesSearch = !query || [
        grievance.grievance_reference,
        grievance.subject,
        grievance.description,
        grievance.loan_account_id ?? '',
        grievance.loan_application_id ?? '',
      ].some(value => value.toLowerCase().includes(query));
      return matchesTab && matchesSearch;
    });
  }, [activeTab, grievances, search]);

  if (loadError) {
    const denied = loadError instanceof AuthSessionError
      && [401, 403].includes(loadError.status ?? 0);
    return (
      <div className="card p-8 text-center">
        <h2 className="font-semibold text-slate-900">
          {denied ? 'Access Denied' : 'Grievance Register Unavailable'}
        </h2>
        <p className="text-sm text-slate-500 mt-1">{loadError.message}</p>
      </div>
    );
  }

  if (!grievances) {
    return <div className="card p-8 text-center text-slate-500">Loading grievances…</div>;
  }

  const overdueCount = grievances.filter(row => row.is_overdue).length;
  const recoveryCount = grievances.filter(
    row => row.grievance_category === 'recovery_conduct_issue',
  ).length;
  const resolvedCount = grievances.filter(row => ['resolved', 'closed'].includes(row.status)).length;
  const openCount = grievances.filter(
    row => ['open', 'investigating', 'escalated'].includes(row.status),
  ).length;
  const hasResolvableRow = grievances.some(row => row.available_actions?.includes('resolve'));

  const openResolution = (grievance: GrievanceProjection) => {
    setSelected(grievance);
    setResolutionStatus('');
    setResolutionReason('');
    setValidationErrors([]);
    setActionError('');
    setSuccess('');
  };

  const submitResolution = async () => {
    if (!selected) return;
    const errors: string[] = [];
    if (resolutionStatus !== 'resolved') errors.push('Resolution status is required.');
    if (!resolutionReason.trim()) errors.push('Resolution reason is required.');
    setValidationErrors(errors);
    if (errors.length) return;

    setSubmitting(true);
    setActionError('');
    setSuccess('');
    try {
      await resolveGrievance(selected.grievance_id, {
        status: 'resolved',
        reason: resolutionReason.trim(),
        idempotency_key: `grievance-resolution-${selected.grievance_id}-${Date.now()}`,
      });
      const refreshed = await fetchGrievances();
      setGrievances(refreshed.items);
      setSelected(null);
      setSuccess('Grievance resolved from canonical backend state.');
      setActiveTab('Resolved');
    } catch (error) {
      const fieldMessage = error instanceof AuthSessionError
        ? Object.values(error.fieldErrors ?? {})[0]
        : undefined;
      setActionError(fieldMessage || errorMessage(error, 'Grievance resolution could not be saved.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <MessageSquareWarning size={20} className="text-amber-600" />
            Grievances
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Track borrower complaints, TAT, assignment, resolution and closure.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          ['Open Grievances', openCount, 'text-slate-900'],
          ['Overdue TAT', overdueCount, 'text-red-600'],
          ['Recovery-related', recoveryCount, 'text-amber-600'],
          ['Resolved', resolvedCount, 'text-green-600'],
        ].map(([label, value, colour]) => (
          <div key={String(label)} className="bg-white p-4 rounded-xl border border-slate-200">
            <div className="text-sm font-medium text-slate-500 mb-1">{label}</div>
            <div className={`text-2xl font-bold ${colour}`}>{value}</div>
          </div>
        ))}
      </div>

      {(overdueCount > 0 || recoveryCount > 0) && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg flex items-start gap-3">
          <AlertOctagon size={18} className="text-red-600 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-900">Attention Required</p>
            {overdueCount > 0 && (
              <p className="text-sm text-red-700 mt-0.5">
                {overdueCount} {overdueCount === 1 ? 'grievance is' : 'grievances are'} overdue.
              </p>
            )}
            {recoveryCount > 0 && (
              <p className="text-sm text-red-700 mt-0.5">
                Recovery-related complaints require CS review.
              </p>
            )}
          </div>
        </div>
      )}

      {success && <AlertBanner type="success" title="Grievance updated" message={success} />}

      {!hasResolvableRow && grievances.length > 0 && (
        <AlertBanner
          type="warning"
          title="Resolution unavailable"
          message="No resolution action is available for your role or this status."
        />
      )}

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden flex flex-col">
        <div className="border-b border-slate-200">
          <div className="flex gap-2 p-2 overflow-x-auto">
            {TABS.map(tab => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-colors ${
                  activeTab === tab
                    ? 'bg-amber-50 text-amber-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              aria-label="Search grievances"
              value={search}
              onChange={event => setSearch(event.target.value)}
              placeholder="Search grievances..."
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 w-64"
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="table-header text-left">Grievance ID</th>
                <th className="table-header text-left">Subject / Source</th>
                <th className="table-header text-left">Category / Mode</th>
                <th className="table-header text-left">Received</th>
                <th className="table-header text-left">Resolution due</th>
                <th className="table-header text-left">Status</th>
                <th className="table-header text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-500">
                    No grievances found in this view.
                  </td>
                </tr>
              ) : filtered.map(grievance => (
                <tr key={grievance.grievance_id} className="hover:bg-slate-50">
                  <td className="table-cell font-semibold text-slate-900 num">
                    {grievance.grievance_reference}
                  </td>
                  <td className="table-cell">
                    <div className="font-medium text-slate-900">{grievance.subject}</div>
                    <div className="text-xs text-slate-500 num">
                      {grievance.loan_account_id || grievance.loan_application_id || grievance.member_id}
                    </div>
                    {grievance.resolution_summary && (
                      <div className="text-xs text-green-700 mt-1">{grievance.resolution_summary}</div>
                    )}
                  </td>
                  <td className="table-cell">
                    <div className="font-medium text-slate-800">
                      {display(grievance.grievance_category)}
                    </div>
                    <div className="text-xs text-slate-500">{display(grievance.received_channel)}</div>
                  </td>
                  <td className="table-cell text-slate-600">{date(grievance.received_date)}</td>
                  <td className={`table-cell font-medium ${
                    grievance.is_overdue ? 'text-red-600' : 'text-slate-700'
                  }`}>
                    {date(grievance.resolution_due_date)}
                    {grievance.is_overdue && (
                      <div className="text-xs">{grievance.days_overdue}d overdue</div>
                    )}
                  </td>
                  <td className="table-cell">
                    <StatusBadge label={display(grievance.status)} size="sm" />
                  </td>
                  <td className="table-cell text-right">
                    {grievance.available_actions?.includes('resolve') ? (
                      <button
                        type="button"
                        onClick={() => openResolution(grievance)}
                        className="text-green-700 hover:text-green-900 font-medium text-xs px-2 py-1 rounded hover:bg-green-50 transition-colors"
                        aria-label={`Resolve ${grievance.grievance_reference}`}
                      >
                        Resolve
                      </button>
                    ) : (
                      <span className="text-xs text-slate-400">Read only</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 text-center">
          Showing {filtered.length} of {grievances.length} grievances in this view.
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setSelected(null)} />
          <div className="w-[500px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col transform transition-transform duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Record Resolution</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">
                  {selected.grievance_reference}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Close resolution"
              >
                <XIcon size={20} />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-slate-500 mb-1">Subject</div>
                  <div className="font-medium text-slate-900">{selected.subject}</div>
                </div>
                <div>
                  <div className="text-slate-500 mb-1">Category</div>
                  <div className="font-medium text-slate-900">
                    {display(selected.grievance_category)}
                  </div>
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-sm text-slate-800">
                {selected.description}
              </div>
              <label className="block text-sm font-medium text-slate-700">
                Resolution status
                <select
                  value={resolutionStatus}
                  onChange={event => setResolutionStatus(event.target.value)}
                  className="mt-1 w-full border border-slate-200 rounded-lg px-3 py-2 bg-white"
                >
                  <option value="">Select status</option>
                  <option value="resolved">Resolved</option>
                </select>
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Resolution reason
                <textarea
                  value={resolutionReason}
                  onChange={event => setResolutionReason(event.target.value)}
                  rows={5}
                  className="mt-1 w-full border border-slate-200 rounded-lg px-3 py-2"
                />
              </label>
              {validationErrors.map(message => (
                <p key={message} className="text-sm text-red-600">{message}</p>
              ))}
              {actionError && <p className="text-sm text-red-600">{actionError}</p>}
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-2">
              <button type="button" onClick={() => setSelected(null)} className="btn-secondary">
                Cancel
              </button>
              <button
                type="button"
                onClick={() => void submitResolution()}
                disabled={submitting}
                className="btn-primary disabled:opacity-50"
              >
                {submitting ? 'Saving…' : 'Submit Resolution'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GrievancesHub;
