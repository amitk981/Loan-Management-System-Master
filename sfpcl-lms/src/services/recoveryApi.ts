import {
  authenticatedAllPagesRequest,
  authenticatedMultipartRequest,
  authenticatedPaginatedRequest,
  authenticatedRequest,
} from './authSession';

export interface DefaultAssessmentProjection {
  default_assessment_id: string;
  default_case_id: string;
  assessment_type: string;
  payment_failure_classification: string;
  reason_summary: string;
  evidence_document_ids: string[];
  borrower_interaction_summary: string;
  recommended_action: string;
  assessed_by_user_id: string;
  assessed_at: string;
}

export interface ExtensionNoteProjection {
  extension_note_id: string;
  default_case_id: string;
  loan_account_id: string;
  extension_reason: string;
  extension_start_date: string;
  extension_end_date: string;
  document_id: string;
  prepared_by_user_id: string;
  approved_by_user_id: string | null;
  status: string;
}

export interface NonPaymentNoteProjection {
  non_payment_note_id: string;
  default_case_id: string;
  loan_account_id: string;
  reason_for_non_payment: string;
  intentionality_assessment: string;
  outstanding_principal_amount: string;
  outstanding_interest_amount: string;
  recommended_recovery_action: string;
  evidence_document_ids: string[];
  frozen_case_facts: Record<string, string | null>;
  document_id: string;
  prepared_by_user_id: string;
  status: string;
  approval_case_id: string | null;
  submitted_to_sanction_committee_at: string | null;
  available_actions?: Array<{ action_code: string }>;
}

export interface RecoveryApproverProjection {
  role_code: string;
  user_id: string;
  full_name: string | null;
  decision?: string | null;
  acted_at?: string | null;
}

export interface RecoveryApprovalProjection {
  approval_case_id: string;
  approval_type: string;
  related_entity_type: string;
  related_entity_id: string;
  current_status: string;
  decision_date: string;
  reason_for_approval: string;
  conflict_block_reason: string | null;
  required_approvers: RecoveryApproverProjection[];
  approval_actions: Array<RecoveryApproverProjection & {
    approval_action_id: string;
    decision: string;
    comments: string;
    acted_at: string;
  }>;
  excluded_approvers: Array<{ user_id: string; conflict_code: string; reason: string }>;
  available_actions: Array<{
    action_code: string;
    label: string;
    enabled: boolean;
    disabled_reason: string | null;
    required_permission: string;
  }>;
}

export interface RecoveryDecisionProjection {
  recovery_decision_id: string;
  default_case_id?: string;
  non_payment_note_id?: string;
  approval_case_id: string;
  decision: string;
  decision_reason: string;
  status: string;
  approval_evidence?: {
    approval_case_status?: string;
    approved_action?: string;
    required_approvers?: RecoveryApproverProjection[];
    approval_actions?: Array<{
      approval_action_id: string;
      approver_user_id: string;
      approver_role_code: string;
      approver_display_name: string;
      decision: string;
      acted_at: string;
    }>;
    closed_at?: string;
  };
  decided_by_user_id?: string;
  decided_by_role_code?: string;
  decided_at?: string;
  available_actions: Array<{ action_code: string; action_type?: string; required_permission?: string }>;
}

export interface RecoveryActionProjection {
  recovery_action_id: string; action_status: 'pending' | 'completed' | 'failed';
  action_type: string; source_security: { security_type: string; security_id: string; status: string };
  initiated_at: string; amount_recovered: string | null; external_sap_status: string;
  interaction_log: Array<{ interaction_at: string; interaction_mode: string; summary: string; grievance_reference: string }>;
  ledger_posting: Record<string, string>; available_actions: Array<{ action_code: string }>;
}

export interface RecoveryDecisionControlProjection {
  action_code: 'record_recovery_decision';
  enabled: boolean;
  disabled_reason: string | null;
  approval_case_id: string | null;
  decision: string | null;
}

export interface DefaultCaseProjection {
  default_case_id: string;
  loan_account_id: string;
  loan_account_number: string;
  member_id: string;
  borrower_name: string;
  principal_outstanding: string;
  interest_outstanding: string;
  total_outstanding: string;
  trigger_event: string;
  scheduled_due_date: string;
  repayment_schedule_id: string;
  default_case_status: string;
  grace_period_start_date: string;
  grace_period_end_date: string;
  grace_state: string;
  current_assessment: DefaultAssessmentProjection | null;
  extension_note: ExtensionNoteProjection | null;
  non_payment_note: NonPaymentNoteProjection | null;
  recovery_decision: RecoveryDecisionProjection | null;
  recovery_decision_control: RecoveryDecisionControlProjection | null;
  recovery_action: RecoveryActionProjection | null;
  reason: string;
  available_actions?: string[];
}

export type RecoveryCaseProjection = DefaultCaseProjection;

export interface ClosureReadinessCheck {
  code: string;
  status: 'pass' | 'fail';
  approved_adjustment?: boolean;
  security_return_required?: boolean;
  physical_share_return_required?: boolean;
  demat_unpledge_required?: boolean;
  blank_cheque_return_required?: boolean;
  poa_release_required?: boolean;
}

export interface ClosureReadinessProjection {
  loan_account_id: string;
  ready_for_closure: boolean;
  checks: ClosureReadinessCheck[];
  principal_outstanding: string;
  interest_outstanding: string;
  charges_outstanding: string;
  total_outstanding: string;
  interest_adjustment_applied: boolean;
  security_return_required: boolean;
  physical_share_return_required: boolean;
  demat_unpledge_required: boolean;
  blank_cheque_return_required: boolean;
  poa_release_required: boolean;
}

export interface LoanClosureProjection {
  loan_closure_id: string;
  loan_account_id: string;
  loan_account_status: string;
  closure_stage: string;
  closure_type: string;
  closed_at: string;
  noc_required: boolean;
  security_return_required: boolean;
  archive_required: boolean;
  requirements: Record<'noc' | 'security_return' | 'archive', string>;
  idempotency_replayed: boolean;
  available_actions: string[];
}

export interface NocProjection {
  noc_id: string;
  loan_closure_id: string;
  loan_account_id: string;
  member_id: string;
  document_id: string;
  issued_by_user_id: string;
  issued_at: string;
  signatory_user_id: string;
  signatory_role_code: string;
  delivery_mode: string;
  delivery_status: string;
  communication_id: string;
  communication_job_id: string;
  borrower_name: string;
  loan_account_number: string;
  application_reference: string;
  disbursed_amount: string;
  full_repayment_at: string;
  idempotency_replayed: boolean;
}

export interface SecurityReturnItemProjection {
  item_type: string;
  status: string;
  source_item_id: string | null;
  custody_location: string;
  returned_released_to: string;
  psn?: string | null;
  urf_date?: string | null;
  unpledge_type?: string | null;
  pledgor_dp_submitted_at?: string | null;
  pledgee_dp_acted_at?: string | null;
  pledgee_dp_outcome?: string | null;
  auto_unpledge_flag?: boolean;
  completed_at?: string | null;
  pledgor_bo_account?: string | null;
  pledgee_bo_account?: string | null;
}

export interface SecurityReturnProjection {
  security_return_id: string;
  loan_closure_id: string;
  security_package_id: string | null;
  status: string;
  version: number;
  completed_at: string | null;
  items: SecurityReturnItemProjection[];
  idempotency_replayed: boolean;
  available_actions: string[];
}

export interface ArchiveRecordProjection {
  archive_record_id: string;
  loan_closure_id: string;
  loan_account_id: string;
  file_location_physical: string | null;
  file_location_digital: string | null;
  retention_start_date: string;
  retention_until_date: string;
  archived_by_user_id: string;
  archived_by_role_code: string;
  archived_at: string;
  destruction_eligible: boolean;
  destruction_certificate_id: string | null;
  idempotency_replayed: boolean;
  available_actions: string[];
}

export interface GrievanceHistoryProjection {
  sequence: number;
  event_type: string;
  previous_status: string | null;
  new_status: string;
  note: string;
  created_at: string;
}

export interface GrievanceProjection {
  grievance_id: string;
  grievance_reference: string;
  member_id: string;
  loan_account_id: string | null;
  loan_application_id: string | null;
  default_case_id: string | null;
  recovery_action_id: string | null;
  grievance_category: string;
  subject: string;
  description: string;
  received_date: string;
  received_channel: string;
  assigned_to_user_id: string;
  resolution_due_date: string;
  status: string;
  tat_days: number;
  days_overdue: number;
  is_overdue: boolean;
  resolution_summary: string;
  closed_at: string | null;
  borrower_informed: boolean;
  borrower_acknowledged: boolean;
  supporting_document_ids?: string[];
  resolution_document_id?: string | null;
  internal_notes?: string;
  borrower_acknowledgement?: string;
  escalation_count?: number;
  notice_communication_id?: string | null;
  notice_delivery_status?: string | null;
  history: GrievanceHistoryProjection[];
  available_actions?: string[];
}

export interface ComplianceControlProjection {
  compliance_control_id: string;
  control_code: string;
  control_name: string;
  control_area: string;
  legal_basis: string;
  control_type: string;
  frequency: string;
  owner_role_code: string;
  owner_user_id: string;
  reviewer_user_id: string;
  first_due_date: string;
  evidence_required: string;
  risk_if_missed: string;
  status: string;
  available_actions: string[];
}

export interface ComplianceTaskProjection {
  compliance_task_id: string;
  compliance_control_id: string;
  control_code: string;
  task_period: string;
  due_date: string;
  assigned_to_user_id: string;
  reviewer_user_id: string;
  task_status: string;
  remarks: string;
  closed_at: string | null;
  compliance_evidence_id: string | null;
  available_actions: string[];
}

export interface Section186TrackerProjection {
  section_186_tracker_id: string;
  financial_year: string;
  quarter: string;
  paid_up_capital_amount: string;
  free_reserves_amount: string;
  securities_premium_amount: string;
  limit_60_percent_basis_amount: string;
  limit_100_percent_basis_amount: string;
  applicable_limit_amount: string;
  total_loans_exposure_amount: string;
  headroom_amount: string;
  within_limit_flag: boolean;
  special_resolution_required_flag: boolean;
  compliance_task_id: string;
  compliance_evidence_id: string;
  review_status: string;
  review_comments: string;
  presented_to_board_flag: boolean;
  available_actions: string[];
}

export interface NbfcPrincipalTestProjection {
  nbfc_principal_test_id: string;
  financial_year: string;
  quarter: string;
  financial_assets_amount: string;
  total_assets_amount: string;
  financial_asset_ratio: string;
  financial_income_amount: string;
  gross_income_amount: string;
  financial_income_ratio: string;
  early_warning_threshold_ratio: string;
  registration_triggered_flag: boolean;
  one_ratio_above_statutory_flag: boolean;
  early_warning_flag: boolean;
  presented_to_board_flag: boolean;
  compliance_task_id: string;
  compliance_evidence_id: string;
  review_status: string;
  review_comments: string;
  available_actions: string[];
}

export interface KycReviewProjection {
  kyc_review_id: string;
  member_id: string;
  member_name: string;
  member_type: string;
  member_status: string;
  kyc_status: string;
  risk_rating: string | null;
  due_date: string;
  days_overdue: number;
  status: string;
  assigned_to_user_id: string;
  completeness: {
    complete?: boolean;
    pan_status?: string;
    ckyc_consent_status?: string;
    [key: string]: unknown;
  };
  available_actions: string[];
}

export interface MoneyLendingReviewProjection {
  money_lending_law_review_id: string;
  financial_year: string;
  state: string;
  applicability: string;
  exemption_applicable_flag: boolean;
  compliance_task_id: string;
  compliance_evidence_id: string;
  reviewed_by_user_id: string;
  reviewed_at: string;
}

export interface StampDutyProjection {
  stamp_duty_record_id: string;
  loan_document_id: string;
  document_type: string;
  loan_application_id: string;
  application_reference_number: string;
  member_id: string;
  borrower_name: string;
  stamp_paper_amount: string;
  stamp_type: string;
  stamp_number: string | null;
  stamp_purchase_date: string | null;
  executed_date: string | null;
  status: string;
  notarisation_status: string | null;
}

export interface ComplianceDashboardProjection {
  controls: ComplianceControlProjection[];
  tasks: ComplianceTaskProjection[];
  section186: Section186TrackerProjection[];
  nbfcTests: NbfcPrincipalTestProjection[];
  kycReviews: KycReviewProjection[];
  moneyLendingReviews: MoneyLendingReviewProjection[];
  stampDuty: StampDutyProjection[];
}

export const fetchDefaultCases = () =>
  authenticatedPaginatedRequest<DefaultCaseProjection>('/api/v1/default-cases/?page_size=100');

export const fetchDefaultCase = (defaultCaseId: string) =>
  authenticatedRequest<DefaultCaseProjection>(`/api/v1/default-cases/${defaultCaseId}/`);

export const fetchRecoveryCases = fetchDefaultCases;

export const fetchRecoveryApprovalCase = (approvalCaseId: string) =>
  authenticatedRequest<RecoveryApprovalProjection>(`/api/v1/approval-cases/${approvalCaseId}/`);

export const createRecoveryDecision = (
  defaultCaseId: string,
  body: { approval_case_id: string; decision: string; decision_reason: string },
) => authenticatedRequest<RecoveryDecisionProjection>(
  `/api/v1/default-cases/${defaultCaseId}/recovery-decision/`,
  { method: 'POST', body },
);

export const uploadRecoveryEvidence = async (loanAccountId: string, file: File) => (
  await authenticatedMultipartRequest<{ document_id: string }>('/api/v1/document-files/', {
    file, document_category: 'recovery', sensitivity_level: 'restricted',
    related_entity_type: 'loan_account', related_entity_id: loanAccountId,
  })
).document_id;
export const initiateRecoveryAction = (decisionId: string, body: Record<string, unknown>) =>
  authenticatedRequest<RecoveryActionProjection>(`/api/v1/recovery-decisions/${decisionId}/actions/`, { method: 'POST', body });
export const completeRecoveryAction = (actionId: string, body: Record<string, unknown>) =>
  authenticatedRequest<RecoveryActionProjection>(`/api/v1/recovery-actions/${actionId}/complete/`, { method: 'POST', body });

export const fetchClosureReadiness = (loanAccountId: string) =>
  authenticatedRequest<ClosureReadinessProjection>(
    `/api/v1/loan-accounts/${loanAccountId}/closure-readiness/`,
  );

export const closeLoan = (
  loanAccountId: string,
  input: { closure_notes: string; idempotency_key: string },
) => authenticatedRequest<LoanClosureProjection>(
  `/api/v1/loan-accounts/${loanAccountId}/closure/`,
  {
    method: 'POST',
    body: {
      closure_type: 'full_repayment',
      closure_notes: input.closure_notes,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchNoc = (loanClosureId: string) =>
  authenticatedRequest<NocProjection>(`/api/v1/loan-closures/${loanClosureId}/noc/`);

export const issueNoc = (
  loanClosureId: string,
  input: {
    document_id: string;
    delivery_mode: 'email';
    recipient_email: string;
    signatory_user_id: string;
    idempotency_key: string;
  },
) => authenticatedRequest<NocProjection>(
  `/api/v1/loan-closures/${loanClosureId}/noc/`,
  {
    method: 'POST',
    body: {
      document_id: input.document_id,
      delivery_mode: input.delivery_mode,
      recipient_email: input.recipient_email,
      signatory_user_id: input.signatory_user_id,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const recordSecurityReturn = (
  loanClosureId: string,
  input: { payload: Record<string, unknown>; idempotency_key: string },
) => authenticatedRequest<SecurityReturnProjection>(
  `/api/v1/loan-closures/${loanClosureId}/security-return/`,
  {
    method: 'POST',
    body: input.payload,
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchArchiveRecord = (loanClosureId: string) =>
  authenticatedRequest<ArchiveRecordProjection>(
    `/api/v1/loan-closures/${loanClosureId}/archive/`,
  );

export const archiveLoanFile = (
  loanClosureId: string,
  input: {
    file_location_physical: string;
    file_location_digital: string;
    idempotency_key: string;
  },
) => authenticatedRequest<ArchiveRecordProjection>(
  `/api/v1/loan-closures/${loanClosureId}/archive/`,
  {
    method: 'POST',
    body: {
      file_location_physical: input.file_location_physical,
      file_location_digital: input.file_location_digital,
    },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchArchiveRecords = (search = '') =>
  authenticatedAllPagesRequest<ArchiveRecordProjection>(
    page => `/api/v1/archive-records/?page=${page}&page_size=100${
      search.trim() ? `&search=${encodeURIComponent(search.trim())}` : ''
    }`,
  );

export interface ArchiveManifestDownload {
  fileName: string;
  content: Blob;
}

export const downloadArchiveManifest = async (
  archive: ArchiveRecordProjection,
): Promise<ArchiveManifestDownload> => {
  const canonical = await fetchArchiveRecord(archive.loan_closure_id);
  return {
    fileName: `archive-manifest-${canonical.archive_record_id}.json`,
    content: new Blob([JSON.stringify(canonical, null, 2)], { type: 'application/json' }),
  };
};

export const fetchGrievances = () =>
  authenticatedAllPagesRequest<GrievanceProjection>(
    page => `/api/v1/grievances/?page=${page}&page_size=100`,
  );

export const resolveGrievance = (
  grievanceId: string,
  input: {
    status: 'resolved';
    reason: string;
    idempotency_key: string;
  },
) => authenticatedRequest<GrievanceProjection>(
  `/api/v1/grievances/${grievanceId}/resolve/`,
  {
    method: 'POST',
    body: { resolution_summary: input.reason },
    headers: { 'Idempotency-Key': input.idempotency_key },
  },
);

export const fetchComplianceDashboard = async (): Promise<ComplianceDashboardProjection> => {
  const [controls, tasks, section186, nbfcTests, kycReviews, moneyLendingReviews, stampDuty] =
    await Promise.all([
      authenticatedPaginatedRequest<ComplianceControlProjection>(
        '/api/v1/compliance-controls/?page_size=100',
      ),
      authenticatedPaginatedRequest<ComplianceTaskProjection>(
        '/api/v1/compliance-tasks/?page_size=100',
      ),
      authenticatedPaginatedRequest<Section186TrackerProjection>(
        '/api/v1/compliance/section-186-trackers/',
      ),
      authenticatedPaginatedRequest<NbfcPrincipalTestProjection>(
        '/api/v1/compliance/nbfc-principal-tests/',
      ),
      authenticatedPaginatedRequest<KycReviewProjection>(
        '/api/v1/kyc-reviews/?page_size=100',
      ),
      authenticatedPaginatedRequest<MoneyLendingReviewProjection>(
        '/api/v1/reports/money-lending-review/?page_size=100',
      ),
      authenticatedPaginatedRequest<StampDutyProjection>(
        '/api/v1/reports/stamp-duty/?page_size=100',
      ),
    ]);
  return {
    controls: controls.items,
    tasks: tasks.items,
    section186: section186.items,
    nbfcTests: nbfcTests.items,
    kycReviews: kycReviews.items,
    moneyLendingReviews: moneyLendingReviews.items,
    stampDuty: stampDuty.items,
  };
};

export const reviewComplianceEvidence = (
  evidenceId: string,
  input: { review_status: 'accepted' | 'rejected'; review_comments: string },
) => authenticatedRequest<ComplianceTaskProjection>(
  `/api/v1/compliance-evidence/${evidenceId}/review/`,
  { method: 'POST', body: input },
);

export interface StatutoryReviewInput {
  decision: 'accepted' | 'rejected';
  comments: string;
  presented_to_board_flag: boolean;
  board_document_id: string | null;
}

export const reviewSection186Tracker = (
  trackerId: string,
  input: StatutoryReviewInput,
) => authenticatedRequest<Section186TrackerProjection>(
  `/api/v1/compliance/section-186-trackers/${trackerId}/review/`,
  { method: 'POST', body: input },
);

export const reviewNbfcPrincipalTest = (
  testId: string,
  input: StatutoryReviewInput,
) => authenticatedRequest<NbfcPrincipalTestProjection>(
  `/api/v1/compliance/nbfc-principal-tests/${testId}/review/`,
  { method: 'POST', body: input },
);
