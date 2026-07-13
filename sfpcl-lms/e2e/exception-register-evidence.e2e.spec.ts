import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for Exception Register visual acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('S25 renders frozen comments and supporting metadata without granting download authority', async ({ page }) => {
  let canDownload = true;
  const observedPaths: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.startsWith('/api/v1/')) observedPaths.push(url.pathname);
  });

  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'register-access', refreshToken: 'register-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, user(canDownload)));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'cfo', cards: [], tasks: [] }));
  await page.route('**/api/v1/exception-register/**', route => {
    const url = new URL(route.request().url());
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('20');
    return paginated(route, [exceptionRow]);
  });

  await page.goto('/');
  await page.getByRole('button', { name: /^Registers$/ }).click();
  await expect(page.getByText('Frozen exception description')).toBeVisible();
  await expect(page.getByText('Seasonal exception is commercially justified.')).toBeVisible();
  await expect(page.getByText('CFO approved with monitoring.')).toBeVisible();
  await expect(page.getByText('cash-flow-evidence.pdf')).toBeVisible();
  await expect(page.getByRole('button', { name: /download/i })).toHaveCount(0);
  await expect(page.getByRole('link', { name: /download/i })).toHaveCount(0);
  await capture(page, 'exception-register-with-supporting-evidence.png');

  canDownload = false;
  await page.reload();
  await page.getByRole('button', { name: /^Registers$/ }).click();
  await expect(page.getByText('cash-flow-evidence.pdf')).toBeVisible();
  await expect(page.getByText('CFO approved with monitoring.')).toBeVisible();
  await expect(page.getByRole('button', { name: /download/i })).toHaveCount(0);
  await expect(page.getByRole('link', { name: /download/i })).toHaveCount(0);
  await capture(page, 'exception-register-evidence-denied.png');

  expect(observedPaths.some(value => value.includes('/document-files/'))).toBe(false);
});

const exceptionRow = {
  exception_register_entry_id: 'exception-visual-007', loan_application_id: 'application-visual-007', loan_account_id: null,
  approval_case_id: 'case-visual-007', cycle_number: 2, exception_type: 'exceeds_loan_limit',
  description: 'Frozen exception description', business_reason: 'Seasonal exception is commercially justified.',
  risk_assessment: 'Medium', status: 'approved', case_status: 'approved', conflict_block_reason: null,
  authority_applied_summary: 'CFO: Visual CFO (approved); Director: Visual Director One (approved); Director: Visual Director Two (approved)',
  route_approvers: [], required_approvers: [],
  approval_actions: [
    { approval_action_id: 'action-cfo', role_code: 'cfo', user_id: 'cfo-visual', full_name: 'Visual CFO', decision: 'approved', comments: 'CFO approved with monitoring.', acted_at: '2026-07-13T10:00:00Z' },
    { approval_action_id: 'action-director', role_code: 'director', user_id: 'director-visual', full_name: 'Visual Director', decision: 'approved', comments: 'Director confirms the documented controls.', acted_at: '2026-07-13T11:00:00Z' },
  ],
  supporting_documents: [
    { document_id: 'document-visual-007', file_name: 'cash-flow-evidence.pdf', mime_type: 'application/pdf', file_size_bytes: 2456, sensitivity_level: 'restricted', uploaded_at: '2026-07-13T09:00:00Z' },
  ],
  created_at: '2026-07-13T09:30:00Z', closed_at: '2026-07-13T11:00:00Z',
};

const user = (canDownload: boolean) => ({
  user_id: 'cfo-visual', full_name: 'Visual CFO', email: 'visual.cfo@sfpcl.example', status: 'active',
  roles: [{ role_code: 'cfo', role_name: 'CFO' }], teams: [], role_codes: ['cfo'], team_codes: [],
  permissions: ['approvals.exception_register.read', ...(canDownload ? ['documents.file.download'] : [])], available_actions: [],
});

const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data }) });
const paginated = (route: Route, data: unknown[]) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, pagination: { page: 1, page_size: 20, total_count: data.length, total_pages: 1, has_next: false, has_previous: false } }) });
const capture = (page: Page, fileName: string) => page.screenshot({ path: path.join(evidenceDir, fileName), fullPage: true, animations: 'disabled' });
