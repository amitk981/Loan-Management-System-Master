import { chromium, expect, test, type Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });
const bundledChromium = chromium.executablePath();
const macOsChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const availableChromium = fs.existsSync(bundledChromium)
  ? bundledChromium
  : fs.existsSync(macOsChrome)
    ? macOsChrome
    : undefined;

test.use({
  viewport: { width: 1280, height: 720 },
  launchOptions: availableChromium ? { executablePath: availableChromium } : {},
});

async function capture(page: Page, name: string) {
  const output = path.join(evidenceDir!, name);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
}
test('008M5 persists staff documentation actions through real Django', async ({ page }) => {
  await staffLogin(page, 'e2e.portal.compliance@sfpcl.example', E2E_PASSWORD);
  await page.getByRole('button', { name: 'Documentation' }).click(); await expect(page.getByRole('heading', { name: 'Document Checklist' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'LO000008L4' })).toBeVisible(); await expect(page.getByText(/Disbursement blocked:/)).toBeVisible();
  await capture(page, 'documentation-checklist-blockers.png');

  const powerOfAttorney = page.locator('tr').filter({ hasText: 'Power of Attorney' });
  await expect(powerOfAttorney.getByRole('button', { name: 'Record borrower signature' })).toBeVisible();
  await expect(powerOfAttorney.getByRole('button', { name: 'Record nominee signature' })).toBeVisible();
  await expect(powerOfAttorney.getByRole('button', { name: 'Record stamp' })).toBeVisible();
  await expect(powerOfAttorney.getByRole('button', { name: 'Record notarisation' })).toBeVisible();

  await page.getByRole('button', { name: 'View Document Pack' }).click();
  const pack = page.getByRole('heading', { name: 'Document Pack — LO000008L4' }).locator('..').locator('..').locator('..');
  for (const label of ['Record borrower signature', 'Record nominee signature', 'Record stamp', 'Record notarisation', 'Upload / re-upload signed copy', 'Request correction']) {
    await expect(pack.getByRole('button', { name: label })).toBeVisible();
  }
  await expect(pack.getByRole('button', { name: 'Download' })).toHaveCount(0);
  await pack.getByRole('button', { name: 'Close' }).click();

  await powerOfAttorney.getByRole('button', { name: 'Upload / re-upload signed copy' }).click();
  await page.getByLabel('Signed document').setInputFiles({
    name: 'signed-power-of-attorney.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\nsigned evidence\n%%EOF'),
  });
  await page.getByLabel('Remarks').fill('Real browser signed-copy upload.');
  await page.getByRole('button', { name: 'Confirm action' }).click();
  await expect(page.getByText(/Action accepted/)).toBeVisible();

  await powerOfAttorney.getByRole('button', { name: 'Request correction' }).click();
  await page.getByLabel('Correction required').fill('Nominee signature must be supplied.');
  await page.getByRole('button', { name: 'Confirm action' }).click();
  await expect(page.getByText(/Action accepted/)).toBeVisible();
  await expect(page.getByText(/Power of Attorney: Correction Requested/i)).toBeVisible();

  await powerOfAttorney.getByRole('button', { name: 'Upload / re-upload signed copy' }).click();
  await page.getByLabel('Signed document').setInputFiles({
    name: 'corrected-signed-power-of-attorney.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.4\ncorrected signed evidence\n%%EOF'),
  });
  await page.getByLabel('Remarks').fill('Corrected signed copy resolves nominee signature request.');
  await page.getByRole('button', { name: 'Confirm action' }).click();
  await expect(page.getByText(/Action accepted/)).toBeVisible();
  await expect(page.getByText(/Power of Attorney: Correction Requested/i)).toHaveCount(0);

  await powerOfAttorney.getByRole('button', { name: 'Record stamp' }).click();
  await page.getByLabel('Stamp amount').fill('not-an-amount');
  await page.getByRole('button', { name: 'Confirm action' }).click();
  await expect(page.getByText('Documentation action failed validation.')).toBeVisible();
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(powerOfAttorney.getByRole('button', { name: 'Record stamp' })).toBeVisible();

  const boundary = await page.evaluate(async () => {
    const session = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const headers = { Authorization: `Bearer ${session.accessToken}`, 'Content-Type': 'application/json' };
    const queue = await fetch('http://127.0.0.1:8000/api/v1/documentation-workspaces/', { headers });
    const application = (await queue.json()).data.find((row: { application_reference_number: string }) => row.application_reference_number === 'LO000008L4');
    const root = `http://127.0.0.1:8000/api/v1/loan-applications/${application.loan_application_id}/documentation-workspace/`;
    const workspace = (await (await fetch(root, { headers })).json()).data;
    const poa = workspace.items.find((item: { item_code: string }) => item.item_code === 'poa');
    const action = poa.available_actions.find((row: { action_code: string }) => row.action_code === 'request_correction');
    const tamperedUrl = action.action_url.slice(0, -2) + (action.action_url.at(-2) === 'a' ? 'b' : 'a') + '/';
    const tampered = await fetch(`http://127.0.0.1:8000${tamperedUrl}`, {
      method: 'POST', headers, body: JSON.stringify({ remarks: 'Tampered action identity.' }),
    });
    const restricted = await fetch(`${root}term_sheet/download/`, { headers });
    const securityPoa = workspace.security_workflows.power_of_attorney;
    return { queue: queue.status, tampered: tampered.status, restricted: restricted.status,
      actionKeys: poa.available_actions.map((row: { action_key: string }) => row.action_key),
      signedCopy: poa.document.signed_copy, securityPoa };
  });
  expect(boundary.queue).toBe(200); expect(boundary.tampered).toBe(404); expect(boundary.restricted).toBe(404);
  expect(new Set(boundary.actionKeys).size).toBe(boundary.actionKeys.length);
  expect(boundary.signedCopy.remarks).toBe('Corrected signed copy resolves nominee signature request.');
  if (boundary.securityPoa.required && boundary.securityPoa.status === 'blocked') {
    expect(boundary.securityPoa.blocker).toBe('governed_attorney_unconfigured');
  }

  await page.getByRole('button', { name: 'Securities' }).click(); await expect(page.getByRole('heading', { name: 'Security Instruments' })).toBeVisible();
  await capture(page, 'documentation-security-workflow.png');

  await page.getByRole('button', { name: 'Checklist' }).click(); await expect(powerOfAttorney.getByRole('button', { name: 'Download' })).toHaveCount(0);
  await capture(page, 'documentation-restricted-state.png');

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole('heading', { name: 'Document Checklist' })).toBeVisible();
  await expect(powerOfAttorney.getByRole('button', { name: 'Record borrower signature' })).toBeVisible();
  await capture(page, 'documentation-checklist-narrow.png');
  await page.setViewportSize({ width: 1280, height: 720 });

  await page.getByRole('button', { name: 'Approvals' }).click(); await expect(page.getByText('Senior Manager Finance', { exact: true }).last()).toBeVisible();
  await capture(page, 'documentation-final-approval.png');
});
