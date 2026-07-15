import { expect, test, type Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 390, height: 844 } });

test('MP11 uploads and resubmits through the real Django lifecycle boundary', async ({ page }) => {
  await portalLogin(page);
  await page.getByRole('button', { name: 'My Applications', exact: true }).click();
  await page.getByText('LO000008L4-R').click();
  await page.getByRole('button', { name: 'Submitted Data & Deficiencies' }).click();
  await expect(page.getByRole('heading', { name: 'Deficiency Response', exact: true })).toBeVisible();
  const deficiencyResponse = page.getByRole('region', { name: 'Deficiency Response' });
  await expect(deficiencyResponse.getByText('Upload the missing six-month bank statement.', { exact: true })).toBeVisible();
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-deficiency-mobile-response.png'), fullPage: true });

  await page.getByLabel('Replacement document').setInputFiles({
    name: 'corrected-bank-statement.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF corrected bank statement'),
  });
  await page.getByLabel('Borrower response remark').fill('The complete six-month statement is attached.');
  await page.getByRole('button', { name: 'Upload response' }).click();
  await expect(page.getByText('Response uploaded for SFPCL review.')).toBeVisible();
  await page.getByLabel('Replacement document').setInputFiles({
    name: 'corrected-bank-statement-v2.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF corrected bank statement v2'),
  });
  await page.getByLabel('Borrower response remark').fill('A clearer complete statement supersedes the first upload.');
  await page.getByRole('button', { name: 'Upload response' }).click();
  await expect(page.getByText('Response uploaded for SFPCL review.')).toBeVisible();
  await page.getByRole('button', { name: 'Resubmit corrections' }).click();
  const applicationHeader = page.getByRole('heading', { name: 'Application LO000008L4-R', exact: true }).locator('..');
  await expect(applicationHeader.getByText('Submitted - Pending Completeness Check', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Deficiency Response', exact: true })).toHaveCount(0);

  const contract = await page.evaluate(async () => {
    const auth = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const headers = { Authorization: `Bearer ${auth.accessToken}` };
    const applications = (await (await fetch('http://127.0.0.1:8000/api/v1/portal/applications/', { headers })).json()).data.items;
    const returned = applications.find((item: { application_reference_number: string }) => item.application_reference_number === 'LO000008L4-R');
    const detailResponse = await fetch(`http://127.0.0.1:8000/api/v1/portal/applications/${returned.loan_application_id}/`, { headers });
    const deficienciesResponse = await fetch(`http://127.0.0.1:8000/api/v1/portal/applications/${returned.loan_application_id}/deficiencies/`, { headers });
    const deficiencies = (await deficienciesResponse.json()).data;
    const replayResponse = await fetch(`http://127.0.0.1:8000/api/v1/portal/applications/${returned.loan_application_id}/deficiencies/resubmit/`, {
      method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: '{}',
    });
    return {
      detailStatus: detailResponse.status,
      applicationStatus: (await detailResponse.json()).data.application_status,
      deficienciesStatus: deficienciesResponse.status,
      responseStatus: deficiencies.items[0].response.response_status,
      staffDeficiencyStatus: deficiencies.items[0].resolution_status,
      resubmissionAllowed: deficiencies.resubmission_allowed,
      replayStatus: replayResponse.status,
    };
  });
  expect(contract).toEqual({
    detailStatus: 200,
    applicationStatus: 'submitted',
    deficienciesStatus: 200,
    responseStatus: 'submitted_for_review',
    staffDeficiencyStatus: 'open',
    resubmissionAllowed: false,
    replayStatus: 409,
  });
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-deficiency-resubmitted.png'), fullPage: true });
});

async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('e2e.portal@sfpcl.example');
  await page.getByLabel('Password').fill('E2eTracer123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}
