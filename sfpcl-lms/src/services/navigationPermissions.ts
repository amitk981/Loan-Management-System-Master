import type { Permission } from '../contexts/RoleContext';
import { DEMO_SURFACES_ENABLED } from './runtimeEnvironment';

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
  | 'audit' | 'settings' | 'admin-users' | 'profile' | 'tracer'
  | 'borrower';

interface PermissionGatedNavItem {
  requiredPermission?: Permission;
  alternativePermissions?: Permission[];
}

const required = (requiredPermission: Permission, alternativePermissions?: Permission[]): PermissionGatedNavItem => ({
  requiredPermission,
  ...(alternativePermissions ? { alternativePermissions } : {}),
});

export const PAGE_NAVIGATION_MANIFEST: Partial<Record<Page, PermissionGatedNavItem>> = {
  applications: required('view_applications'),
  'applications/new': required('create_application'),
  'applications/detail': required('view_applications'),
  completeness: required('do_completeness_check'),
  members: required('view_members'),
  'members/profile': required('view_members'),
  'members/borrower360': required('view_members'),
  appraisal: required('do_appraisal'),
  sanction: required('view_sanction'),
  documentation: required('view_documentation'),
  disbursement: required('initiate_disbursement'),
  cfc: required('authorise_disbursement'),
  interest: required('manage_interest'),
  'loan-accounts': required('view_loan_accounts'),
  'loan-accounts/detail': required('view_loan_accounts'),
  repayments: required('post_repayment'),
  monitoring: required('view_monitoring'),
  defaults: required('manage_defaults'),
  closure: required('manage_closure'),
  compliance: required('view_compliance'),
  registers: required('view_registers', ['view_approval_registers']),
  reports: required('view_reports'),
  grievances: required('view_compliance'),
  audit: required('view_audit'),
  settings: required('view_settings', ['view_approval_matrix']),
  'admin-users': required('manage_users'),
  tracer: required('run_tracer'),
  borrower: required('view_own_loan'),
};

export const navigationPermissionsFor = (page: Page): PermissionGatedNavItem => PAGE_NAVIGATION_MANIFEST[page] ?? {};

export const PAGE_PERMISSIONS = Object.fromEntries(
  Object.entries(PAGE_NAVIGATION_MANIFEST).map(([page, item]) => [page, item.requiredPermission]),
) as Partial<Record<Page, Permission>>;

export const PAGE_ALTERNATIVE_PERMISSIONS = Object.fromEntries(
  Object.entries(PAGE_NAVIGATION_MANIFEST)
    .filter(([, item]) => item.alternativePermissions)
    .map(([page, item]) => [page, item.alternativePermissions]),
) as Partial<Record<Page, Permission[]>>;

interface NavigationAttempt {
  page: Page;
  blockedPage: Page | null;
  allowed: boolean;
}

export const visibleStaffNavItems = <NavItem extends PermissionGatedNavItem>(
  items: NavItem[],
  canUsePermission: (permission: Permission) => boolean,
): NavItem[] => items.filter(item => (
  !item.requiredPermission
  || canUsePermission(item.requiredPermission)
  || item.alternativePermissions?.some(canUsePermission)
));

export const resolveNavigationAttempt = (
  target: Page,
  canUsePermission: (permission: Permission) => boolean,
): NavigationAttempt => {
  if (target === 'tracer' && !DEMO_SURFACES_ENABLED) {
    return {
      page: 'dashboard',
      blockedPage: target,
      allowed: false,
    };
  }

  const { requiredPermission, alternativePermissions: alternatives = [] } = navigationPermissionsFor(target);
  if (requiredPermission && !canUsePermission(requiredPermission) && !alternatives.some(canUsePermission)) {
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
