import type {
  Member, LoanApplication, LoanAccount, RepaymentRecord,
  DocumentRecord, SecurityInstrument, AuditEvent, ComplianceRecord, User, DashboardStats
} from '../types';

export const currentUser: User = {
  id: 'u1',
  name: 'Priya Kulkarni',
  role: 'credit_manager',
  email: 'priya.kulkarni@sfpcl.in',
  team: 'Credit Assessment',
};

export const members: Member[] = [
  {
    id: 'm001', memberType: 'individual', name: 'Ramesh Patil', folioNumber: 'FO-0042',
    sharesHeld: 500, shareMode: 'physical', aadhaar: '****-****-4521', pan: 'ABCDE1234F',
    mobile: '9823001234', email: 'ramesh.patil@gmail.com',
    address: 'Gat No. 142, Dindori, Nashik, Maharashtra 422 202',
    activeStatus: 'active', kycStatus: 'verified', supplyYears: 5,
    subsidiaryLinkage: 'Sahyadri Farms Post Harvest Care Ltd.',
    defaultStatus: 'no_default', registeredOn: '2019-04-12', currentExposure: 0,
  },
  {
    id: 'm002', memberType: 'individual', name: 'Sunita Bhosale', folioNumber: 'FO-0118',
    sharesHeld: 300, shareMode: 'demat', aadhaar: '****-****-7789', pan: 'FGHIJ5678K',
    mobile: '9765432100', email: 'sunita.bhosale@gmail.com',
    address: 'Sr. No. 88, Igatpuri, Nashik, Maharashtra 422 403',
    activeStatus: 'active', kycStatus: 'verified', supplyYears: 3,
    subsidiaryLinkage: 'Sahyadri Farms Post Harvest Care Ltd.',
    defaultStatus: 'no_default', registeredOn: '2021-06-15', currentExposure: 120000,
  },
  {
    id: 'm003', memberType: 'fpc', name: 'Kisan Samruddhi FPC Ltd.', folioNumber: 'FO-0207',
    sharesHeld: 2000, shareMode: 'demat', aadhaar: 'N/A', pan: 'KLMNO9012P',
    mobile: '9812345678', email: 'admin@kisanfpc.in',
    address: 'Office No. 5, Agri Complex, Pune, Maharashtra 411 001',
    activeStatus: 'active', kycStatus: 'rekyc_due', supplyYears: 4,
    subsidiaryLinkage: 'Sahyadri Farms Post Harvest Care Ltd.',
    defaultStatus: 'no_default', registeredOn: '2020-01-20', currentExposure: 500000,
  },
  {
    id: 'm004', memberType: 'individual', name: 'Vijay Deshmukh', folioNumber: 'FO-0334',
    sharesHeld: 200, shareMode: 'physical', aadhaar: '****-****-3312', pan: 'PQRST3456U',
    mobile: '9700112233', email: 'vijay.deshmukh@gmail.com',
    address: 'House 22, Sinnar, Nashik, Maharashtra 422 103',
    activeStatus: 'active', kycStatus: 'verified', supplyYears: 2,
    defaultStatus: 'no_default', registeredOn: '2022-09-08', currentExposure: 0,
  },
  {
    id: 'm005', memberType: 'individual', name: 'Lalita Shinde', folioNumber: 'FO-0089',
    sharesHeld: 450, shareMode: 'demat', aadhaar: '****-****-9901', pan: 'UVWXY7890Z',
    mobile: '9654321012', email: 'lalita.shinde@gmail.com',
    address: 'Gat No. 77, Trimbakeshwar, Nashik, Maharashtra 422 212',
    activeStatus: 'inactive', kycStatus: 'expired', supplyYears: 1,
    defaultStatus: 'past_default', registeredOn: '2018-11-03', currentExposure: 45000,
  },
];

export const loanApplications: LoanApplication[] = [
  {
    id: 'app001', applicationNumber: 'LO00000042', applicationDate: '2026-06-10',
    memberId: 'm001', memberName: 'Ramesh Patil', memberType: 'individual',
    nomineeId: 'nom001', requestedAmount: 450000, purpose: 'crop_production',
    loanType: 'short_term', tenure: 12, sharesHeld: 500, shareMode: 'physical',
    landAreaAcres: 4.5, status: 'pending_sanction', documentationStatus: 'not_started',
    disbursementStatus: 'pending_documentation', eligibleAmount: 480000,
    shareholdingLimit: 600000, landBasedLimit: 90000, isException: false,
    currentOwner: 'Sanction Committee', currentOwnerRole: 'sanction_committee',
    submittedAt: '2026-06-10T09:30:00Z', referenceGeneratedAt: '2026-06-10T11:00:00Z',
    sanctionDecision: 'pending', riskRating: 'low', tatDaysRemaining: 1,
  },
  {
    id: 'app002', applicationNumber: 'LO00000043', applicationDate: '2026-06-12',
    memberId: 'm002', memberName: 'Sunita Bhosale', memberType: 'individual',
    nomineeId: 'nom002', requestedAmount: 350000, purpose: 'crop_production',
    loanType: 'short_term', tenure: 12, sharesHeld: 300, shareMode: 'demat',
    landAreaAcres: 3.2, status: 'reference_generated', documentationStatus: 'not_started',
    disbursementStatus: 'pending_documentation', eligibleAmount: 360000,
    shareholdingLimit: 360000, landBasedLimit: 64000, isException: false,
    currentOwner: 'Priya Kulkarni', currentOwnerRole: 'deputy_manager_finance',
    submittedAt: '2026-06-12T10:00:00Z', referenceGeneratedAt: '2026-06-12T14:00:00Z',
    sanctionDecision: 'pending', riskRating: 'low', tatDaysRemaining: 0,
  },
  {
    id: 'app003', applicationNumber: 'LO00000044', applicationDate: '2026-06-14',
    memberId: 'm003', memberName: 'Kisan Samruddhi FPC Ltd.', memberType: 'fpc',
    nomineeId: 'nom003', requestedAmount: 800000, purpose: 'agriculture_activity',
    loanType: 'long_term', tenure: 24, sharesHeld: 2000, shareMode: 'demat',
    landAreaAcres: 18, status: 'credit_review', documentationStatus: 'not_started',
    disbursementStatus: 'pending_documentation', eligibleAmount: 360000,
    shareholdingLimit: 2400000, landBasedLimit: 360000, isException: true,
    exceptionReason: 'Requested amount ₹8,00,000 exceeds eligible limit ₹3,60,000',
    currentOwner: 'Priya Kulkarni', currentOwnerRole: 'credit_manager',
    submittedAt: '2026-06-14T08:00:00Z', referenceGeneratedAt: '2026-06-14T10:30:00Z',
    sanctionDecision: 'pending', riskRating: 'medium', tatDaysRemaining: 2,
  },
  {
    id: 'app004', applicationNumber: 'LO00000039', applicationDate: '2026-05-20',
    memberId: 'm004', memberName: 'Vijay Deshmukh', memberType: 'individual',
    nomineeId: 'nom004', requestedAmount: 200000, purpose: 'crop_production',
    loanType: 'short_term', tenure: 12, sharesHeld: 200, shareMode: 'physical',
    landAreaAcres: 2.0, status: 'sanctioned', documentationStatus: 'in_progress',
    disbursementStatus: 'pending_documentation', eligibleAmount: 200000,
    shareholdingLimit: 240000, landBasedLimit: 40000, isException: false,
    currentOwner: 'Compliance Team', currentOwnerRole: 'compliance_team',
    submittedAt: '2026-05-20T09:00:00Z', referenceGeneratedAt: '2026-05-20T11:00:00Z',
    sanctionedAt: '2026-05-25T14:00:00Z', sanctionDecision: 'approved',
    riskRating: 'low', sapCustomerCode: 'SAP-240039',
  },
  {
    id: 'app005', applicationNumber: 'LO00000035', applicationDate: '2026-04-15',
    memberId: 'm002', memberName: 'Sunita Bhosale', memberType: 'individual',
    nomineeId: 'nom002', requestedAmount: 120000, purpose: 'crop_production',
    loanType: 'short_term', tenure: 12, sharesHeld: 300, shareMode: 'demat',
    landAreaAcres: 3.2, status: 'sanctioned', documentationStatus: 'complete',
    disbursementStatus: 'completed', eligibleAmount: 120000,
    shareholdingLimit: 360000, landBasedLimit: 64000, isException: false,
    currentOwner: 'Accounts', currentOwnerRole: 'accounts',
    submittedAt: '2026-04-15T10:00:00Z', referenceGeneratedAt: '2026-04-15T12:00:00Z',
    sanctionedAt: '2026-04-20T10:00:00Z', disbursedAt: '2026-04-28T15:00:00Z',
    disbursedAmount: 120000, sanctionDecision: 'approved',
    riskRating: 'low', sapCustomerCode: 'SAP-230035',
    bankAccount: '****1234', bankIfsc: 'RATN0000001',
  },
];

export const loanAccounts: LoanAccount[] = [
  {
    id: 'ln001', applicationId: 'app005', applicationNumber: 'LO00000035',
    accountNumber: 'LN-2026-000035', memberId: 'm002', memberName: 'Sunita Bhosale',
    memberType: 'individual', sanctionedAmount: 120000, disbursedAmount: 120000,
    outstandingPrincipal: 120000, accruedInterest: 4800, interestRate: 12.5,
    loanType: 'short_term', disbursementDate: '2026-04-28', repaymentDueDate: '2027-04-28',
    status: 'active', dpd: 0, dpdBucket: '0_30', lastRepaymentDate: undefined,
    sapCustomerCode: 'SAP-230035',
  },
  {
    id: 'ln002', applicationId: 'app006', applicationNumber: 'LO00000028',
    accountNumber: 'LN-2025-000028', memberId: 'm001', memberName: 'Ramesh Patil',
    memberType: 'individual', sanctionedAmount: 380000, disbursedAmount: 380000,
    outstandingPrincipal: 380000, accruedInterest: 23750, interestRate: 12.5,
    loanType: 'short_term', disbursementDate: '2025-06-15', repaymentDueDate: '2026-06-15',
    status: 'overdue', dpd: 9, dpdBucket: '0_30', lastRepaymentDate: '2026-01-10',
    lastRepaymentAmount: 50000, sapCustomerCode: 'SAP-220028',
  },
  {
    id: 'ln003', applicationId: 'app007', applicationNumber: 'LO00000019',
    accountNumber: 'LN-2024-000019', memberId: 'm005', memberName: 'Lalita Shinde',
    memberType: 'individual', sanctionedAmount: 80000, disbursedAmount: 80000,
    outstandingPrincipal: 80000, accruedInterest: 13000, interestRate: 12.5,
    loanType: 'short_term', disbursementDate: '2024-03-10', repaymentDueDate: '2025-03-10',
    status: 'grace_period', dpd: 456, dpdBucket: '1_2_years',
    gracePeriodEnd: '2026-06-10', lastRepaymentDate: '2024-12-01',
    lastRepaymentAmount: 10000, sapCustomerCode: 'SAP-210019',
  },
];

export const repaymentRecords: RepaymentRecord[] = [
  {
    id: 'rep001', loanAccountId: 'ln002', receiptDate: '2026-01-10',
    amount: 50000, principalAllocation: 50000, interestAllocation: 0,
    channel: 'direct_rtgs', bankReference: 'UTR20260110001234',
    sapEntryStatus: 'posted', postedBy: 'Accounts Team',
  },
  {
    id: 'rep002', loanAccountId: 'ln003', receiptDate: '2024-12-01',
    amount: 10000, principalAllocation: 10000, interestAllocation: 0,
    channel: 'subsidiary_deduction', subsidiaryName: 'Sahyadri Farms Post Harvest Care Ltd.',
    bankReference: 'UTR20241201005678', sapEntryStatus: 'posted',
  },
];

// Alias export for Borrower360
export const repayments = repaymentRecords;

export const documents: DocumentRecord[] = [
  { id: 'd001', applicationId: 'app004', documentType: 'pan', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd002', applicationId: 'app004', documentType: 'aadhaar', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd003', applicationId: 'app004', documentType: 'share_certificate', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd004', applicationId: 'app004', documentType: 'land_712', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd005', applicationId: 'app004', documentType: 'crop_plan', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd006', applicationId: 'app004', documentType: 'bank_statement', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd007', applicationId: 'app004', documentType: 'poa', requiredFlag: 'mandatory', status: 'signed', version: 1, stampStatus: 'pending', notarisationStatus: 'pending' },
  { id: 'd008', applicationId: 'app004', documentType: 'loan_agreement', requiredFlag: 'mandatory', status: 'pending_upload', version: 1, stampStatus: 'pending', notarisationStatus: 'pending' },
  { id: 'd009', applicationId: 'app004', documentType: 'term_sheet', requiredFlag: 'mandatory', status: 'uploaded', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
  { id: 'd010', applicationId: 'app004', documentType: 'cancelled_cheque', requiredFlag: 'mandatory', status: 'verified', version: 1, stampStatus: 'not_required', notarisationStatus: 'not_required' },
];

export const securities: SecurityInstrument[] = [
  { id: 's001', applicationId: 'app004', securityType: 'sh4', status: 'held', executionDate: '2026-05-28', custodian: 'Company Secretary', stampDutyStatus: 'complete', notarisationStatus: 'not_required', invocationApprovalRequired: true, invocationStatus: 'not_initiated' },
  { id: 's002', applicationId: 'app004', securityType: 'poa', status: 'executed', executionDate: '2026-05-28', custodian: 'Company Secretary', stampDutyStatus: 'pending', notarisationStatus: 'pending', invocationApprovalRequired: true, invocationStatus: 'not_initiated' },
  { id: 's003', applicationId: 'app004', securityType: 'blank_cheque', status: 'held', executionDate: '2026-05-28', custodian: 'Company Secretary', invocationApprovalRequired: true, invocationStatus: 'not_initiated' },
  { id: 's004', applicationId: 'app005', securityType: 'cdsl_pledge', status: 'pledged', executionDate: '2026-04-22', custodian: 'Company Secretary', invocationApprovalRequired: true, invocationStatus: 'not_initiated', psnNumber: 'CDSL-2026-00234' },
];

export const auditEvents: AuditEvent[] = [
  { id: 'ae001', entityType: 'application', entityId: 'app001', eventType: 'Application Submitted', timestamp: '2026-06-10T09:30:00Z', actorName: 'Credit Assessment Team', actorRole: 'deputy_manager_finance', newState: 'submitted' },
  { id: 'ae002', entityType: 'application', entityId: 'app001', eventType: 'Reference Number Generated', timestamp: '2026-06-10T11:00:00Z', actorName: 'Priya Kulkarni', actorRole: 'deputy_manager_finance', previousState: 'submitted', newState: 'reference_generated', comment: 'Application complete. Ref LO00000042 issued.' },
  { id: 'ae003', entityType: 'application', entityId: 'app001', eventType: 'Appraisal Note Prepared', timestamp: '2026-06-11T10:00:00Z', actorName: 'Priya Kulkarni', actorRole: 'deputy_manager_finance', previousState: 'appraisal_pending', newState: 'credit_review' },
  { id: 'ae004', entityType: 'application', entityId: 'app001', eventType: 'Submitted to Sanction Committee', timestamp: '2026-06-11T15:30:00Z', actorName: 'Priya Kulkarni', actorRole: 'credit_manager', previousState: 'credit_review', newState: 'pending_sanction' },
];

export const complianceRecords: ComplianceRecord[] = [
  { id: 'c001', area: 'Producer Company Lending — Members Only', frequency: 'ongoing', owner: 'Company Secretary', lastReviewDate: '2026-06-01', nextDueDate: '2026-07-01', status: 'compliant', evidenceCount: 42 },
  { id: 'c002', area: 'Section 186 Loan Limits', frequency: 'quarterly', owner: 'CFO', lastReviewDate: '2026-04-01', nextDueDate: '2026-07-01', status: 'warning', evidenceCount: 3 },
  { id: 'c003', area: 'NBFC Principal Business Test', frequency: 'quarterly', owner: 'CFO', lastReviewDate: '2026-04-01', nextDueDate: '2026-07-01', status: 'compliant', evidenceCount: 2 },
  { id: 'c004', area: 'KYC / AML Verification', frequency: 'ongoing', owner: 'Credit Head', lastReviewDate: '2026-06-15', nextDueDate: '2026-08-15', status: 'warning', evidenceCount: 8 },
  { id: 'c005', area: 'Re-KYC (2-year cycle)', frequency: 'ongoing', owner: 'Credit Head', lastReviewDate: '2026-03-01', nextDueDate: '2026-09-01', status: 'warning', evidenceCount: 3 },
  { id: 'c006', area: 'Stamp Duty & Notarisation', frequency: 'ongoing', owner: 'Company Secretary', lastReviewDate: '2026-06-10', nextDueDate: '2026-06-25', status: 'pending', evidenceCount: 1 },
  { id: 'c007', area: 'Money-Lending Law Exemption Review', frequency: 'annual', owner: 'Company Secretary', lastReviewDate: '2026-01-15', nextDueDate: '2027-01-15', status: 'compliant', evidenceCount: 1 },
  { id: 'c008', area: 'Record Retention & Archive (8 years)', frequency: 'annual', owner: 'Company Secretary', lastReviewDate: '2026-03-31', nextDueDate: '2027-03-31', status: 'compliant', evidenceCount: 38 },
];

export const dashboardStats: DashboardStats = {
  newApplications: 3,
  pendingCompleteness: 1,
  pendingAppraisal: 2,
  pendingSanction: 1,
  documentationPending: 1,
  readyForDisbursement: 0,
  activeLoans: 8,
  overdueLoans: 3,
  totalPortfolio: 3850000,
  sectionUtilisation: 68,
  openExceptions: 1,
  reKycDue: 2,
};

