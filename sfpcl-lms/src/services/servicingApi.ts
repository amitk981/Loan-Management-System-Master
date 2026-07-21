import {
  authenticatedPaginatedRequest,
  authenticatedRequest,
  type PaginatedResult,
} from './authSession';

export type Money = string;

export interface RepaymentScheduleRow {
  repayment_schedule_id: string;
  installment_number: number;
  due_date: string;
  principal_due: Money;
  interest_due: Money;
  charges_due: Money;
  total_due: Money;
  paid_principal: Money;
  paid_interest: Money;
  paid_charges: Money;
  amount_received: Money;
  schedule_status: string;
  extended_due_date: string | null;
  created_at: string;
}

export interface LoanLedgerRow {
  transaction_date: string;
  transaction_type: string;
  owner_reference: { entity_type: string; entity_id: string };
  reference: string;
  debit: Money;
  credit: Money;
  principal_balance: Money;
  interest_balance: Money;
  total_outstanding: Money;
  actor: { user_id: string; display_name: string };
  sap_status: string;
  remarks: string;
}

export interface RepaymentAllocationProjection {
  allocated_to_principal: Money;
  allocated_to_interest: Money;
  allocated_to_charges: Money;
  unallocated_amount: Money;
  exception_reason: string | null;
}

export interface RepaymentProjection {
  repayment_id: string;
  loan_account_id: string;
  repayment_source: 'direct_farmer' | 'subsidiary_deduction';
  amount_received: Money;
  received_date: string;
  payment_method: string;
  bank_reference_number: string;
  bank_statement_line_id: string | null;
  statement_match_status: string;
  allocation_status: string;
  sap_posting_status: string;
  sap_posting_due_date: string;
  sap_entry_reference: string | null;
  sap_posted_at: string | null;
  allocation: RepaymentAllocationProjection | null;
  subsidiary_reconciliation: null | {
    subsidiary_company_id: string;
    produce_payment_reference: string;
    transfer_reference: string;
    tri_party_agreement_id: string;
    reconciliation_status: string;
    treasury_verification_status: string;
  };
}

export interface BankStatementLineProjection {
  bank_statement_line_id: string;
  line_number: number;
  transaction_date: string | null;
  value_date: string | null;
  amount: Money | null;
  parse_status: string;
  match_status: string;
  match_reason_code: string;
  matched_repayment_id: string | null;
  repayment_evidence: null | {
    repayment_id: string;
    bank_statement_line_id: string;
    statement_match_status: string;
    allocation_status: string;
  };
}

export interface DirectRepaymentCapture {
  repayment_source: 'direct_farmer';
  amount_received: Money;
  received_date: string;
  payment_method: 'rtgs' | 'neft';
  bank_reference_number: string;
  bank_statement_line_id?: string;
  remarks: string;
}

export interface CapturedRepayment {
  repayment_id: string;
  loan_account_id: string;
  repayment_source: string;
  amount_received: Money;
  received_date: string;
  payment_method: string;
  bank_reference_number: string;
  bank_statement_line_id: string | null;
  statement_match_status: string;
  allocation_status: string;
  sap_posting: {
    status: string;
    due_date: string;
    sap_entry_reference: string | null;
    posted_at: string | null;
  };
}

export interface AllocationResult extends RepaymentAllocationProjection {
  repayment_allocation_id: string;
  repayment_id: string;
  allocation_rule: 'principal_first';
  allocation_rule_version: string;
  allocation_status: string;
  loan_account: {
    principal_outstanding: Money;
    interest_outstanding: Money;
    charges_outstanding: Money;
    total_outstanding: Money;
  };
}

interface Replay<T> { idempotency_replayed: true; original_response: T }

export const fetchRepaymentSchedule = (loanAccountId: string, page = 1, pageSize = 20) =>
  authenticatedPaginatedRequest<RepaymentScheduleRow>(
    `/api/v1/loan-accounts/${loanAccountId}/repayment-schedule/?page=${page}&page_size=${pageSize}`,
  );

export const fetchLoanLedger = (loanAccountId: string, page = 1, pageSize = 20) =>
  authenticatedPaginatedRequest<LoanLedgerRow>(
    `/api/v1/loan-accounts/${loanAccountId}/ledger/?page=${page}&page_size=${pageSize}`,
  );

export const fetchRepayments = (loanAccountId: string, page = 1, pageSize = 20) =>
  authenticatedPaginatedRequest<RepaymentProjection>(
    `/api/v1/loan-accounts/${loanAccountId}/repayments/?page=${page}&page_size=${pageSize}`,
  );

export const fetchBankStatementLines = (
  matchStatus: 'unmatched' | 'exception', page = 1, pageSize = 20,
) => authenticatedPaginatedRequest<BankStatementLineProjection>(
  `/api/v1/bank-statement-lines/?match_status=${matchStatus}&page=${page}&page_size=${pageSize}`,
);

interface DirectRepaymentAttempt {
  loanAccountId: string;
  capture: DirectRepaymentCapture;
  sapPosting: { sap_entry_reference: string; sap_posted_at: string; remarks: string };
  idempotencyKey: string;
  permissions: string[];
  roleCodes: string[];
}

export interface DirectRepaymentAttemptResult {
  replayed: boolean;
  capture: CapturedRepayment;
  allocation: AllocationResult | null;
}

const REQUIRED_COMBINED_PERMISSIONS = [
  'finance.repayment.create',
  'finance.repayment.mark_sap_posted',
  'finance.repayment.allocate',
];

export const canPostAndAllocateRepayment = (permissions: string[], roleCodes: string[]) =>
  roleCodes.some(role => ['credit_manager', 'accounts_head'].includes(role))
  && REQUIRED_COMBINED_PERMISSIONS.every(permission => permissions.includes(permission));

export const postAndAllocateDirectRepayment = async (
  attempt: DirectRepaymentAttempt,
): Promise<DirectRepaymentAttemptResult> => {
  if (!canPostAndAllocateRepayment(attempt.permissions, attempt.roleCodes)) {
    throw new Error('Receipt capture, SAP posting, and repayment allocation permissions are required.');
  }
  const captured = await authenticatedRequest<CapturedRepayment | Replay<CapturedRepayment>>(
    `/api/v1/loan-accounts/${attempt.loanAccountId}/repayments/`,
    {
      method: 'POST', body: attempt.capture,
      headers: { 'Idempotency-Key': attempt.idempotencyKey },
    },
  );
  if ('idempotency_replayed' in captured) {
    return { replayed: true, capture: captured.original_response, allocation: null };
  }
  await authenticatedRequest<CapturedRepayment>(
    `/api/v1/repayments/${captured.repayment_id}/mark-sap-posted/`,
    { method: 'POST', body: attempt.sapPosting },
  );
  const allocation = await authenticatedRequest<AllocationResult | Replay<AllocationResult>>(
    `/api/v1/repayments/${captured.repayment_id}/allocate/`,
    {
      method: 'POST',
      body: { allocation_rule: 'principal_first', remarks: 'Allocate confirmed receipt under the approved SOP.' },
      headers: { 'Idempotency-Key': `${attempt.idempotencyKey}:allocation` },
    },
  );
  return {
    replayed: 'idempotency_replayed' in allocation,
    capture: captured,
    allocation: 'idempotency_replayed' in allocation ? allocation.original_response : allocation,
  };
};

export type ServicingPage<T> = PaginatedResult<T>;
