import { expect, test } from '@playwright/test';
import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
}
const djangoPython = process.env.E2E_DJANGO_PYTHON;
if (!djangoPython) {
  throw new Error('E2E_DJANGO_PYTHON is required for trusted browser acceptance');
}
fs.mkdirSync(evidenceDir, { recursive: true });

const repoRoot = path.resolve(__dirname, '..', '..');
const managePy = path.join(repoRoot, 'sfpcl_credit', 'manage.py');
const smokeEmail = 'e2e.smoke@sfpcl.example';
const backendBaseUrl = 'http://127.0.0.1:8000';

test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

for (const repetition of [1, 2]) {
  test(`012H deployment smoke readiness contract repetition ${repetition}`, async ({ page }) => {
    const live = await page.request.get(`${backendBaseUrl}/health/live/`);
    expect(live.status()).toBe(200);
    expect(await live.json()).toEqual({ status: 'live' });

    const ready = await page.request.get(`${backendBaseUrl}/health/ready/`);
    expect(ready.status()).toBe(200);
    expect(await ready.json()).toEqual({ status: 'ready' });

    const smoke = spawnSync(
      djangoPython,
      [managePy, 'smoke_check', '--base-url', backendBaseUrl],
      {
        cwd: repoRoot,
        encoding: 'utf8',
        env: {
          ...process.env,
          SFPCL_SMOKE_CHECK_EMAIL: smokeEmail,
          SFPCL_SMOKE_CHECK_PASSWORD: E2E_PASSWORD,
        },
      },
    );
    expect(smoke.status, `${smoke.stdout}\n${smoke.stderr}`).toBe(0);
    expect(smoke.stdout).toContain('Smoke check passed: 8 read-only workflows');
    expect(smoke.stdout).not.toContain(E2E_PASSWORD);

    await staffLogin(page, smokeEmail, E2E_PASSWORD);
    await expect(page.getByText('Compliance Dashboard')).toBeVisible();
    await expect(page.getByText('Compliance tasks due')).toBeVisible();

    const screenshotName = repetition === 1
      ? 'deployment-smoke-readiness.png'
      : 'deployment-smoke-readiness-run-2.png';
    const screenshotPath = path.join(evidenceDir, screenshotName);
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled',
    });
    expect(fs.statSync(screenshotPath).size).toBeGreaterThan(10_000);
  });
}
