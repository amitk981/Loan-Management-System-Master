import React, { createContext, useContext, useState } from 'react';
import { Role } from '../types';

interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  team?: string;
}

const ROLE_USERS: Record<Role, User> = {
  credit_manager:         { id: 'u01', name: 'Priya Kulkarni',   email: 'priya.kulkarni@sfpcl.in',  role: 'credit_manager',        team: 'credit_assessment' },
  deputy_manager_finance: { id: 'u02', name: 'Suresh Patil',     email: 'suresh.patil@sfpcl.in',    role: 'deputy_manager_finance', team: 'credit_assessment' },
  compliance_team:        { id: 'u03', name: 'Meera Joshi',      email: 'meera.joshi@sfpcl.in',     role: 'compliance_team',        team: 'compliance' },
  company_secretary:      { id: 'u04', name: 'Aarti Desai',      email: 'aarti.desai@sfpcl.in',     role: 'company_secretary',      team: 'secretarial' },
  sanction_committee:     { id: 'u05', name: 'Rajesh Sharma',    email: 'rajesh.sharma@sfpcl.in',   role: 'sanction_committee',     team: 'sanction' },
  cfo:                    { id: 'u06', name: 'Vikram Nair',       email: 'vikram.nair@sfpcl.in',     role: 'cfo',                    team: 'executive' },
  director:               { id: 'u07', name: 'Anita Mehta',      email: 'anita.mehta@sfpcl.in',     role: 'director',               team: 'board' },
  senior_manager_finance: { id: 'u08', name: 'Deepak Rao',       email: 'deepak.rao@sfpcl.in',      role: 'senior_manager_finance', team: 'finance' },
  cfc:                    { id: 'u09', name: 'Santosh Kumar',     email: 'santosh.kumar@sfpcl.in',   role: 'cfc',                    team: 'finance' },
  accounts:               { id: 'u10', name: 'Kavita More',       email: 'kavita.more@sfpcl.in',     role: 'accounts',               team: 'accounts' },
  auditor:                { id: 'u11', name: 'Ramesh Iyer',       email: 'ramesh.iyer@sfpcl.in',     role: 'auditor',                team: 'audit' },
  admin:                  { id: 'u12', name: 'Sneha Bhosale',     email: 'sneha.bhosale@sfpcl.in',   role: 'admin',                  team: 'it' },
  borrower:               { id: 'b01', name: 'Ganesh Thorat',     email: 'ganesh.thorat@sfpcl.in',   role: 'borrower' },
};

export const ROLE_LABELS: Record<Role, string> = {
  credit_manager:         'Credit Manager',
  deputy_manager_finance: 'Deputy Manager – Finance',
  compliance_team:        'Compliance Team',
  company_secretary:      'Company Secretary',
  sanction_committee:     'Sanction Committee',
  cfo:                    'CFO',
  director:               'Director',
  senior_manager_finance: 'Senior Manager – Finance',
  cfc:                    'Chief Financial Controller',
  accounts:               'Accounts',
  auditor:                'Auditor',
  admin:                  'Administrator',
  borrower:               'Borrower / Member',
};

interface RoleContextValue {
  currentUser: User;
  setRole: (role: Role) => void;
  can: (permission: Permission) => boolean;
}

export type Permission =
  | 'view_applications' | 'create_application' | 'edit_application'
  | 'view_members' | 'edit_members'
  | 'do_appraisal' | 'do_completeness_check'
  | 'view_sanction' | 'approve_sanction' | 'reject_sanction'
  | 'view_documentation' | 'manage_documentation'
  | 'initiate_disbursement' | 'authorise_disbursement'
  | 'view_loan_accounts' | 'post_repayment'
  | 'view_monitoring' | 'manage_defaults' | 'approve_recovery'
  | 'view_compliance' | 'manage_compliance'
  | 'view_registers' | 'export_registers'
  | 'view_reports' | 'view_settings' | 'manage_settings'
  | 'view_audit' | 'manage_users'
  | 'view_own_loan';

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  deputy_manager_finance: [
    'view_applications', 'create_application', 'edit_application',
    'view_members', 'do_appraisal', 'do_completeness_check',
    'view_documentation', 'view_loan_accounts', 'view_registers',
  ],
  credit_manager: [
    'view_applications', 'create_application', 'edit_application',
    'view_members', 'edit_members', 'do_appraisal', 'do_completeness_check',
    'view_sanction', 'view_documentation', 'manage_documentation',
    'view_loan_accounts', 'post_repayment',
    'view_monitoring', 'manage_defaults',
    'view_compliance', 'view_registers', 'export_registers',
    'view_reports', 'view_audit',
  ],
  compliance_team: [
    'view_applications', 'view_members',
    'view_documentation', 'manage_documentation',
    'view_compliance', 'manage_compliance',
    'view_registers', 'view_audit',
  ],
  company_secretary: [
    'view_applications', 'view_members',
    'view_documentation', 'manage_documentation',
    'view_compliance', 'manage_compliance',
    'view_registers', 'export_registers',
    'view_audit',
  ],
  sanction_committee: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_registers', 'view_audit',
  ],
  cfo: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_loan_accounts',
    'view_monitoring', 'manage_defaults', 'approve_recovery',
    'view_compliance', 'manage_compliance',
    'view_registers', 'export_registers',
    'view_reports', 'view_audit', 'view_settings',
  ],
  director: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_registers', 'view_audit',
  ],
  senior_manager_finance: [
    'view_applications', 'view_members',
    'view_documentation', 'view_loan_accounts',
    'initiate_disbursement',
    'view_registers', 'view_audit',
  ],
  cfc: [
    'view_applications', 'view_loan_accounts',
    'authorise_disbursement',
    'view_registers', 'view_audit',
  ],
  accounts: [
    'view_applications', 'view_members',
    'view_loan_accounts', 'post_repayment',
    'view_monitoring',
    'view_registers', 'export_registers',
    'view_reports',
  ],
  auditor: [
    'view_applications', 'view_members',
    'view_sanction', 'view_documentation',
    'view_loan_accounts', 'view_monitoring',
    'view_compliance', 'view_registers',
    'view_reports', 'view_audit',
  ],
  admin: [
    'view_applications', 'view_members',
    'view_sanction', 'view_documentation',
    'view_loan_accounts', 'view_monitoring',
    'view_compliance', 'view_registers',
    'view_reports', 'view_settings', 'manage_settings', 'view_audit', 'manage_users',
  ],
  borrower: ['view_own_loan'],
};

const RoleContext = createContext<RoleContextValue | null>(null);

export const RoleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User>(ROLE_USERS.credit_manager);

  const setRole = (role: Role) => setCurrentUser(ROLE_USERS[role]);

  const can = (permission: Permission): boolean =>
    ROLE_PERMISSIONS[currentUser.role]?.includes(permission) ?? false;

  return (
    <RoleContext.Provider value={{ currentUser, setRole, can }}>
      {children}
    </RoleContext.Provider>
  );
};

export const useRole = (): RoleContextValue => {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRole must be used within RoleProvider');
  return ctx;
};

export { ROLE_USERS };
export type { User };
