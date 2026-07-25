import { expect, test, type Page } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { E2E_PASSWORD, TRACER_EMAIL, staffLogin } from './helpers';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for trusted browser acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

const epic009Password = 'ChecklistPass123!';
const uatPassword = 'CriticalUat123!';
const financeEmail = 'e2e.epic009.finance@sfpcl.example';
const creditEmail = 'e2e.epic009.credit@sfpcl.example';
const cfcEmail = 'e2e.epic009.cfc@sfpcl.example';
const cfoEmail = 'e2e.uat.cfo@sfpcl.example';
const accountsEmail = 'e2e.uat.accounts@sfpcl.example';
const auditorEmail = 'e2e.uat.auditor@sfpcl.example';
const zeroEmail = 'e2e.zero@sfpcl.example';
const accountNumber = 'LN-REAL-OWNER-001';
const scheduleDueDate = '2026-06-30';
const section186TaskId = '00000000-0000-4000-8320-000000000001';
const section186EvidenceId = '00000000-0000-4000-8340-000000000001';
const nbfcTaskId = '00000000-0000-4000-8320-000000000002';
const nbfcEvidenceId = '00000000-0000-4000-8340-000000000002';

test.use({ viewport: { width: 1280, height: 720 }, timezoneId: 'Asia/Kolkata' });

test('critical UAT tracer proves the automated public journeys and retains the manual boundary', async ({ page }) => {
  const startedAt = Date.now();
  const results: Record<string, unknown> = {};

  await test.step('UAT-001/011/012/013: standard physical-share loan reaches active disbursement', async () => {
    await staffLogin(page, financeEmail, epic009Password);
    await page.getByRole('button', { name: 'Loan Accounts', exact: true }).click();
    await expect(page.getByText(accountNumber, { exact: true })).toBeVisible();

    await page.getByRole('button', { name: 'SAP & Disbursement', exact: true }).click();
    await page.waitForLoadState('networkidle');
    await page.getByLabel('Final verification comments').fill(
      'All current owner evidence verified for critical UAT.',
    );
    const initiation = page.waitForResponse(response =>
      response.request().method() === 'POST'
      && /\/api\/v1\/loan-accounts\/[^/]+\/disbursements\/initiate\/$/.test(response.url()),
    );
    await page.getByRole('button', { name: 'Initiate payment' }).click();
    const initiationEnvelope = await successEnvelope(await initiation);
    expect(initiationEnvelope.data).toMatchObject({
      initiation_status: 'initiated',
      authorisation_status: 'pending',
      bank_transfer_status: 'pending',
    });

    await switchActor(page, cfcEmail, epic009Password);
    await page.getByRole('button', { name: 'Payment Authorisation', exact: true }).click();
    await page.getByLabel('Comments').fill('Independent CFC authorisation retained.');
    const authorisation = page.waitForResponse(response =>
      response.request().method() === 'POST'
      && /\/api\/v1\/disbursements\/[^/]+\/authorise\/$/.test(response.url()),
    );
    await page.getByRole('button', { name: 'Authorise payment' }).click();
    const authorisationEnvelope = await successEnvelope(await authorisation);
    expect(authorisationEnvelope.data).toMatchObject({
      authorisation_status: 'approved',
      bank_transfer_status: 'pending',
    });

    await switchActor(page, financeEmail, epic009Password);
    await page.getByRole('button', { name: 'SAP & Disbursement', exact: true }).click();
    const evidenceId = await transferEvidenceId(page);
    const transferDateTime = await browserLocalMinuteAfter(
      page,
      String(authorisationEnvelope.data.authorised_at),
    );
    await page.getByLabel('UTR / bank reference').fill('RBL-CRITICAL-UAT-UTR');
    await page.getByLabel('Transfer date and time').fill(transferDateTime);
    await page.getByLabel('Bank evidence document ID').fill(evidenceId);
    await expect(page.getByLabel('UTR / bank reference')).toHaveValue('RBL-CRITICAL-UAT-UTR');
    await expect(page.getByLabel('Transfer date and time')).toHaveValue(transferDateTime);
    await expect(page.getByLabel('Bank evidence document ID')).toHaveValue(evidenceId);
    const transfer = page.waitForResponse(response =>
      response.request().method() === 'POST'
      && /\/api\/v1\/disbursements\/[^/]+\/mark-transfer-successful\/$/.test(response.url()),
    );
    const transferRequest = page.waitForRequest(request =>
      request.method() === 'POST'
      && /\/api\/v1\/disbursements\/[^/]+\/mark-transfer-successful\/$/.test(request.url()),
    );
    await page.getByRole('button', { name: 'Record transfer success' }).click();
    expect((await transferRequest).postDataJSON()).toMatchObject({
      bank_reference_number: 'RBL-CRITICAL-UAT-UTR',
      bank_transfer_evidence_document_id: evidenceId,
    });
    const transferEnvelope = await successEnvelope(await transfer);
    expect(transferEnvelope.data).toMatchObject({
      bank_transfer_status: 'successful',
      loan_account_status: 'active',
    });

    await switchActor(page, creditEmail, epic009Password);
    await page.getByRole('button', { name: 'Loan Accounts', exact: true }).click();
    await page.getByText(accountNumber, { exact: true }).click();
    await expect(page.getByText('Active', { exact: true })).toBeVisible();
    await expect(page.getByText('₹4,00,000.00 disbursed', { exact: true })).toBeVisible();
    await page.screenshot({
      path: path.join(evidenceDir, 'critical-uat-standard-loan.png'),
      fullPage: true,
      animations: 'disabled',
    });
    results.standardLoan = transferEnvelope.data;
  });

  let accountId = '';
  await test.step('UAT-006/007/008: below, at, above, and exception approval rules are canonical', async () => {
    await switchActor(page, cfoEmail, uatPassword);
    const rules = await api(page, '/api/v1/approval-matrix-rules/?page=1&page_size=100');
    expect(rules.status).toBe(200);
    const rows = asRows(rules.data);
    expect(rows).toEqual(expect.arrayContaining([
      expect.objectContaining({
        amount_min: '0.00',
        amount_max: '500000.00',
        required_director_count: 1,
      }),
      expect.objectContaining({
        amount_min: '500000.01',
        amount_max: null,
        required_director_count: 2,
      }),
      expect.objectContaining({
        condition_code: 'exceeds_permissible_limit',
        required_director_count: 2,
      }),
    ]));

    await switchActor(page, 'e2e.portal.cfo@sfpcl.example', E2E_PASSWORD);
    const cases = await api(page, '/api/v1/approval-cases/?page=1&page_size=100');
    expect(cases.status).toBe(200);
    const belowThresholdCase = asRows(cases.data).find(row => row.amount === '400000.00');
    expect(belowThresholdCase).toMatchObject({
      amount: '400000.00',
      current_status: 'approved',
      matrix_projection: expect.objectContaining({
        amount_max: '500000.00',
        required_director_count: 1,
      }),
    });

    await switchActor(page, zeroEmail, E2E_PASSWORD);
    const invalidAuthority = await api(
      page,
      `/api/v1/approval-cases/${String(belowThresholdCase!.approval_case_id)}/approve/`,
      {
        method: 'POST',
        body: {
          version: belowThresholdCase!.version,
          comments: 'A zero-authority actor must never approve an exception.',
        },
      },
    );
    expect(invalidAuthority.status).toBe(403);
    results.approvalBoundaries = {
      belowThresholdCase,
      atThresholdRule: rows.find(row => row.amount_max === '500000.00'),
      aboveThresholdRule: rows.find(row => row.amount_min === '500000.01'),
      exceptionRule: rows.find(row => row.condition_code === 'exceeds_permissible_limit'),
      invalidAuthority: invalidAuthority.error,
    };
    results.approvalRules = rows.map(row => ({
      amount_min: row.amount_min,
      amount_max: row.amount_max,
      condition_code: row.condition_code,
      required_director_count: row.required_director_count,
    }));
  });

  await test.step('UAT-014/015/016/017: direct/subsidiary receipts, interest, DPD, and replay safety', async () => {
    await switchActor(page, creditEmail, epic009Password);
    const accounts = await api(page, '/api/v1/loan-accounts/?page=1&page_size=20');
    const account = asRows(accounts.data).find(row => row.loan_account_number === accountNumber);
    expect(account).toBeTruthy();
    accountId = String(account!.loan_account_id);

    const directBody = {
      capture: {
        repayment_source: 'direct_farmer',
        amount_received: '100000.00',
        received_date: '2026-07-25',
        payment_method: 'rtgs',
        bank_reference_number: 'UTR-CRITICAL-UAT-DIRECT',
        remarks: 'Critical UAT direct receipt.',
      },
      sap_posting: {
        sap_entry_reference: 'SAP-CRITICAL-UAT-DIRECT',
        sap_posted_at: '2026-07-25T10:00:00Z',
        remarks: 'Synthetic SAP confirmation.',
      },
    };
    const direct = await api(page, `/api/v1/loan-accounts/${accountId}/direct-repayment-command/`, {
      method: 'POST',
      body: directBody,
      headers: { 'Idempotency-Key': 'critical-uat-direct-001' },
    });
    const directReplay = await api(page, `/api/v1/loan-accounts/${accountId}/direct-repayment-command/`, {
      method: 'POST',
      body: directBody,
      headers: { 'Idempotency-Key': 'critical-uat-direct-001' },
    });
    expect(direct.status).toBe(200);
    expect(direct.data).toMatchObject({
      replayed: false,
      capture: {
        received_date: '2026-07-25',
      },
      allocation: {
        allocated_to_principal: '100000.00',
        loan_account: { principal_outstanding: '300000.00' },
      },
    });
    expect(directReplay.data).toMatchObject({ replayed: true });

    const subsidiaryBody = {
      repayment_source: 'subsidiary_deduction',
      amount_received: '75000.00',
      received_date: '2026-07-25',
      payment_method: 'subsidiary_transfer',
      bank_reference_number: 'SUB-CRITICAL-UAT-001',
      subsidiary_company_id: '00000000-0000-4000-8350-000000000001',
      produce_payment_reference: 'PRODUCE-CRITICAL-UAT-001',
      transfer_reference: 'SUB-CRITICAL-UAT-001',
      remarks: 'Deducted under the verified tri-party agreement.',
    };
    const subsidiary = await api(page, `/api/v1/loan-accounts/${accountId}/repayments/`, {
      method: 'POST',
      body: subsidiaryBody,
      headers: { 'Idempotency-Key': 'critical-uat-subsidiary-001' },
    });
    const subsidiaryReplay = await api(page, `/api/v1/loan-accounts/${accountId}/repayments/`, {
      method: 'POST',
      body: subsidiaryBody,
      headers: { 'Idempotency-Key': 'critical-uat-subsidiary-001' },
    });
    expect(subsidiary.status).toBe(200);
    expect(subsidiary.data).toMatchObject({
      repayment_source: 'subsidiary_deduction',
      reconciliation_status: 'pending_statement',
    });
    expect(subsidiaryReplay.data).toEqual({
      idempotency_replayed: true,
      original_response: subsidiary.data,
    });

    await switchActor(page, accountsEmail, uatPassword);
    const invoice = await api(page, `/api/v1/loan-accounts/${accountId}/interest-invoices/`, {
      method: 'POST',
      body: { financial_year: 'FY2026-27' },
      headers: { 'Idempotency-Key': 'critical-uat-interest-001' },
    });
    expect(invoice.status).toBe(200);
    expect(invoice.data).toMatchObject({
      loan_account_id: accountId,
      financial_year: 'FY2026-27',
    });

    await switchActor(page, creditEmail, epic009Password);
    const dpd = await api(page, `/api/v1/loan-accounts/${accountId}/dpd-status/calculate/`, {
      method: 'POST',
      body: { as_of_date: '2026-07-01' },
    });
    expect(dpd.status).toBe(200);
    expect(dpd.data).toMatchObject({
      as_of_date: '2026-07-01',
      days_past_due: 1,
      principal_overdue_amount: '400000.00',
      calculation_inputs: {
        schedule_lines: [
          expect.objectContaining({
            principal_due: '400000.00',
            principal_paid_as_of: '0.00',
          }),
        ],
      },
    });
    results.servicing = {
      direct: direct.data,
      subsidiary: subsidiary.data,
      invoice: invoice.data,
      dpd: dpd.data,
    };
  });

  await test.step('UAT-018/019/020: default opens; recovery and closure fail closed before authority/readiness', async () => {
    const opened = await api(page, `/api/v1/loan-accounts/${accountId}/default-cases/open/`, {
      method: 'POST',
      body: {
        trigger_event: 'missed_principal_repayment',
        scheduled_due_date: scheduleDueDate,
        reason: 'Critical UAT scheduled principal repayment missed.',
      },
    });
    expect(opened.status).toBe(200);
    expect(opened.data).toMatchObject({
      default_case_status: 'grace_period_active',
      grace_period_end_date: '2026-09-30',
    });
    const defaultCaseId = String(asRecord(opened.data).default_case_id);
    const recoveryDenied = await api(page, `/api/v1/default-cases/${defaultCaseId}/recovery-decision/`, {
      method: 'POST',
      body: {
        approval_case_id: '00000000-0000-4000-8360-000000000001',
        decision: 'invoke_sh4',
        decision_reason: 'Must not proceed without approved recovery authority.',
      },
    });
    expect([403, 409]).toContain(recoveryDenied.status);
    const closure = await api(page, `/api/v1/loan-accounts/${accountId}/closure-readiness/`);
    expect(closure.status).toBe(200);
    expect(closure.data).toMatchObject({ ready_for_closure: false });

    await switchActor(page, TRACER_EMAIL, E2E_PASSWORD);
    await page.getByRole('button', { name: 'Tracer', exact: true }).click();
    await page.getByRole('button', { name: 'Run tracer' }).click();
    await expect(page.getByText('Closed', { exact: true })).toBeVisible();
    results.defaultRecoveryAndClosureBoundaries = {
      opened: opened.data,
      recoveryDenied: recoveryDenied.error,
      prematureClosure: closure.data,
      separatePublicClosureTracer: true,
    };
  });

  await test.step('UAT-021/022: Section 186 and NBFC calculations retain governed evidence', async () => {
    await switchActor(page, cfoEmail, uatPassword);
    const section186 = await api(page, '/api/v1/compliance/section-186-trackers/', {
      method: 'POST',
      body: {
        financial_year: 'FY2026-27',
        quarter: 'Q1',
        paid_up_capital_amount: '100.00',
        free_reserves_amount: '100.00',
        securities_premium_amount: '0.00',
        total_loans_exposure_amount: '100.00',
        compliance_task_id: section186TaskId,
        compliance_evidence_id: section186EvidenceId,
      },
    });
    expect(section186.status).toBe(200);
    expect(section186.data).toMatchObject({
      applicable_limit_amount: '120.00',
      total_loans_exposure_amount: '100.00',
      within_limit_flag: true,
      special_resolution_required_flag: false,
    });
    const nbfc = await api(page, '/api/v1/compliance/nbfc-principal-tests/', {
      method: 'POST',
      body: {
        financial_year: 'FY2026-27',
        quarter: 'Q1',
        financial_assets_amount: '51.00',
        total_assets_amount: '100.00',
        financial_income_amount: '51.00',
        gross_income_amount: '100.00',
        early_warning_threshold_ratio: '40.0000',
        compliance_task_id: nbfcTaskId,
        compliance_evidence_id: nbfcEvidenceId,
      },
    });
    expect(nbfc.status).toBe(200);
    expect(nbfc.data).toMatchObject({
      financial_asset_ratio: '51.0000',
      financial_income_ratio: '51.0000',
      registration_triggered_flag: true,
    });
    results.compliance = { section186: section186.data, nbfc: nbfc.data };
  });

  await test.step('UAT-024/025: report rows reconcile; export and audit retain actor/outcome/reason evidence', async () => {
    const report = await api(
      page,
      '/api/v1/reports/loan-portfolio/?status=partially_repaid&page=1&page_size=100',
    );
    expect(report.status).toBe(200);
    const reportRows = asRows(report.data);
    expect(reportRows.every(candidate => candidate.loan_account_status === 'partially_repaid')).toBe(true);
    const row = reportRows.find(candidate => candidate.loan_account_number === accountNumber);
    expect(row).toMatchObject({
      loan_account_status: 'partially_repaid',
      principal_outstanding: '300000.00',
    });
    expect(asRecord(report.pagination).total_count).toBe(reportRows.length);
    const exportJob = await api(page, '/api/v1/reports/exports/', {
      method: 'POST',
      body: {
        report_code: 'loan-portfolio',
        format: 'csv',
        filters: { status: 'partially_repaid' },
      },
      headers: { 'Idempotency-Key': 'critical-uat-export-001' },
    });
    expect(exportJob.status).toBe(202);
    expect(exportJob.data).toMatchObject({ report_code: 'loan-portfolio', status: 'queued' });

    await switchActor(page, auditorEmail, uatPassword);
    const criticalActions = [
      'disbursement.authorised',
      'repayment.allocated',
      'default.case_opened',
      'compliance.section186.created',
      'compliance.nbfc_test.created',
      'report.export.requested',
    ];
    const criticalAudit = [];
    for (const action of criticalActions) {
      const audit = await api(
        page,
        `/api/v1/audit-logs/?action=${encodeURIComponent(action)}&page=1&page_size=20`,
      );
      expect(audit.status).toBe(200);
      const entry = asRows(audit.data)[0];
      expect(entry).toMatchObject({
        action,
        actor: expect.objectContaining({ full_name: expect.any(String) }),
        new_value: expect.any(Object),
      });
      criticalAudit.push(entry);
    }
    const authorised = criticalAudit[0];
    expect(authorised).toMatchObject({
      action: 'disbursement.authorised',
      actor: expect.objectContaining({ full_name: 'Epic 009 Browser CFC' }),
      new_value: expect.objectContaining({
        outcome: 'approved',
        comments_digest: expect.any(String),
      }),
    });
    results.reportingAudit = {
      filteredCount: reportRows.length,
      report: row,
      exportJob: exportJob.data,
      audit: criticalAudit,
    };
  });

  await test.step('UAT-026: object/RBAC, export, audit mutation, and sensitive masking fail closed', async () => {
    await switchActor(page, zeroEmail, E2E_PASSWORD);
    const deniedExport = await api(page, '/api/v1/reports/exports/', {
      method: 'POST',
      body: { report_code: 'loan-portfolio', format: 'csv', filters: {} },
      headers: { 'Idempotency-Key': 'critical-uat-denied-export' },
    });
    const deniedAuditMutation = await api(page, '/api/v1/audit-logs/', {
      method: 'POST',
      body: { action: 'forged.audit' },
    });
    const deniedAccount = await api(page, `/api/v1/loan-accounts/${accountId}/`);
    expect(deniedExport.status).toBe(403);
    expect([403, 405]).toContain(deniedAuditMutation.status);
    expect([403, 404]).toContain(deniedAccount.status);
    await expect(page.getByRole('button', { name: 'Reports', exact: true })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Audit & Archive', exact: true })).toHaveCount(0);

    await switchActor(page, 'e2e.credit.finance@sfpcl.example', E2E_PASSWORD);
    const maskedMember = await api(
      page,
      '/api/v1/members/00000000-0000-4000-8000-000000000602/',
    );
    expect(maskedMember.status).toBe(200);
    const sensitiveSurface = JSON.stringify(maskedMember.data);
    expect(sensitiveSurface).not.toContain('ABCDE0602F');
    expect(sensitiveSurface).not.toContain('600000000602');
    expect(sensitiveSurface).toMatch(/\*{2,}/);

    await switchActor(page, zeroEmail, E2E_PASSWORD);
    await page.screenshot({
      path: path.join(evidenceDir, 'critical-uat-permission-negative.png'),
      fullPage: true,
      animations: 'disabled',
    });
    results.permissionNegative = {
      deniedExport: deniedExport.error,
      deniedAuditMutation: deniedAuditMutation.error,
      deniedAccount: deniedAccount.error,
      maskedMember: maskedMember.data,
    };
  });

  writeEvidence({
    duration_ms: Date.now() - startedAt,
    test_count: 1,
    skipped: 0,
    public_results: results,
  });
});

type ApiEnvelope = {
  status: number;
  success: boolean;
  data: unknown;
  error: unknown;
  pagination: unknown;
};

const api = (
  page: Page,
  apiPath: string,
  options: { method?: string; body?: unknown; headers?: Record<string, string> } = {},
): Promise<ApiEnvelope> => page.evaluate(async input => {
  const raw = localStorage.getItem('sfpcl_staff_auth_session');
  if (!raw) throw new Error('Authenticated staff session is required');
  const session = JSON.parse(raw) as { accessToken: string };
  const response = await fetch(`http://127.0.0.1:8000${input.apiPath}`, {
    method: input.method ?? 'GET',
    headers: {
      Authorization: `Bearer ${session.accessToken}`,
      Accept: 'application/json',
      ...(input.body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...input.headers,
    },
    body: input.body === undefined ? undefined : JSON.stringify(input.body),
  });
  const responseText = await response.text();
  const envelope = responseText
    ? JSON.parse(responseText) as {
        success?: boolean;
        data?: unknown;
        error?: unknown;
        pagination?: unknown;
      }
    : {};
  return {
    status: response.status,
    success: Boolean(envelope.success),
    data: envelope.data,
    error: envelope.error,
    pagination: envelope.pagination,
  };
}, { apiPath, ...options });

const successEnvelope = async (response: { ok(): boolean; json(): Promise<unknown> }) => {
  const envelope = await response.json() as { success: boolean; data: Record<string, unknown> };
  expect(response.ok(), JSON.stringify(envelope)).toBe(true);
  expect(envelope.success).toBe(true);
  return envelope;
};

const asRecord = (value: unknown): Record<string, unknown> => {
  expect(value).toBeTruthy();
  expect(typeof value).toBe('object');
  return value as Record<string, unknown>;
};

const asRows = (value: unknown): Array<Record<string, unknown>> => {
  expect(Array.isArray(value)).toBe(true);
  return value as Array<Record<string, unknown>>;
};

const switchActor = async (page: Page, email: string, password: string) => {
  await page.evaluate(() => localStorage.removeItem('sfpcl_staff_auth_session'));
  await page.reload();
  await staffLogin(page, email, password);
};

const transferEvidenceId = async (page: Page): Promise<string> => {
  const response = await api(page, '/api/v1/notifications/?category=finance');
  expect(response.status).toBe(200);
  const notification = asRows(response.data).find(
    row => row.notification_type === 'e2e_transfer_evidence',
  );
  expect(notification?.related_entity_id).toBeTruthy();
  return String(notification!.related_entity_id);
};

const browserLocalMinuteAfter = (page: Page, instant: string): Promise<string> => page.evaluate(value => {
  const localValue = new Date(value);
  if (Number.isNaN(localValue.getTime())) throw new Error('Django authorisation time is invalid');
  localValue.setSeconds(0, 0);
  localValue.setMinutes(localValue.getMinutes() + 1);
  const part = (number: number) => String(number).padStart(2, '0');
  return `${localValue.getFullYear()}-${part(localValue.getMonth() + 1)}-${part(localValue.getDate())}`
    + `T${part(localValue.getHours())}:${part(localValue.getMinutes())}`;
}, instant);

const scenarioMatrix = [
  ['UAT-001', 'E2E-001', 'automated', 'Field Officer → Finance → CFC', 'standard loan, documents, SAP, disbursement'],
  ['UAT-002', 'E2E-002', 'manual', 'Company Secretary', 'repeat standard loan with demat/CDSL evidence and unpledge'],
  ['UAT-003', 'E2E-003', 'manual', 'Credit Manager', 'repeat standard loan with FPC and beneficial-owner evidence'],
  ['UAT-004', 'E2E-004', 'manual', 'Deputy Manager Finance', 'return and resolve named deficiencies'],
  ['UAT-005', 'E2E-005', 'manual', 'Credit Manager', 'reject failed eligibility and retain communication'],
  ['UAT-006', 'E2E-006', 'automated', 'CFO + Director', 'below-threshold rule'],
  ['UAT-007', 'E2E-006', 'automated', 'CFO + two Directors', 'above-threshold rule'],
  ['UAT-008', 'E2E-007', 'automated', 'CFO + two Directors', 'permissible-limit exception rule'],
  ['UAT-009', 'E2E-008', 'manual', 'Non-conflicted Directors', 'general-meeting evidence and abstention'],
  ['UAT-010', 'E2E-009', 'manual', 'Company Secretary', 'signature mismatch resolution evidence'],
  ['UAT-011', 'E2E-001', 'automated', 'Company Secretary/Credit/Sanction', 'current checklist evidence'],
  ['UAT-012', 'E2E-010', 'automated', 'Senior Manager Finance', 'completed SAP code'],
  ['UAT-013', 'E2E-001', 'automated', 'Senior Finance/CFC', 'initiate, authorise, transfer'],
  ['UAT-014', 'E2E-011', 'automated', 'Credit Manager', 'direct receipt and principal-first allocation'],
  ['UAT-015', 'E2E-012', 'automated', 'Credit Manager', 'subsidiary receipt and reconciliation state'],
  ['UAT-016', 'E2E-013', 'automated', 'Credit Manager', 'interest invoice'],
  ['UAT-017', 'E2E-013', 'automated', 'Credit Manager', 'DPD from schedule truth'],
  ['UAT-018', 'E2E-014', 'automated', 'Credit Manager', 'default and grace period'],
  ['UAT-019', 'E2E-014', 'automated-negative/manual-positive', 'Credit Manager/authority', 'recovery denied before approval; approve manually'],
  ['UAT-020', 'E2E-015', 'automated', 'Credit Manager', 'premature closure denied and public tracer closes fully-paid loan'],
  ['UAT-021', 'E2E-016', 'automated', 'CFO', 'Section 186 calculation'],
  ['UAT-022', 'E2E-016', 'automated', 'CFO', 'NBFC principal-business calculation'],
  ['UAT-023', 'E2E-017', 'manual', 'Compliance Team', 'two-year re-KYC completion with updated documents'],
  ['UAT-024', 'E2E-001/011/016', 'automated', 'CFO', 'report reconciliation and export job'],
  ['UAT-025', 'E2E-018', 'automated', 'Internal Auditor', 'immutable actor/outcome/reason-digest audit'],
  ['UAT-026', 'E2E-018', 'automated', 'Zero-permission staff', 'RBAC/object/export/audit/masking negatives'],
] as const;

const writeEvidence = (run: Record<string, unknown>) => {
  fs.writeFileSync(
    path.join(evidenceDir!, 'critical-uat-scenario-matrix.json'),
    `${JSON.stringify({
      source: [
        'test-plan.md §16, §18-22, §27.1-27.2, §28, §29.4',
        'implementation-roadmap.md §17.4-17.6, §27.3',
        'product-requirements.md §11-12',
        'screen-spec.md §13',
        'technical-architecture.md §29.4',
      ],
      scenarios: scenarioMatrix.map(([uat, e2e, mode, role, evidence]) => ({
        uat, e2e, mode, role, precondition: 'fresh deterministic guarded seed',
        public_steps: evidence,
        expected_records_ledger_audit: mode.startsWith('manual')
          ? 'Retain the named owner evidence during business UAT.'
          : 'Asserted in critical-uat-smoke.e2e.spec.ts through public UI/API.',
        retained_evidence: mode.startsWith('manual') ? 'manual UAT worksheet' : 'run JSON/PNG/trace',
      })),
    }, null, 2)}\n`,
  );
  fs.writeFileSync(
    path.join(evidenceDir!, 'critical-uat-seed-manifest.json'),
    `${JSON.stringify({
      guards: ['SFPCL_DEBUG=true', 'SFPCL_ALLOW_E2E_SEED=true', 'isolated SFPCL_DB_PATH'],
      commands: [
        'seed_role_catalogue', 'seed_e2e_users', 'seed_portal_e2e_fixture',
        'seed_epic_009_e2e_fixture', 'seed_critical_uat_e2e_fixture',
      ],
      providers: ['manual/fake SAP', 'manual/fake bank', 'local document storage', 'queued communications'],
      live_providers: false,
      isolation: 'Playwright config deletes and migrates the isolated database before every run.',
      run,
    }, null, 2)}\n`,
  );
};
