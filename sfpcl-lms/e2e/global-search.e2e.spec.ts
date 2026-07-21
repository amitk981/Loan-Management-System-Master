import { expect, test } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test.use({ viewport: { width: 1280, height: 720 } });

async function capture(page: import('@playwright/test').Page, name: string) {
  const output = path.join(evidenceDir!, name);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
}

test('010N searches real permission-scoped groups and renders the empty state', async ({ page }) => {
  const requests: Array<{ method: string; body: unknown }> = [];
  page.on('request', request => {
    if (new URL(request.url()).pathname === '/api/v1/global-search/') {
      requests.push({ method: request.method(), body: request.postDataJSON() });
    }
  });
  await staffLogin(page, 'e2e.credit.finance@sfpcl.example', E2E_PASSWORD);

  const headerSearch = page.getByPlaceholder(/Search: borrower name/);
  await headerSearch.fill('Epic 006 Browser Member');
  await headerSearch.press('Enter');
  await expect(page.getByRole('heading', { name: 'Global Search Results' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Members' })).toBeVisible();
  await expect(page.getByText('FOL-E2E-006', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Loan Applications' })).toBeVisible();
  await expect(page.getByText('LOE2E00601', { exact: true })).toBeVisible();
  expect(requests.at(-1)).toEqual({
    method: 'POST', body: { search: 'Epic 006 Browser Member', pages: {} },
  });
  expect(page.url()).not.toContain('Epic%20006');
  await capture(page, 'global-search-results.png');

  const pageSearch = page.getByPlaceholder(/Borrower, folio/);
  await pageSearch.fill('No matching authorised record');
  await page.getByRole('button', { name: 'Search', exact: true }).click();
  await expect(page.getByText('No matching records found')).toBeVisible();
  expect(requests.at(-1)).toEqual({
    method: 'POST', body: { search: 'No matching authorised record', pages: {} },
  });
  await capture(page, 'global-search-empty.png');
});
