import fs from 'fs';
import path from 'path';
import { expect, test, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for the 012DAC reports, exports, and audit acceptance contract');
}
fs.mkdirSync(evidenceDir, { recursive: true });

test.beforeEach(async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => localStorage.setItem(
    'sfpcl_staff_auth_session',
    JSON.stringify({ accessToken: 'report-browser-access', refreshToken: 'report-browser-refresh' }),
  ));
  await page.route('**/api/v1/auth/me/', route => ok(route, reportReader));
  await page.route('**/api/v1/dashboard/', route => ok(route, {
    role_context: 'cfo',
    cards: [],
    tasks: [],
  }));
  await page.route('**/api/v1/reports/loan-portfolio/**', route => {
    const url = new URL(route.request().url());
    const requestedPage = Number(url.searchParams.get('page') ?? '1');
    const rows = requestedPage === 2 ? [portfolioRow(21)] : Array.from(
      { length: 20 },
      (_value, index) => portfolioRow(index + 1),
    );
    return listOk(route, rows, {
      page: requestedPage,
      page_size: 20,
      total_count: 21,
      total_pages: 2,
      has_next: requestedPage === 1,
      has_previous: requestedPage === 2,
    });
  });
});

test('S69 report results retain backend filters, ordering, pagination, and reconciliation', async ({ page }) => {
  const reportRequests: URL[] = [];
  const mutations: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/reports/loan-portfolio/') reportRequests.push(url);
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Reports & MIS' }).click();
  await expect(page.getByRole('heading', { name: 'Reports & MIS Center' })).toBeVisible();
  await expect(page.getByText('LN-BROWSER-REPORT-001')).toBeVisible();
  await expect(page.getByText('21 records')).toBeVisible();

  await page.getByLabel('As of date').fill('2026-06-30');
  await page.getByLabel('Account status').fill('active');
  await page.getByRole('button', { name: 'Apply filters' }).click();
  await expect.poll(() => reportRequests.at(-1)?.search).toContain(
    'status=active&as_of_date=2026-06-30',
  );

  await page.getByRole('button', { name: 'Sort by Total outstanding' }).click();
  await expect.poll(() => reportRequests.at(-1)?.searchParams.get('ordering'))
    .toBe('total_outstanding');
  await expect.poll(() => reportRequests.at(-1)?.searchParams.get('status')).toBe('active');

  await page.getByRole('button', { name: 'Next' }).click();
  await expect(page.getByText('LN-BROWSER-REPORT-021')).toBeVisible();
  await expect(page.getByText('Page 2 of 2')).toBeVisible();
  expect(reportRequests.at(-1)?.searchParams.get('page')).toBe('2');
  expect(reportRequests.at(-1)?.searchParams.get('as_of_date')).toBe('2026-06-30');
  expect(reportRequests.at(-1)?.searchParams.get('status')).toBe('active');
  expect(reportRequests.at(-1)?.searchParams.get('ordering')).toBe('total_outstanding');
  expect(mutations).toEqual([]);

  await page.screenshot({
    path: path.join(evidenceDir, 'report-results.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('report export preserves job identity and enables only the audited ready download', async ({ page }) => {
  let statusReads = 0;
  const exportRequests: { body: unknown; idempotencyKey: string | undefined }[] = [];
  await page.route('**/api/v1/reports/exports/', route => {
    exportRequests.push({
      body: route.request().postDataJSON(),
      idempotencyKey: route.request().headers()['idempotency-key'],
    });
    return ok(route, exportJob('queued'));
  });
  await page.route('**/api/v1/reports/exports/export-browser-012dab/', route => {
    statusReads += 1;
    return ok(route, statusReads === 1
      ? exportJob('running')
      : {
          ...exportJob('completed'),
          checksum_sha256: 'browser-export-checksum',
          file_size_bytes: 128,
          download_url: '/api/v1/reports/exports/export-browser-012dab/download/?token=signed-browser-grant',
          expires_at: '2026-07-25T06:15:00Z',
        });
  });
  await page.route('**/api/v1/reports/exports/export-browser-012dab/download/?token=*', route => (
    route.fulfill({
      status: 200,
      contentType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      body: 'masked audited browser export',
    })
  ));

  await page.goto('/');
  await page.getByRole('button', { name: 'Reports & MIS' }).click();
  await expect(page.getByText('LN-BROWSER-REPORT-001')).toBeVisible();
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  await expect(page.getByText('Export queued')).toBeVisible();
  await expect(page.getByText(/export-browser-012dab/)).toBeVisible();
  expect(exportRequests).toHaveLength(1);
  expect(exportRequests[0].body).toEqual({
    report_code: 'loan-portfolio',
    format: 'xlsx',
    filters: { ordering: '-created_at' },
  });
  expect(exportRequests[0].idempotencyKey).toBeTruthy();

  await page.getByRole('button', { name: 'Refresh export status' }).click();
  await expect(page.getByText('Export running')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download export' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Refresh export status' }).click();
  await expect(page.getByText('Export ready')).toBeVisible();

  const auditedDownload = page.waitForRequest(request => (
    new URL(request.url()).pathname
      === '/api/v1/reports/exports/export-browser-012dab/download/'
  ));
  await page.getByRole('button', { name: 'Download export' }).click();
  await auditedDownload;
  await expect(page.getByText('Audited download started.')).toBeVisible();

  await page.screenshot({
    path: path.join(evidenceDir, 'export-job-status.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('register export keeps backend masking visible and failed or stale jobs non-downloadable', async ({ page }) => {
  await page.route('**/api/v1/reports/exports/', route => ok(route, {
    ...exportJob('completed'),
    export_job_id: 'masked-register-export-012dab',
    report_code: 'loan-portfolio',
    checksum_sha256: 'masked-register-checksum',
    file_size_bytes: 256,
    download_url: null,
    download_expired: true,
    expires_at: '2026-07-25T05:45:00Z',
  }));

  await page.goto('/');
  await page.getByRole('button', { name: 'Registers' }).click();
  await expect(page.getByRole('heading', { name: 'Registers' })).toBeVisible();
  await expect(page.getByText('Scoped Report Member 1').first()).toBeVisible();
  await page.getByRole('button', { name: 'Export Register' }).click();
  await expect(page.getByText('Export expired')).toBeVisible();
  await expect(page.getByText(/PAN, Aadhaar, bank, cheque/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Download export' })).toHaveCount(0);

  await page.screenshot({
    path: path.join(evidenceDir, 'masked-export.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('S74 audit explorer preserves backend scope, filters, pagination, and restricted-field protection', async ({ page }) => {
  const auditRequests: URL[] = [];
  const auditMutations: string[] = [];
  await page.route('**/api/v1/auth/me/', route => ok(route, auditReader));
  await page.route('**/api/v1/dashboard/', route => ok(route, {
    role_context: 'internal_auditor',
    cards: [],
    tasks: [],
  }));
  await page.route('**/api/v1/archive-records/**', route => listOk(route, [], emptyPagination));
  await page.route('**/api/v1/audit-observations/**', route => listOk(route, [], emptyPagination));
  await page.route('**/api/v1/audit-logs/**', route => {
    const url = new URL(route.request().url());
    const requestedPage = Number(url.searchParams.get('page') ?? '1');
    const rows = requestedPage === 2 ? [auditRow(21)] : Array.from(
      { length: 20 },
      (_value, index) => auditRow(index + 1),
    );
    return listOk(route, rows, {
      page: requestedPage,
      page_size: 20,
      total_count: 21,
      total_pages: 2,
      has_next: requestedPage === 1,
      has_previous: requestedPage === 2,
    });
  });
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/audit-logs/') auditRequests.push(url);
    if (
      (url.pathname === '/api/v1/audit-logs/' || url.pathname.startsWith('/api/v1/audit-observations/'))
      && request.method() !== 'GET'
    ) {
      auditMutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Audit & Archive' }).click();
  await expect(page.getByRole('heading', { name: 'Audit & Archive' })).toBeVisible();
  await expect(page.getByText('compliance.evidence_submitted').first()).toBeVisible();
  await expect(page.getByText('ABCDE1234F')).toHaveCount(0);
  await expect(page.getByText('123456789012')).toHaveCount(0);
  await expect(page.getByText('private/audit/evidence.pdf')).toHaveCount(0);

  await page.getByLabel('Entity type').fill('compliance_evidence');
  await page.getByLabel('Action', { exact: true }).fill('compliance.evidence_submitted');
  await page.getByLabel('Actor user ID').fill('actor-browser-012dac');
  await page.getByLabel('From date').fill('2026-07-01');
  await page.getByLabel('To date').fill('2026-07-25');
  await page.getByRole('button', { name: 'Apply audit filters' }).click();
  await expect.poll(() => auditRequests.at(-1)?.search).toContain(
    'entity_type=compliance_evidence&action=compliance.evidence_submitted&actor_user_id=actor-browser-012dac&created_from=2026-07-01&created_to=2026-07-25',
  );

  await page.getByRole('button', { name: 'Next audit page' }).click();
  await expect(page.getByText('evidence-browser-021')).toBeVisible();
  await expect(page.getByText(/Page 2 of 2/)).toBeVisible();
  expect(auditRequests.at(-1)?.searchParams.get('page')).toBe('2');
  expect(auditMutations).toEqual([]);
  await expect(page.getByRole('button', { name: /edit|delete|update audit/i })).toHaveCount(0);

  await page.screenshot({
    path: path.join(evidenceDir, 'audit-explorer.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('scoped Internal Auditor records and revisits a separate immutable observation', async ({ page }) => {
  const observationPosts: unknown[] = [];
  let observationCreated = false;
  const recordedObservation = auditObservation();
  await page.route('**/api/v1/auth/me/', route => ok(route, auditReader));
  await page.route('**/api/v1/dashboard/', route => ok(route, {
    role_context: 'internal_auditor',
    cards: [],
    tasks: [],
  }));
  await page.route('**/api/v1/archive-records/**', route => listOk(route, [], emptyPagination));
  await page.route('**/api/v1/audit-logs/**', route => listOk(route, [auditRow(1)], {
    ...emptyPagination,
    total_count: 1,
  }));
  await page.route('**/api/v1/audit-observations/**', route => {
    if (route.request().method() === 'POST') {
      observationPosts.push(route.request().postDataJSON());
      observationCreated = true;
      return ok(route, recordedObservation);
    }
    return listOk(route, observationCreated ? [recordedObservation] : [], {
      ...emptyPagination,
      total_count: observationCreated ? 1 : 0,
    });
  });
  await page.route('**/api/v1/audit-observations/observation-browser-012dac/', route => (
    ok(route, recordedObservation)
  ));

  await page.goto('/');
  await page.getByRole('button', { name: 'Audit & Archive' }).click();
  await page.getByRole('button', { name: 'View audit event audit-log-browser-001' }).click();
  await page.getByRole('button', { name: 'Sample this event' }).click();
  await page.getByLabel('Auditor observation').fill(
    'M14-FR-012 sample is complete and traceable.',
  );
  await page.getByRole('button', { name: 'Record observation' }).click();

  await expect(page.getByText('Observation recorded as immutable.')).toBeVisible();
  expect(observationPosts).toEqual([{
    audit_scope: 'audit_readonly',
    observation: 'M14-FR-012 sample is complete and traceable.',
    source_references: [{
      source_type: 'audit_log',
      source_id: 'audit-log-browser-001',
    }],
  }]);
  await expect(page.getByText('This audit event is immutable and read-only.')).toBeVisible();

  await page.screenshot({
    path: path.join(evidenceDir, 'audit-observation-recorded.png'),
    fullPage: true,
    animations: 'disabled',
  });

  await page.getByRole('button', { name: 'Close audit event detail' }).click();
  await page.getByRole('button', { name: 'Auditor Observations' }).click();
  await page.getByRole('button', { name: 'View observation observation-browser-012dac' }).click();
  await expect(page.getByRole('heading', { name: 'Observation Detail' })).toBeVisible();
  await expect(page.getByText(
    'Creator, scope, source references, text and time cannot be edited.',
  )).toBeVisible();
  await expect(page.getByRole('button', { name: /edit|save|delete|update/i })).toHaveCount(0);
});

const reportReader = {
  user_id: 'report-reader-browser-012daa',
  full_name: 'Browser CFO Report Reader',
  email: 'report-reader-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'cfo', role_name: 'CFO' }],
  teams: [{ team_code: 'finance', team_name: 'Finance' }],
  role_codes: ['cfo'],
  team_codes: ['finance'],
  permissions: [
    'reports.application_pipeline.read',
    'reports.portfolio.read',
    'reports.dpd.read',
    'reports.compliance.read',
    'reports.export',
    'approvals.sanction_register.read',
    'documents.checklist.read',
    'finance.disbursement.readiness',
    'finance.loan_account.read',
    'monitoring.dpd.read',
    'compliance.section186.read',
    'compliance.nbfc_test.read',
  ],
  available_actions: [],
};

const auditReader = {
  user_id: 'auditor-browser-012dac',
  full_name: 'Browser Internal Auditor',
  email: 'auditor-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'internal_auditor', role_name: 'Internal Auditor' }],
  teams: [{ team_code: 'audit', team_name: 'Audit' }],
  role_codes: ['internal_auditor'],
  team_codes: ['audit'],
  permissions: [
    'audit.audit_log.read',
    'audit.observation.read',
    'audit.observation.create',
    'closure.archive.read',
  ],
  available_actions: [],
};

const portfolioRow = (index: number) => ({
  loan_account_id: `loan-browser-report-${index}`,
  loan_account_number: `LN-BROWSER-REPORT-${String(index).padStart(3, '0')}`,
  loan_application_id: `application-browser-report-${index}`,
  member_id: `member-browser-report-${index}`,
  borrower_name: index === 21 ? 'Seeded Browser Reconciled Member' : `Scoped Report Member ${index}`,
  loan_account_status: 'active',
  sanctioned_amount: '150000.00',
  disbursed_amount: '150000.00',
  principal_outstanding: index === 21 ? '125000.00' : '100000.00',
  interest_outstanding: index === 21 ? '5000.00' : '2500.00',
  charges_outstanding: '0.00',
  total_outstanding: index === 21 ? '130000.00' : '102500.00',
  loan_type: 'short_term',
  tenure_start_date: '2026-04-01',
  tenure_end_date: '2027-03-31',
  repayment_date: '2026-09-30',
  current_interest_rate: '10.0000',
  created_at: `2026-04-${String(Math.min(index, 28)).padStart(2, '0')}T10:00:00Z`,
});

const exportJob = (status: 'queued' | 'running' | 'completed' | 'failed') => ({
  export_job_id: 'export-browser-012dab',
  report_code: 'loan-portfolio',
  format: 'xlsx',
  filters: { ordering: '-created_at' },
  status,
  failure_code: status === 'failed' ? 'RENDER_FAILED' : null,
  idempotency_replayed: false,
  requested_at: '2026-07-25T05:30:00Z',
  started_at: status === 'queued' ? null : '2026-07-25T05:30:01Z',
  completed_at: status === 'completed' || status === 'failed' ? '2026-07-25T05:30:02Z' : null,
});

const auditRow = (index: number) => ({
  audit_log_id: `audit-log-browser-${String(index).padStart(3, '0')}`,
  actor: {
    user_id: 'actor-browser-012dac',
    full_name: 'Browser Internal Auditor',
  },
  actor_type: 'user',
  actor_role_codes: ['internal_auditor'],
  actor_team_codes: ['audit'],
  action: 'compliance.evidence_submitted',
  module: 'compliance',
  entity_type: 'compliance_evidence',
  entity_id: `evidence-browser-${String(index).padStart(3, '0')}`,
  linked_record: {
    entity_type: 'compliance_evidence',
    entity_id: `evidence-browser-${String(index).padStart(3, '0')}`,
  },
  old_value: {
    status: 'missing',
    pan_number: 'ABCDE1234F',
  },
  new_value: {
    status: 'accepted',
    bank_account_number: '123456789012',
    storage_key: 'private/audit/evidence.pdf',
  },
  reason: index === 1 ? 'M14-FR-012 quarterly sample' : 'Governed audit sample',
  outcome: 'success',
  request_id: `request-browser-${index}`,
  ip_address: '10.0.0.8',
  device: 'AuditBrowser/1.0',
  created_at: `2026-07-25T06:${String(Math.min(index, 59)).padStart(2, '0')}:00Z`,
});

const auditObservation = () => ({
  audit_observation_id: 'observation-browser-012dac',
  creator: {
    user_id: 'auditor-browser-012dac',
    full_name: 'Browser Internal Auditor',
    role_code: 'internal_auditor',
    team_codes: ['audit'],
  },
  audit_scope: 'audit_readonly',
  observation: 'M14-FR-012 sample is complete and traceable.',
  source_references: [{
    source_type: 'audit_log',
    source_id: 'audit-log-browser-001',
    entity_type: 'compliance_evidence',
    entity_id: 'evidence-browser-001',
  }],
  created_at: '2026-07-25T06:10:00Z',
});

const emptyPagination = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const ok = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    meta: { request_id: 'report-browser-contract' },
  }),
});

const listOk = (
  route: Route,
  data: unknown[],
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  },
) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    pagination,
    meta: { request_id: 'report-browser-list-contract' },
  }),
});
