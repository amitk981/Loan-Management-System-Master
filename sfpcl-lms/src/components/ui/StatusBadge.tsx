import React from 'react';
import {
  CheckCircle2, XCircle, Clock, AlertTriangle, AlertOctagon,
  Inbox, Banknote, Archive, BadgeCheck, Circle
} from 'lucide-react';

type Family = 'neutral' | 'info' | 'pending' | 'approved' | 'rejected' |
  'blocked' | 'exception' | 'disbursed' | 'closed' | 'archived' | 'teal';

interface StatusBadgeProps {
  label: string;
  family?: Family;
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  /** Legacy hint used by some callers; styling is derived from `family` or `label`. */
  type?: string;
}

const familyStyles: Record<Family, { bg: string; text: string; border: string }> = {
  neutral:   { bg: 'bg-slate-100',   text: 'text-slate-700',  border: 'border-slate-200' },
  info:      { bg: 'bg-blue-50',     text: 'text-blue-900',   border: 'border-blue-100' },
  pending:   { bg: 'bg-amber-50',    text: 'text-amber-900',  border: 'border-amber-100' },
  approved:  { bg: 'bg-green-50',    text: 'text-green-900',  border: 'border-green-100' },
  rejected:  { bg: 'bg-red-50',      text: 'text-red-900',    border: 'border-red-100' },
  blocked:   { bg: 'bg-red-50',      text: 'text-red-900',    border: 'border-red-200' },
  exception: { bg: 'bg-violet-50',   text: 'text-violet-800', border: 'border-violet-100' },
  disbursed: { bg: 'bg-green-50',    text: 'text-green-900',  border: 'border-green-200' },
  closed:    { bg: 'bg-teal-50',     text: 'text-teal-700',   border: 'border-teal-100' },
  archived:  { bg: 'bg-slate-100',   text: 'text-slate-600',  border: 'border-slate-300' },
  teal:      { bg: 'bg-teal-50',     text: 'text-teal-700',   border: 'border-teal-100' },
};

const familyIcons: Record<Family, React.ReactNode> = {
  neutral:   <Circle size={10} />,
  info:      <Inbox size={10} />,
  pending:   <Clock size={10} />,
  approved:  <CheckCircle2 size={10} />,
  rejected:  <XCircle size={10} />,
  blocked:   <AlertTriangle size={10} />,
  exception: <AlertOctagon size={10} />,
  disbursed: <Banknote size={10} />,
  closed:    <BadgeCheck size={10} />,
  archived:  <Archive size={10} />,
  teal:      <BadgeCheck size={10} />,
};

const sizeStyles = {
  sm: 'text-xs px-2 py-0.5 h-5',
  md: 'text-xs px-2.5 py-1 h-6',
  lg: 'text-sm px-3 py-1.5 h-8',
};

export const getStatusFamily = (status: string): Family => {
  const map: Record<string, Family> = {
    draft: 'neutral', submitted: 'info', incomplete: 'pending', completeness_check: 'info',
    pending_completeness: 'info', submitted_by_internal_team: 'info',
    reference_generated: 'info', appraisal_in_progress: 'pending', appraisal_pending: 'pending',
    'application_complete_/_appraisal_in_progress': 'pending',
    pending_credit_manager_review: 'pending', credit_review: 'pending',
    pending_sanction_committee_approval: 'pending', pending_sanction: 'pending',
    under_sanction_review: 'pending', clarification_requested: 'pending',
    sanctioned: 'approved',
    rejected_by_credit_manager: 'rejected', rejected_credit: 'rejected',
    rejected_by_sanction_committee: 'rejected', rejected_sanction: 'rejected',
    rejected_completeness: 'rejected', returned_for_rectification: 'blocked',
    'deficiency_raised_/_returned_for_rectification': 'blocked',
    not_started: 'neutral', in_progress: 'pending', pending_signature: 'pending',
    pending_stamp: 'pending', pending_notarisation: 'pending',
    pending_cs_review: 'pending', pending_credit_review: 'pending',
    pending_final_approval: 'pending',
    documentation_in_progress: 'pending', documentation_deficiency_raised: 'blocked',
    pending_final_checklist_approvals: 'pending',
    complete: 'approved', blocked: 'blocked',
    pending_documentation: 'pending', pending_sap_code: 'pending',
    sap_code_created: 'info', pending_bank_verification: 'pending',
    ready_for_payment: 'approved', pending_disbursement: 'pending',
    disbursement_ready: 'approved', sap_customer_code_pending: 'pending',
    sap_customer_code_confirmed: 'info', payment_initiated: 'info',
    pending_cfc_approval: 'info', payment_authorized: 'approved',
    payment_authorization_pending: 'pending', payment_authorisation_pending: 'pending',
    transfer_executed: 'disbursed', completed: 'disbursed', disbursed: 'disbursed',
    failed: 'rejected',
    active: 'approved', active_repayment: 'approved', overdue: 'blocked', grace_period: 'pending',
    extension: 'pending', extended: 'pending', default_review: 'rejected', recovery_review: 'rejected',
    recovery_approved: 'exception', recovery_action_approved: 'exception',
    recovery_in_progress: 'exception', recovered: 'teal', closure_review: 'pending',
    closed: 'closed', archived: 'archived',
    deficiency_raised: 'blocked',
    no_default: 'approved', past_default: 'pending', current_default: 'rejected',
    verified: 'approved', pending_upload: 'pending', under_review: 'pending',
    uploaded: 'info', signed: 'info', stamped: 'info', notarised: 'approved',
    not_required: 'neutral', held: 'info', pledged: 'approved', invoked: 'rejected',
    released: 'teal', returned: 'teal', executed: 'approved',
    compliant: 'approved', warning: 'pending', breach: 'rejected',
    low: 'approved', medium: 'pending', high: 'rejected',
    active_member: 'approved', inactive_member: 'rejected', rekyc_due: 'pending', expired: 'rejected',
  };
  return map[status] || 'neutral';
};

export const formatStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    draft: 'Draft', submitted: 'Submitted - Pending Completeness Check',
    pending_completeness: 'Pending Completeness',
    submitted_by_internal_team: 'Submitted by Internal Team - Pending Completeness Check',
    completeness_check: 'Under Completeness Check',
    incomplete: 'Returned for Rectification', deficiency_raised: 'Deficiency Raised',
    returned_for_rectification: 'Returned for Rectification',
    'deficiency_raised_/_returned_for_rectification': 'Deficiency Raised / Returned for Rectification',
    reference_generated: 'Reference Generated',
    appraisal_in_progress: 'Appraisal In Progress',
    'application_complete_/_appraisal_in_progress': 'Appraisal In Progress',
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
    rejected_completeness: 'Rejected at Completeness',
    not_started: 'Not Started', in_progress: 'In Progress', pending_signature: 'Signature pending',
    pending_stamp: 'Pending Stamp', pending_notarisation: 'Pending Notarisation',
    pending_cs_review: 'Pending CS Review', pending_credit_review: 'Pending Credit Review',
    pending_final_approval: 'Pending Final Approval',
    documentation_in_progress: 'Documentation In Progress',
    documentation_deficiency_raised: 'Documentation Deficiency Raised',
    pending_final_checklist_approvals: 'Pending Final Checklist Approvals',
    complete: 'Complete', blocked: 'Blocked',
    pending_documentation: 'Pending Documentation', pending_sap_code: 'SAP Customer Code Pending',
    sap_code_created: 'SAP Customer Code Confirmed', pending_bank_verification: 'SAP Customer Code Confirmed',
    ready_for_payment: 'Disbursement Ready', pending_disbursement: 'Disbursement Ready',
    disbursement_ready: 'Disbursement Ready',
    sap_customer_code_pending: 'SAP Customer Code Pending',
    sap_customer_code_confirmed: 'SAP Customer Code Confirmed',
    payment_initiated: 'Payment Initiated',
    pending_cfc_approval: 'Payment Initiated',
    payment_authorization_pending: 'Payment Initiated',
    payment_authorisation_pending: 'Payment Initiated',
    payment_authorized: 'Payment Authorized',
    transfer_executed: 'Transfer Executed',
    completed: 'Disbursed', disbursed: 'Disbursed', failed: 'Failed',
    active: 'Active Repayment', active_repayment: 'Active Repayment',
    overdue: 'Overdue', grace_period: 'Grace Period',
    extension: 'Extension Granted', extended: 'Extension Granted',
    default_review: 'Recovery Review', recovery_review: 'Recovery Review',
    recovery_approved: 'Recovery Action Approved',
    recovery_action_approved: 'Recovery Action Approved',
    recovery_in_progress: 'Recovery In Progress',
    recovered: 'Recovered', closure_review: 'Closure Review',
    closed: 'Closed', archived: 'Archived',
    no_default: 'No Default', past_default: 'Past Default', current_default: 'Current Default',
    verified: 'Verified', pending_upload: 'Pending Upload', under_review: 'Under Review',
    uploaded: 'Uploaded', signed: 'Signed', stamped: 'Stamped', notarised: 'Notarised',
    held: 'Held in Custody', pledged: 'Pledged', invoked: 'Invoked',
    released: 'Released', returned: 'Returned', executed: 'Executed',
    compliant: 'Compliant', warning: 'Warning', breach: 'Breach',
    low: 'Low Risk', medium: 'Medium Risk', high: 'High Risk',
    individual: 'Individual Farmer', fpc: 'FPC', producer_institution: 'Producer Institution',
    short_term: 'Short-term (1 yr)', long_term: 'Long-term',
    physical: 'Physical Shares', demat: 'Demat Shares',
    rekyc_due: 'Re-KYC Due', expired: 'KYC Expired',
    active_member: 'Active Member', inactive_member: 'Inactive',
  };
  return labels[status] || status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const StatusBadge: React.FC<StatusBadgeProps> = ({ label, family, size = 'md', dot = false }) => {
  const resolvedFamily = family || getStatusFamily(label.toLowerCase().replace(/\s+/g, '_'));
  const styles = familyStyles[resolvedFamily];
  const icon = familyIcons[resolvedFamily];

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-full border whitespace-nowrap ${styles.bg} ${styles.text} ${styles.border} ${sizeStyles[size]}`}>
      {dot ? (
        <span className={`w-1.5 h-1.5 rounded-full ${resolvedFamily === 'approved' ? 'bg-green-600' : resolvedFamily === 'rejected' || resolvedFamily === 'blocked' ? 'bg-red-500' : resolvedFamily === 'exception' ? 'bg-violet-600' : resolvedFamily === 'closed' || resolvedFamily === 'teal' ? 'bg-teal-600' : 'bg-amber-500'}`} />
      ) : icon}
      {formatStatusLabel(label)}
    </span>
  );
};

export default StatusBadge;
