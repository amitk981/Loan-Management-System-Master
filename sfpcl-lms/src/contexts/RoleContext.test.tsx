import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { RoleProvider, useRole, UNAUTHENTICATED_USER } from './RoleContext';

const Probe: React.FC = () => {
  const { currentUser, can } = useRole();
  return (
    <div>
      <span data-testid="name">{currentUser.name}</span>
      <span data-testid="perm-count">{currentUser.prototypePermissions.length}</span>
      <span data-testid="role-codes">{currentUser.roleCodes.length}</span>
      <span data-testid="can-view-members">{String(can('view_members'))}</span>
      <span data-testid="backend-session">{String(Boolean(currentUser.isBackendSession))}</span>
    </div>
  );
};

describe('RoleContext pre-login authority (005FA2 regression)', () => {
  it('defaults to an unauthenticated user with no permissions or role codes', () => {
    const html = renderToStaticMarkup(
      <RoleProvider>
        <Probe />
      </RoleProvider>,
    );

    expect(html).toContain('Not signed in');
    expect(html).not.toContain('Suresh Patil');
    expect(html).toContain('<span data-testid="perm-count">0</span>');
    expect(html).toContain('<span data-testid="role-codes">0</span>');
    expect(html).toContain('<span data-testid="can-view-members">false</span>');
    expect(html).toContain('<span data-testid="backend-session">false</span>');
  });

  it('keeps the unauthenticated constant permission-free', () => {
    expect(UNAUTHENTICATED_USER.prototypePermissions).toHaveLength(0);
    expect(UNAUTHENTICATED_USER.permissions).toHaveLength(0);
    expect(UNAUTHENTICATED_USER.availableActions).toHaveLength(0);
  });
});
