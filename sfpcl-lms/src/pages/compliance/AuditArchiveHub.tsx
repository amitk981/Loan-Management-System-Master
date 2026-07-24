import React, { useCallback, useEffect, useState } from 'react';
import {
  Download,
  History,
  Search,
  ShieldCheck,
  X as XIcon,
} from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  downloadArchiveManifest,
  fetchArchiveRecords,
  type ArchiveRecordProjection,
} from '../../services/recoveryApi';

const TABS = ['Audit Log', 'Workflow Timeline', 'Archive Register', 'Evidence Packs'] as const;
type ArchiveTab = typeof TABS[number];

const date = (value: string) =>
  new Date(`${value.slice(0, 10)}T00:00:00Z`).toLocaleDateString('en-GB', { timeZone: 'UTC' });
const dateTime = (value: string) =>
  new Date(value).toLocaleString('en-GB', { timeZone: 'UTC' });

const AuditArchiveHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ArchiveTab>('Archive Register');
  const [records, setRecords] = useState<ArchiveRecordProjection[] | null>(null);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<ArchiveRecordProjection | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');
  const [success, setSuccess] = useState('');

  const load = useCallback(async (query = '') => {
    setLoadError(null);
    try {
      const result = await fetchArchiveRecords(query);
      setRecords(result.items);
    } catch (error) {
      setLoadError(error instanceof Error ? error : new Error('Archive records could not be loaded.'));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loadError) {
    const denied = loadError instanceof AuthSessionError
      && [401, 403].includes(loadError.status ?? 0);
    return (
      <div className="card p-8 text-center">
        <h2 className="font-semibold text-slate-900">
          {denied ? 'Access Denied' : 'Audit Archive Unavailable'}
        </h2>
        <p className="text-sm text-slate-500 mt-1">{loadError.message}</p>
      </div>
    );
  }

  if (!records) {
    return <div className="card p-8 text-center text-slate-500">Loading archive records…</div>;
  }

  const retentionDue = records.filter(record => record.destruction_eligible).length;
  const physicalCount = records.filter(record => Boolean(record.file_location_physical)).length;
  const digitalCount = records.filter(record => Boolean(record.file_location_digital)).length;

  const download = async (record: ArchiveRecordProjection) => {
    setDownloadingId(record.archive_record_id);
    setActionError('');
    setSuccess('');
    try {
      const manifest = await downloadArchiveManifest(record);
      const url = URL.createObjectURL(manifest.content);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = manifest.fileName;
      anchor.click();
      URL.revokeObjectURL(url);
      setSuccess('Archive manifest downloaded through the audited read endpoint.');
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Archive manifest could not be downloaded.');
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <History size={20} className="text-indigo-600" />
            Audit & Archive
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Review system events, evidence packs, closed files and retention status.
          </p>
        </div>
        <div className="bg-slate-100 px-4 py-2 rounded-lg flex items-center gap-2 border border-slate-200">
          <ShieldCheck size={16} className="text-indigo-600" />
          <span className="text-sm font-medium text-slate-700">
            Read-only access — archive records cannot be edited.
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          ['Archived records', records.length, 'text-slate-900'],
          ['Physical locations', physicalCount, 'text-indigo-600'],
          ['Digital locations', digitalCount, 'text-indigo-600'],
          ['Retention due', retentionDue, retentionDue ? 'text-red-600' : 'text-green-600'],
          ['Read-only records', records.length, 'text-green-600'],
        ].map(([label, value, colour]) => (
          <div key={String(label)} className="bg-white p-4 rounded-xl border border-slate-200">
            <div className="text-sm font-medium text-slate-500 mb-1">{label}</div>
            <div className={`text-2xl font-bold ${colour}`}>{value}</div>
          </div>
        ))}
      </div>

      {success && (
        <AlertBanner type="success" title="Archive manifest downloaded" message={success} />
      )}
      {actionError && (
        <AlertBanner type="error" title="Archive manifest unavailable" message={actionError} />
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
                    ? 'bg-indigo-50 text-indigo-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {activeTab !== 'Archive Register' ? (
          <div className="p-6 text-center text-sm text-slate-500">
            {activeTab} is available through its separately governed owner; this hub exposes only
            the retained archive manifest from the closure archive API.
          </div>
        ) : (
          <div className="flex flex-col">
            <form
              className="p-4 bg-slate-50/50 border-b border-slate-200 flex items-center justify-between"
              onSubmit={event => {
                event.preventDefault();
                void load(search);
              }}
            >
              <span className="text-sm text-slate-600 font-medium">
                Loan records must be retained for at least 8 years after closure.
              </span>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    aria-label="Search archive records"
                    value={search}
                    onChange={event => setSearch(event.target.value)}
                    placeholder="Loan, member or location"
                    className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64"
                  />
                </div>
                <button type="submit" className="btn-secondary text-sm">Search</button>
              </div>
            </form>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Archive ID</th>
                    <th className="table-header text-left">Loan account</th>
                    <th className="table-header text-left">Archive date</th>
                    <th className="table-header text-left">Retention start</th>
                    <th className="table-header text-left">Retention end</th>
                    <th className="table-header text-left">Archive location</th>
                    <th className="table-header text-left">Status</th>
                    <th className="table-header text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {records.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-8 text-center text-slate-500">
                        No archive records are available in your scope.
                      </td>
                    </tr>
                  ) : records.map(record => (
                    <tr key={record.archive_record_id} className="hover:bg-slate-50">
                      <td className="table-cell font-semibold text-slate-900 num">
                        {record.archive_record_id}
                      </td>
                      <td className="table-cell text-slate-700 num">{record.loan_account_id}</td>
                      <td className="table-cell text-slate-600">{dateTime(record.archived_at)}</td>
                      <td className="table-cell text-slate-600">{date(record.retention_start_date)}</td>
                      <td className="table-cell font-medium text-slate-800">
                        {date(record.retention_until_date)}
                      </td>
                      <td className="table-cell text-slate-600">
                        <div>{record.file_location_physical || 'No physical location'}</div>
                        {record.file_location_digital && (
                          <div className="text-xs text-slate-500 mt-1">{record.file_location_digital}</div>
                        )}
                      </td>
                      <td className="table-cell">
                        <StatusBadge
                          label={record.destruction_eligible ? 'Retention Due' : 'Archived'}
                          size="sm"
                        />
                      </td>
                      <td className="table-cell text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => setSelected(record)}
                            className="text-indigo-600 hover:text-indigo-800 font-medium text-xs px-2 py-1 rounded hover:bg-indigo-50"
                          >
                            View
                          </button>
                          <button
                            type="button"
                            onClick={() => void download(record)}
                            disabled={downloadingId === record.archive_record_id}
                            aria-label={`Download manifest ${record.archive_record_id}`}
                            className="text-slate-600 hover:text-slate-900 font-medium text-xs px-2 py-1 rounded hover:bg-slate-100 flex items-center gap-1 disabled:opacity-50"
                          >
                            <Download size={12} />
                            {downloadingId === record.archive_record_id ? 'Reading…' : 'Download manifest'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="p-4 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 text-center">
              Showing {records.length} archive records from canonical backend state.
            </div>
          </div>
        )}
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setSelected(null)} />
          <div className="w-[550px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col transform transition-transform duration-300">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Archive Manifest</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">
                  {selected.archive_record_id}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Close archive manifest"
              >
                <XIcon size={20} />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-x-4 gap-y-6 text-sm">
                {[
                  ['Loan closure', selected.loan_closure_id],
                  ['Loan account', selected.loan_account_id],
                  ['Physical location', selected.file_location_physical || 'Not recorded'],
                  ['Digital location', selected.file_location_digital || 'Not recorded'],
                  ['Retention start', date(selected.retention_start_date)],
                  ['Retention end', date(selected.retention_until_date)],
                  ['Archived by role', selected.archived_by_role_code.replace(/_/g, ' ')],
                  ['Archived at', dateTime(selected.archived_at)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div className="text-slate-500 mb-1">{label}</div>
                    <div className="font-medium text-slate-900 break-all">{value}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50">
              <div className="text-xs text-slate-500">
                This retained manifest is read-only. Access is recorded by the backend audit trail.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditArchiveHub;
