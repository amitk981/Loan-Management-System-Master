import fs from 'fs';
import path from 'path';
import { expect, test, type Page } from '@playwright/test';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for witness correction authority');
fs.mkdirSync(evidenceDir, { recursive: true });

const FINANCE_EMAIL = 'e2e.credit.finance@sfpcl.example';
const FINANCE_NAME = 'E2E Deputy Manager Finance';
const CHECKER_EMAIL = 'e2e.credit.manager@sfpcl.example';
const APPLICATION_REFERENCE = 'LOE2E00601';
const WITNESS_MEMBER_ID = '00000000-0000-4000-8000-000000000611';

test('contact and maker-checker identity corrections persist through routed real sessions', async ({ page }) => {
  await staffLogin(page, FINANCE_EMAIL, E2E_PASSWORD);
  await openWitnessTab(page);

  await page.getByLabel('Member ID').fill(WITNESS_MEMBER_ID);
  await page.getByLabel('Witness Name').fill('Epic 006 Browser Witness');
  await page.getByLabel('PAN').fill('ABCDE1234F');
  await page.getByLabel('Aadhaar').fill('123412341234');
  await page.getByLabel('Address').fill('Initial Witness Road');
  await page.getByLabel('Mobile').fill('9876543210');
  await page.getByRole('button', { name: 'Capture Witness' }).click();
  await expect(page.getByText('Initial Witness Road')).toBeVisible();

  await page.getByRole('button', { name: 'Correct Witness Contact' }).click();
  await page.getByLabel('Correction Address').fill('Canonical Contact Road');
  await page.getByLabel('Correction Mobile').fill('9123456780');
  await page.getByRole('button', { name: 'Save Contact Correction' }).click();
  await expect(page.getByText('Canonical Contact Road')).toBeVisible();
  await page.reload();
  await openWitnessTab(page);
  await expect(page.getByText('Canonical Contact Road')).toBeVisible();
  await capture(page, 'witness-contact-correction-reloaded.png');

  await expect(page.getByText('A different authorised user must correct verified witness identity.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Correct Witness Identity' })).toHaveCount(0);
  await capture(page, 'witness-verifier-identity-denied.png');

  await signOut(page);
  await staffLogin(page, CHECKER_EMAIL, E2E_PASSWORD);
  await openWitnessTab(page);
  await page.getByRole('button', { name: 'Correct Witness Identity' }).click();
  await page.getByLabel('Correction PAN').fill('KLMNO9876P');
  await page.getByLabel('Correction Aadhaar').fill('987698769876');
  await page.getByRole('button', { name: 'Save Identity Correction' }).click();
  await expect(page.getByText('******876P')).toBeVisible();
  await page.reload();
  await openWitnessTab(page);
  await expect(page.getByText('******876P')).toBeVisible();
  await capture(page, 'witness-checker-identity-corrected.png');
});

async function openWitnessTab(page: Page) {
  await page.getByRole('button', { name: 'Applications' }).click();
  await page.getByPlaceholder('Search by number or member…').fill(APPLICATION_REFERENCE);
  await page.getByRole('row').filter({ hasText: APPLICATION_REFERENCE }).click();
  await page.getByRole('button', { name: 'Witness' }).click();
  await expect(page.getByRole('heading', { name: 'Witness Details' })).toBeVisible();
}

async function signOut(page: Page) {
  await page.getByRole('button', { name: new RegExp(`^${FINANCE_NAME}`) }).click();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('heading', { name: 'Sign in to your account' })).toBeVisible();
}

const capture = (page: Page, name: string) => page.screenshot({
  path: path.join(evidenceDir, name),
  fullPage: true,
  animations: 'disabled',
});
