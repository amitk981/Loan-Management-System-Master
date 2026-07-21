import {
  authenticatedAllPagesRequest,
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

interface Replay<T> { idempotency_replayed: true; original_response: T }

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
  const result = await authenticatedRequest<
    DirectRepaymentAttemptResult | CapturedRepayment | Replay<CapturedRepayment>
  >(
    `/api/v1/loan-accounts/${attempt.loanAccountId}/direct-repayment-command/`,
    {
      method: 'POST',
      body: { capture: attempt.capture, sap_posting: attempt.sapPosting },
      headers: { 'Idempotency-Key': attempt.idempotencyKey },
    },
  );
  if ('capture' in result) return result;

  // Resume a partially deployed CR-015 transport response through the same
  // server-owned SAP/allocation seams; the canonical command never enters this path.
  const capture = 'idempotency_replayed' in result ? result.original_response : result;
  await authenticatedRequest<CapturedRepayment>(
    `/api/v1/repayments/${capture.repayment_id}/mark-sap-posted/`,
    { method: 'POST', body: attempt.sapPosting },
  );
  const allocated = await authenticatedRequest<AllocationResult | Replay<AllocationResult>>(
    `/api/v1/repayments/${capture.repayment_id}/allocate/`,
    {
      method: 'POST',
      body: {
        allocation_rule: 'principal_first',
        remarks: 'Allocate confirmed receipt under the approved SOP.',
      },
      headers: { 'Idempotency-Key': `${attempt.idempotencyKey}:allocation` },
    },
  );
  return {
    replayed: 'idempotency_replayed' in result || 'idempotency_replayed' in allocated,
    capture,
    allocation: 'idempotency_replayed' in allocated
      ? allocated.original_response
      : allocated,
  };
};

export interface InterestInvoiceProjection {
  interest_invoice_id: string;
  loan_account_id: string;
  member_id: string;
  financial_year: string;
  invoice_number: string;
  invoice_date: string;
  interest_period_start: string;
  interest_period_end: string;
  principal_base_amount: Money;
  interest_rate: string;
  gross_interest_amount: Money;
  interest_paid_amount: Money;
  tax_amount: Money;
  fixed_fee_amount: Money;
  interest_amount: Money;
  invoice_status: string;
  rate_version_number: number;
  calculation_version: string;
  document_id: string | null;
  communication_id: string | null;
  delivery_status: string | null;
  generated_by_user_id: string;
  generated_at: string;
  issued_by_user_id: string | null;
  issued_at: string | null;
}

export interface AccrualProjection {
  accrual_entry_id: string;
  loan_account_id: string;
  accrual_month: string;
  principal_base_amount: Money;
  interest_rate: string;
  calculation_days: number;
  day_count_basis: string;
  interest_accrued_amount: Money;
  sap_posting_status: string;
  generated_at: string;
}

export interface AccrualRunProjection {
  accrual_month: string;
  dry_run: boolean;
  results: Array<{
    loan_account_id: string;
    outcome: string;
    persisted: boolean;
    reason?: string;
    interest_accrued_amount?: Money;
  }>;
}

export interface PortfolioAccrualRunProjection extends AccrualRunProjection {
  selection: {
    loan_account_count: number;
    batch_count: number;
    completed_batches: number;
  };
}

export class PortfolioAccrualError extends Error {
  completedRun: PortfolioAccrualRunProjection;

  constructor(message: string, completedRun: PortfolioAccrualRunProjection) {
    super(message);
    this.name = 'PortfolioAccrualError';
    this.completedRun = completedRun;
  }
}

export interface CapitalisationPreviewRow {
  loan_account_id: string;
  eligible: boolean;
  reason_code: string;
  old_principal_amount: Money;
  unpaid_interest_amount: Money;
  new_principal_amount: Money;
}

export interface CapitalisationPreview {
  financial_year: string;
  as_of_date: string;
  dry_run: true;
  results: CapitalisationPreviewRow[];
}

export interface InterestCapitalisationProjection {
  interest_capitalisation_id: string;
  loan_account_id: string;
  financial_year: string;
  old_principal_amount: Money;
  unpaid_interest_amount: Money;
  new_principal_amount: Money;
  status: string;
  borrower_intimation?: { email_delivery_status: string; letter_document_id: string };
}

export interface DpdPortfolioRow {
  dpd_status_id: string;
  loan_account_id: string;
  loan_account_number: string;
  member_display_name: string;
  loan_account_status: string;
  principal_outstanding: Money;
  interest_outstanding: Money;
  repayment_date: string;
  as_of_date: string;
  days_past_due: number;
  sop_bucket: string;
  standard_bucket: string | null;
  principal_overdue_amount: Money;
  interest_overdue_amount: Money;
  total_overdue_amount: Money;
}

export interface DpdPortfolioProjection {
  sop_bucket_counts: Record<'current' | 'one_to_two_years' | 'two_to_three_years' | 'more_than_three_years', number>;
  total_count: number;
  rows: DpdPortfolioRow[];
}

export interface ReminderProjection {
  reminder_id: string;
  loan_account_id: string;
  member_id: string;
  quarter_end_date: string;
  eligibility_decision: { eligible: boolean; reason: string };
  reminder_type: string;
  origin: string;
  channel: string;
  delivery_status: string;
  status_reason: string | null;
  next_follow_up_date: string | null;
  call_outcome: string | null;
  created_by: { user_id: string; display_name: string };
  created_at: string;
}

export const canGenerateInvoice = (permissions: string[]) =>
  permissions.includes('finance.interest_invoice.create');
export const canGenerateAccrual = (permissions: string[]) =>
  permissions.includes('finance.accrual.bulk_generate');
export const canCapitaliseInterest = (permissions: string[]) =>
  permissions.includes('finance.interest_capitalise');

export const fetchInterestInvoices = (page = 1, pageSize = 100) =>
  authenticatedPaginatedRequest<InterestInvoiceProjection>(
    `/api/v1/interest-invoices/?page=${page}&page_size=${pageSize}`,
  );

export const fetchAllInterestInvoices = () =>
  authenticatedAllPagesRequest<InterestInvoiceProjection>(
    page => `/api/v1/interest-invoices/?page=${page}&page_size=100`,
  );

export const generateInterestInvoice = (
  loanAccountId: string, financialYear: string, idempotencyKey: string,
) => authenticatedRequest<InterestInvoiceProjection>(
  `/api/v1/loan-accounts/${loanAccountId}/interest-invoices/`,
  { method: 'POST', body: { financial_year: financialYear }, headers: { 'Idempotency-Key': idempotencyKey } },
);

export const runInterestAccrual = (
  accrualMonth: string, loanAccountIds: string[], idempotencyKey: string,
) => authenticatedRequest<AccrualRunProjection>('/api/v1/accrual-entries/bulk-generate/', {
  method: 'POST',
  body: { accrual_month: accrualMonth, dry_run: false, loan_account_ids: loanAccountIds },
  headers: { 'Idempotency-Key': idempotencyKey },
});

export const runPortfolioInterestAccrual = async (
  accrualMonth: string,
  loanAccountIds: string[],
  idempotencyKey: string,
): Promise<PortfolioAccrualRunProjection> => {
  const batches = Array.from(
    { length: Math.ceil(loanAccountIds.length / 100) },
    (_, index) => loanAccountIds.slice(index * 100, (index + 1) * 100),
  );
  const results: AccrualRunProjection['results'] = [];
  for (const [index, batch] of batches.entries()) {
    try {
      const run = await runInterestAccrual(
        accrualMonth,
        batch,
        `${idempotencyKey}:batch-${index + 1}-of-${batches.length}`,
      );
      if (
        run.accrual_month !== accrualMonth
        || run.dry_run !== false
        || run.results.length !== batch.length
        || run.results.some((result, resultIndex) => result.loan_account_id !== batch[resultIndex])
      ) {
        throw new Error('The backend returned incomplete accrual batch membership.');
      }
      results.push(...run.results);
    } catch (error) {
      const completedRun: PortfolioAccrualRunProjection = {
        accrual_month: accrualMonth,
        dry_run: false,
        results,
        selection: {
          loan_account_count: loanAccountIds.length,
          batch_count: batches.length,
          completed_batches: index,
        },
      };
      const reason = error instanceof Error ? error.message : 'The backend rejected the batch.';
      throw new PortfolioAccrualError(
        `Portfolio accrual stopped after ${results.length} of ${loanAccountIds.length} selected loans (${index} of ${batches.length} batches). ${reason}`,
        completedRun,
      );
    }
  }
  return {
    accrual_month: accrualMonth,
    dry_run: false,
    results,
    selection: {
      loan_account_count: loanAccountIds.length,
      batch_count: batches.length,
      completed_batches: batches.length,
    },
  };
};

export const previewInterestCapitalisations = (financialYear: string, asOfDate: string) =>
  authenticatedRequest<CapitalisationPreview>('/api/v1/interest-capitalisations/check/', {
    method: 'POST', body: { financial_year: financialYear, as_of_date: asOfDate, dry_run: true },
  });

export const capitaliseInterest = (
  loanAccountId: string, financialYear: string, capitalisationDate: string, idempotencyKey: string,
) => authenticatedRequest<InterestCapitalisationProjection>(
  `/api/v1/loan-accounts/${loanAccountId}/interest-capitalisations/`,
  { method: 'POST', body: { financial_year: financialYear, capitalisation_date: capitalisationDate }, headers: { 'Idempotency-Key': idempotencyKey } },
);

export const fetchDpdPortfolio = () =>
  authenticatedRequest<DpdPortfolioProjection>('/api/v1/dpd-statuses/');

export const fetchReminders = async () => {
  const rows: ReminderProjection[] = [];
  let page = 1;
  let hasNext = true;
  while (hasNext) {
    const result = await authenticatedPaginatedRequest<ReminderProjection>(`/api/v1/reminders/?page=${page}&page_size=100`);
    rows.push(...result.items);
    hasNext = result.pagination.has_next;
    page += 1;
  }
  return rows;
};

export type ServicingPage<T> = PaginatedResult<T>;
