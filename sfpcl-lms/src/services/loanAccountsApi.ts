import {
  authenticatedAllPagesRequest,
  authenticatedPaginatedRequest,
  authenticatedRequest,
} from './authSession';

export interface LoanAccountProjection {
  loan_account_id: string;
  loan_account_number: string;
  loan_application_id: string;
  application_reference_number: string | null;
  member: { member_id: string; display_name: string };
  sap_customer_code: string | null;
  loan_type: string;
  facility_type: string;
  interest_rate_type: string;
  current_interest_rate: string;
  sanctioned_amount: string;
  disbursed_amount: string;
  principal_outstanding: string;
  interest_outstanding: string;
  charges_outstanding: string;
  total_outstanding: string;
  loan_account_status: string;
  tenure_start_date: string | null;
  tenure_end_date: string | null;
  repayment_date: string;
  tenure_months: number;
  created_at: string;
  activated_at: string | null;
}

export function fetchLoanAccounts(page = 1, pageSize = 20) {
  return authenticatedPaginatedRequest<LoanAccountProjection>(
    `/api/v1/loan-accounts/?page=${page}&page_size=${pageSize}`,
  );
}

export function fetchAllLoanAccounts() {
  return authenticatedAllPagesRequest<LoanAccountProjection>(
    page => `/api/v1/loan-accounts/?page=${page}&page_size=100`,
  );
}

export function fetchLoanAccount(loanAccountId: string) {
  return authenticatedRequest<LoanAccountProjection>(
    `/api/v1/loan-accounts/${loanAccountId}/`,
  );
}
