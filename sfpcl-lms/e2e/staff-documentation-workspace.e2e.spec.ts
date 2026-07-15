import { expect, test, type Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });
test.use({ viewport: { width: 1280, height: 720 } });

async function capture(page: Page, name: string) {
  const output = path.join(evidenceDir!, name);
  await page.screenshot({ path: output, fullPage: true, animations: 'disabled' });
  expect(fs.statSync(output).size).toBeGreaterThan(10_000);
}
test('008M2 closes the real staff documentation workspace contract', async ({ page }) => {
  await staffLogin(page, 'e2e.portal.compliance@sfpcl.example', E2E_PASSWORD);
  await page.getByRole('button', { name: 'Documentation' }).click(); await expect(page.getByRole('heading', { name: 'Document Checklist' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'LO000008L4' })).toBeVisible(); await expect(page.getByText(/Disbursement blocked:/)).toBeVisible();
  await capture(page, 'documentation-checklist-blockers.png');

  const termSheet = page.locator('tr').filter({ hasText: 'Term Sheet' });
  await expect(termSheet.getByRole('button', { name: 'Record stamp' })).toHaveCount(0);
  const boundary = await page.evaluate(async () => {
    const session = JSON.parse(localStorage.getItem('sfpcl_staff_auth_session') || '{}');
    const headers = { Authorization: `Bearer ${session.accessToken}`, 'Content-Type': 'application/json' };
    const queue = await fetch('http://127.0.0.1:8000/api/v1/documentation-workspaces/', { headers });
    const application = (await queue.json()).data.find((row: { application_reference_number: string }) => row.application_reference_number === 'LO000008L4');
    const root = `http://127.0.0.1:8000/api/v1/loan-applications/${application.loan_application_id}/documentation-workspace/`;
    const workspace = (await (await fetch(root, { headers })).json()).data;
    const term = workspace.items.find((item: { item_code: string }) => item.item_code === 'term_sheet');
    const replay = await fetch(`http://127.0.0.1:8000/api/v1/checklist-items/${term.checklist_item_id}/complete/`, {
      method: 'POST', headers, body: JSON.stringify({ loan_document_id: term.document.loan_document_id, remarks: 'Published signed Term Sheet for portal proof.' }),
    });
    const conflict = await fetch(`http://127.0.0.1:8000/api/v1/checklist-items/${term.checklist_item_id}/complete/`, {
      method: 'POST', headers, body: JSON.stringify({ loan_document_id: term.document.loan_document_id, remarks: 'Changed replay' }),
    });
    const restricted = await fetch(`${root}term_sheet/download/`, { headers });
    return { queue: queue.status, replay: replay.status, conflict: conflict.status, restricted: restricted.status };
  });
  expect(boundary).toEqual({ queue: 200, replay: 200, conflict: 409, restricted: 404 });
  await expect(termSheet.getByText('Complete', { exact: true })).toBeVisible();

  await page.getByRole('button', { name: 'Securities' }).click(); await expect(page.getByRole('heading', { name: 'Security Instruments' })).toBeVisible();
  await capture(page, 'documentation-security-workflow.png');

  await page.getByRole('button', { name: 'Checklist' }).click(); await expect(termSheet.getByRole('button', { name: 'Download' })).toHaveCount(0);
  await capture(page, 'documentation-restricted-state.png');

  await page.getByRole('button', { name: 'Approvals' }).click(); await expect(page.getByText('Senior Manager Finance', { exact: true }).last()).toBeVisible();
  await capture(page, 'documentation-final-approval.png');
});
