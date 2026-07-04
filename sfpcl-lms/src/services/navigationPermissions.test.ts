import { describe, expect, it } from 'vitest';
import type { Permission } from '../contexts/RoleContext';
import { allNavItems } from '../components/layout/Sidebar';
import { mapBackendUserToFrontendUser, mapCanonicalPermissions } from './authSession';
import {
  PAGE_PERMISSIONS,
  resolveNavigationAttempt,
  visibleStaffNavItems,
} from './navigationPermissions';

describe('role-aware staff navigation contract', () => {
  it('gates every staff sidebar item except Dashboard with its matching page permission', () => {
    expect(allNavItems.length).toBe(24);

    allNavItems.forEach(item => {
      if (item.id === 'dashboard') {
        expect(item.requiredPermission).toBeUndefined();
        expect(PAGE_PERMISSIONS[item.id]).toBeUndefined();
        return;
      }

      expect(item.requiredPermission).toBeDefined();
      expect(PAGE_PERMISSIONS[item.id]).toBe(item.requiredPermission);
    });
  });

  it('hides every protected sidebar item when the user lacks its required permission', () => {
    allNavItems
      .filter(item => item.id !== 'dashboard')
      .forEach(item => {
        const permissionsWithoutThisItem =
          allNavItems
            .map(navItem => navItem.requiredPermission)
            .filter((permission): permission is Permission => Boolean(permission) && permission !== item.requiredPermission);

        expect(item.requiredPermission).toBeDefined();
        expect(visibleStaffNavItems(allNavItems, permission => permissionsWithoutThisItem.includes(permission))).not.toContainEqual(item);
      });
  });

  it('uses the Sidebar visibility path to show only Dashboard for backend sessions with no prototype permissions', () => {
    const zeroPermissionUsers = [
      mapBackendUserToFrontendUser({
        user_id: 'it-head',
        full_name: 'IT Head',
        email: 'it.head@sfpcl.example',
        status: 'active',
        roles: [{ role_code: 'it_head', role_name: 'IT Head' }],
        teams: [],
        permissions: [],
        available_actions: [],
      }),
      mapBackendUserToFrontendUser({
        user_id: 'unknown-role',
        full_name: 'Unknown Role',
        email: 'unknown.role@sfpcl.example',
        status: 'active',
        roles: [{ role_code: 'future_unknown_role', role_name: 'Future Unknown Role' }],
        teams: [],
        permissions: [],
        available_actions: [],
      }),
      mapBackendUserToFrontendUser({
        user_id: 'empty-role',
        full_name: 'Empty Role',
        email: 'empty.role@sfpcl.example',
        status: 'active',
        roles: [],
        teams: [],
        permissions: [],
        available_actions: [],
      }),
    ];

    zeroPermissionUsers.forEach(user => {
      const prototypePermissions = mapCanonicalPermissions(user.permissions);

      expect(visibleStaffNavItems(allNavItems, permission => prototypePermissions.includes(permission)).map(item => item.id)).toEqual(['dashboard']);
      expect(resolveNavigationAttempt('applications', permission => prototypePermissions.includes(permission))).toEqual({
        page: 'dashboard',
        blockedPage: 'applications',
        allowed: false,
      });
      expect(resolveNavigationAttempt('settings', permission => prototypePermissions.includes(permission))).toEqual({
        page: 'dashboard',
        blockedPage: 'settings',
        allowed: false,
      });
      expect(resolveNavigationAttempt('tracer', permission => prototypePermissions.includes(permission))).toEqual({
        page: 'dashboard',
        blockedPage: 'tracer',
        allowed: false,
      });
    });
  });

  it('uses the Sidebar visibility path to keep tracer-only backend sessions isolated to Dashboard and Tracer', () => {
    const prototypePermissions = mapCanonicalPermissions(['tracer.lifecycle.run']);
    const visibleIds = visibleStaffNavItems(allNavItems, permission => prototypePermissions.includes(permission)).map(item => item.id);

    expect(visibleIds).toEqual(['dashboard', 'tracer']);
    expect(visibleIds).not.toContain('applications');
    expect(visibleIds).not.toContain('members');
    expect(visibleIds).not.toContain('loan-accounts');
    expect(visibleIds).not.toContain('reports');
    expect(visibleIds).not.toContain('settings');
    expect(visibleIds).not.toContain('audit');

    expect(resolveNavigationAttempt('tracer', permission => prototypePermissions.includes(permission))).toEqual({
      page: 'tracer',
      blockedPage: null,
      allowed: true,
    });
    expect(resolveNavigationAttempt('members', permission => prototypePermissions.includes(permission))).toEqual({
      page: 'dashboard',
      blockedPage: 'members',
      allowed: false,
    });
  });

  it('shows and guards Admin Users only through mapped manage_users permission', () => {
    const prototypePermissions = mapCanonicalPermissions(['users.user.update']);
    const visibleIds = visibleStaffNavItems(allNavItems, permission => prototypePermissions.includes(permission)).map(item => item.id);

    expect(visibleIds).toEqual(['dashboard', 'admin-users']);
    expect(PAGE_PERMISSIONS['admin-users']).toBe('manage_users');
    expect(resolveNavigationAttempt('admin-users', permission => prototypePermissions.includes(permission))).toEqual({
      page: 'admin-users',
      blockedPage: null,
      allowed: true,
    });
    expect(resolveNavigationAttempt('admin-users', () => false)).toEqual({
      page: 'dashboard',
      blockedPage: 'admin-users',
      allowed: false,
    });
  });

  it('blocks guarded page navigation and returns the dashboard blocked-banner target', () => {
    allNavItems
      .filter(item => item.requiredPermission)
      .forEach(item => {
        const result = resolveNavigationAttempt(item.id, () => false);

        expect(result).toEqual({
          page: 'dashboard',
          blockedPage: item.id,
          allowed: false,
        });
      });
  });

  it('allows guarded page navigation only when the mapped prototype permission is present', () => {
    allNavItems
      .filter((item): item is typeof item & { requiredPermission: Permission } => Boolean(item.requiredPermission))
      .forEach(item => {
        const result = resolveNavigationAttempt(item.id, permission => permission === item.requiredPermission);

        expect(result).toEqual({
          page: item.id,
          blockedPage: null,
          allowed: true,
        });
      });
  });
});
