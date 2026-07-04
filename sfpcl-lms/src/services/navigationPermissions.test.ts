import { describe, expect, it } from 'vitest';
import type { Permission } from '../contexts/RoleContext';
import { allNavItems } from '../components/layout/Sidebar';
import {
  PAGE_PERMISSIONS,
  resolveNavigationAttempt,
} from './navigationPermissions';

describe('role-aware staff navigation contract', () => {
  it('gates every staff sidebar item except Dashboard with its matching page permission', () => {
    expect(allNavItems.length).toBe(23);

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
        const permissionsWithoutThisItem = new Set<Permission>(
          allNavItems
            .map(navItem => navItem.requiredPermission)
            .filter((permission): permission is Permission => Boolean(permission) && permission !== item.requiredPermission),
        );

        expect(item.requiredPermission).toBeDefined();
        expect(permissionsWithoutThisItem.has(item.requiredPermission as Permission)).toBe(false);
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
