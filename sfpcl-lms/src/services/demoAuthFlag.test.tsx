import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, describe, expect, it, vi } from 'vitest';
import LoginScreen from '../pages/auth/LoginScreen';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

const renderBoundary = (demoEnabled: boolean) => renderToStaticMarkup(
  <LoginScreen
    onLogin={vi.fn()}
    onOpenMemberPortal={vi.fn()}
    onDemoLogin={demoEnabled ? vi.fn() : undefined}
    showDemoRoleSelector={demoEnabled}
  />,
);

describe('VITE_ENABLE_DEMO_AUTH module isolation (005FA3)', () => {
  it.each([undefined, 'false'])('keeps demo surfaces absent when the flag is %s', async value => {
    if (value === undefined) vi.stubEnv('VITE_ENABLE_DEMO_AUTH', '');
    else vi.stubEnv('VITE_ENABLE_DEMO_AUTH', value);
    vi.resetModules();

    const { DEMO_AUTH_ENABLED } = await import('./authSession');
    const html = renderBoundary(DEMO_AUTH_ENABLED);

    expect(DEMO_AUTH_ENABLED).toBe(false);
    expect(html).not.toContain('Demo role (select to preview as any user)');
    expect(html).not.toContain('Continue with demo role');
    expect(html).toContain('Open Member Portal Login');
  });

  it('shows only the approved staff demo controls when the flag is true', async () => {
    vi.stubEnv('VITE_ENABLE_DEMO_AUTH', 'true');
    vi.resetModules();

    const { DEMO_AUTH_ENABLED } = await import('./authSession');
    const html = renderBoundary(DEMO_AUTH_ENABLED);

    expect(DEMO_AUTH_ENABLED).toBe(true);
    expect(html).toContain('Demo role (select to preview as any user)');
    expect(html).toContain('Continue with demo role');
    expect(html).toContain('Open Member Portal Login');
    expect(html).not.toContain('portal credential bypass');
  });
});
