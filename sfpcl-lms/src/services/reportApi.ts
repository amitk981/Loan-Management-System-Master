import {
  authenticatedPaginatedRequest,
  type PaginatedResult,
} from './authSession';

export type ReportCode =
  | 'application-pipeline'
  | 'documentation-readiness'
  | 'disbursement-pending'
  | 'loan-portfolio'
  | 'dpd'
  | 'compliance-dashboard';

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
  reportCode: ReportCode,
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

const add = (
  params: URLSearchParams,
  key: string,
  value: string | number | undefined,
) => {
  if (value !== undefined && value !== '') params.set(key, String(value));
};
