import React, { useCallback, useEffect, useState } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
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
import {
  fetchAuditLogs,
  createAuditObservation,
  fetchAuditObservation,
  fetchAuditObservations,
  type AuditLogProjection,
  type AuditLogQuery,
  type AuditObservationProjection,
} from '../../services/auditExplorerApi';
import { useRole } from '../../contexts/RoleContext';
import AuditorEpic011View from './AuditorEpic011View';

const TABS = [
  'Audit Log',
  'Workflow Timeline',
  'Auditor Observations',
  'Auditor Records',
  'Archive Register',
  'Evidence Packs',
] as const;
type ArchiveTab = typeof TABS[number];

const date = (value: string) =>
  new Date(`${value.slice(0, 10)}T00:00:00Z`).toLocaleDateString('en-GB', { timeZone: 'UTC' });
const dateTime = (value: string) =>
  new Date(value).toLocaleString('en-GB', { timeZone: 'UTC' });
const restrictedAuditKey = /pan|aadhaar|bank|account|cheque|bo_|password|secret|token|request_body|storage|document/i;
const sensitiveAuditValue = /(?:[A-Z]{5}\d{4}[A-Z])|(?:\d{8,})|(?:bearer\s+\S+)/i;
const safeChangeRows = (mapping: Record<string, unknown>) => Object.entries(mapping)
  .filter(([key, value]) => (
    !restrictedAuditKey.test(key)
    && (value === null || ['string', 'number', 'boolean'].includes(typeof value))
  ))
  .map(([key, value]) => [
    key.replace(/_/g, ' '),
    typeof value === 'string' && sensitiveAuditValue.test(value) ? '[REDACTED]' : String(value),
  ] as const);

const AuditArchiveHub: React.FC = () => {
  const { currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<ArchiveTab>('Audit Log');
  const [records, setRecords] = useState<ArchiveRecordProjection[] | null>(null);
  const [loadError, setLoadError] = useState<Error | null>(null);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<ArchiveRecordProjection | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState('');
  const [success, setSuccess] = useState('');
  const [auditRows, setAuditRows] = useState<AuditLogProjection[] | null>(null);
  const [auditPagination, setAuditPagination] = useState({
    page: 1,
    page_size: 20,
    total_count: 0,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  });
  const [auditError, setAuditError] = useState<Error | null>(null);
  const [auditQuery, setAuditQuery] = useState<AuditLogQuery>({ page: 1, pageSize: 20 });
  const [draftFilters, setDraftFilters] = useState<AuditLogQuery>({});
  const [selectedAudit, setSelectedAudit] = useState<AuditLogProjection | null>(null);
  const [sampledAuditId, setSampledAuditId] = useState<string | null>(null);
  const [observations, setObservations] = useState<AuditObservationProjection[] | null>(null);
  const [observationError, setObservationError] = useState<Error | null>(null);
  const [observationDetailError, setObservationDetailError] = useState('');
  const [observationText, setObservationText] = useState('');
  const [observationActionError, setObservationActionError] = useState('');
  const [observationSuccess, setObservationSuccess] = useState('');
  const [savingObservation, setSavingObservation] = useState(false);
  const [selectedObservation, setSelectedObservation] = useState<AuditObservationProjection | null>(null);
  const [loadingObservationId, setLoadingObservationId] = useState<string | null>(null);
  const canReadObservations = currentUser.roleCodes.includes('internal_auditor')
    && currentUser.permissions.includes('audit.observation.read');
  const canCreateObservations = canReadObservations
    && currentUser.permissions.includes('audit.observation.create');

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

  const loadAudit = useCallback(async (query: AuditLogQuery) => {
    setAuditRows(null);
    setAuditError(null);
    try {
      const result = await fetchAuditLogs(query);
      setAuditRows(result.items);
      setAuditPagination(result.pagination);
    } catch (error) {
      setAuditError(error instanceof Error ? error : new Error('Audit events could not be loaded.'));
    }
  }, []);

  useEffect(() => {
    void loadAudit(auditQuery);
  }, [auditQuery, loadAudit]);

  const loadObservations = useCallback(async () => {
    if (!canReadObservations) {
      setObservations([]);
      return;
    }
    setObservationError(null);
    try {
      const result = await fetchAuditObservations({ page: 1, pageSize: 20 });
      setObservations(result.items);
    } catch (error) {
      setObservations(null);
      setObservationError(error instanceof Error
        ? error
        : new Error('Auditor observations could not be loaded.'));
    }
  }, [canReadObservations]);

  useEffect(() => {
    void loadObservations();
  }, [loadObservations]);

  const recordObservation = async () => {
    if (!selectedAudit || !canCreateObservations) return;
    setSavingObservation(true);
    setObservationActionError('');
    setObservationSuccess('');
    try {
      await createAuditObservation({
        observation: observationText,
        sourceReferences: [{
          source_type: 'audit_log',
          source_id: selectedAudit.audit_log_id,
        }],
      });
      setObservationText('');
      setObservationSuccess('Observation recorded as immutable.');
      await loadObservations();
    } catch (error) {
      const message = error instanceof AuthSessionError
        ? error.fieldErrors?.observation ?? error.message
        : error instanceof Error
          ? error.message
          : 'Observation could not be recorded.';
      setObservationActionError(message);
    } finally {
      setSavingObservation(false);
    }
  };

  const revisitObservation = async (observationId: string) => {
    setLoadingObservationId(observationId);
    setObservationDetailError('');
    try {
      setSelectedObservation(await fetchAuditObservation(observationId));
    } catch (error) {
      setObservationDetailError(error instanceof Error
        ? error.message
        : 'Observation detail could not be loaded.');
    } finally {
      setLoadingObservationId(null);
    }
  };

  if (activeTab === 'Archive Register' && loadError) {
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

  if (activeTab === 'Archive Register' && !records) {
    return <div className="card p-8 text-center text-slate-500">Loading archive records…</div>;
  }

  const archiveRows = records ?? [];
  const retentionDue = archiveRows.filter(record => record.destruction_eligible).length;
  const physicalCount = archiveRows.filter(record => Boolean(record.file_location_physical)).length;
  const digitalCount = archiveRows.filter(record => Boolean(record.file_location_digital)).length;

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
          ['Audit events', auditPagination.total_count, 'text-slate-900'],
          ['Archived records', archiveRows.length, 'text-slate-900'],
          ['Physical locations', physicalCount, 'text-indigo-600'],
          ['Digital locations', digitalCount, 'text-indigo-600'],
          ['Retention due', retentionDue, retentionDue ? 'text-red-600' : 'text-green-600'],
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

        {activeTab === 'Audit Log' ? (
          <div className="flex flex-col">
            <form
              className="p-4 bg-slate-50/50 border-b border-slate-200 flex flex-col md:flex-row gap-3 items-end flex-wrap"
              onSubmit={event => {
                event.preventDefault();
                setAuditQuery({
                  ...draftFilters,
                  page: 1,
                  pageSize: 20,
                });
              }}
            >
              {[
                ['Entity type', 'entityType'],
                ['Action', 'action'],
                ['Actor user ID', 'actorUserId'],
              ].map(([label, field]) => (
                <label key={field} className="text-sm text-slate-600 flex-1">
                  <span className="block mb-1">{label}</span>
                  <input
                    aria-label={label}
                    className="field-input text-sm"
                    value={String(draftFilters[field as keyof AuditLogQuery] ?? '')}
                    onChange={event => setDraftFilters(current => ({
                      ...current,
                      [field]: event.target.value,
                    }))}
                  />
                </label>
              ))}
              <label className="text-sm text-slate-600 flex-1">
                <span className="block mb-1">From date</span>
                <input
                  aria-label="From date"
                  type="date"
                  className="field-input text-sm"
                  value={draftFilters.createdFrom ?? ''}
                  onChange={event => setDraftFilters(current => ({
                    ...current,
                    createdFrom: event.target.value,
                  }))}
                />
              </label>
              <label className="text-sm text-slate-600 flex-1">
                <span className="block mb-1">To date</span>
                <input
                  aria-label="To date"
                  type="date"
                  className="field-input text-sm"
                  value={draftFilters.createdTo ?? ''}
                  onChange={event => setDraftFilters(current => ({
                    ...current,
                    createdTo: event.target.value,
                  }))}
                />
              </label>
              <button type="submit" className="btn-secondary text-sm">
                <Search size={14} /> Apply audit filters
              </button>
            </form>

            {auditError ? (
              <div className="p-8 text-center">
                <h2 className="font-semibold text-slate-900">
                  {auditError instanceof AuthSessionError
                    && [401, 403].includes(auditError.status ?? 0)
                    ? 'Audit access is not authorised.'
                    : 'Audit events could not be loaded.'}
                </h2>
                <p className="text-sm text-slate-500 mt-1">{auditError.message}</p>
                <button
                  type="button"
                  className="btn-secondary mt-4"
                  onClick={() => void loadAudit(auditQuery)}
                >
                  Retry
                </button>
              </div>
            ) : !auditRows ? (
              <div className="p-8 text-center text-slate-500">Loading audit events…</div>
            ) : auditRows.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                No audit events are available for these filters and your scope.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="table-header text-left">Timestamp</th>
                      <th className="table-header text-left">Actor</th>
                      <th className="table-header text-left">Module</th>
                      <th className="table-header text-left">Action</th>
                      <th className="table-header text-left">Record</th>
                      <th className="table-header text-left">Outcome</th>
                      <th className="table-header text-right">Read-only detail</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {auditRows.map(row => (
                      <tr key={row.audit_log_id} className="hover:bg-slate-50">
                        <td className="table-cell text-slate-600">{dateTime(row.created_at)}</td>
                        <td className="table-cell text-slate-700">
                          {row.actor?.full_name ?? row.actor_type}
                        </td>
                        <td className="table-cell text-slate-600">{row.module}</td>
                        <td className="table-cell font-medium text-slate-900">{row.action}</td>
                        <td className="table-cell text-slate-600">
                          <div>{row.entity_type}</div>
                          <div className="text-xs font-mono mt-1">{row.entity_id ?? 'No record ID'}</div>
                        </td>
                        <td className="table-cell">
                          <StatusBadge label={String(row.outcome ?? 'recorded')} size="sm" />
                        </td>
                        <td className="table-cell text-right">
                          <button
                            type="button"
                            className="btn-secondary text-xs"
                            onClick={() => {
                              setSelectedAudit(row);
                              setSampledAuditId(null);
                              setObservationActionError('');
                              setObservationSuccess('');
                            }}
                            aria-label={`View audit event ${row.audit_log_id}`}
                          >
                            <Eye size={14} /> View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Page {auditPagination.page} of {auditPagination.total_pages}
                {' · '}{auditPagination.total_count} backend-scoped events
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn-secondary text-xs"
                  aria-label="Previous audit page"
                  disabled={!auditPagination.has_previous}
                  onClick={() => setAuditQuery(current => ({
                    ...current,
                    page: Math.max(1, auditPagination.page - 1),
                  }))}
                >
                  <ChevronLeft size={14} /> Previous
                </button>
                <button
                  type="button"
                  className="btn-secondary text-xs"
                  aria-label="Next audit page"
                  disabled={!auditPagination.has_next}
                  onClick={() => setAuditQuery(current => ({
                    ...current,
                    page: auditPagination.page + 1,
                  }))}
                >
                  Next <ChevronRight size={14} />
                </button>
              </div>
            </div>
          </div>
        ) : activeTab === 'Auditor Observations' ? (
          !canReadObservations ? (
            <div className="p-8 text-center">
              <h2 className="font-semibold text-slate-900">
                Observation access is not authorised.
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                Internal Auditor role, active audit scope, and observation read permission are required.
              </p>
            </div>
          ) : observationError ? (
            <div className="p-8 text-center">
              <h2 className="font-semibold text-slate-900">
                Auditor observations could not be loaded.
              </h2>
              <p className="text-sm text-slate-500 mt-1">{observationError.message}</p>
              <button
                type="button"
                className="btn-secondary mt-4"
                onClick={() => void loadObservations()}
              >
                Retry
              </button>
            </div>
          ) : !observations ? (
            <div className="p-8 text-center text-slate-500">
              Loading auditor observations…
            </div>
          ) : observations.length === 0 ? (
            <div className="p-8 text-center text-slate-500">
              No immutable auditor observations are available in your scope.
            </div>
          ) : (
            <div>
              {observationDetailError && (
                <div className="p-4 border-b border-slate-200">
                  <AlertBanner
                    type="error"
                    title="Observation detail unavailable"
                    message={observationDetailError}
                  />
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Recorded at</th>
                    <th className="table-header text-left">Creator</th>
                    <th className="table-header text-left">Observation</th>
                    <th className="table-header text-left">Sample references</th>
                    <th className="table-header text-right">Immutable detail</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {observations.map(observation => (
                    <tr key={observation.audit_observation_id} className="hover:bg-slate-50">
                      <td className="table-cell text-slate-600">
                        {dateTime(observation.created_at)}
                      </td>
                      <td className="table-cell text-slate-700">
                        <div>{observation.creator.full_name}</div>
                        <div className="text-xs text-slate-500 mt-1">
                          {observation.creator.role_code.replace(/_/g, ' ')}
                        </div>
                      </td>
                      <td className="table-cell text-slate-900">{observation.observation}</td>
                      <td className="table-cell text-slate-600">
                        {observation.source_references.length}
                      </td>
                      <td className="table-cell text-right">
                        <button
                          type="button"
                          className="btn-secondary text-xs"
                          aria-label={`View observation ${observation.audit_observation_id}`}
                          disabled={loadingObservationId === observation.audit_observation_id}
                          onClick={() => void revisitObservation(observation.audit_observation_id)}
                        >
                          <Eye size={14} />
                          {loadingObservationId === observation.audit_observation_id
                            ? 'Loading…'
                            : 'View'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
                </table>
              </div>
            </div>
          )
        ) : activeTab !== 'Archive Register' ? (
          activeTab === 'Auditor Records' && currentUser.roleCodes.includes('internal_auditor') ? (
            <div className="p-6">
              <AuditorEpic011View />
            </div>
          ) : (
            <div className="p-6 text-center text-sm text-slate-500">
              {activeTab} is available through its separately governed owner.
            </div>
          )
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
                  {archiveRows.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-8 text-center text-slate-500">
                        No archive records are available in your scope.
                      </td>
                    </tr>
                  ) : archiveRows.map(record => (
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
              Showing {archiveRows.length} archive records from canonical backend state.
            </div>
          </div>
        )}
      </div>

      {selectedAudit && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm"
            onClick={() => setSelectedAudit(null)}
          />
          <div className="w-[550px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Audit Event Detail</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">
                  {selectedAudit.audit_log_id}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedAudit(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Close audit event detail"
              >
                <XIcon size={20} />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-x-4 gap-y-6 text-sm">
                {[
                  ['Timestamp', dateTime(selectedAudit.created_at)],
                  ['Actor', selectedAudit.actor?.full_name ?? selectedAudit.actor_type],
                  ['Actor role', selectedAudit.actor_role_codes.join(', ') || 'Not recorded'],
                  ['Actor team', selectedAudit.actor_team_codes.join(', ') || 'Not recorded'],
                  ['Module', selectedAudit.module],
                  ['Action', selectedAudit.action],
                  ['Entity type', selectedAudit.entity_type],
                  ['Entity ID', selectedAudit.entity_id ?? 'Not recorded'],
                  ['Outcome', String(selectedAudit.outcome ?? 'recorded')],
                  ['Request ID', String(selectedAudit.request_id ?? 'Not recorded')],
                  ['IP address', selectedAudit.ip_address ?? 'Not recorded'],
                  ['Device', selectedAudit.device ?? 'Not recorded'],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div className="text-slate-500 mb-1">{label}</div>
                    <div className="font-medium text-slate-900 break-all">{value}</div>
                  </div>
                ))}
              </div>
              <div>
                <div className="text-sm text-slate-500 mb-1">Reason</div>
                <div className="text-sm text-slate-900">
                  {String(selectedAudit.reason ?? 'No reason recorded')}
                </div>
              </div>
              {[
                ['Before value', safeChangeRows(selectedAudit.old_value)],
                ['After value', safeChangeRows(selectedAudit.new_value)],
              ].map(([label, rows]) => (
                <div key={String(label)}>
                  <div className="text-sm text-slate-500 mb-2">{label}</div>
                  {(rows as ReturnType<typeof safeChangeRows>).length === 0 ? (
                    <div className="text-sm text-slate-500">
                      No safe change fields are available.
                    </div>
                  ) : (rows as ReturnType<typeof safeChangeRows>).map(([field, value]) => (
                    <div
                      key={field}
                      className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs mb-2"
                    >
                      <span className="font-medium text-slate-700 capitalize">{field}: </span>
                      <span className="text-slate-900">{value}</span>
                    </div>
                  ))}
                </div>
              ))}
              <div className="border-t border-slate-100 pt-5">
                <h3 className="text-sm font-semibold text-slate-900">
                  Separate auditor observation
                </h3>
                <p className="text-xs text-slate-500 mt-1 mb-3">
                  An observation creates a new immutable record and does not change this audit event.
                </p>
                {!canCreateObservations ? (
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-600">
                    Observation creation is not authorised for this role or scope.
                  </div>
                ) : sampledAuditId !== selectedAudit.audit_log_id ? (
                  <button
                    type="button"
                    className="btn-secondary text-sm"
                    onClick={() => setSampledAuditId(selectedAudit.audit_log_id)}
                  >
                    Sample this event
                  </button>
                ) : (
                  <form
                    className="space-y-3"
                    onSubmit={event => {
                      event.preventDefault();
                      void recordObservation();
                    }}
                  >
                    <label className="text-sm text-slate-600 block">
                      <span className="block mb-1">Auditor observation</span>
                      <textarea
                        aria-label="Auditor observation"
                        className="field-input text-sm min-h-24"
                        maxLength={2000}
                        required
                        value={observationText}
                        onChange={event => setObservationText(event.target.value)}
                      />
                    </label>
                    {observationActionError && (
                      <AlertBanner
                        type="error"
                        title="Observation not recorded"
                        message={observationActionError}
                      />
                    )}
                    {observationSuccess && (
                      <AlertBanner
                        type="success"
                        title="Observation recorded"
                        message={observationSuccess}
                      />
                    )}
                    <button
                      type="submit"
                      className="btn-primary text-sm"
                      disabled={savingObservation || !observationText.trim()}
                    >
                      {savingObservation ? 'Recording…' : 'Record observation'}
                    </button>
                  </form>
                )}
              </div>
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50">
              <div className="text-xs text-slate-500">
                This audit event is immutable and read-only.
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedObservation && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm"
            onClick={() => setSelectedObservation(null)}
          />
          <div className="w-[550px] bg-white border-l border-slate-200 h-full shadow-2xl relative flex flex-col">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Observation Detail</h2>
                <div className="text-xs text-slate-500 font-mono mt-0.5">
                  {selectedObservation.audit_observation_id}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedObservation(null)}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                aria-label="Close observation detail"
              >
                <XIcon size={20} />
              </button>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-x-4 gap-y-6 text-sm">
                {[
                  ['Creator', selectedObservation.creator.full_name],
                  ['Creator role', selectedObservation.creator.role_code.replace(/_/g, ' ')],
                  ['Audit scope', selectedObservation.audit_scope.replace(/_/g, ' ')],
                  ['Recorded at', dateTime(selectedObservation.created_at)],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div className="text-slate-500 mb-1">{label}</div>
                    <div className="font-medium text-slate-900 break-all">{value}</div>
                  </div>
                ))}
              </div>
              <div>
                <div className="text-sm text-slate-500 mb-1">Observation</div>
                <div className="text-sm text-slate-900">{selectedObservation.observation}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500 mb-2">Sample references</div>
                {selectedObservation.source_references.map(reference => (
                  <div
                    key={`${reference.source_type}-${reference.source_id}`}
                    className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs mb-2"
                  >
                    <div className="font-medium text-slate-900">
                      {reference.source_type.replace(/_/g, ' ')}
                    </div>
                    <div className="font-mono text-slate-600 mt-1">{reference.source_id}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="p-4 border-t border-slate-100 bg-slate-50">
              <div className="text-xs text-slate-500">
                Creator, scope, source references, text and time cannot be edited.
              </div>
            </div>
          </div>
        </div>
      )}

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
