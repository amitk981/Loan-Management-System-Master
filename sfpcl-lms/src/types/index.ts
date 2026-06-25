// ─── Core domain types for SFPCL LMS ──────────────────────────────────────

export type MemberType = 'individual' | 'fpc' | 'producer_institution';
export type ShareMode = 'physical' | 'demat';
export type LoanType = 'short_term' | 'long_term';
export type LoanPurpose = 'crop_production' | 'agriculture_activity' | 'allied_activity';

export type ApplicationStatus =
  | 'draft' | 'submitted' | 'incomplete' | 'reference_generated'
  | 'appraisal_pending' | 'credit_review' | 'pending_sanction'
  | 'sanctioned' | 'rejected_credit' | 'rejected_sanction';

export type DocumentationStatus =
  | 'not_started' | 'in_progress' | 'pending_signature' | 'pending_stamp'
  | 'pending_notarisation' | 'pending_cs_review' | 'pending_credit_review'
  | 'pending_final_approval' | 'complete' | 'blocked';

export type DisbursementStatus =
  | 'pending_documentation' | 'pending_sap_code' | 'sap_code_created'
  | 'pending_bank_verification' | 'ready_for_payment' | 'payment_initiated'
  | 'pending_cfc_approval' | 'completed' | 'failed';

export type LoanStatus =
  | 'sanctioned' | 'documentation_pending' | 'disbursement_pending'
  | 'active' | 'overdue' | 'grace_period' | 'extension' | 'default_review'
  | 'recovery_approved' | 'recovery_in_progress' | 'closed' | 'archived';

export type DPDBucket = '0_30' | '31_60' | '61_90' | '91_365' | '1_2_years' | '2_3_years' | '3plus_years';

export type SecurityType = 'poa' | 'sh4' | 'cdsl_pledge' | 'blank_cheque' | 'tri_party';
export type SecurityStatus = 'pending' | 'executed' | 'held' | 'pledged' | 'invoked' | 'released' | 'returned';

export type DocumentType =
  | 'pan' | 'aadhaar' | 'share_certificate' | 'land_712' | 'crop_plan' | 'bank_statement'
  | 'poa' | 'tri_party' | 'sh4' | 'term_sheet' | 'loan_agreement' | 'cancelled_cheque'
  | 'blank_cheque' | 'bank_verification_letter' | 'checklist' | 'appraisal_note'
  | 'rejection_note' | 'noc' | 'extension_note' | 'non_payment_note';

export type DocumentStatus =
  | 'not_started' | 'pending_upload' | 'uploaded' | 'under_review'
  | 'verified' | 'rejected' | 'signed' | 'stamped' | 'notarised' | 'complete' | 'returned';

export type Role =
  | 'deputy_manager_finance' | 'credit_manager' | 'compliance_team'
  | 'company_secretary' | 'sanction_committee' | 'cfo' | 'director'
  | 'senior_manager_finance' | 'cfc' | 'accounts' | 'auditor' | 'admin' | 'borrower';

// ─── Entity interfaces ────────────────────────────────────────────────────

export interface Member {
  id: string;
  memberType: MemberType;
  name: string;
  folioNumber: string;
  sharesHeld: number;
  shareMode: ShareMode;
  aadhaar: string;
  pan: string;
  mobile: string;
  email: string;
  address: string;
  activeStatus: 'active' | 'inactive' | 'under_review';
  kycStatus: 'pending' | 'verified' | 'rekyc_due' | 'expired';
  supplyYears: number;
  subsidiaryLinkage?: string;
  defaultStatus: 'no_default' | 'past_default' | 'current_default';
  registeredOn: string;
  currentExposure: number;
  sapCustomerCode?: string;
}

export interface Nominee {
  id: string;
  memberId: string;
  name: string;
  age: number;
  aadhaar: string;
  pan: string;
  gender: 'male' | 'female' | 'other';
  relationship: string;
  signatureStatus: 'pending' | 'obtained';
}

export interface LoanApplication {
  id: string;
  applicationNumber: string;
  applicationDate: string;
  memberId: string;
  memberName: string;
  memberType: MemberType;
  nomineeId: string;
  requestedAmount: number;
  purpose: LoanPurpose;
  loanType: LoanType;
  tenure: number;
  sharesHeld: number;
  shareMode: ShareMode;
  landAreaAcres: number;
  status: ApplicationStatus;
  documentationStatus: DocumentationStatus;
  disbursementStatus: DisbursementStatus;
  eligibleAmount: number;
  shareholdingLimit: number;
  landBasedLimit: number;
  isException: boolean;
  exceptionReason?: string;
  currentOwner: string;
  currentOwnerRole: Role;
  submittedAt: string;
  referenceGeneratedAt?: string;
  sanctionedAt?: string;
  disbursedAt?: string;
  disbursedAmount?: number;
  sanctionDecision?: 'approved' | 'rejected' | 'pending';
  rejectionReason?: string;
  sapCustomerCode?: string;
  bankAccount?: string;
  bankIfsc?: string;
  riskRating?: 'low' | 'medium' | 'high';
  specialCase?: boolean;
  tatDaysRemaining?: number;
}

export interface LoanAccount {
  id: string;
  applicationId: string;
  applicationNumber: string;
  accountNumber: string;
  memberId: string;
  memberName: string;
  memberType: MemberType;
  sanctionedAmount: number;
  disbursedAmount: number;
  outstandingPrincipal: number;
  accruedInterest: number;
  interestRate: number;
  loanType: LoanType;
  disbursementDate: string;
  repaymentDueDate: string;
  status: LoanStatus;
  dpd: number;
  dpdBucket: DPDBucket;
  lastRepaymentDate?: string;
  lastRepaymentAmount?: number;
  gracePeriodEnd?: string;
  extensionEnd?: string;
  revisedPrincipal?: number;
  sapCustomerCode: string;
}

export interface RepaymentRecord {
  id: string;
  loanAccountId: string;
  receiptDate: string;
  amount: number;
  principalAllocation: number;
  interestAllocation: number;
  channel: 'direct_rtgs' | 'direct_neft' | 'subsidiary_deduction' | 'other';
  subsidiaryName?: string;
  bankReference: string;
  sapEntryStatus: 'pending' | 'posted' | 'failed';
  postedBy?: string;
}

export interface DocumentRecord {
  id: string;
  applicationId: string;
  documentType: DocumentType;
  requiredFlag: 'mandatory' | 'conditional' | 'optional';
  status: DocumentStatus;
  uploadedAt?: string;
  verifiedAt?: string;
  verifiedBy?: string;
  fileName?: string;
  stampStatus?: 'pending' | 'complete' | 'not_required';
  notarisationStatus?: 'pending' | 'complete' | 'not_required';
  version: number;
  rejectionReason?: string;
}

export interface SecurityInstrument {
  id: string;
  applicationId: string;
  securityType: SecurityType;
  status: SecurityStatus;
  executionDate?: string;
  custodian?: string;
  stampDutyStatus?: 'pending' | 'complete' | 'not_required';
  notarisationStatus?: 'pending' | 'complete' | 'not_required';
  invocationApprovalRequired: boolean;
  invocationStatus?: 'not_initiated' | 'proposed' | 'approved' | 'invoked' | 'completed';
  returnDate?: string;
  psnNumber?: string;
}

export interface AuditEvent {
  id: string;
  entityType: string;
  entityId: string;
  eventType: string;
  timestamp: string;
  actorName: string;
  actorRole: Role;
  previousState?: string;
  newState?: string;
  reason?: string;
  comment?: string;
}

export interface ComplianceRecord {
  id: string;
  area: string;
  frequency: 'monthly' | 'quarterly' | 'annual' | 'ongoing';
  owner: string;
  lastReviewDate?: string;
  nextDueDate: string;
  status: 'compliant' | 'warning' | 'breach' | 'pending';
  evidenceCount: number;
}

export interface User {
  id: string;
  name: string;
  role: Role;
  email: string;
  team: string;
}

export interface DashboardStats {
  newApplications: number;
  pendingCompleteness: number;
  pendingAppraisal: number;
  pendingSanction: number;
  documentationPending: number;
  readyForDisbursement: number;
  activeLoans: number;
  overdueLoans: number;
  totalPortfolio: number;
  sectionUtilisation: number;
  openExceptions: number;
  reKycDue: number;
}
