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
    draft: 'neutral', submitted: 'info', incomplete: 'pending',
    reference_generated: 'info', appraisal_pending: 'pending',
    credit_review: 'pending', pending_sanction: 'pending',
    sanctioned: 'approved', rejected_credit: 'rejected', rejected_sanction: 'rejected',
    not_started: 'neutral', in_progress: 'pending', pending_signature: 'pending',
    pending_stamp: 'pending', pending_notarisation: 'pending',
    pending_cs_review: 'pending', pending_credit_review: 'pending',
    pending_final_approval: 'pending', complete: 'approved', blocked: 'blocked',
    pending_documentation: 'pending', pending_sap_code: 'pending',
    sap_code_created: 'info', pending_bank_verification: 'pending',
    ready_for_payment: 'approved', payment_initiated: 'info',
    pending_cfc_approval: 'pending', completed: 'disbursed', failed: 'rejected',
    active: 'approved', overdue: 'blocked', grace_period: 'pending',
    extension: 'pending', default_review: 'rejected', recovery_approved: 'exception',
    recovery_in_progress: 'exception', closed: 'closed', archived: 'archived',
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
    draft: 'Draft', submitted: 'Submitted', incomplete: 'Incomplete',
    reference_generated: 'Reference Issued', appraisal_pending: 'Appraisal Pending',
    credit_review: 'Credit Review', pending_sanction: 'Pending Sanction',
    sanctioned: 'Sanctioned', rejected_credit: 'Rejected (Credit)', rejected_sanction: 'Rejected (Sanction)',
    not_started: 'Not Started', in_progress: 'In Progress', pending_signature: 'Pending Signature',
    pending_stamp: 'Pending Stamp', pending_notarisation: 'Pending Notarisation',
    pending_cs_review: 'Pending CS Review', pending_credit_review: 'Pending Credit Review',
    pending_final_approval: 'Pending Final Approval', complete: 'Complete', blocked: 'Blocked',
    pending_documentation: 'Pending Documentation', pending_sap_code: 'Pending SAP Code',
    sap_code_created: 'SAP Code Created', pending_bank_verification: 'Pending Bank Verification',
    ready_for_payment: 'Ready for Payment', payment_initiated: 'Payment Initiated',
    pending_cfc_approval: 'Pending CFC Approval', completed: 'Disbursed', failed: 'Failed',
    active: 'Active', overdue: 'Overdue', grace_period: 'Grace Period',
    extension: 'Extension Granted', default_review: 'Default Review',
    recovery_approved: 'Recovery Approved', recovery_in_progress: 'Recovery In Progress',
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
    <span className={`inline-flex items-center gap-1 font-medium rounded-full border ${styles.bg} ${styles.text} ${styles.border} ${sizeStyles[size]}`}>
      {dot ? (
        <span className={`w-1.5 h-1.5 rounded-full ${resolvedFamily === 'approved' ? 'bg-green-600' : resolvedFamily === 'rejected' || resolvedFamily === 'blocked' ? 'bg-red-500' : resolvedFamily === 'exception' ? 'bg-violet-600' : resolvedFamily === 'closed' || resolvedFamily === 'teal' ? 'bg-teal-600' : 'bg-amber-500'}`} />
      ) : icon}
      {formatStatusLabel(label)}
    </span>
  );
};

export default StatusBadge;
