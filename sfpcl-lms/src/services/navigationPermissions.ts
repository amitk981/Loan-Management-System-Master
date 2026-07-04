import type { Permission } from '../contexts/RoleContext';

export type Page =
  | 'dashboard' | 'tasks'
  | 'search' | 'notifications'
  | 'applications' | 'applications/new' | 'applications/detail' | 'completeness'
  | 'members' | 'members/profile' | 'members/borrower360'
  | 'appraisal' | 'sanction'
  | 'documentation' | 'disbursement' | 'cfc'
  | 'interest'
  | 'loan-accounts' | 'loan-accounts/detail'
  | 'repayments' | 'monitoring'
  | 'defaults' | 'closure'
  | 'compliance' | 'registers'
  | 'reports' | 'grievances'
  | 'audit' | 'settings' | 'profile' | 'tracer'
  | 'borrower';

export const PAGE_PERMISSIONS: Partial<Record<Page, Permission>> = {
  tasks: 'view_applications',
  applications: 'view_applications',
  'applications/new': 'create_application',
  'applications/detail': 'view_applications',
  completeness: 'do_completeness_check',
  members: 'view_members',
  'members/profile': 'view_members',
  'members/borrower360': 'view_members',
  appraisal: 'do_appraisal',
  sanction: 'view_sanction',
  documentation: 'view_documentation',
  disbursement: 'initiate_disbursement',
  cfc: 'authorise_disbursement',
  interest: 'manage_interest',
  'loan-accounts': 'view_loan_accounts',
  'loan-accounts/detail': 'view_loan_accounts',
  repayments: 'post_repayment',
  monitoring: 'view_monitoring',
  defaults: 'manage_defaults',
  closure: 'manage_closure',
  compliance: 'view_compliance',
  registers: 'view_registers',
  reports: 'view_reports',
  grievances: 'view_compliance',
  audit: 'view_audit',
  settings: 'view_settings',
  tracer: 'run_tracer',
  borrower: 'view_own_loan',
};

interface NavigationAttempt {
  page: Page;
  blockedPage: Page | null;
  allowed: boolean;
}

interface PermissionGatedNavItem {
  requiredPermission?: Permission;
}

export const visibleStaffNavItems = <NavItem extends PermissionGatedNavItem>(
  items: NavItem[],
  canUsePermission: (permission: Permission) => boolean,
): NavItem[] => items.filter(item => !item.requiredPermission || canUsePermission(item.requiredPermission));

export const resolveNavigationAttempt = (
  target: Page,
  canUsePermission: (permission: Permission) => boolean,
): NavigationAttempt => {
  const requiredPermission = PAGE_PERMISSIONS[target];
  if (requiredPermission && !canUsePermission(requiredPermission)) {
    return {
      page: 'dashboard',
      blockedPage: target,
      allowed: false,
    };
  }

  return {
    page: target,
    blockedPage: null,
    allowed: true,
  };
};
