import React, { useEffect, useMemo, useRef, useState } from 'react';
import { BarChart2, ChevronDown, ChevronLeft, ChevronRight, ChevronUp, Download, Filter } from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError, type Pagination } from '../../services/authSession';
import {
  downloadReportExport,
  fetchReport,
  fetchReportExport,
  reportQueryToExportFilters,
  requestReportExport,
  type ReportExportJob,
  type ReportCode,
  type ReportQuery,
  type ReportRow,
} from '../../services/reportApi';

type Column = {
  key: string;
  label: string;
  format?: 'money' | 'date' | 'dateTime' | 'status' | 'boolean' | 'list';
  align?: 'left' | 'right';
  sortable?: boolean;
};

type FilterField = {
  key: 'fromDate' | 'toDate' | 'status' | 'stage' | 'asOfDate' | 'sopBucket' | 'financialYear';
  label: string;
  type?: 'date';
  placeholder?: string;
};

type ReportDefinition = {
  code: ReportCode;
  label: string;
  description: string;
  requiredPermissions: string[];
  defaultOrdering: string;
  filters: FilterField[];
  columns: Column[];
};

const REPORTS: ReportDefinition[] = [
  {
    code: 'loan-portfolio',
    label: 'Loan Portfolio',
    description: 'Loan account balances reconciled to the scoped loan register.',
    requiredPermissions: ['reports.portfolio.read', 'finance.loan_account.read'],
    defaultOrdering: '-created_at',
    filters: [
      { key: 'asOfDate', label: 'As of date', type: 'date' },
      { key: 'status', label: 'Account status', placeholder: 'e.g. active' },
    ],
    columns: [
      { key: 'loan_account_number', label: 'Loan account', sortable: true },
      { key: 'borrower_name', label: 'Borrower', sortable: true },
      { key: 'loan_account_status', label: 'Status', format: 'status', sortable: true },
      { key: 'sanctioned_amount', label: 'Sanctioned', format: 'money', align: 'right', sortable: true },
      { key: 'principal_outstanding', label: 'Principal outstanding', format: 'money', align: 'right', sortable: true },
      { key: 'interest_outstanding', label: 'Interest outstanding', format: 'money', align: 'right', sortable: true },
      { key: 'total_outstanding', label: 'Total outstanding', format: 'money', align: 'right', sortable: true },
      { key: 'repayment_date', label: 'Repayment date', format: 'date', sortable: true },
    ],
  },
  {
    code: 'application-pipeline',
    label: 'Application Pipeline',
    description: 'Loan Request Register applications within the backend-owned actor scope.',
    requiredPermissions: ['reports.application_pipeline.read'],
    defaultOrdering: '-date_received',
    filters: [
      { key: 'fromDate', label: 'From date', type: 'date' },
      { key: 'toDate', label: 'To date', type: 'date' },
      { key: 'status', label: 'Register status', placeholder: 'e.g. reference_generated' },
      { key: 'stage', label: 'Application stage', placeholder: 'e.g. credit_assessment' },
    ],
    columns: [
      { key: 'application_reference_number', label: 'Application', sortable: true },
      { key: 'borrower_name', label: 'Borrower', sortable: true },
      { key: 'date_received', label: 'Received', format: 'date', sortable: true },
      { key: 'register_status', label: 'Register status', format: 'status' },
      { key: 'requested_amount', label: 'Requested amount', format: 'money', align: 'right', sortable: true },
      { key: 'current_stage', label: 'Current stage', format: 'status', sortable: true },
      { key: 'current_owner_role', label: 'Current owner', format: 'status' },
    ],
  },
  {
    code: 'documentation-readiness',
    label: 'Documentation Readiness',
    description: 'Required checklist progress and current document blockers.',
    requiredPermissions: ['documents.checklist.read'],
    defaultOrdering: '-updated_at',
    filters: [
      { key: 'status', label: 'Checklist status', placeholder: 'e.g. pending' },
    ],
    columns: [
      { key: 'application_reference_number', label: 'Application', sortable: true },
      { key: 'borrower_name', label: 'Borrower', sortable: true },
      { key: 'checklist_status', label: 'Checklist status', format: 'status', sortable: true },
      { key: 'required_item_count', label: 'Required', align: 'right' },
      { key: 'completed_item_count', label: 'Complete', align: 'right' },
      { key: 'pending_item_count', label: 'Pending', align: 'right' },
      { key: 'blocker_codes', label: 'Current blockers', format: 'list' },
      { key: 'updated_at', label: 'Updated', format: 'dateTime', sortable: true },
    ],
  },
  {
    code: 'disbursement-pending',
    label: 'Disbursement Pending',
    description: 'Initiated disbursements awaiting authorisation or bank transfer.',
    requiredPermissions: ['finance.disbursement.readiness', 'finance.loan_account.read'],
    defaultOrdering: '-initiated_at',
    filters: [],
    columns: [
      { key: 'loan_account_number', label: 'Loan account', sortable: true },
      { key: 'borrower_name', label: 'Borrower', sortable: true },
      { key: 'disbursement_amount', label: 'Disbursement', format: 'money', align: 'right', sortable: true },
      { key: 'initiation_status', label: 'Initiation', format: 'status' },
      { key: 'authorisation_status', label: 'Authorisation', format: 'status', sortable: true },
      { key: 'bank_transfer_status', label: 'Bank transfer', format: 'status', sortable: true },
      { key: 'initiated_at', label: 'Initiated', format: 'dateTime', sortable: true },
    ],
  },
  {
    code: 'dpd',
    label: 'DPD & Ageing',
    description: 'Latest scoped days-past-due snapshots and overdue amounts.',
    requiredPermissions: ['reports.dpd.read', 'monitoring.dpd.read', 'finance.loan_account.read'],
    defaultOrdering: '-days_past_due',
    filters: [
      { key: 'asOfDate', label: 'As of date', type: 'date' },
      { key: 'sopBucket', label: 'SOP bucket', placeholder: 'e.g. one_to_two_years' },
    ],
    columns: [
      { key: 'loan_account_number', label: 'Loan account', sortable: true },
      { key: 'borrower_name', label: 'Borrower', sortable: true },
      { key: 'as_of_date', label: 'As of date', format: 'date', sortable: true },
      { key: 'days_past_due', label: 'DPD', align: 'right', sortable: true },
      { key: 'sop_bucket', label: 'SOP bucket', format: 'status', sortable: true },
      { key: 'total_overdue_amount', label: 'Total overdue', format: 'money', align: 'right', sortable: true },
      { key: 'principal_outstanding', label: 'Principal outstanding', format: 'money', align: 'right', sortable: true },
    ],
  },
  {
    code: 'compliance-dashboard',
    label: 'Compliance MIS',
    description: 'Section 186 and NBFC principal-business tracker results.',
    requiredPermissions: [
      'reports.compliance.read',
      'compliance.section186.read',
      'compliance.nbfc_test.read',
    ],
    defaultOrdering: '-report_type',
    filters: [
      { key: 'financialYear', label: 'Financial year', placeholder: 'FY2026-27' },
    ],
    columns: [
      { key: 'report_type', label: 'Report', format: 'status', sortable: true },
      { key: 'financial_year', label: 'Financial year', sortable: true },
      { key: 'quarter', label: 'Quarter', sortable: true },
      { key: 'total_loans_exposure_amount', label: 'Loan exposure', format: 'money', align: 'right' },
      { key: 'headroom_amount', label: 'Headroom', format: 'money', align: 'right' },
      { key: 'financial_asset_ratio', label: 'Financial asset ratio', align: 'right' },
      { key: 'financial_income_ratio', label: 'Financial income ratio', align: 'right' },
      { key: 'review_status', label: 'Review', format: 'status', sortable: true },
      { key: 'prepared_at', label: 'Prepared', format: 'dateTime', sortable: true },
    ],
  },
];

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const ReportsMIS: React.FC = () => {
  const { currentUser, can } = useRole();
  const availableReports = useMemo(
    () => REPORTS.filter(report => (
      report.requiredPermissions.every(permission => currentUser.permissions.includes(permission))
    )),
    [currentUser.permissions],
  );
  const [activeCode, setActiveCode] = useState<ReportCode | null>(
    availableReports[0]?.code ?? null,
  );
  const activeReport = availableReports.find(report => report.code === activeCode) ?? null;
  const [draftFilters, setDraftFilters] = useState<ReportQuery>({});
  const [query, setQuery] = useState<ReportQuery>({
    ordering: activeReport?.defaultOrdering,
    page: 1,
    pageSize: 20,
  });
  const [rows, setRows] = useState<ReportRow[]>([]);
  const [pagination, setPagination] = useState<Pagination>(emptyPagination);
  const [loading, setLoading] = useState(Boolean(activeReport));
  const [error, setError] = useState<Error | null>(null);
  const [exportJob, setExportJob] = useState<ReportExportJob | null>(null);
  const [exportBusy, setExportBusy] = useState(false);
  const [exportError, setExportError] = useState<Error | null>(null);
  const [downloaded, setDownloaded] = useState(false);
  const exportAttemptKey = useRef(crypto.randomUUID());

  useEffect(() => {
    if (activeReport) return;
    const replacement = availableReports[0];
    if (replacement) setActiveCode(replacement.code);
  }, [activeReport, availableReports]);

  useEffect(() => {
    if (!activeReport) {
      setRows([]);
      setPagination(emptyPagination);
      setLoading(false);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    void fetchReport(activeReport.code, query)
      .then(result => {
        if (cancelled) return;
        setRows(result.items);
        setPagination(result.pagination);
      })
      .catch(reason => {
        if (cancelled) return;
        setRows([]);
        setPagination(emptyPagination);
        setError(reason instanceof Error ? reason : new Error('Report results could not be loaded.'));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeReport, query]);

  const selectReport = (report: ReportDefinition) => {
    setActiveCode(report.code);
    setDraftFilters({});
    setQuery({ ordering: report.defaultOrdering, page: 1, pageSize: 20 });
    setRows([]);
    setPagination(emptyPagination);
    setError(null);
    setExportJob(null);
    setExportError(null);
    setDownloaded(false);
    exportAttemptKey.current = crypto.randomUUID();
  };

  const applyFilters = () => {
    if (!activeReport) return;
    setQuery({
      ...draftFilters,
      ordering: query.ordering ?? activeReport.defaultOrdering,
      page: 1,
      pageSize: query.pageSize ?? 20,
    });
  };

  const changeOrdering = (field: string) => {
    const current = query.ordering ?? activeReport?.defaultOrdering ?? '';
    const next = current === field ? `-${field}` : field;
    setQuery(previous => ({ ...previous, ordering: next, page: 1 }));
  };

  const changePage = (page: number) => {
    setQuery(previous => ({ ...previous, page }));
  };

  const startExport = async () => {
    if (!activeReport || exportBusy) return;
    setExportBusy(true);
    setExportError(null);
    setDownloaded(false);
    try {
      const job = await requestReportExport({
        reportCode: activeReport.code,
        format: 'xlsx',
        filters: reportQueryToExportFilters(query),
      }, exportAttemptKey.current);
      setExportJob(job);
    } catch (reason) {
      setExportJob(null);
      setExportError(reason instanceof Error ? reason : new Error('The export request failed.'));
    } finally {
      setExportBusy(false);
    }
  };

  const refreshExport = async () => {
    if (!exportJob || exportBusy) return;
    setExportBusy(true);
    setExportError(null);
    try {
      setExportJob(await fetchReportExport(exportJob.export_job_id));
    } catch (reason) {
      setExportError(reason instanceof Error ? reason : new Error('Export status could not be loaded.'));
    } finally {
      setExportBusy(false);
    }
  };

  const downloadExport = async () => {
    if (!exportJob || exportBusy) return;
    setExportBusy(true);
    setExportError(null);
    try {
      const content = await downloadReportExport(exportJob);
      const url = URL.createObjectURL(content);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `${exportJob.report_code}.${exportJob.format}`;
      anchor.click();
      URL.revokeObjectURL(url);
      setDownloaded(true);
    } catch (reason) {
      setExportError(reason instanceof Error ? reason : new Error('The export could not be downloaded.'));
    } finally {
      setExportBusy(false);
    }
  };

  if (!activeReport) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center py-20 text-center">
          <BarChart2 size={40} className="text-slate-300 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400">
            No report is available for the permissions in this session.
          </p>
        </div>
      </div>
    );
  }

  const denied = error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0);
  const canExport = can('export_registers');

  return (
    <div className="p-6">
      <div className="flex items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Reports & MIS Center</h1>
          <p className="text-sm text-slate-500 mt-1">
            Scoped operational, financial, risk, and compliance reports from the system of record.
          </p>
        </div>
        {canExport && (
          <button
            type="button"
            disabled={exportBusy || Boolean(exportJob)}
            onClick={() => void startExport()}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Download size={15} />
            Export
          </button>
        )}
      </div>

      {exportError && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
          <p className="font-semibold">
            {exportError instanceof AuthSessionError && exportError.code === 'VALIDATION_ERROR'
              ? 'Export validation failed'
              : exportError instanceof AuthSessionError && [401, 403].includes(exportError.status ?? 0)
              ? 'Export permission denied'
              : 'Export unavailable'}
          </p>
          <p className="mt-0.5">
            {exportError instanceof AuthSessionError && [401, 403].includes(exportError.status ?? 0)
              ? 'The backend did not authorize this export request.'
              : exportError.message}
          </p>
        </div>
      )}

      {exportJob && (
        <div className={`mb-4 rounded-lg border px-4 py-3 text-sm ${
          exportJob.status === 'failed'
            ? 'bg-red-50 border-red-200 text-red-700'
            : exportJob.status === 'completed'
              ? 'bg-green-50 border-green-200 text-green-700'
              : 'bg-blue-50 border-blue-200 text-blue-700'
        }`}>
          <p className="font-semibold">
            Export {exportJob.download_expired
              ? 'expired'
              : exportJob.status === 'completed'
                ? exportJob.download_url ? 'ready' : 'finalizing'
                : exportJob.status}
          </p>
          <p className="mt-0.5">
            Job {exportJob.export_job_id}. Standard exports keep sensitive values masked by default.
          </p>
          {downloaded && <p className="mt-1 font-medium">Audited download started.</p>}
          <div className="mt-2 flex gap-2">
            {(['queued', 'running'].includes(exportJob.status)
              || (exportJob.status === 'completed' && !exportJob.download_url && !exportJob.download_expired)) && (
              <button
                type="button"
                disabled={exportBusy}
                onClick={() => void refreshExport()}
                className="border border-current rounded-lg px-3 py-1.5 text-xs font-medium"
              >
                Refresh export status
              </button>
            )}
            {exportJob.status === 'completed' && exportJob.download_url && !exportJob.download_expired && (
              <button
                type="button"
                disabled={exportBusy}
                onClick={() => void downloadExport()}
                className="border border-current rounded-lg px-3 py-1.5 text-xs font-medium"
              >
                Download export
              </button>
            )}
          </div>
        </div>
      )}

      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {availableReports.map(report => (
            <button
              key={report.code}
              type="button"
              onClick={() => selectReport(report)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeReport.code === report.code
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {report.label}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl mb-5">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="font-semibold text-slate-900">{activeReport.label}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{activeReport.description}</p>
        </div>
        {activeReport.filters.length > 0 && (
          <div className="px-6 py-4 flex flex-wrap items-end gap-3">
            {activeReport.filters.map(field => (
              <div key={field.key}>
                <label htmlFor={`report-filter-${field.key}`} className="block text-xs font-medium text-slate-600 mb-1">
                  {field.label}
                </label>
                <input
                  id={`report-filter-${field.key}`}
                  type={field.type ?? 'text'}
                  value={String(draftFilters[field.key] ?? '')}
                  placeholder={field.placeholder}
                  onChange={event => setDraftFilters(previous => ({
                    ...previous,
                    [field.key]: event.target.value,
                  }))}
                  className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                />
              </div>
            ))}
            <button
              type="button"
              onClick={applyFilters}
              className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50"
            >
              <Filter size={14} />
              Apply filters
            </button>
          </div>
        )}
      </div>

      {loading && (
        <div className="bg-white border border-slate-200 rounded-xl p-10 text-center text-sm text-slate-500">
          Loading report results…
        </div>
      )}

      {!loading && error && (
        <div className="bg-white border border-slate-200 rounded-xl p-10 text-center">
          <BarChart2 size={32} className="text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-slate-800">
            {denied ? 'Report access denied' : 'Report unavailable'}
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            {denied ? 'The backend did not authorize this report request.' : error.message}
          </p>
        </div>
      )}

      {!loading && !error && rows.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-10 text-center">
          <BarChart2 size={32} className="text-slate-300 mx-auto mb-3" />
          <h3 className="font-semibold text-slate-800">No report results</h3>
          <p className="text-sm text-slate-500 mt-1">
            No scoped system-of-record rows match the active filters.
          </p>
        </div>
      )}

      {!loading && !error && rows.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="px-6 py-3 border-b border-slate-100 flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">
              {pagination.total_count} {pagination.total_count === 1 ? 'record' : 'records'}
            </span>
            <span className="text-xs text-slate-500">
              Page {pagination.page} of {pagination.total_pages}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  {activeReport.columns.map(column => (
                    <th
                      key={column.key}
                      className={`${column.align === 'right' ? 'text-right' : 'text-left'} px-4 py-3 text-xs font-semibold text-slate-500 uppercase whitespace-nowrap`}
                    >
                      {column.sortable ? (
                        <button
                          type="button"
                          onClick={() => changeOrdering(column.key)}
                          className={`inline-flex items-center gap-1 ${column.align === 'right' ? 'justify-end' : ''}`}
                          aria-label={`Sort by ${column.label}`}
                        >
                          {column.label}
                          {query.ordering?.replace(/^-/, '') === column.key
                            ? query.ordering.startsWith('-')
                              ? <ChevronDown size={13} />
                              : <ChevronUp size={13} />
                            : null}
                        </button>
                      ) : column.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {rows.map(row => {
                  const record = row as unknown as Record<string, unknown>;
                  const rowKey = String(
                    record.loan_account_id
                    ?? record.loan_request_register_entry_id
                    ?? record.document_checklist_id
                    ?? record.disbursement_id
                    ?? record.dpd_status_id
                    ?? record.report_record_id,
                  );
                  return (
                    <tr key={rowKey} className="hover:bg-slate-50">
                      {activeReport.columns.map(column => (
                        <td
                          key={column.key}
                          className={`${column.align === 'right' ? 'text-right' : 'text-left'} px-4 py-3 text-slate-700 whitespace-nowrap`}
                        >
                          {formatValue(record[column.key], column.format)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="px-6 py-3 border-t border-slate-100 flex items-center justify-between">
            <button
              type="button"
              disabled={!pagination.has_previous}
              onClick={() => changePage(pagination.page - 1)}
              className="disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 text-sm text-slate-600"
            >
              <ChevronLeft size={15} />
              Previous
            </button>
            <button
              type="button"
              disabled={!pagination.has_next}
              onClick={() => changePage(pagination.page + 1)}
              className="disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1 text-sm text-slate-600"
            >
              Next
              <ChevronRight size={15} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const formatValue = (value: unknown, format?: Column['format']) => {
  if (value === null || value === undefined || value === '') return '—';
  if (format === 'money') {
    const amount = Number(value);
    if (!Number.isFinite(amount)) return String(value);
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2,
    }).format(amount);
  }
  if (format === 'date' || format === 'dateTime') {
    const parsed = new Date(String(value));
    if (Number.isNaN(parsed.valueOf())) return String(value);
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      ...(format === 'dateTime' ? { hour: '2-digit', minute: '2-digit' } : {}),
    }).format(parsed);
  }
  if (format === 'boolean') return value ? 'Yes' : 'No';
  if (format === 'list' && Array.isArray(value)) return value.length ? value.join(', ') : '—';
  if (format === 'status') return String(value).replace(/_/g, ' ');
  return String(value);
};

export default ReportsMIS;
