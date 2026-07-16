import { expect, test, type Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const evidenceRoot = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceRoot) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceRoot, { recursive: true });

test.use({ viewport: { width: 1280, height: 720 } });

test('MP07 uses the real portal session, upload, current download, and denial boundary', async ({ page }) => {
  await portalLogin(page);
  await page.getByRole('navigation').getByRole('button', { name: 'My Documents', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'My Documents', exact: true, level: 2 })).toBeVisible();

  await page.getByRole('button', { name: 'Upload Cancelled Cheque' }).click();
  await expect(page.getByText('Click to select file or drag and drop')).toBeVisible();
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-documentation-upload-modal.png'), fullPage: true });
  await page.getByLabel('Document file').setInputFiles({
    name: 'cancelled-cheque.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF real cancelled cheque'),
  });
  await page.getByLabel('Notes (optional)').fill('Borrower portal browser proof.');
  await page.getByRole('button', { name: 'Upload', exact: true }).click();
  await expect(page.getByText('Document uploaded for SFPCL review.')).toBeVisible();
  const cancelledChequeAction = page.getByRole('group', { name: 'Cancelled Cheque documentation action' });
  await expect(cancelledChequeAction.getByText('Submitted for review', { exact: true })).toBeVisible();

  await expect(page.getByText('Complete', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download Term Sheet' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Upload Term Sheet' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Re-upload Term Sheet' })).toHaveCount(0);

  const contract = await page.evaluate(async () => {
    const auth = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const headers = { Authorization: `Bearer ${auth.accessToken}`, 'X-Request-ID': 'browser-portal-download' };
    const applicationsResponse = await fetch('http://127.0.0.1:8000/api/v1/portal/applications/', { headers });
    const applications = (await applicationsResponse.json()).data.items;
    const approved = applications.find((item: { application_reference_number: string }) => item.application_reference_number === 'LO000008L4');
    const root = `http://127.0.0.1:8000/api/v1/portal/applications/${approved.loan_application_id}/documentation-actions/term_sheet`;
    const descriptorResponse = await fetch(`${root}/download/`, { headers });
    const descriptor = (await descriptorResponse.json()).data;
    const content = await fetch(`http://127.0.0.1:8000${descriptor.download_url}`, { headers });
    const tokenUrl = new URL(`http://127.0.0.1:8000${descriptor.download_url}`);
    const token = tokenUrl.searchParams.get('token') || '';
    tokenUrl.searchParams.set('token', `${token.slice(0, -1)}${token.endsWith('a') ? 'b' : 'a'}`);
    const tampered = await fetch(tokenUrl, { headers });
    const crafted = await fetch(`${root}/upload/`, { method: 'POST', headers, body: new FormData() });
    return {
      applicationStatus: applicationsResponse.status,
      descriptorStatus: descriptorResponse.status,
      contentStatus: content.status,
      cacheControl: content.headers.get('cache-control'),
      tamperedStatus: tampered.status,
      craftedStatus: crafted.status,
    };
  });
  expect(contract).toEqual({
    applicationStatus: 200,
    descriptorStatus: 200,
    contentStatus: 200,
    cacheControl: 'no-store',
    tamperedStatus: 404,
    craftedStatus: 409,
  });
  await page.screenshot({ path: path.join(evidenceRoot, 'portal-documentation-complete-upload-denied.png'), fullPage: true });
});

async function portalLogin(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open Member Portal Login' }).click();
  await page.getByLabel('Mobile Number or Email').fill('e2e.portal@sfpcl.example');
  await page.getByLabel('Password').fill('E2eTracer123!');
  await page.getByRole('button', { name: 'Sign in securely' }).click();
  await expect(page.getByRole('main').getByRole('heading', { name: 'Portal Contract Member', level: 2 })).toBeVisible();
}
