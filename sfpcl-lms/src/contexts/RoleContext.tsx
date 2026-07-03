import React, { createContext, useCallback, useContext, useState } from 'react';
import { Role } from '../types';
import { FrontendCurrentUser, mapCanonicalPermissions } from '../services/authSession';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  roleName: string;
  team?: string;
  teamName?: string;
  mobileNumber?: string;
  status?: string;
  roleCodes: string[];
  teamCodes: string[];
  permissions: string[];
  availableActions: string[];
  prototypePermissions: Permission[];
  isBackendSession?: boolean;
}

const makeDemoUser = (user: Omit<User, 'roleName' | 'roleCodes' | 'teamCodes' | 'permissions' | 'availableActions' | 'prototypePermissions'>): User => ({
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

const makeBackendUser = (user: FrontendCurrentUser): User => {
  const prototypePermissions = mapCanonicalPermissions(user.permissions);
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    role: user.role,
    roleName: user.roleName,
    team: user.team,
    teamName: user.teamName,
    mobileNumber: user.mobileNumber,
    status: user.status,
    roleCodes: user.roleCodes,
    teamCodes: user.teamCodes,
    permissions: user.permissions,
    availableActions: user.availableActions,
    prototypePermissions,
    isBackendSession: true,
  };
}

export const ROLE_LABELS: Record<Role, string> = {
  field_officer:          'Field Officer',
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
  sales_team_user:        'Sales Team User',
  auditor:                'Auditor',
  admin:                  'Administrator',
  borrower:               'Borrower / Member',
  backend_staff:          'Staff User',
};

interface RoleContextValue {
  currentUser: User;
  setRole: (role: Role) => void;
  setBackendUser: (user: FrontendCurrentUser) => void;
  can: (permission: Permission) => boolean;
}

export type Permission =
  | 'view_applications' | 'create_application' | 'edit_application'
  | 'view_members' | 'edit_members'
  | 'do_appraisal' | 'do_completeness_check'
  | 'view_sanction' | 'approve_sanction' | 'reject_sanction'
  | 'view_documentation' | 'manage_documentation' | 'approve_credit_checklist'
  | 'initiate_disbursement' | 'authorise_disbursement'
  | 'view_loan_accounts' | 'post_repayment'
  | 'view_monitoring' | 'manage_defaults' | 'approve_recovery'
  | 'view_compliance' | 'manage_compliance'
  | 'view_registers' | 'export_registers'
  | 'view_reports' | 'view_settings' | 'manage_settings'
  | 'view_audit' | 'manage_users'
  | 'view_own_loan'
  | 'manage_interest' | 'manage_closure';

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  field_officer: [
    'view_applications', 'create_application', 'edit_application',
    'view_members',
  ],
  deputy_manager_finance: [
    'view_applications', 'create_application', 'edit_application',
    'view_members', 'do_appraisal', 'do_completeness_check',
    'view_documentation',
  ],
  credit_manager: [
    'view_applications', 'create_application', 'edit_application',
    'view_members', 'edit_members', 'do_appraisal', 'do_completeness_check',
    'view_sanction', 'view_documentation', 'approve_credit_checklist',
    'view_loan_accounts',
    'view_monitoring', 'manage_defaults',
    'view_registers', 'export_registers',
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
    'view_audit', 'manage_closure',
  ],
  sanction_committee: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_registers', 'view_audit',
    'approve_recovery', 'manage_defaults',
  ],
  cfo: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_loan_accounts',
    'view_monitoring', 'manage_defaults', 'approve_recovery',
    'view_compliance',
    'view_registers', 'export_registers',
    'view_reports', 'view_audit', 'view_settings',
    'manage_interest', 'manage_closure',
  ],
  director: [
    'view_applications', 'view_members',
    'view_sanction', 'approve_sanction', 'reject_sanction',
    'view_documentation', 'view_registers', 'view_audit',
    'approve_recovery', 'manage_defaults',
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
    'view_monitoring', 'manage_interest',
    'view_registers', 'export_registers',
    'view_reports',
  ],
  sales_team_user: [
    'view_applications', 'view_members',
    'view_loan_accounts', 'manage_interest',
    'view_registers', 'view_reports',
  ],
  auditor: [
    'view_applications', 'view_members',
    'view_sanction', 'view_documentation',
    'view_loan_accounts', 'view_monitoring',
    'view_compliance', 'view_registers',
    'view_reports', 'view_audit',
  ],
  admin: [
    'view_settings', 'manage_settings', 'manage_users',
  ],
  borrower: ['view_own_loan'],
  backend_staff: [],
};

const ROLE_USERS: Record<Role, User> = {
  field_officer:          makeDemoUser({ id: 'u00', name: 'Amit Kallapa',     email: 'amit.kallapa@sfpcl.in',    role: 'field_officer',         team: 'field_intake' }),
  credit_manager:         makeDemoUser({ id: 'u01', name: 'Priya Kulkarni',   email: 'priya.kulkarni@sfpcl.in',  role: 'credit_manager',        team: 'credit_assessment' }),
  deputy_manager_finance: makeDemoUser({ id: 'u02', name: 'Suresh Patil',     email: 'suresh.patil@sfpcl.in',    role: 'deputy_manager_finance', team: 'credit_assessment' }),
  compliance_team:        makeDemoUser({ id: 'u03', name: 'Meera Joshi',      email: 'meera.joshi@sfpcl.in',     role: 'compliance_team',        team: 'compliance' }),
  company_secretary:      makeDemoUser({ id: 'u04', name: 'Aarti Desai',      email: 'aarti.desai@sfpcl.in',     role: 'company_secretary',      team: 'secretarial' }),
  sanction_committee:     makeDemoUser({ id: 'u05', name: 'Rajesh Sharma',    email: 'rajesh.sharma@sfpcl.in',   role: 'sanction_committee',     team: 'sanction' }),
  cfo:                    makeDemoUser({ id: 'u06', name: 'Vikram Nair',      email: 'vikram.nair@sfpcl.in',     role: 'cfo',                    team: 'executive' }),
  director:               makeDemoUser({ id: 'u07', name: 'Anita Mehta',      email: 'anita.mehta@sfpcl.in',     role: 'director',               team: 'board' }),
  senior_manager_finance: makeDemoUser({ id: 'u08', name: 'Deepak Rao',       email: 'deepak.rao@sfpcl.in',      role: 'senior_manager_finance', team: 'finance' }),
  cfc:                    makeDemoUser({ id: 'u09', name: 'Santosh Kumar',    email: 'santosh.kumar@sfpcl.in',   role: 'cfc',                    team: 'finance' }),
  accounts:               makeDemoUser({ id: 'u10', name: 'Kavita More',      email: 'kavita.more@sfpcl.in',     role: 'accounts',               team: 'accounts' }),
  sales_team_user:        makeDemoUser({ id: 'u13', name: 'Nikhil Jagtap',    email: 'nikhil.jagtap@sfpcl.in',   role: 'sales_team_user',        team: 'sales' }),
  auditor:                makeDemoUser({ id: 'u11', name: 'Ramesh Iyer',      email: 'ramesh.iyer@sfpcl.in',     role: 'auditor',                team: 'audit' }),
  admin:                  makeDemoUser({ id: 'u12', name: 'Sneha Bhosale',    email: 'sneha.bhosale@sfpcl.in',   role: 'admin',                  team: 'it' }),
  borrower:               makeDemoUser({ id: 'b01', name: 'Ganesh Thorat',    email: 'ganesh.thorat@sfpcl.in',   role: 'borrower' }),
  backend_staff:          makeDemoUser({ id: 'u14', name: 'Backend Staff',     email: 'backend.staff@sfpcl.in',   role: 'backend_staff' }),
};

const RoleContext = createContext<RoleContextValue | null>(null);

export const RoleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User>(ROLE_USERS.deputy_manager_finance);

  const setRole = useCallback((role: Role) => setCurrentUser(ROLE_USERS[role]), []);
  const setBackendUser = useCallback((user: FrontendCurrentUser) => setCurrentUser(makeBackendUser(user)), []);

  const can = useCallback((permission: Permission): boolean =>
    currentUser.prototypePermissions.includes(permission), [currentUser.prototypePermissions]);

  return (
    <RoleContext.Provider value={{ currentUser, setRole, setBackendUser, can }}>
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
