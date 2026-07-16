import { describe, expect, it } from 'vitest';

import {
  BrowserInfrastructureError,
  resolveChromiumExecutable,
} from '../playwright.browser';

describe('central Playwright browser resolution', () => {
  it('honors an explicit executable override before automatic discovery', () => {
    expect(
      resolveChromiumExecutable({
        overrideExecutable: '/opt/managed/chrome',
        bundledExecutable: '/cache/ms-playwright/chromium',
        systemCandidates: [],
        exists: () => true,
      }),
    ).toEqual({ executablePath: '/opt/managed/chrome', source: 'override' });
  });

  it('selects the Playwright-managed Chromium executable when it exists', () => {
    expect(
      resolveChromiumExecutable({
        bundledExecutable: '/cache/ms-playwright/chromium',
        systemCandidates: ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'],
        exists: (candidate) => candidate === '/cache/ms-playwright/chromium',
      }),
    ).toEqual({
      executablePath: '/cache/ms-playwright/chromium',
      source: 'bundled',
    });
  });

  it('falls back to an installed system Chrome when the bundled browser is absent', () => {
    const systemChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

    expect(
      resolveChromiumExecutable({
        bundledExecutable: '/missing/ms-playwright/chromium',
        systemCandidates: [systemChrome],
        exists: (candidate) => candidate === systemChrome,
      }),
    ).toEqual({ executablePath: systemChrome, source: 'system' });
  });

  it('classifies an unavailable browser as infrastructure failure', () => {
    expect(() =>
      resolveChromiumExecutable({
        bundledExecutable: '/missing/ms-playwright/chromium',
        systemCandidates: ['/missing/system/chrome'],
        exists: () => false,
      }),
    ).toThrowError(BrowserInfrastructureError);

    try {
      resolveChromiumExecutable({
        bundledExecutable: '/missing/ms-playwright/chromium',
        systemCandidates: ['/missing/system/chrome'],
        exists: () => false,
      });
    } catch (error) {
      expect(error).toMatchObject({
        code: 'PLAYWRIGHT_BROWSER_UNAVAILABLE',
        name: 'BrowserInfrastructureError',
      });
    }
  });
});
