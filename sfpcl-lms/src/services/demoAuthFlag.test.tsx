import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

const renderRealAppBoundary = async (flag: string | undefined) => {
  vi.unstubAllEnvs();
  if (flag === undefined) {
    vi.stubEnv('VITE_ENABLE_DEMO_AUTH', undefined);
  } else {
    vi.stubEnv('VITE_ENABLE_DEMO_AUTH', flag);
  }
  vi.resetModules();

  const [{ default: App }, { DEMO_AUTH_ENABLED }] = await Promise.all([
    import('../App'),
    import('./authSession'),
  ]);

  return {
    demoEnabled: DEMO_AUTH_ENABLED,
    html: renderToStaticMarkup(<App />),
  };
};

const expectNoAuthorityOrProtectedContent = (html: string) => {
  expect(html).not.toContain('Continue with demo role');
  expect(html).not.toContain('Demo role (select to preview as a staff user)');
  expect(html).not.toContain('Rendered Portal Member');
  expect(html).not.toContain('portal.loan_application.read_own');
  expect(html).not.toContain('portal.loan_application.create_own');
  expect(html).not.toContain('Borrower / Member');
  expect(html).not.toContain('Dashboard');
  expect(html).not.toContain('Sign out');
};

describe('VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4)', () => {
  it.each([
    ['unset', undefined],
    ['explicit false', 'false'],
  ])('fails closed when the flag is %s', async (_label, flag) => {
    const { demoEnabled, html } = await renderRealAppBoundary(flag);

    expect(demoEnabled).toBe(false);
    expectNoAuthorityOrProtectedContent(html);
    expect(html).toContain('Open Member Portal Login');
    expect(html).toContain('Sign in to your account');
  });

  it('exposes only approved staff demo controls when the flag is true', async () => {
    const { demoEnabled, html } = await renderRealAppBoundary('true');

    expect(demoEnabled).toBe(true);
    expect(html).toContain('Demo role (select to preview as a staff user)');
    expect(html).toContain('Continue with demo role');
    expect(html).toContain('Open Member Portal Login');
    expect(html).not.toContain('Rendered Portal Member');
    expect(html).not.toContain('portal.loan_application.read_own');
    expect(html).not.toContain('portal.loan_application.create_own');
    expect(html).not.toContain('Borrower / Member');
    expect(html).not.toContain('Dashboard');
    expect(html).not.toContain('Sign out');
  });
});
