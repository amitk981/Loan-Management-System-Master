import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Archive, BookOpen, Download, RefreshCw } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import Tabs from '../../components/ui/Tabs';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError, type Pagination } from '../../services/authSession';
import {
  downloadReportExport,
  fetchReport,
  fetchReportExport,
  requestReportExport,
  type ExportReportCode,
  type ReportExportJob,
} from '../../services/reportApi';
import {
  CreditSanctionRegisterPanel,
  ExceptionRegisterPanel,
} from './ApprovalRegisterPanels';
import { formatMoney } from '../../utils/formatMoney';

type RegisterDefinition = {
  id: string;
  label: string;
  description: string;
  reportCode: ExportReportCode;
  requiredPermissions: string[];
  permissionMode?: 'all' | 'any';
  approvalPanel?: 'sanction' | 'exception';
};

// Display metadata only. Rows, totals, masking, status, and permissions remain backend-owned.
const REGISTER_DEFINITIONS: RegisterDefinition[] = [
  { id: 'loan_register', label: 'Loan account register', description: 'Scoped loan accounts and current balances', reportCode: 'loan-portfolio', requiredPermissions: ['reports.portfolio.read', 'finance.loan_account.read'] },
  { id: 'loan_request_register', label: 'Loan request register', description: 'Scoped applications and current workflow stage', reportCode: 'application-pipeline', requiredPermissions: ['reports.application_pipeline.read'] },
  { id: 'sanction_register', label: 'Credit sanction register', description: 'Frozen sanction decisions and approval evidence', reportCode: 'credit-sanction', requiredPermissions: ['approvals.sanction_register.read'], approvalPanel: 'sanction' },
  { id: 'security_register', label: 'Security register', description: 'Security instrument custody records', reportCode: 'security-custody', requiredPermissions: ['security.package.read'] },
  { id: 'exception_register', label: 'Exception register', description: 'Approved and pending governed exceptions', reportCode: 'exception', requiredPermissions: ['approvals.exception_register.read'], approvalPanel: 'exception' },
  { id: 'compliance_register', label: 'Compliance register', description: 'Section 186 compliance tracker', reportCode: 'section-186', requiredPermissions: ['compliance.section186.read'] },
  { id: 'stamp_duty', label: 'Stamp duty register', description: 'Stamping and notarisation evidence', reportCode: 'stamp-duty', requiredPermissions: ['documents.checklist.read'] },
  { id: 'grievance_register', label: 'Grievance register', description: 'Borrower grievance receipt and resolution status', reportCode: 'grievance', requiredPermissions: ['compliance.grievance.read'] },
  { id: 'recovery_log', label: 'Recovery log', description: 'Approved recovery actions and completion evidence', reportCode: 'recovery', requiredPermissions: ['defaults.case.read'] },
  { id: 'security_custody', label: 'Security custody register', description: 'Held SH-4 and blank-cheque custody records', reportCode: 'security-custody', requiredPermissions: ['security.package.read'] },
  { id: 'sap_register', label: 'SAP customer code register', description: 'Pending SAP customer setup records', reportCode: 'sap-pending', requiredPermissions: ['finance.sap_code.read'] },
  { id: 'disbursement_register', label: 'Disbursement register', description: 'Payment initiation and transfer evidence', reportCode: 'disbursement', requiredPermissions: ['finance.disbursement.readiness'] },
  { id: 'repayment_register', label: 'Repayment register', description: 'Receipts and backend allocation status', reportCode: 'repayment', requiredPermissions: ['finance.loan_account.read'] },
  { id: 'interest_invoice_register', label: 'Interest invoice register', description: 'Issued interest invoices and status', reportCode: 'interest-invoice', requiredPermissions: ['finance.loan_account.read'] },
  { id: 'accrual_register', label: 'Accrual register', description: 'Posted interest accrual evidence', reportCode: 'interest-accrual', requiredPermissions: ['finance.loan_account.read'] },
  { id: 'dpd_register', label: 'DPD / monitoring register', description: 'Backend DPD and portfolio-at-risk snapshots', reportCode: 'dpd', requiredPermissions: ['reports.dpd.read', 'monitoring.dpd.read', 'finance.loan_account.read'] },
  { id: 'noc_register', label: 'NOC / closure register', description: 'Closure readiness and NOC evidence', reportCode: 'closure-noc', requiredPermissions: ['closure.readiness.read'] },
  { id: 'kyc_register', label: 'KYC / re-KYC register', description: 'Masked KYC review status and due dates', reportCode: 'kyc-rekyc', requiredPermissions: ['compliance.kyc_review.manage', 'compliance.task.read'], permissionMode: 'any' },
  { id: 'money_lending_review', label: 'Money-lending annual review', description: 'Annual licence review evidence', reportCode: 'money-lending-review', requiredPermissions: ['compliance.money_lending_review.manage', 'compliance.task.read'], permissionMode: 'any' },
];

const emptyPagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

interface RegistersHubProps {
  onOpenLoan?: (id: string) => void;
  onOpenApplication?: (id: string) => void;
}

const RegistersHub: React.FC<RegistersHubProps> = ({ onOpenLoan, onOpenApplication }) => {
  const { can, currentUser } = useRole();
  const definitions = useMemo(() => REGISTER_DEFINITIONS.filter(definition => (
    definition.permissionMode === 'any'
      ? definition.requiredPermissions.some(permission => currentUser.permissions.includes(permission))
      : definition.requiredPermissions.every(permission => currentUser.permissions.includes(permission))
  )), [currentUser.permissions]);
  const [activeIndex, setActiveIndex] = useState(0);
  const activeDefinition = definitions[activeIndex] ?? definitions[0] ?? null;
  const [exportJob, setExportJob] = useState<ReportExportJob | null>(null);
  const [exportError, setExportError] = useState<Error | null>(null);
  const [exportBusy, setExportBusy] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const exportAttemptKey = useRef(crypto.randomUUID());
  const canExport = can('export_registers');

  useEffect(() => {
    if (activeIndex < definitions.length) return;
    setActiveIndex(0);
  }, [activeIndex, definitions.length]);

  useEffect(() => {
    setExportJob(null);
    setExportError(null);
    setDownloaded(false);
    exportAttemptKey.current = crypto.randomUUID();
  }, [activeDefinition?.id]);

  if (!activeDefinition) {
    return (
      <div className="p-6">
        <AlertBanner
          type="error"
          title="Registers unavailable"
          message="You do not have register read permission."
        />
      </div>
    );
  }

  const startExport = async () => {
    if (exportBusy) return;
    setExportBusy(true);
    setExportError(null);
    setDownloaded(false);
    try {
      setExportJob(await requestReportExport({
        reportCode: activeDefinition.reportCode,
        format: 'xlsx',
        filters: {},
      }, exportAttemptKey.current));
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

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen size={20} className="text-green-600" />
            Registers
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Permission-scoped statutory and internal registers
          </p>
        </div>
        {canExport && (
          <button
            type="button"
            disabled={exportBusy || Boolean(exportJob)}
            onClick={() => void startExport()}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            <Archive size={14} />
            Export Register
          </button>
        )}
      </div>

      {exportError && (
        <AlertBanner
          type="error"
          title={exportError instanceof AuthSessionError && exportError.code === 'VALIDATION_ERROR'
            ? 'Export validation failed'
            : exportError instanceof AuthSessionError && [401, 403].includes(exportError.status ?? 0)
            ? 'Export permission denied'
            : 'Export unavailable'}
          message={exportError instanceof AuthSessionError && [401, 403].includes(exportError.status ?? 0)
            ? 'The backend did not authorize this export request.'
            : exportError.message}
        />
      )}

      {exportJob && (
        <AlertBanner
          type={exportJob.status === 'failed' ? 'error' : exportJob.status === 'completed' ? 'success' : 'info'}
          title={`Export ${exportJob.download_expired
            ? 'expired'
            : exportJob.status === 'completed'
              ? exportJob.download_url ? 'ready' : 'finalizing'
              : exportJob.status}`}
          message={(
            <span>
              Job {exportJob.export_job_id}. Standard exports keep PAN, Aadhaar, bank, cheque,
              and BO-account values masked by default.
              {downloaded && ' Audited download started.'}
            </span>
          )}
          actions={(
            <>
              {(['queued', 'running'].includes(exportJob.status)
                || (exportJob.status === 'completed' && !exportJob.download_url && !exportJob.download_expired)) && (
                <button
                  type="button"
                  disabled={exportBusy}
                  onClick={() => void refreshExport()}
                  className="btn-secondary flex items-center gap-2 text-xs"
                >
                  <RefreshCw size={13} />
                  Refresh export status
                </button>
              )}
              {exportJob.status === 'completed' && exportJob.download_url && !exportJob.download_expired && (
                <button
                  type="button"
                  disabled={exportBusy}
                  onClick={() => void downloadExport()}
                  className="btn-secondary flex items-center gap-2 text-xs"
                >
                  <Download size={13} />
                  Download export
                </button>
              )}
            </>
          )}
        />
      )}

      <Tabs
        tabs={definitions.map(definition => ({ id: definition.id, label: definition.label }))}
        activeIndex={activeIndex}
        onChange={setActiveIndex}
      >
        {definitions.map(definition => (
          definition.approvalPanel === 'sanction'
            ? <CreditSanctionRegisterPanel key={definition.id} />
            : definition.approvalPanel === 'exception'
              ? <ExceptionRegisterPanel key={definition.id} />
              : <BackendRegisterPanel key={definition.id} definition={definition} onOpenLoan={onOpenLoan} onOpenApplication={onOpenApplication} />
        ))}
      </Tabs>
    </div>
  );
};

const BackendRegisterPanel: React.FC<{
  definition: RegisterDefinition;
  onOpenLoan?: (id: string) => void;
  onOpenApplication?: (id: string) => void;
}> = ({ definition, onOpenLoan, onOpenApplication }) => {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [pagination, setPagination] = useState<Pagination>(emptyPagination);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void fetchReport(definition.reportCode, { page: 1, pageSize: 20 })
      .then(result => {
        if (cancelled) return;
        setRows(result.items as unknown as Record<string, unknown>[]);
        setPagination(result.pagination);
      })
      .catch(reason => {
        if (cancelled) return;
        setRows([]);
        setPagination(emptyPagination);
        setError(reason instanceof Error ? reason : new Error('Register rows could not be loaded.'));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [definition.reportCode]);

  const columns = rows.length ? Object.keys(rows[0]) : [];
  const denied = error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0);

  return (
    <div className="card p-0 overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-200">
        <p className="text-sm font-semibold text-slate-900">{definition.label}</p>
        <p className="text-xs text-slate-500 mt-0.5">{definition.description}</p>
      </div>
      {loading && <div className="p-10 text-center text-sm text-slate-500">Loading register…</div>}
      {!loading && error && (
        <div className="p-10 text-center">
          <p className="font-semibold text-slate-800">
            {denied ? 'Register access denied' : 'Register unavailable'}
          </p>
          <p className="text-sm text-slate-500 mt-1">
            {denied ? 'The backend did not authorize this register request.' : error.message}
          </p>
        </div>
      )}
      {!loading && !error && rows.length === 0 && (
        <div className="p-10 text-center">
          <p className="font-semibold text-slate-800">No register records</p>
          <p className="text-sm text-slate-500 mt-1">No scoped system-of-record rows are available.</p>
        </div>
      )}
      {!loading && !error && rows.length > 0 && (
        <>
          <div className="px-4 py-3 border-b border-slate-100 text-sm text-slate-600">
            {pagination.total_count} {pagination.total_count === 1 ? 'record' : 'records'}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  {columns.map(column => (
                    <th key={column} className={`table-header ${numericColumn(column) ? 'text-right' : 'text-left'}`}>
                      {column.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row, index) => (
                  <tr key={rowKey(row, index)} className="hover:bg-slate-50">
                    {columns.map(column => (
                      <td key={column} className={`table-cell ${numericColumn(column) ? 'text-right num' : ''}`}>
                        {column.includes('status') && typeof row[column] === 'string'
                          ? <StatusBadge label={String(row[column])} size="sm" />
                          : column === 'loan_account_number' && row.loan_account_id && onOpenLoan
                            ? <button type="button" onClick={() => onOpenLoan(String(row.loan_account_id))} className="font-semibold text-green-700 hover:underline">{displayValue(row[column])}</button>
                            : column === 'application_reference_number' && row.loan_application_id && onOpenApplication
                              ? <button type="button" onClick={() => onOpenApplication(String(row.loan_application_id))} className="font-semibold text-green-700 hover:underline">{displayValue(row[column])}</button>
                              : displayValue(row[column], column)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

const rowKey = (row: Record<string, unknown>, index: number) => {
  const identity = Object.entries(row).find(([key]) => key.endsWith('_id'));
  return identity ? String(identity[1]) : String(index);
};

const displayValue = (value: unknown, column = ''): string => {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return value.length ? value.map(item => displayValue(item)).join(', ') : '—';
  if (typeof value === 'object') return Object.values(value as Record<string, unknown>).map(item => displayValue(item)).join(' · ');
  if (/(amount|outstanding|exposure|headroom|recovered)$/.test(column)) return formatMoney(String(value));
  if (/(_at|_date|_on)$/.test(column)) {
    const parsed = new Date(String(value));
    if (!Number.isNaN(parsed.valueOf())) return new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(parsed);
  }
  return String(value).replace(/_/g, ' ');
};

const numericColumn = (column: string) => (
  /(amount|outstanding|exposure|headroom|recovered|count|days|rate|ratio)$/.test(column)
);

export default RegistersHub;
