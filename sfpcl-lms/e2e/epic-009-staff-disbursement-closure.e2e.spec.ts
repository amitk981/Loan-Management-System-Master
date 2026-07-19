import { expect, test, type Locator, type Page } from '@playwright/test';
import { createHash } from 'crypto';
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required');
const djangoPython = process.env.E2E_DJANGO_PYTHON;
if (!djangoPython) throw new Error('E2E_DJANGO_PYTHON is required');

const repoRoot = path.resolve(__dirname, '../..');
const e2eDbPath = process.env.SFPCL_DB_PATH || path.join(repoRoot, 'sfpcl_credit', 'e2e.sqlite3');
const e2eStorageRoot = process.env.SFPCL_DOCUMENT_STORAGE_ROOT
  || path.join(process.env.TMPDIR || '/tmp', 'sfpcl-e2e-document-storage', path.basename(repoRoot));
const password = 'ChecklistPass123!';
const financeEmail = 'e2e.epic009.finance@sfpcl.example';
const creditEmail = 'e2e.epic009.credit@sfpcl.example';
const cfcEmail = 'e2e.epic009.cfc@sfpcl.example';
const accountNumber = 'LN-REAL-OWNER-001';
const screenshots = [
  'loan-account-list.png',
  'loan-account-sanctioned-summary.png',
  'loan-account-active-summary.png',
  'sap-request-and-confirmation.png',
  'disbursement-readiness-blockers.png',
  'payment-initiation.png',
  'cfc-authorisation.png',
  'transfer-and-advice-success.png',
  'loan-account-safe-error.png',
] as const;

test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

test('S36-S41 and initial Loan Account 360 use real Django and retain distinct evidence', async ({ page }) => {
  clearPriorEvidence();
  await staffLogin(page, financeEmail, password);

  await open(page, 'Loan Accounts');
  await expect(page.getByRole('heading', { name: 'Loan Accounts', exact: true })).toBeVisible();
  await expect(page.getByText(accountNumber, { exact: true })).toBeVisible();
  await shot(page, 'loan-account-list.png');

  await page.getByText(accountNumber, { exact: true }).click();
  const accountHeader = page.getByRole('heading', { name: accountNumber, exact: true }).locator('..');
  await expect(accountHeader.getByText('Sanctioned', { exact: true })).toBeVisible();
  await expect(page.getByText('₹0.00 disbursed', { exact: true })).toBeVisible();
  await shot(page, 'loan-account-sanctioned-summary.png');

  await open(page, 'SAP & Disbursement');
  const sapCard = cardWithHeading(page, 'SAP Customer Code and Bank Verification');
  await expect(sapCard.getByText('Completed', { exact: true })).toBeVisible();
  await expect(sapCard.getByText('******-001', { exact: true })).toBeVisible();
  await shot(page, 'sap-request-and-confirmation.png', sapCard);

  const readinessCard = cardWithHeading(page, 'Disbursement Readiness');
  await expect(readinessCard.getByText('Source bank account configured', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Initiate payment' })).toBeDisabled();
  await shot(page, 'disbursement-readiness-blockers.png', readinessCard);

  advanceFixture('--make-ready');
  await page.reload();
  await open(page, 'SAP & Disbursement');
  await page.waitForLoadState('networkidle');
  await expect(page.getByRole('heading', { name: 'Payment Initiation', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Initiate payment' })).toBeEnabled();
  await expect(page.getByLabel('Disbursement amount')).toHaveValue('400000.00');
  await shot(page, 'payment-initiation.png');
  const finalVerification = page.getByLabel('Final verification comments');
  await finalVerification.fill('All current owner evidence verified.');
  await expect(finalVerification).toHaveValue('All current owner evidence verified.');
  const initiationResponsePromise = page.waitForResponse(response =>
    response.request().method() === 'POST'
    && /\/api\/v1\/loan-accounts\/[^/]+\/disbursements\/initiate\/$/.test(response.url()),
  );
  await page.getByRole('button', { name: 'Initiate payment' }).click();
  const initiationResponse = await initiationResponsePromise;
  const initiationEnvelope = await initiationResponse.json() as {
    success: boolean;
    data: { initiation_status: string; authorisation_status: string; bank_transfer_status: string };
  };
  expect(
    initiationResponse.ok(),
    `Real Django initiation failed: ${JSON.stringify(initiationEnvelope)}`,
  ).toBe(true);
  expect(initiationEnvelope).toMatchObject({
    success: true,
    data: {
      initiation_status: 'initiated',
      authorisation_status: 'pending',
      bank_transfer_status: 'pending',
    },
  });
  await expect(page.getByRole('button', { name: 'Initiate payment' })).toBeHidden();
  await expect(page.getByText('Pending', { exact: true }).first()).toBeVisible();

  await switchActor(page, cfcEmail);
  await open(page, 'Payment Authorisation');
  await expect(page.getByRole('button', { name: 'Authorise payment' })).toBeVisible();
  await expect(page.getByText('Pending', { exact: true }).first()).toBeVisible();
  await shot(page, 'cfc-authorisation.png');
  await page.getByLabel('Comments').fill('Independent CFC authorisation retained.');
  const authorisationResponsePromise = page.waitForResponse(response =>
    response.request().method() === 'POST'
    && /\/api\/v1\/disbursements\/[^/]+\/authorise\/$/.test(response.url()),
  );
  await page.getByRole('button', { name: 'Authorise payment' }).click();
  const authorisationResponse = await authorisationResponsePromise;
  const authorisationEnvelope = await authorisationResponse.json() as {
    success: boolean;
    data: {
      authorisation_status: string;
      bank_transfer_status: string;
      next_action: string;
      authorised_at: string;
    };
  };
  expect(
    authorisationResponse.ok(),
    `Real Django authorisation failed: ${JSON.stringify(authorisationEnvelope)}`,
  ).toBe(true);
  expect(authorisationEnvelope).toMatchObject({
    success: true,
    data: {
      authorisation_status: 'approved',
      bank_transfer_status: 'pending',
      next_action: 'record_bank_transfer',
    },
  });
  await expect(page.getByText('No payment authorisations in your scope')).toBeVisible();

  advanceFixture('--prepare-transfer');
  await switchActor(page, financeEmail);
  await open(page, 'SAP & Disbursement');
  await expect(page.getByRole('button', { name: 'Record transfer success' })).toBeVisible();
  const evidenceId = await transferEvidenceId(page);
  const transferDateTime = await browserLocalMinuteAfter(
    page,
    authorisationEnvelope.data.authorised_at,
  );
  const transferInstant = await page.evaluate(value => new Date(value).toISOString(), transferDateTime);
  expect(
    Date.parse(transferInstant),
    'Transfer evidence must be later than the real Django CFC authorisation.',
  ).toBeGreaterThan(Date.parse(authorisationEnvelope.data.authorised_at));
  await page.getByLabel('UTR / bank reference').fill('RBL-E2E-009-UTR');
  await page.getByLabel('Transfer date and time').fill(transferDateTime);
  await page.getByLabel('Bank evidence document ID').fill(evidenceId);
  const transferResponsePromise = page.waitForResponse(response =>
    response.request().method() === 'POST'
    && /\/api\/v1\/disbursements\/[^/]+\/mark-transfer-successful\/$/.test(response.url()),
  );
  await page.getByRole('button', { name: 'Record transfer success' }).click();
  const transferResponse = await transferResponsePromise;
  const transferEnvelope = await transferResponse.json() as {
    success: boolean;
    data: { bank_transfer_status: string; loan_account_status: string };
  };
  expect(
    transferResponse.ok(),
    `Real Django transfer failed: ${JSON.stringify(transferEnvelope)}`,
  ).toBe(true);
  expect(transferEnvelope).toMatchObject({
    success: true,
    data: { bank_transfer_status: 'successful', loan_account_status: 'active' },
  });

  await expect(page.getByText('Successful', { exact: true }).first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'Send disbursement advice' })).toBeVisible();
  await shot(page, 'transfer-and-advice-success.png');

  await switchActor(page, creditEmail);
  await open(page, 'Loan Accounts');
  await page.getByText(accountNumber, { exact: true }).click();
  await expect(page.getByText('Active', { exact: true })).toBeVisible();
  await expect(page.getByText('₹4,00,000.00 disbursed', { exact: true })).toBeVisible();
  await shot(page, 'loan-account-active-summary.png');

  await switchActor(page, financeEmail);
  await page.locator('button:has(.lucide-bell)').click();
  await page.getByRole('button', { name: 'View all notifications' }).click();
  const missing = page.locator('div.w-full.p-4').filter({ hasText: 'Open inaccessible loan account' });
  await missing.getByRole('button', { name: 'Open loan account' }).click();
  await expect(page.getByText('Loan Accounts Unavailable', { exact: true })).toBeVisible();
  await expect(page.getByText('The loan account was not found or is inaccessible.')).toBeVisible();
  await shot(page, 'loan-account-safe-error.png');

  writeAndVerifyManifest();
});

const open = async (page: Page, name: string) => {
  await page.getByRole('button', { name, exact: true }).click();
  await page.waitForLoadState('networkidle');
};

const switchActor = async (page: Page, email: string) => {
  await page.evaluate(() => localStorage.removeItem('sfpcl_staff_auth_session'));
  await page.reload();
  await staffLogin(page, email, password);
};

const cardWithHeading = (page: Page, heading: string) => page
  .getByRole('heading', { name: heading, exact: true })
  .locator('xpath=ancestor::div[contains(concat(" ", normalize-space(@class), " "), " card ")][1]');

const shot = async (page: Page, name: typeof screenshots[number], locator?: Locator) => {
  const output = path.join(evidenceDir!, name);
  if (locator) await locator.screenshot({ path: output, animations: 'disabled' });
  else await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
};

const advanceFixture = (flag: '--make-ready' | '--prepare-transfer') => {
  execFileSync(
    djangoPython!,
    [path.join(repoRoot, 'sfpcl_credit', 'manage.py'), 'seed_epic_009_e2e_fixture', flag],
    {
      cwd: repoRoot,
      env: {
        ...process.env,
        SFPCL_DB_PATH: e2eDbPath,
        SFPCL_DOCUMENT_STORAGE_ROOT: e2eStorageRoot,
        SFPCL_DEBUG: 'true',
        SFPCL_ALLOW_E2E_SEED: 'true',
      },
      stdio: 'pipe',
    },
  );
};

const transferEvidenceId = async (page: Page): Promise<string> => page.evaluate(async () => {
  const raw = localStorage.getItem('sfpcl_staff_auth_session');
  if (!raw) throw new Error('Authenticated staff session is required');
  const session = JSON.parse(raw) as { accessToken: string };
  const response = await fetch('http://127.0.0.1:8000/api/v1/notifications/?category=finance', {
    headers: { Authorization: `Bearer ${session.accessToken}`, Accept: 'application/json' },
  });
  const envelope = await response.json() as {
    success: boolean;
    data: Array<{ notification_type: string; related_entity_id: string | null }>;
  };
  if (!response.ok || !envelope.success) throw new Error('Real notification API failed');
  const notification = envelope.data.find(row => row.notification_type === 'e2e_transfer_evidence');
  if (!notification?.related_entity_id) throw new Error('Transfer evidence notification is missing');
  return notification.related_entity_id;
});

const browserLocalMinuteAfter = (page: Page, instant: string): Promise<string> => page.evaluate(value => {
  const localValue = new Date(value);
  if (Number.isNaN(localValue.getTime())) throw new Error('Django authorisation time is invalid');
  localValue.setSeconds(0, 0);
  localValue.setMinutes(localValue.getMinutes() + 1);
  const part = (number: number) => String(number).padStart(2, '0');
  return `${localValue.getFullYear()}-${part(localValue.getMonth() + 1)}-${part(localValue.getDate())}`
    + `T${part(localValue.getHours())}:${part(localValue.getMinutes())}`;
}, instant);

const clearPriorEvidence = () => {
  fs.mkdirSync(evidenceDir!, { recursive: true });
  for (const name of [...screenshots, 'epic-009-screenshot-sha256.txt']) {
    const target = path.join(evidenceDir!, name);
    if (fs.existsSync(target)) fs.unlinkSync(target);
  }
};

const writeAndVerifyManifest = () => {
  const rows = screenshots.map(name => {
    const file = path.join(evidenceDir!, name);
    expect(fs.existsSync(file), `${name} must be freshly captured`).toBe(true);
    return { name, hash: createHash('sha256').update(fs.readFileSync(file)).digest('hex') };
  });
  expect(new Set(rows.map(row => row.hash)).size).toBe(screenshots.length);
  const manifest = rows
    .slice()
    .sort((left, right) => left.name.localeCompare(right.name))
    .map(row => `${row.hash}  ${row.name}`)
    .join('\n');
  fs.writeFileSync(path.join(evidenceDir!, 'epic-009-screenshot-sha256.txt'), `${manifest}\n`);
};
