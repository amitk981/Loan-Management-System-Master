import { authenticatedRequest } from './authSession';

export type LoanPolicyStatus = 'draft' | 'active' | 'retired';

export interface LoanPolicyVersion {
  loan_policy_config_id: string;
  policy_name: string;
  policy_version: string;
  effective_from: string;
  effective_to: string | null;
  short_term_duration_months: number;
  min_secured_loan_months: number | null;
  max_secured_loan_years: number | null;
  approval_threshold_amount: string;
  default_scale_of_finance_per_acre_amount: string;
  share_limit_percentage: string | null;
  per_share_cap_amount: string | null;
  interest_rate_type: string;
  interest_benchmark: string | null;
  penal_interest_rate: string | null;
  rekyc_frequency_months: number;
  record_retention_years: number;
  grace_period_months: number;
  non_intentional_extension_months: number;
  board_approval_reference: string | null;
  status: LoanPolicyStatus;
}

export type CreateLoanPolicyVersion = Omit<LoanPolicyVersion, 'loan_policy_config_id' | 'status'>;

export const fetchLoanPolicyVersions = ({ page, pageSize }: { page: number; pageSize: number }): Promise<LoanPolicyVersion[]> => (
  authenticatedRequest<LoanPolicyVersion[]>(`/api/v1/config/loan-policy/?page=${page}&page_size=${pageSize}`)
);

export const createLoanPolicyVersion = (payload: CreateLoanPolicyVersion): Promise<LoanPolicyVersion> => (
  authenticatedRequest<LoanPolicyVersion>('/api/v1/config/loan-policy/', { method: 'POST', body: payload })
);
