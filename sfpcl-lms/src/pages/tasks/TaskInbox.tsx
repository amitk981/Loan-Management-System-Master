import React, { useState } from 'react';
import {
  Inbox, Clock, AlertTriangle, CheckCircle2, ChevronRight,
  Filter, Calendar, User, ArrowRight, Download, MoreVertical,
  MessageSquare, UserPlus, Ban, FileText
} from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole, ROLE_LABELS } from '../../contexts/RoleContext';

type TaskPriority = 'critical' | 'high' | 'normal';
type TaskType =
  | 'completeness_check' | 'appraisal' | 'sanction' | 'document_verification'
  | 'sap_setup' | 'disbursement' | 'repayment_posting' | 'default_review' | 'approval';

interface Task {
  id: string;
  type: TaskType;
  loanNo: string;
  borrower: string;
  amount: number;
  priority: TaskPriority;
  tatRemaining: string;
  status: string;
  assignedRole: string;
  assignedUser?: string;
  createdDate: string;
  dueDate: string;
  borrowerType: 'individual' | 'fpc';
  isSpecialCase: boolean;
  isException: boolean;
}

const typeLabels: Record<TaskType, string> = {
  completeness_check:  'Completeness Check',
  appraisal:           'Prepare Appraisal',
  sanction:            'Sanction Decision',
  document_verification: 'Document Verification',
  sap_setup:           'SAP Setup',
  disbursement:        'Disbursement Initiation',
  repayment_posting:   'Repayment Posting',
  default_review:      'Recovery Review',
  approval:            'Approval Required',
};

const typeColors: Record<TaskType, string> = {
  completeness_check:  'bg-blue-50 text-blue-700',
  appraisal:           'bg-amber-50 text-amber-700',
  sanction:            'bg-violet-50 text-violet-700',
  document_verification: 'bg-teal-50 text-teal-700',
  sap_setup:           'bg-slate-50 text-slate-600',
  disbursement:        'bg-green-50 text-green-700',
  repayment_posting:   'bg-indigo-50 text-indigo-700',
  default_review:      'bg-red-50 text-red-700',
  approval:            'bg-orange-50 text-orange-700',
};

const roleTaskTypes: Record<string, TaskType[]> = {
  field_officer:          ['completeness_check', 'document_verification'],
  deputy_manager_finance: ['completeness_check', 'appraisal'],
  credit_manager:         ['completeness_check', 'appraisal', 'sanction', 'default_review'],
  sanction_committee:     ['sanction', 'approval'],
  cfo:                    ['sanction', 'approval'],
  director:               ['sanction', 'approval'],
  compliance_team:        ['document_verification'],
  company_secretary:      ['document_verification'],
  senior_manager_finance: ['sap_setup', 'disbursement'],
  accounts:               ['repayment_posting'],
  sales_team_user:        ['repayment_posting'],
  cfc:                    ['sanction', 'approval', 'default_review'],
  auditor:                [], // view only
  admin:                  Object.keys(typeLabels) as TaskType[],
};

const allTasks: Task[] = [
  { id: 'T100', type: 'completeness_check', loanNo: 'APP-2026-000100', borrower: 'Ramesh Iyer', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'submitted', assignedRole: 'field_officer', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T101', type: 'document_verification', loanNo: 'LO00000101', borrower: 'Ganesh Thorat', amount: 200000, priority: 'critical', tatRemaining: 'Overdue', status: 'documentation_deficiency_raised', assignedRole: 'field_officer', assignedUser: 'Amit Kallapa', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T102', type: 'completeness_check', loanNo: 'APP-2026-000102', borrower: 'Pooja Sharma', amount: 100000, priority: 'normal', tatRemaining: '2 days', status: 'submitted', assignedRole: 'field_officer', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: false, isException: true },
  { id: 'T103', type: 'document_verification', loanNo: 'LO00000103', borrower: 'Nitin Gupta', amount: 200000, priority: 'high', tatRemaining: '4 hrs', status: 'documentation_in_progress', assignedRole: 'field_officer', assignedUser: 'Amit Kallapa', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: true },
  { id: 'T104', type: 'completeness_check', loanNo: 'APP-INT-2026-000104', borrower: 'Varsha Deshmukh', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'returned_for_rectification', assignedRole: 'field_officer', assignedUser: 'Amit Kallapa', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: false, isException: false },
  { id: 'T105', type: 'completeness_check', loanNo: 'APP-2026-000105', borrower: 'Anjali Wagh', amount: 250000, priority: 'high', tatRemaining: '4 hrs', status: 'submitted', assignedRole: 'credit_manager', assignedUser: 'Priya Kulkarni', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T106', type: 'appraisal', loanNo: 'LO00000106', borrower: 'Ramesh Kulkarni', amount: 150000, priority: 'high', tatRemaining: '4 hrs', status: 'pending_credit_manager_review', assignedRole: 'credit_manager', assignedUser: 'Priya Kulkarni', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: true },
  { id: 'T107', type: 'sanction', loanNo: 'LO00000107', borrower: 'Sunita Kamble', amount: 300000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_sanction_committee_approval', assignedRole: 'credit_manager', assignedUser: 'Priya Kulkarni', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T108', type: 'default_review', loanNo: 'LO00000108', borrower: 'Prakash Rao', amount: 100000, priority: 'normal', tatRemaining: '2 days', status: 'recovery_review', assignedRole: 'credit_manager', assignedUser: 'Priya Kulkarni', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: false },
  { id: 'T109', type: 'completeness_check', loanNo: 'APP-2026-000109', borrower: 'Kiran Pawar', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'submitted', assignedRole: 'credit_manager', assignedUser: 'Priya Kulkarni', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T110', type: 'completeness_check', loanNo: 'APP-INT-2026-000001', borrower: 'Sanjay Pawar', amount: 180000, priority: 'high', tatRemaining: '4 hrs', status: 'submitted', assignedRole: 'deputy_manager_finance', assignedUser: 'Suresh Patil', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T111', type: 'appraisal', loanNo: 'LO00000111', borrower: 'Vijay Patil', amount: 300000, priority: 'high', tatRemaining: '4 hrs', status: 'appraisal_in_progress', assignedRole: 'deputy_manager_finance', assignedUser: 'Suresh Patil', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: false },
  { id: 'T112', type: 'completeness_check', loanNo: 'APP-2026-000001', borrower: 'Nashik Grape Growers Coop', amount: 1200000, priority: 'high', tatRemaining: '4 hrs', status: 'returned_for_rectification', assignedRole: 'deputy_manager_finance', assignedUser: 'Suresh Patil', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: true, isException: true },
  { id: 'T113', type: 'appraisal', loanNo: 'LO00000113', borrower: 'Malti Shinde', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'appraisal_in_progress', assignedRole: 'deputy_manager_finance', assignedUser: 'Suresh Patil', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T114', type: 'completeness_check', loanNo: 'APP-INT-2026-000002', borrower: 'Vijay Deshmukh', amount: 250000, priority: 'high', tatRemaining: '4 hrs', status: 'deficiency_raised', assignedRole: 'deputy_manager_finance', assignedUser: 'Suresh Patil', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T115', type: 'document_verification', loanNo: 'LO00000115', borrower: 'Ramesh Iyer', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'documentation_in_progress', assignedRole: 'compliance_team', assignedUser: 'Meera Joshi', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T116', type: 'document_verification', loanNo: 'LO00000116', borrower: 'Ganesh Thorat', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'documentation_in_progress', assignedRole: 'compliance_team', assignedUser: 'Meera Joshi', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: true },
  { id: 'T117', type: 'document_verification', loanNo: 'LO00000117', borrower: 'Pooja Sharma', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'documentation_deficiency_raised', assignedRole: 'compliance_team', assignedUser: 'Meera Joshi', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: true, isException: false },
  { id: 'T118', type: 'document_verification', loanNo: 'LO00000118', borrower: 'Nitin Gupta', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_final_checklist_approvals', assignedRole: 'compliance_team', assignedUser: 'Meera Joshi', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T119', type: 'document_verification', loanNo: 'LO00000119', borrower: 'Varsha Deshmukh', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'documentation_deficiency_raised', assignedRole: 'compliance_team', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T120', type: 'document_verification', loanNo: 'LO00000120', borrower: 'Anjali Wagh', amount: 250000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_final_checklist_approvals', assignedRole: 'company_secretary', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: true },
  { id: 'T121', type: 'document_verification', loanNo: 'LO00000121', borrower: 'Ramesh Kulkarni', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'documentation_in_progress', assignedRole: 'company_secretary', assignedUser: 'Aarti Desai', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: true },
  { id: 'T122', type: 'document_verification', loanNo: 'LO00000122', borrower: 'Sunita Kamble', amount: 150000, priority: 'high', tatRemaining: '4 hrs', status: 'documentation_in_progress', assignedRole: 'company_secretary', assignedUser: 'Aarti Desai', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T123', type: 'document_verification', loanNo: 'LO00000123', borrower: 'Prakash Rao', amount: 100000, priority: 'normal', tatRemaining: '2 days', status: 'documentation_in_progress', assignedRole: 'company_secretary', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T124', type: 'document_verification', loanNo: 'LO00000124', borrower: 'Kiran Pawar', amount: 300000, priority: 'high', tatRemaining: '4 hrs', status: 'documentation_deficiency_raised', assignedRole: 'company_secretary', assignedUser: 'Aarti Desai', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: true, isException: true },
  { id: 'T125', type: 'sanction', loanNo: 'LO00000125', borrower: 'Asha Bhosale', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'pending_sanction_committee_approval', assignedRole: 'sanction_committee', assignedUser: 'Rajesh Sharma', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: true },
  { id: 'T126', type: 'approval', loanNo: 'LO00000126', borrower: 'Vijay Patil', amount: 250000, priority: 'normal', tatRemaining: '2 days', status: 'sanctioned', assignedRole: 'sanction_committee', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: false, isException: false },
  { id: 'T127', type: 'sanction', loanNo: 'LO00000127', borrower: 'Manoj Thorat', amount: 250000, priority: 'high', tatRemaining: '4 hrs', status: 'sanctioned', assignedRole: 'sanction_committee', assignedUser: 'Rajesh Sharma', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T128', type: 'approval', loanNo: 'LO00000128', borrower: 'Malti Shinde', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'sanctioned', assignedRole: 'sanction_committee', assignedUser: 'Rajesh Sharma', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T129', type: 'sanction', loanNo: 'LO00000129', borrower: 'Kavita Desai', amount: 250000, priority: 'high', tatRemaining: '4 hrs', status: 'clarification_requested', assignedRole: 'sanction_committee', assignedUser: 'Rajesh Sharma', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T130', type: 'sanction', loanNo: 'LO00000130', borrower: 'Ramesh Iyer', amount: 200000, priority: 'high', tatRemaining: '4 hrs', status: 'sanctioned', assignedRole: 'cfo', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: true },
  { id: 'T131', type: 'approval', loanNo: 'LO00000131', borrower: 'Ganesh Thorat', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'pending_sanction_committee_approval', assignedRole: 'cfo', assignedUser: 'Vikram Nair', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: false, isException: false },
  { id: 'T132', type: 'sanction', loanNo: 'LO00000132', borrower: 'Pooja Sharma', amount: 200000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_sanction_committee_approval', assignedRole: 'cfo', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T133', type: 'approval', loanNo: 'LO00000133', borrower: 'Nitin Gupta', amount: 250000, priority: 'critical', tatRemaining: 'Overdue', status: 'sanctioned', assignedRole: 'cfo', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: false },
  { id: 'T134', type: 'sanction', loanNo: 'LO00000134', borrower: 'Varsha Deshmukh', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_sanction_committee_approval', assignedRole: 'cfo', assignedUser: 'Vikram Nair', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T135', type: 'sanction', loanNo: 'LO00000135', borrower: 'Anjali Wagh', amount: 250000, priority: 'normal', tatRemaining: '2 days', status: 'clarification_requested', assignedRole: 'director', assignedUser: 'Anita Mehta', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T136', type: 'approval', loanNo: 'LO00000136', borrower: 'Ramesh Kulkarni', amount: 300000, priority: 'critical', tatRemaining: 'Overdue', status: 'sanctioned', assignedRole: 'director', assignedUser: 'Anita Mehta', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T137', type: 'sanction', loanNo: 'LO00000137', borrower: 'Sunita Kamble', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'sanctioned', assignedRole: 'director', assignedUser: 'Anita Mehta', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T138', type: 'approval', loanNo: 'LO00000138', borrower: 'Prakash Rao', amount: 200000, priority: 'high', tatRemaining: '4 hrs', status: 'pending_sanction_committee_approval', assignedRole: 'director', assignedUser: 'Anita Mehta', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T139', type: 'sanction', loanNo: 'LO00000139', borrower: 'Kiran Pawar', amount: 100000, priority: 'high', tatRemaining: '4 hrs', status: 'pending_sanction_committee_approval', assignedRole: 'director', assignedUser: 'Anita Mehta', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T140', type: 'sap_setup', loanNo: 'LO00000140', borrower: 'Asha Bhosale', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'sap_customer_code_pending', assignedRole: 'senior_manager_finance', assignedUser: 'Deepak Rao', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T141', type: 'disbursement', loanNo: 'LO00000141', borrower: 'Vijay Patil', amount: 300000, priority: 'critical', tatRemaining: 'Overdue', status: 'disbursement_ready', assignedRole: 'senior_manager_finance', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T142', type: 'sap_setup', loanNo: 'LO00000142', borrower: 'Manoj Thorat', amount: 100000, priority: 'normal', tatRemaining: '2 days', status: 'sap_customer_code_confirmed', assignedRole: 'senior_manager_finance', assignedUser: 'Deepak Rao', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T143', type: 'disbursement', loanNo: 'LO00000143', borrower: 'Malti Shinde', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'payment_initiated', assignedRole: 'senior_manager_finance', assignedUser: 'Deepak Rao', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: true },
  { id: 'T144', type: 'sap_setup', loanNo: 'LO00000144', borrower: 'Kavita Desai', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'sap_customer_code_pending', assignedRole: 'senior_manager_finance', assignedUser: 'Deepak Rao', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T145', type: 'sanction', loanNo: 'LO00000145', borrower: 'Ramesh Iyer', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'clarification_requested', assignedRole: 'cfc', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: false, isException: false },
  { id: 'T146', type: 'approval', loanNo: 'LO00000146', borrower: 'Ganesh Thorat', amount: 250000, priority: 'normal', tatRemaining: '2 days', status: 'pending_sanction_committee_approval', assignedRole: 'cfc', assignedUser: 'Santosh Kumar', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T147', type: 'default_review', loanNo: 'LO00000147', borrower: 'Pooja Sharma', amount: 250000, priority: 'critical', tatRemaining: 'Overdue', status: 'recovery_action_approved', assignedRole: 'cfc', assignedUser: 'Santosh Kumar', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T148', type: 'sanction', loanNo: 'LO00000148', borrower: 'Nitin Gupta', amount: 300000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_sanction_committee_approval', assignedRole: 'cfc', assignedUser: 'Santosh Kumar', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: true, isException: false },
  { id: 'T149', type: 'approval', loanNo: 'DR-2026-000149', borrower: 'Varsha Deshmukh', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'draft', assignedRole: 'cfc', assignedUser: 'Santosh Kumar', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T150', type: 'repayment_posting', loanNo: 'LO00000150', borrower: 'Anjali Wagh', amount: 150000, priority: 'high', tatRemaining: '4 hrs', status: 'active_repayment', assignedRole: 'accounts', assignedUser: 'Kavita More', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T151', type: 'repayment_posting', loanNo: 'LO00000151', borrower: 'Ramesh Kulkarni', amount: 250000, priority: 'critical', tatRemaining: 'Overdue', status: 'active_repayment', assignedRole: 'accounts', assignedUser: 'Kavita More', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T152', type: 'repayment_posting', loanNo: 'LO00000152', borrower: 'Sunita Kamble', amount: 200000, priority: 'normal', tatRemaining: '2 days', status: 'recovery_review', assignedRole: 'accounts', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'fpc', isSpecialCase: true, isException: false },
  { id: 'T153', type: 'repayment_posting', loanNo: 'LO00000153', borrower: 'Prakash Rao', amount: 250000, priority: 'critical', tatRemaining: 'Overdue', status: 'active_repayment', assignedRole: 'accounts', assignedUser: 'Kavita More', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T154', type: 'repayment_posting', loanNo: 'LO00000154', borrower: 'Kiran Pawar', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'active_repayment', assignedRole: 'accounts', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: true, isException: false },
  { id: 'T155', type: 'repayment_posting', loanNo: 'LO00000155', borrower: 'Asha Bhosale', amount: 300000, priority: 'normal', tatRemaining: '2 days', status: 'active_repayment', assignedRole: 'sales_team_user', assignedUser: 'Nikhil Jagtap', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T156', type: 'repayment_posting', loanNo: 'LO00000156', borrower: 'Vijay Patil', amount: 200000, priority: 'critical', tatRemaining: 'Overdue', status: 'recovery_review', assignedRole: 'sales_team_user', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T157', type: 'repayment_posting', loanNo: 'LO00000157', borrower: 'Manoj Thorat', amount: 300000, priority: 'critical', tatRemaining: 'Overdue', status: 'recovery_review', assignedRole: 'sales_team_user', assignedUser: 'Nikhil Jagtap', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T158', type: 'repayment_posting', loanNo: 'LO00000158', borrower: 'Malti Shinde', amount: 100000, priority: 'normal', tatRemaining: '2 days', status: 'recovery_review', assignedRole: 'sales_team_user', assignedUser: 'Nikhil Jagtap', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T159', type: 'repayment_posting', loanNo: 'LO00000159', borrower: 'Kavita Desai', amount: 300000, priority: 'normal', tatRemaining: '2 days', status: 'active_repayment', assignedRole: 'sales_team_user', assignedUser: 'Nikhil Jagtap', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T160', type: 'completeness_check', loanNo: 'APP-2026-000160', borrower: 'Ramesh Iyer', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'submitted', assignedRole: 'admin', assignedUser: 'Sneha Bhosale', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T161', type: 'appraisal', loanNo: 'LO00000161', borrower: 'Ganesh Thorat', amount: 150000, priority: 'critical', tatRemaining: 'Overdue', status: 'pending_credit_manager_review', assignedRole: 'admin', assignedUser: 'Sneha Bhosale', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T162', type: 'sanction', loanNo: 'LO00000162', borrower: 'Pooja Sharma', amount: 150000, priority: 'normal', tatRemaining: '2 days', status: 'pending_sanction_committee_approval', assignedRole: 'admin', assignedUser: 'Sneha Bhosale', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T163', type: 'sap_setup', loanNo: 'LO00000163', borrower: 'Nitin Gupta', amount: 100000, priority: 'critical', tatRemaining: 'Overdue', status: 'sap_customer_code_pending', assignedRole: 'admin', assignedUser: 'Sneha Bhosale', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
  { id: 'T164', type: 'completeness_check', loanNo: 'APP-INT-2026-000164', borrower: 'Varsha Deshmukh', amount: 100000, priority: 'high', tatRemaining: '4 hrs', status: 'returned_for_rectification', assignedRole: 'admin', assignedUser: 'Sneha Bhosale', createdDate: '2026-06-25', dueDate: '2026-06-28', borrowerType: 'individual', isSpecialCase: false, isException: false },
];

const priorityConfig: Record<TaskPriority, { color: string; label: string }> = {
  critical: { color: 'bg-red-100 text-red-700',    label: 'Critical' },
  high:     { color: 'bg-amber-100 text-amber-700', label: 'High' },
  normal:   { color: 'bg-slate-100 text-slate-600', label: 'Normal' },
};

const formatTaskDate = (date: string) =>
  new Date(date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });

const getTaskStatusLabel = (task: Task) => {
  if (task.type === 'completeness_check') {
    if (task.status === 'submitted') return 'pending_completeness';
    if (task.status === 'deficiency_raised' || task.status === 'returned_for_rectification' || task.status === 'incomplete') {
      return 'returned_for_rectification';
    }
  }
  if (task.type === 'appraisal') {
    if (['pending_credit_manager_review', 'credit_review', 'pending_sanction'].includes(task.status)) return 'pending_credit_manager_review';
    return 'appraisal_in_progress';
  }
  if (task.type === 'sanction' || task.type === 'approval') {
    if (['rejected_by_credit_manager', 'rejected_credit'].includes(task.status)) return 'rejected_by_credit_manager';
    if (['rejected_by_sanction_committee', 'rejected_sanction'].includes(task.status)) return 'rejected_by_sanction_committee';
    if (['clarification_requested', 'default_review'].includes(task.status)) return 'clarification_requested';
    if (['sanctioned', 'ready_for_payment', 'disbursement_ready'].includes(task.status)) return 'sanctioned';
    return 'pending_sanction_committee_approval';
  }
  if (task.type === 'document_verification') {
    if (task.status === 'ready_for_payment' || task.status === 'pending_final_checklist_approvals') return 'pending_final_checklist_approvals';
    if (task.status === 'default_review' || task.status === 'documentation_deficiency_raised') return 'documentation_deficiency_raised';
    return 'documentation_in_progress';
  }
  if (task.type === 'sap_setup') {
    if (task.status === 'sap_customer_code_confirmed') return 'sap_customer_code_confirmed';
    return 'sap_customer_code_pending';
  }
  if (task.type === 'disbursement') {
    if (['payment_authorized', 'transfer_executed', 'completed', 'disbursed'].includes(task.status)) return 'payment_authorized';
    if (task.status === 'payment_initiated' || task.status === 'pending_sanction') return 'payment_initiated';
    return 'disbursement_ready';
  }
  if (task.type === 'default_review') {
    if (task.status === 'recovery_action_approved' || task.status === 'sanctioned') return 'recovery_action_approved';
    return 'recovery_review';
  }
  if (task.type === 'repayment_posting') {
    if (task.status === 'default_review') return 'recovery_review';
    if (task.status === 'ready_for_payment' || task.status === 'pending_sanction') return 'active_repayment';
  }
  if (task.status === 'appraisal_in_progress' || task.status === 'reference_generated') return 'appraisal_in_progress';
  return task.status;
};

const getTaskStatusFamily = (task: Task) => {
  if (task.type === 'completeness_check' && task.status === 'submitted') return undefined;
  if (
    task.type === 'completeness_check' &&
    ['deficiency_raised', 'returned_for_rectification', 'incomplete'].includes(task.status)
  ) {
    return undefined;
  }
  if (task.status === 'appraisal_in_progress' || task.status === 'reference_generated') return 'pending' as const;
  if (task.type === 'document_verification' && task.status === 'default_review') return 'blocked' as const;
  if (task.type === 'sanction' || task.type === 'approval') {
    if (['rejected_by_credit_manager', 'rejected_credit', 'rejected_by_sanction_committee', 'rejected_sanction'].includes(task.status)) return 'rejected' as const;
    if (['sanctioned', 'ready_for_payment'].includes(task.status)) return 'approved' as const;
    return 'pending' as const;
  }
  if (task.type === 'sap_setup' || task.type === 'disbursement') return 'pending' as const;
  if (task.type === 'default_review') return 'exception' as const;
  return undefined;
};

const getTaskReference = (task: Task) => {
  if (task.type === 'completeness_check' && task.loanNo.startsWith('LO')) {
    const serial = task.loanNo.replace(/\D/g, '').slice(-6).padStart(6, '0');
    return `APP-2026-${serial}`;
  }
  if (task.status === 'draft' && task.loanNo.startsWith('LO')) {
    const serial = task.loanNo.replace(/\D/g, '').slice(-6).padStart(6, '0');
    return `DR-2026-${serial}`;
  }
  return task.loanNo;
};

interface TaskInboxProps {
  onNavigate?: (page: any, id?: string) => void;
}

const TaskInbox: React.FC<TaskInboxProps> = ({ onNavigate }) => {
  const { currentUser } = useRole();
  const [filter, setFilter] = useState<'all' | TaskPriority>('all');
  const [typeFilter, setTypeFilter] = useState<TaskType | 'all'>('all');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  
  // Advanced filters
  const [timeFilter, setTimeFilter] = useState<'all' | 'due_today' | 'overdue'>('all');
  const [borrowerTypeFilter, setBorrowerTypeFilter] = useState<'all' | 'individual' | 'fpc'>('all');
  const [amountFilter, setAmountFilter] = useState<'all' | 'over_5l' | 'under_5l'>('all');
  const [specialCaseFilter, setSpecialCaseFilter] = useState<'all' | 'yes'>('all');
  const [exceptionFilter, setExceptionFilter] = useState<'all' | 'yes'>('all');
  const [assignmentFilter, setAssignmentFilter] = useState<'team' | 'me'>(currentUser.role === 'credit_manager' ? 'me' : 'team');

  const myTasks = allTasks.filter(t =>
    t.assignedRole === currentUser.role ||
    currentUser.role === 'admin'
  );

  const filtered = myTasks.filter(t => {
    if (filter !== 'all' && t.priority !== filter) return false;
    if (typeFilter !== 'all' && t.type !== typeFilter) return false;
    
    if (timeFilter === 'due_today' && t.dueDate !== new Date().toISOString().split('T')[0]) return false;
    if (timeFilter === 'overdue' && t.tatRemaining !== 'Overdue') return false;
    
    if (borrowerTypeFilter !== 'all' && t.borrowerType !== borrowerTypeFilter) return false;
    if (amountFilter === 'over_5l' && t.amount <= 500000) return false;
    if (amountFilter === 'under_5l' && t.amount > 500000) return false;
    if (specialCaseFilter === 'yes' && !t.isSpecialCase) return false;
    if (exceptionFilter === 'yes' && !t.isException) return false;
    
    if (assignmentFilter === 'me' && t.assignedUser !== currentUser.name) return false;
    
    return true;
  });

  const criticalCount = myTasks.filter(t => t.priority === 'critical').length;
  const highCount     = myTasks.filter(t => t.priority === 'high').length;

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Task Inbox</h1>
          <p className="text-sm text-slate-500 mt-1">
            {currentUser.role === 'credit_manager' ? (
              <>Credit Manager work items assigned to you.</>
            ) : currentUser.role === 'deputy_manager_finance' ? (
              <>Deputy Manager – Finance work items assigned to your team.</>
            ) : (
              <>Your pending tasks for role: <span className="font-medium text-green-700">{currentUser.name}</span></>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {criticalCount > 0 && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-red-700 bg-red-100 px-3 py-1.5 rounded-full">
              <AlertTriangle size={12} />
              {criticalCount === 1 ? '1 critical' : `${criticalCount} critical`}
            </span>
          )}
          {highCount > 0 && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-amber-700 bg-amber-100 px-3 py-1.5 rounded-full">
              <Clock size={12} />
              {highCount} high priority
            </span>
          )}
          <button
            onClick={() => {
              // Mock CSV export
              alert(`Exporting ${filtered.length} tasks to CSV...`);
            }}
            className="flex items-center gap-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors ml-2"
          >
            <Download size={16} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-5 flex-wrap">
        <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-1">
          {(['all', 'critical', 'high', 'normal'] as const).map(p => (
            <button
              key={p}
              onClick={() => setFilter(p)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors capitalize ${
                filter === p ? 'bg-green-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              {p === 'all' ? 'All' : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value as TaskType | 'all')}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
        >
          <option value="all">All task types</option>
          {(roleTaskTypes[currentUser.role] || Object.keys(typeLabels) as TaskType[]).map(k => (
            <option key={k} value={k}>{typeLabels[k]}</option>
          ))}
        </select>
        
        <button
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          className={`flex items-center gap-2 text-sm px-3 py-2 border rounded-lg transition-colors ${
            showAdvancedFilters ? 'bg-slate-100 border-slate-300 text-slate-800' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          <Filter size={16} />
          Advanced Filters
        </button>
      </div>

      {showAdvancedFilters && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Assignment</label>
            <select value={assignmentFilter} onChange={e => setAssignmentFilter(e.target.value as any)} className="field-select text-sm py-1.5 w-full">
              <option value="team">Assigned to My Team</option>
              <option value="me">Assigned to Me</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Time</label>
            <select value={timeFilter} onChange={e => setTimeFilter(e.target.value as any)} className="field-select text-sm py-1.5 w-full">
              <option value="all">Any time</option>
              <option value="due_today">Due Today</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Borrower Type</label>
            <select value={borrowerTypeFilter} onChange={e => setBorrowerTypeFilter(e.target.value as any)} className="field-select text-sm py-1.5 w-full">
              <option value="all">Any type</option>
              <option value="individual">Individual</option>
              <option value="fpc">FPC</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Amount Threshold</label>
            <select value={amountFilter} onChange={e => setAmountFilter(e.target.value as any)} className="field-select text-sm py-1.5 w-full">
              <option value="all">Any amount</option>
              <option value="over_5l">&gt; ₹5 Lakhs</option>
              <option value="under_5l">&le; ₹5 Lakhs</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">Flags</label>
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input type="checkbox" checked={specialCaseFilter === 'yes'} onChange={e => setSpecialCaseFilter(e.target.checked ? 'yes' : 'all')} className="w-4 h-4 rounded text-green-600 focus:ring-green-500" />
                Special Cases only
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input type="checkbox" checked={exceptionFilter === 'yes'} onChange={e => setExceptionFilter(e.target.checked ? 'yes' : 'all')} className="w-4 h-4 rounded text-green-600 focus:ring-green-500" />
                Exceptions only
              </label>
            </div>
          </div>
        </div>
      )}

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-center">
          <CheckCircle2 size={40} className="text-green-400 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">All clear!</h2>
          <p className="text-sm text-slate-400">No pending tasks for your role.</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="px-6 py-3 border-b border-slate-100 bg-slate-50 flex items-center gap-2 text-xs font-semibold text-slate-500">
            <Inbox size={14} />
            {filtered.length} pending task{filtered.length !== 1 ? 's' : ''}
          </div>
          <div className="divide-y divide-slate-50 overflow-x-auto">
            {filtered.map(task => (
              <div
                key={task.id}
                className={`px-6 py-4 min-w-[1290px] grid grid-cols-[4px_160px_minmax(390px,1fr)_360px_100px_96px_118px] items-center gap-4 hover:bg-slate-50 transition-colors ${
                  task.priority === 'critical' ? 'bg-red-50/30' : ''
                }`}
              >
                {/* Priority indicator */}
                <div className={`w-1 h-12 rounded-full ${
                  task.priority === 'critical' ? 'bg-red-500' :
                  task.priority === 'high'     ? 'bg-amber-400' :
                  'bg-slate-200'
                }`} />

                {/* Task type chip */}
                <div className="min-w-0">
                  <span className={`text-xs font-medium px-2 py-1 rounded-lg ${typeColors[task.type]}`}>
                    {task.type === 'default_review' && currentUser.role === 'credit_manager' ? 'Recovery follow-up' : typeLabels[task.type]}
                  </span>
                </div>

                {/* Details */}
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm text-slate-600 whitespace-nowrap">{getTaskReference(task)}</span>
                    <span className="text-slate-400">·</span>
                    <span className="text-sm font-medium text-slate-900 truncate">{task.borrower}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-slate-500 min-w-0">
                    <span className="whitespace-nowrap">₹{(task.amount / 100000).toFixed(1)}L</span>
                    <span className="whitespace-nowrap">Created {formatTaskDate(task.createdDate)}</span>
                    <span className="flex items-center gap-1 whitespace-nowrap"><Calendar size={12}/> Due {formatTaskDate(task.dueDate)}</span>
                    {assignmentFilter === 'team' && (
                      <span className="flex items-center gap-1 min-w-0">
                        <User size={12} className="flex-shrink-0"/>
                        <span className="truncate">{task.assignedUser ? `Assigned: ${task.assignedUser}` : currentUser.role === 'deputy_manager_finance' ? `Owner role: ${ROLE_LABELS[task.assignedRole as keyof typeof ROLE_LABELS] || task.assignedRole}` : task.assignedRole.replace(/_/g, ' ')}</span>
                      </span>
                    )}
                  </div>
                </div>

                <div className="min-w-0">
                  <StatusBadge label={getTaskStatusLabel(task)} family={getTaskStatusFamily(task)} size="sm" />
                </div>

                {/* TAT */}
                <div className="text-right">
                  <div className={`text-sm font-semibold flex justify-end ${
                    task.tatRemaining === 'Overdue' ? 'text-red-600' :
                    task.tatRemaining.includes('hrs') ? 'text-amber-600' :
                    'text-slate-700'
                  }`}>
                    {task.tatRemaining === 'Overdue' ? (
                      <span className="flex items-center gap-1"><AlertTriangle size={12} />Overdue</span>
                    ) : task.tatRemaining}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    {task.tatRemaining === 'Overdue' ? 'TAT breached' : 'TAT remaining'}
                  </div>
                </div>

                {/* Priority */}
                <div>
                  <span className={`text-xs px-2 py-1 rounded-full font-semibold ${priorityConfig[task.priority].color}`}>
                    {priorityConfig[task.priority].label}
                  </span>
                </div>

                {/* Action */}
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => {
                      if (!onNavigate) return;
                      const map: Record<TaskType, string> = {
                        completeness_check: 'completeness',
                        appraisal: 'appraisal',
                        sanction: 'sanction',
                        document_verification: 'documentation',
                        sap_setup: 'disbursement',
                        disbursement: 'disbursement',
                        repayment_posting: 'repayments',
                        default_review: 'defaults',
                        approval: 'sanction',
                      };
                      onNavigate(map[task.type], getTaskReference(task));
                    }}
                    className="flex items-center gap-1 bg-green-600 hover:bg-green-700 text-white text-xs font-medium px-3 py-2 rounded-lg transition-colors"
                  >
                    {currentUser.role === 'credit_manager' ? 'Review' 
                     : (currentUser.role === 'deputy_manager_finance' && task.type === 'completeness_check') ? 'Review'
                     : (currentUser.role === 'deputy_manager_finance' && task.type === 'appraisal') ? 'Prepare'
                     : 'Open'} <ArrowRight size={12} />
                  </button>
                  <div className="relative">
                    <button
                      onClick={() => setActiveMenu(activeMenu === task.id ? null : task.id)}
                      className="p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 rounded-lg transition-colors"
                    >
                      <MoreVertical size={16} />
                    </button>
                    {activeMenu === task.id && (
                      <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-slate-200 rounded-xl shadow-lg z-10 py-1">
                        {currentUser.role === 'credit_manager' ? (
                          <>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                              <MessageSquare size={14} /> Add follow-up note
                            </button>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                              <FileText size={14} /> Prepare note
                            </button>
                            <div className="border-t border-slate-100 my-1"></div>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-green-600 hover:bg-green-50 transition-colors">
                              <ArrowRight size={14} /> Route for approval
                            </button>
                          </>
                        ) : currentUser.role === 'deputy_manager_finance' ? (
                          <>
                            {task.type === 'completeness_check' ? (
                              <>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                                  <FileText size={14} /> Review completeness
                                </button>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-amber-600 hover:bg-amber-50 transition-colors">
                                  <AlertTriangle size={14} /> Mark deficiency
                                </button>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                                  <MessageSquare size={14} /> Request documents
                                </button>
                                <div className="border-t border-slate-100 my-1"></div>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-green-600 hover:bg-green-50 transition-colors">
                                  <ArrowRight size={14} /> Submit for appraisal
                                </button>
                              </>
                            ) : (
                              <>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                                  <FileText size={14} /> Prepare appraisal
                                </button>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                                  <Inbox size={14} /> Save draft
                                </button>
                                <div className="border-t border-slate-100 my-1"></div>
                                <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-green-600 hover:bg-green-50 transition-colors">
                                  <ArrowRight size={14} /> Submit to Credit Manager
                                </button>
                              </>
                            )}
                          </>
                        ) : (
                          <>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                              <UserPlus size={14} /> Reassign Task
                            </button>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                              <MessageSquare size={14} /> Add Comment
                            </button>
                            <div className="border-t border-slate-100 my-1"></div>
                            <button className="w-full flex items-center gap-2 px-3 py-2 text-xs text-red-600 hover:bg-red-50 transition-colors">
                              <Ban size={14} /> Mark Blocked
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>

              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskInbox;
