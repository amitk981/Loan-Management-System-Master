import type { LoanApplication } from '../types';

const PRE_REFERENCE_STATUSES = new Set([
  'draft',
  'submitted',
  'completeness_check',
  'incomplete',
  'deficiency_raised',
  'returned_for_rectification',
  'rejected_completeness',
]);

export const hasFormalLoanReference = (app: LoanApplication) =>
  !PRE_REFERENCE_STATUSES.has(app.status);

export const getApplicationReference = (app: LoanApplication) =>
  hasFormalLoanReference(app)
    ? app.officialReference || app.applicationNumber
    : app.intakeReference || app.applicationNumber;

export const getApplicationStatusLabel = (app: LoanApplication) => {
  if (app.status === 'draft') {
    return app.source === 'assisted_entry' ? 'Internal Draft / Assisted Draft' : 'Draft';
  }
  if (app.status === 'submitted') {
    return 'Pending Completeness';
  }
  if (app.status === 'completeness_check') {
    return 'Pending Completeness';
  }
  if (app.status === 'deficiency_raised' || app.status === 'returned_for_rectification' || app.status === 'incomplete') {
    return 'Returned for Rectification';
  }
  if (app.status === 'rejected_completeness') {
    return 'Rejected at Completeness';
  }
  if (app.status === 'reference_generated') {
    return 'Reference Generated';
  }
  if (app.status === 'appraisal_in_progress') {
    return 'Appraisal In Progress';
  }
  const labels: Record<string, string> = {
    appraisal_pending: 'Appraisal Pending',
    pending_credit_manager_review: 'Pending Credit Manager Review',
    credit_review: 'Pending Credit Manager Review',
    pending_sanction_committee_approval: 'Pending Sanction Committee Approval',
    pending_sanction: 'Pending Sanction Committee Approval',
    rejected_by_credit_manager: 'Rejected by Credit Manager',
    rejected_credit: 'Rejected by Credit Manager',
    under_sanction_review: 'Under Sanction Review',
    clarification_requested: 'Clarification Requested',
    rejected_by_sanction_committee: 'Rejected by Sanction Committee',
    rejected_sanction: 'Rejected by Sanction Committee',
    sanctioned: 'Sanctioned',
    documentation_in_progress: 'Documentation In Progress',
    documentation_deficiency_raised: 'Documentation Deficiency Raised',
    pending_final_checklist_approvals: 'Pending Final Checklist Approvals',
    disbursement_ready: 'Disbursement Ready',
    sap_customer_code_pending: 'SAP Customer Code Pending',
    sap_customer_code_confirmed: 'SAP Customer Code Confirmed',
    payment_initiated: 'Payment Initiated',
    payment_authorized: 'Payment Authorized',
    transfer_executed: 'Transfer Executed',
    disbursed: 'Disbursed',
  };
  if (labels[app.status]) return labels[app.status];
  return app.status;
};

export const getBackendStatusLabel = (app: LoanApplication) => {
  if (app.status === 'draft' && app.source === 'assisted_entry') return 'Draft with source = assisted_entry';
  if (app.status === 'submitted' && app.source === 'assisted_entry') return 'Submitted with source = assisted_entry';
  if (app.status === 'appraisal_in_progress') return 'Appraisal_In_Progress';
  if (app.status === 'pending_credit_manager_review') return 'Pending_Credit_Manager_Review';
  if (app.status === 'pending_sanction_committee_approval') return 'Pending_Sanction_Committee_Approval';
  if (app.status === 'rejected_by_credit_manager') return 'Rejected_By_Credit_Manager';
  if (app.status === 'under_sanction_review') return 'Under_Sanction_Review';
  if (app.status === 'clarification_requested') return 'Clarification_Requested';
  if (app.status === 'rejected_by_sanction_committee') return 'Rejected_By_Sanction_Committee';
  if (app.status === 'returned_for_rectification') return 'Returned_For_Rectification';
  return app.status
    .split('_')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join('_');
};
