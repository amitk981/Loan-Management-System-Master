import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { MyProfileView } from './MyProfile';
import type { User } from '../../contexts/RoleContext';

describe('MyProfileView', () => {
  it('renders backend current-user identity, role, team, status, mobile, and permission codes read-only', () => {
    const html = renderToStaticMarkup(<MyProfileView currentUser={backendUser} />);

    expect(html).toContain('Credit Manager');
    expect(html).toContain('credit.manager@sfpcl.example');
    expect(html).toContain('+919999999999');
    expect(html).toContain('Credit Assessment Team');
    expect(html).toContain('credit_manager');
    expect(html).toContain('credit_assessment');
    expect(html).toContain('applications.loan_application.read');
    expect(html).toContain('active');
    expect(html).not.toContain('26 Jun 2026, 03:45 PM');
    expect(html).not.toContain('Change password');
    expect(html).not.toContain('<input');
  });
});

const backendUser: User = {
  id: 'user-1',
  name: 'Credit Manager',
  email: 'credit.manager@sfpcl.example',
  role: 'credit_manager',
  roleName: 'Credit Manager',
  team: 'credit_assessment',
  teamName: 'Credit Assessment Team',
  mobileNumber: '+919999999999',
  status: 'active',
  roleCodes: ['credit_manager'],
  teamCodes: ['credit_assessment'],
  permissions: ['applications.loan_application.read', 'communications.notification.read'],
  availableActions: ['applications.loan_application.read'],
  prototypePermissions: ['view_applications'],
  isBackendSession: true,
};
