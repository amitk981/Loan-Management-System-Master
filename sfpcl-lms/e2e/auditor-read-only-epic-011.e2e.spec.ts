import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for auditor Epic 011 acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await page.addInitScript(() => localStorage.setItem(
    'sfpcl_staff_auth_session',
    JSON.stringify({ accessToken: 'auditor-access', refreshToken: 'auditor-refresh' }),
  ));
  await page.route('**/api/v1/auth/me/', route => ok(route, auditor));
  await page.route('**/api/v1/dashboard/', route => ok(route, { role_context: 'auditor', cards: [], tasks: [] }));
});

test('auditor opens populated action-free Epic 011 evidence', async ({ page }) => {
  const mutationRequests: string[] = [];
  page.on('request', request => {
    if (['POST', 'PATCH', 'DELETE'].includes(request.method()) && new URL(request.url()).pathname.includes('/api/v1/')) {
      mutationRequests.push(`${request.method()} ${new URL(request.url()).pathname}`);
    }
  });
  await page.route('**/api/v1/auditor/epic-011/', route => ok(route, populated));

  await openAuditorView(page);
  await expect(page.getByRole('heading', { name: 'Epic 011 Audit View' })).toBeVisible();
  await expect(page.getByText('LN-AUD-BROWSER-001')).toBeVisible();
  await page.getByLabel('Record family').selectOption('compliance');
  await page.getByRole('button', { name: 'View task-browser-1' }).click();
  await expect(page.getByText('audit-task-browser-1')).toBeVisible();
  await expect(page.getByRole('button', {
    name: /^(approve|review evidence|update|close loan|issue noc|return security|archive file)$/i,
  })).toHaveCount(0);
  expect(mutationRequests).toEqual([]);
  await capture(page, 'auditor-epic-011-populated.png');
});

test('auditor sees the explicit empty state', async ({ page }) => {
  await page.route('**/api/v1/auditor/epic-011/', route => ok(route, empty));
  await openAuditorView(page);
  await expect(page.getByRole('heading', { name: 'Epic 011 Audit View' })).toBeVisible();
  await expect(page.getByText('No Epic 011 records match this view.')).toBeVisible();
  await capture(page, 'auditor-epic-011-empty.png');
});

test('missing audit scope renders the explicit unauthorised state', async ({ page }) => {
  await page.route('**/api/v1/auditor/epic-011/', route => route.fulfill({
    status: 403,
    contentType: 'application/json',
    body: JSON.stringify({
      success: false,
      error: { code: 'FORBIDDEN', message: 'Compliance authority is required.' },
    }),
  }));
  await openAuditorView(page);
  await expect(page.getByText('Auditor access is not authorised.')).toBeVisible();
  await capture(page, 'auditor-epic-011-unauthorised.png');
});

async function openAuditorView(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Audit & Archive' }).click();
}

const capture = (page: Page, fileName: string) =>
  page.screenshot({ path: path.join(evidenceDir, fileName), fullPage: true, animations: 'disabled' });

const ok = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, meta: { request_id: 'auditor-browser' } }),
});

const auditor = {
  user_id: 'auditor-browser',
  full_name: 'Browser Internal Auditor',
  email: 'auditor-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'internal_auditor', role_name: 'Internal Auditor' }],
  teams: [{ team_code: 'audit', team_name: 'Audit Team' }],
  role_codes: ['internal_auditor'],
  team_codes: ['audit'],
  permissions: [
    'audit.audit_log.read',
    'audit.workflow_event.read',
    'audit.version_history.read',
    'reports.compliance.read',
    'defaults.case.read',
    'closure.archive.read',
    'compliance.control.read',
    'compliance.task.read',
    'compliance.section186.read',
    'compliance.nbfc_test.read',
    'compliance.grievance.read',
  ],
  available_actions: [],
};

const empty = {
  summary: { default_cases: 0, closures: 0, compliance_items: 0, grievances: 0 },
  default_cases: [],
  closures: [],
  compliance_items: [],
  grievances: [],
};

const populated = {
  summary: { default_cases: 1, closures: 1, compliance_items: 1, grievances: 1 },
  default_cases: [{
    default_case_id: 'default-browser-1',
    loan_account_number: 'LN-AUD-BROWSER-001',
    borrower_name: 'Masked Browser Member',
    default_case_status: 'recovery_in_progress',
    total_outstanding: '125000.00',
    audit_references: ['audit-default-browser-1'],
    workflow_references: ['workflow-default-browser-1'],
  }],
  closures: [{
    loan_closure_id: 'closure-browser-1',
    loan_account_number: 'LN-AUD-BROWSER-002',
    borrower_name: 'Closed Browser Member',
    closure_stage: 'financially_closed',
    closed_at: '2026-07-22T10:00:00Z',
    requirements: [{ requirement_type: 'noc', requirement_status: 'completed' }],
    audit_references: ['audit-closure-browser-1'],
    workflow_references: ['workflow-closure-browser-1'],
  }],
  compliance_items: [{
    record_type: 'task',
    record_id: 'task-browser-1',
    details: {
      control_code: 'RECOVERY_CONDUCT',
      task_period: '2026-Q2',
      task_status: 'evidence_submitted',
      evidence_metadata: [{
        evidence_id: 'evidence-browser-1',
        document_id: 'document-browser-1',
        file_name: 'recovery-conduct.pdf',
        sensitivity_level: 'restricted',
        download_path: '/api/v1/document-files/document-browser-1/download/',
      }],
    },
    audit_references: ['audit-task-browser-1'],
    workflow_references: [],
  }],
  grievances: [{
    grievance_id: 'grievance-browser-1',
    grievance_reference: 'GRV-2026-AUD-BROWSER',
    grievance_category: 'recovery_conduct_issue',
    status: 'open',
    description: 'Recovery interaction requires review.',
    audit_references: ['audit-grievance-browser-1'],
    workflow_references: [],
  }],
};
