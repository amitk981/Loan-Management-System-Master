import type { User, Permission } from '../contexts/RoleContext';
import { ROLE_LABELS } from '../contexts/RoleContext';
import type { Role } from '../types';


const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  field_officer: ['view_applications', 'create_application', 'edit_application', 'view_members'],
  deputy_manager_finance: [
    'view_applications', 'create_application', 'edit_application', 'view_members',
    'do_appraisal', 'do_completeness_check', 'view_documentation',
  ],
  credit_manager: [
    'view_applications', 'create_application', 'edit_application', 'view_members',
    'edit_members', 'do_appraisal', 'do_completeness_check', 'view_sanction',
    'view_documentation', 'approve_credit_checklist', 'view_loan_accounts',
    'view_monitoring', 'manage_defaults', 'view_registers', 'export_registers',
    'view_reports', 'view_audit',
  ],
  compliance_team: [
    'view_applications', 'view_members', 'view_documentation', 'manage_documentation',
    'view_compliance', 'manage_compliance', 'view_registers', 'view_audit',
  ],
  company_secretary: [
    'view_applications', 'view_members', 'view_documentation', 'manage_documentation',
    'view_compliance', 'manage_compliance', 'view_registers', 'export_registers',
    'view_audit', 'manage_closure',
  ],
  sanction_committee: [
    'view_applications', 'view_members', 'view_sanction', 'approve_sanction',
    'reject_sanction', 'view_documentation', 'view_registers', 'view_audit',
    'approve_recovery', 'manage_defaults',
  ],
  cfo: [
    'view_applications', 'view_members', 'view_sanction', 'approve_sanction',
    'reject_sanction', 'view_documentation', 'view_loan_accounts', 'view_monitoring',
    'manage_defaults', 'approve_recovery', 'view_compliance', 'view_registers',
    'export_registers', 'view_reports', 'view_audit', 'view_settings',
    'manage_interest', 'manage_closure',
  ],
  director: [
    'view_applications', 'view_members', 'view_sanction', 'approve_sanction',
    'reject_sanction', 'view_documentation', 'view_registers', 'view_audit',
    'approve_recovery', 'manage_defaults',
  ],
  senior_manager_finance: [
    'view_applications', 'view_members', 'view_documentation', 'view_loan_accounts',
    'initiate_disbursement', 'view_registers', 'view_audit',
  ],
  cfc: [
    'view_applications', 'view_loan_accounts', 'authorise_disbursement',
    'view_registers', 'view_audit',
  ],
  accounts: [
    'view_applications', 'view_members', 'view_loan_accounts', 'post_repayment',
    'view_monitoring', 'manage_interest', 'view_registers', 'export_registers',
    'view_reports',
  ],
  sales_team_user: [
    'view_applications', 'view_members', 'view_loan_accounts', 'manage_interest',
    'view_registers', 'view_reports',
  ],
  auditor: [
    'view_applications', 'view_members', 'view_sanction', 'view_documentation',
    'view_loan_accounts', 'view_monitoring', 'view_compliance', 'view_registers',
    'view_reports', 'view_audit',
  ],
  admin: ['view_settings', 'manage_settings', 'manage_users'],
  borrower: ['view_own_loan'],
  backend_staff: [],
};

const makeDemoUser = (
  user: Omit<
    User,
    'roleName' | 'roleCodes' | 'teamCodes' | 'permissions'
    | 'availableActions' | 'prototypePermissions'
  >,
): User => ({
  ...user,
  roleName: ROLE_LABELS[user.role],
  teamName: user.team,
  roleCodes: [user.role],
  teamCodes: user.team ? [user.team] : [],
  permissions: [],
  availableActions: [],
  prototypePermissions: ROLE_PERMISSIONS[user.role] ?? [],
  isBackendSession: false,
});

export const ROLE_USERS: Record<Role, User> = {
  field_officer: makeDemoUser({ id: 'u00', name: 'Amit Kallapa', email: 'amit.kallapa@sfpcl.in', role: 'field_officer', team: 'field_intake' }),
  credit_manager: makeDemoUser({ id: 'u01', name: 'Priya Kulkarni', email: 'priya.kulkarni@sfpcl.in', role: 'credit_manager', team: 'credit_assessment' }),
  deputy_manager_finance: makeDemoUser({ id: 'u02', name: 'Suresh Patil', email: 'suresh.patil@sfpcl.in', role: 'deputy_manager_finance', team: 'credit_assessment' }),
  compliance_team: makeDemoUser({ id: 'u03', name: 'Meera Joshi', email: 'meera.joshi@sfpcl.in', role: 'compliance_team', team: 'compliance' }),
  company_secretary: makeDemoUser({ id: 'u04', name: 'Aarti Desai', email: 'aarti.desai@sfpcl.in', role: 'company_secretary', team: 'secretarial' }),
  sanction_committee: makeDemoUser({ id: 'u05', name: 'Rajesh Sharma', email: 'rajesh.sharma@sfpcl.in', role: 'sanction_committee', team: 'sanction' }),
  cfo: makeDemoUser({ id: 'u06', name: 'Vikram Nair', email: 'vikram.nair@sfpcl.in', role: 'cfo', team: 'executive' }),
  director: makeDemoUser({ id: 'u07', name: 'Anita Mehta', email: 'anita.mehta@sfpcl.in', role: 'director', team: 'board' }),
  senior_manager_finance: makeDemoUser({ id: 'u08', name: 'Deepak Rao', email: 'deepak.rao@sfpcl.in', role: 'senior_manager_finance', team: 'finance' }),
  cfc: makeDemoUser({ id: 'u09', name: 'Santosh Kumar', email: 'santosh.kumar@sfpcl.in', role: 'cfc', team: 'finance' }),
  accounts: makeDemoUser({ id: 'u10', name: 'Kavita More', email: 'kavita.more@sfpcl.in', role: 'accounts', team: 'accounts' }),
  sales_team_user: makeDemoUser({ id: 'u13', name: 'Nikhil Jagtap', email: 'nikhil.jagtap@sfpcl.in', role: 'sales_team_user', team: 'sales' }),
  auditor: makeDemoUser({ id: 'u11', name: 'Ramesh Iyer', email: 'ramesh.iyer@sfpcl.in', role: 'auditor', team: 'audit' }),
  admin: makeDemoUser({ id: 'u12', name: 'Sneha Bhosale', email: 'sneha.bhosale@sfpcl.in', role: 'admin', team: 'it' }),
  borrower: makeDemoUser({ id: 'b01', name: 'Ganesh Thorat', email: 'ganesh.thorat@sfpcl.in', role: 'borrower' }),
  backend_staff: makeDemoUser({ id: 'u14', name: 'Backend Staff', email: 'backend.staff@sfpcl.in', role: 'backend_staff' }),
};

export const DEMO_ROLE_OPTIONS: { role: Role; group: string }[] = [
  { role: 'field_officer', group: 'Intake' },
  { role: 'credit_manager', group: 'Credit Assessment' },
  { role: 'deputy_manager_finance', group: 'Credit Assessment' },
  { role: 'compliance_team', group: 'Compliance' },
  { role: 'company_secretary', group: 'Compliance' },
  { role: 'sanction_committee', group: 'Sanction' },
  { role: 'cfo', group: 'Sanction' },
  { role: 'director', group: 'Sanction' },
  { role: 'senior_manager_finance', group: 'Finance' },
  { role: 'cfc', group: 'Finance' },
  { role: 'accounts', group: 'Finance' },
  { role: 'sales_team_user', group: 'Sales' },
  { role: 'auditor', group: 'Audit' },
  { role: 'admin', group: 'IT' },
];

export const STAFF_DEMO_ROLES = DEMO_ROLE_OPTIONS.map(option => option.role);
