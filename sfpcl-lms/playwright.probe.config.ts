import { defineConfig, devices } from '@playwright/test';

import { resolveChromiumExecutable } from './playwright.browser';

const chromiumExecutable = resolveChromiumExecutable();

export default defineConfig({
  testDir: './e2e',
  testMatch: 'browser-launch.probe.ts',
  retries: 0,
  workers: 1,
  reporter: [['list']],
  projects: [
    {
      name: 'chromium-probe',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: { executablePath: chromiumExecutable.executablePath },
      },
    },
  ],
});
