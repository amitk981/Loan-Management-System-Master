import { afterEach, describe, expect, it, vi } from 'vitest';


afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe('production demo surface isolation', () => {
  it('removes tracer navigation and rejects direct tracer navigation even with permission', async () => {
    vi.stubEnv('PROD', true);
    vi.stubEnv('VITE_ENABLE_DEMO_SURFACES', 'true');
    vi.resetModules();

    const [
      { allNavItems },
      { resolveNavigationAttempt },
      { DEMO_SURFACES_ENABLED },
    ] = await Promise.all([
      import('../components/layout/Sidebar'),
      import('./navigationPermissions'),
      import('./runtimeEnvironment'),
    ]);

    expect(DEMO_SURFACES_ENABLED).toBe(false);
    expect(allNavItems.some(item => item.id === 'tracer')).toBe(false);
    expect(resolveNavigationAttempt('tracer', () => true)).toEqual({
      page: 'dashboard',
      blockedPage: 'tracer',
      allowed: false,
    });
  });
});
