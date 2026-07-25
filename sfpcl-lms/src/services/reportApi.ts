import {
  AuthSessionError,
  authenticatedBlobRequest,
  authenticatedPaginatedRequest,
  authenticatedRequest,
  type PaginatedResult,
} from './authSession';

export type ReportCode =
  | 'application-pipeline'
  | 'documentation-readiness'
  | 'disbursement-pending'
  | 'loan-portfolio'
  | 'dpd'
  | 'compliance-dashboard';

export type ExportReportCode = ReportCode
  | 'section-186'
  | 'nbfc-test'
  | 'credit-sanction'
  | 'default'
  | 'exception'
  | 'security-custody'
  | 'sap-pending'
  | 'disbursement'
  | 'repayment'
  | 'recovery'
  | 'closure-noc'
  | 'kyc-rekyc'
  | 'stamp-duty'
  | 'money-lending-review'
  | 'grievance'
  | 'interest-invoice'
  | 'interest-accrual'
  | 'cfo-quarterly-mis'
  | 'audit-log-export';

export type ReportExportFormat = 'csv' | 'xlsx' | 'pdf' | 'json';
export type ReportExportStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface ReportExportJob {
  export_job_id: string;
  report_code: ExportReportCode;
  format: ReportExportFormat;
  filters: Record<string, string>;
  status: ReportExportStatus;
  failure_code: string | null;
  idempotency_replayed: boolean;
  requested_at: string;
  started_at: string | null;
  completed_at: string | null;
  checksum_sha256?: string;
  file_size_bytes?: number;
  download_url?: string | null;
  download_expired?: boolean;
  expires_at?: string | null;
}

export interface ReportExportRequest {
  reportCode: ExportReportCode;
  format: ReportExportFormat;
  filters: Record<string, string>;
  columns?: string[];
  sensitiveReason?: string;
}

export interface ReportQuery {
  fromDate?: string;
  toDate?: string;
  status?: string;
  stage?: string;
  asOfDate?: string;
  sopBucket?: string;
  financialYear?: string;
  ordering?: string;
  page?: number;
  pageSize?: number;
}

export interface ApplicationPipelineRow {
  loan_request_register_entry_id: string;
  application_reference_number: string;
  borrower_name: string;
  date_received: string;
  register_status: string;
  requested_amount: string | null;
  current_stage: string;
  current_owner_role: string;
}

export interface DocumentationReadinessRow {
  document_checklist_id: string;
  application_reference_number: string;
  borrower_name: string;
  checklist_status: string;
  required_item_count: number;
  completed_item_count: number;
  pending_item_count: number;
  blocker_codes: string[];
  updated_at: string;
}

export interface DisbursementPendingRow {
  disbursement_id: string;
  loan_account_number: string;
  borrower_name: string;
  disbursement_amount: string;
  initiation_status: string;
  authorisation_status: string;
  bank_transfer_status: string;
  initiated_at: string;
}

export interface LoanPortfolioRow {
  loan_account_id: string;
  loan_account_number: string;
  borrower_name: string;
  loan_account_status: string;
  sanctioned_amount: string;
  disbursed_amount: string;
  principal_outstanding: string;
  interest_outstanding: string;
  total_outstanding: string;
  loan_type: string;
  repayment_date: string;
  created_at: string;
}

export interface DpdReportRow {
  dpd_status_id: string;
  loan_account_number: string;
  borrower_name: string;
  as_of_date: string;
  days_past_due: number;
  sop_bucket: string;
  standard_bucket: string | null;
  total_overdue_amount: string;
  principal_outstanding: string;
  loan_account_status: string;
}

export interface ComplianceDashboardRow {
  report_type: 'section_186' | 'nbfc_principal_business';
  report_record_id: string;
  financial_year: string;
  quarter: string;
  review_status: string;
  prepared_at: string;
  applicable_limit_amount?: string;
  total_loans_exposure_amount?: string;
  headroom_amount?: string;
  within_limit_flag?: boolean;
  financial_asset_ratio?: string;
  financial_income_ratio?: string;
  registration_triggered_flag?: boolean;
}

export type ReportRow =
  | ApplicationPipelineRow
  | DocumentationReadinessRow
  | DisbursementPendingRow
  | LoanPortfolioRow
  | DpdReportRow
  | ComplianceDashboardRow;

export const fetchReport = async (
  reportCode: ExportReportCode,
  query: ReportQuery = {},
): Promise<PaginatedResult<ReportRow>> => {
  const params = new URLSearchParams();
  add(params, 'from_date', query.fromDate);
  add(params, 'to_date', query.toDate);
  add(params, 'status', query.status);
  add(params, 'stage', query.stage);
  add(params, 'as_of_date', query.asOfDate);
  add(params, 'sop_bucket', query.sopBucket);
  add(params, 'financial_year', query.financialYear);
  add(params, 'ordering', query.ordering);
  add(params, 'page', query.page);
  add(params, 'page_size', query.pageSize);
  const suffix = params.size ? `?${params.toString()}` : '';
  return authenticatedPaginatedRequest<ReportRow>(
    `/api/v1/reports/${reportCode}/${suffix}`,
  );
};

export const requestReportExport = (
  input: ReportExportRequest,
  idempotencyKey: string,
): Promise<ReportExportJob> => authenticatedRequest<ReportExportJob>(
  '/api/v1/reports/exports/',
  {
    method: 'POST',
    headers: { 'Idempotency-Key': idempotencyKey },
    body: {
      report_code: input.reportCode,
      format: input.format,
      filters: input.filters,
      ...(input.columns ? { columns: input.columns } : {}),
      ...(input.sensitiveReason !== undefined
        ? { sensitive_reason: input.sensitiveReason }
        : {}),
    },
  },
);

export const fetchReportExport = (exportJobId: string): Promise<ReportExportJob> => (
  authenticatedRequest<ReportExportJob>(`/api/v1/reports/exports/${exportJobId}/`)
);

export const downloadReportExport = async (job: ReportExportJob): Promise<Blob> => {
  if (job.status !== 'completed' || !job.download_url || job.download_expired) {
    throw new AuthSessionError(
      'EXPORT_NOT_READY',
      'The report export is not ready for download.',
      409,
    );
  }
  const expectedPrefix = `/api/v1/reports/exports/${job.export_job_id}/download/?token=`;
  if (!job.download_url.startsWith(expectedPrefix)) {
    throw new AuthSessionError(
      'INVALID_DOWNLOAD_ACTION',
      'The report export download capability is invalid.',
      400,
    );
  }
  return authenticatedBlobRequest(job.download_url);
};

export const reportQueryToExportFilters = (
  query: ReportQuery,
): Record<string, string> => {
  const filters: Record<string, string> = {};
  const values: Array<[string, string | undefined]> = [
    ['from_date', query.fromDate],
    ['to_date', query.toDate],
    ['status', query.status],
    ['stage', query.stage],
    ['as_of_date', query.asOfDate],
    ['sop_bucket', query.sopBucket],
    ['financial_year', query.financialYear],
    ['ordering', query.ordering],
  ];
  values.forEach(([key, value]) => {
    if (value) filters[key] = value;
  });
  return filters;
};

const add = (
  params: URLSearchParams,
  key: string,
  value: string | number | undefined,
) => {
  if (value !== undefined && value !== '') params.set(key, String(value));
};
