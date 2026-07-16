import { existsSync } from 'node:fs';

import { chromium } from '@playwright/test';

type BrowserResolverOptions = {
  overrideExecutable?: string;
  bundledExecutable?: string;
  systemCandidates?: readonly string[];
  exists?: (candidate: string) => boolean;
};

export type ChromiumExecutable = {
  executablePath: string;
  source: 'override' | 'bundled' | 'system';
};

export class BrowserInfrastructureError extends Error {
  readonly code = 'PLAYWRIGHT_BROWSER_UNAVAILABLE';

  constructor(candidates: readonly string[]) {
    super(
      `No usable Chromium executable was found. Checked: ${candidates.join(', ')}. ` +
        'Install Playwright Chromium or set PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH.',
    );
    this.name = 'BrowserInfrastructureError';
  }
}

const defaultSystemCandidates = [
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
];

export function resolveChromiumExecutable(
  options: BrowserResolverOptions = {},
): ChromiumExecutable {
  const bundledExecutable = options.bundledExecutable ?? chromium.executablePath();
  const exists = options.exists ?? existsSync;
  const systemCandidates = options.systemCandidates ?? defaultSystemCandidates;
  const overrideExecutable =
    options.overrideExecutable ?? process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;

  if (overrideExecutable) {
    if (exists(overrideExecutable)) {
      return { executablePath: overrideExecutable, source: 'override' };
    }
    throw new BrowserInfrastructureError([overrideExecutable]);
  }

  if (exists(bundledExecutable)) {
    return { executablePath: bundledExecutable, source: 'bundled' };
  }

  for (const executablePath of systemCandidates) {
    if (exists(executablePath)) {
      return { executablePath, source: 'system' };
    }
  }

  throw new BrowserInfrastructureError([bundledExecutable, ...systemCandidates]);
}
