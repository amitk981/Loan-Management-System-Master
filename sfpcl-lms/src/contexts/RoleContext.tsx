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
  memberId?: string;
  portalAccountId?: string;
  portalRole?: string;
  memberDisplayName?: string;
}

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
    memberId: user.memberId,
    portalAccountId: user.portalAccountId,
    portalRole: user.portalRole,
    memberDisplayName: user.memberDisplayName,
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
  setDemoUser: (user: User) => void;
  setBackendUser: (user: FrontendCurrentUser) => void;
  clearUser: () => void;
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
  | 'view_registers' | 'view_approval_registers' | 'export_registers'
  | 'view_reports' | 'view_settings' | 'view_approval_matrix' | 'manage_settings'
  | 'view_audit' | 'manage_users'
  | 'view_own_loan'
  | 'manage_interest' | 'manage_closure'
  | 'run_tracer';

// Pre-login state: no identity, no role codes, no permissions. Nothing role-gated
// may render from this user; a real session arrives only via setBackendUser or
// the separately bundled demo controls.
export const UNAUTHENTICATED_USER: User = {
  id: 'anonymous',
  name: 'Not signed in',
  email: '',
  role: 'backend_staff',
  roleName: 'Not signed in',
  roleCodes: [],
  teamCodes: [],
  permissions: [],
  availableActions: [],
  prototypePermissions: [],
  isBackendSession: false,
};

const RoleContext = createContext<RoleContextValue | null>(null);

export const RoleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User>(UNAUTHENTICATED_USER);

  const setDemoUser = useCallback((user: User) => setCurrentUser(user), []);
  const setBackendUser = useCallback((user: FrontendCurrentUser) => setCurrentUser(makeBackendUser(user)), []);
  const clearUser = useCallback(() => setCurrentUser(UNAUTHENTICATED_USER), []);

  const can = useCallback((permission: Permission): boolean =>
    currentUser.prototypePermissions.includes(permission), [currentUser.prototypePermissions]);

  return (
    <RoleContext.Provider value={{ currentUser, setDemoUser, setBackendUser, clearUser, can }}>
      {children}
    </RoleContext.Provider>
  );
};

export const useRole = (): RoleContextValue => {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRole must be used within RoleProvider');
  return ctx;
};
