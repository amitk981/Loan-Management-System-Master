import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { E2E_PASSWORD, staffLogin, ZERO_EMAIL } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for member governance closure');
fs.mkdirSync(evidenceDir, { recursive: true });
const FINANCE_EMAIL = 'e2e.credit.finance@sfpcl.example';

test('real member governance and witness capture remain reachable and permission-bound', async ({ page }, testInfo) => {
  await staffLogin(page, FINANCE_EMAIL, E2E_PASSWORD);
  await page.getByRole('button', { name: 'Members & Borrowers' }).click();
  await page.getByRole('button', { name: 'Register Member' }).click();
  await expect(page.getByRole('heading', { name: 'Register Member' })).toBeVisible();
  await capture(page, testInfo, 'member-create');

  await page.getByRole('button', { name: 'Cancel' }).click();
  await page.getByPlaceholder('Search by name or folio...').fill('Epic 006 Browser Member');
  const memberRow = page.getByRole('row').filter({ hasText: 'Epic 006 Browser Member' });
  await memberRow.getByRole('button', { name: 'Profile' }).click();
  await expect(page.getByText('Verified identity locked')).toBeVisible();
  await capture(page, testInfo, 'member-identity-locked');
  await page.getByRole('button', { name: 'Correct verified identity' }).click();
  await expect(page.getByLabel('Reverification Reason')).toBeVisible();
  await capture(page, testInfo, 'member-reverification');

  await page.getByRole('button', { name: 'Applications' }).click();
  await page.getByText('LOE2E00601').click();
  await page.getByRole('button', { name: 'Witness' }).click();
  await page.getByLabel('member id').fill('00000000-0000-4000-8000-000000000602');
  await page.getByLabel('witness name').fill('Epic 006 Browser Member');
  await page.getByLabel('pan').fill('ABCDE1234F');
  await page.getByLabel('aadhaar').fill('123412341234');
  await page.getByRole('button', { name: 'Capture Witness' }).click();
  await expect(page.getByText('FOL-E2E-006')).toBeVisible();
  await capture(page, testInfo, 'witness-capture');

  await page.evaluate(() => localStorage.removeItem('sfpcl_staff_auth_session'));
  await page.context().clearCookies();
  await staffLogin(page, ZERO_EMAIL, E2E_PASSWORD);
  await expect(page.getByRole('button', { name: 'Members & Borrowers' })).toHaveCount(0);
  await capture(page, testInfo, 'member-governance-unauthorized');
});

async function capture(page: Page, testInfo: TestInfo, name: string) {
  const png = testInfo.snapshotPath(`${name}.png`);
  const encoded = `${png}.base64`;
  if (!fs.existsSync(png) && fs.existsSync(encoded)) fs.writeFileSync(png, Buffer.from(fs.readFileSync(encoded, 'utf8'), 'base64'));
  if (!fs.existsSync(png)) {
    fs.mkdirSync(path.dirname(png), { recursive: true });
    await page.screenshot({ path: png, fullPage: true, animations: 'disabled' });
    fs.writeFileSync(encoded, fs.readFileSync(png).toString('base64'));
  }
  await page.screenshot({ path: path.join(evidenceDir, `${name}.png`), fullPage: true, animations: 'disabled' });
  await expect(page).toHaveScreenshot(`${name}.png`, { fullPage: true, animations: 'disabled' });
  fs.rmSync(png);
}
