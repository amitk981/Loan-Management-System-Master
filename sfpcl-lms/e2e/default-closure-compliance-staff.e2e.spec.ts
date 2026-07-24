import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for the 011PE staff acceptance contract');
}
fs.mkdirSync(evidenceDir, { recursive: true });

test.beforeEach(async ({ page }) => {
  let decided = false;
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => localStorage.setItem(
    'sfpcl_staff_auth_session',
    JSON.stringify({ accessToken: 'default-staff-access', refreshToken: 'default-staff-refresh' }),
  ));
  await page.route('**/api/v1/auth/me/', route => ok(route, creditManager));
  await page.route('**/api/v1/dashboard/', route => ok(route, {
    role_context: 'credit_manager',
    cards: [],
    tasks: [],
  }));
  await page.route('**/api/v1/default-cases/**', route => {
    const url = new URL(route.request().url());
    if (url.pathname === '/api/v1/default-cases/') {
      return listOk(route, [defaultCase]);
    }
    if (url.pathname.endsWith('/recovery-decision/')) {
      decided = true;
      return ok(route, approvedDecision);
    }
    return ok(route, decided ? decidedDefaultCase : defaultCase);
  });
  await page.route('**/api/v1/approval-cases/approval-browser-011pb/', route => ok(route, approvalCase));
  await page.route('**/api/v1/loan-accounts/**', route => {
    const url = new URL(route.request().url());
    if (url.pathname === '/api/v1/loan-accounts/') return listOk(route, [closureAccount]);
    if (url.pathname.endsWith('/closure-readiness/')) return ok(route, blockedClosureReadiness);
    return route.fallback();
  });
  await page.route('**/api/v1/compliance-controls/**', route => listOk(route, [complianceControl]));
  await page.route('**/api/v1/compliance-tasks/**', route => listOk(route, [complianceTask]));
  await page.route('**/api/v1/compliance/section-186-trackers/**', route => listOk(route, [section186]));
  await page.route('**/api/v1/compliance/nbfc-principal-tests/**', route => listOk(route, [nbfcTest]));
  await page.route('**/api/v1/kyc-reviews/**', route => listOk(route, [kycReview]));
  await page.route('**/api/v1/reports/money-lending-review/**', route => listOk(route, [moneyLendingReview]));
  await page.route('**/api/v1/reports/stamp-duty/**', route => listOk(route, [stampDutyRecord]));
  let grievanceResolved = false;
  await page.route('**/api/v1/grievances/**', route => {
    const url = new URL(route.request().url());
    if (url.pathname === '/api/v1/grievances/') {
      return listOk(route, [grievanceResolved ? resolvedGrievance : grievance]);
    }
    if (url.pathname.endsWith('/resolve/')) {
      grievanceResolved = true;
      return ok(route, resolvedGrievance);
    }
    return ok(route, grievanceResolved ? resolvedGrievance : grievance);
  });
  await page.route('**/api/v1/archive-records/**', route => listOk(route, [archiveRecord]));
  await page.route(
    '**/api/v1/loan-closures/closure-browser-011pe/archive/',
    route => ok(route, archiveRecord),
  );
});

test('S53-S57 render governed notes, record the decision, and open canonical recovery execution', async ({ page }) => {
  const mutations: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await openDefaultWorkbench(page);
  await expect(page.getByRole('heading', { name: 'Default & Recovery Management' })).toBeVisible();
  await expect(page.getByText('LN-BROWSER-DEFAULT-001').first()).toBeVisible();
  await expect(page.getByText('Seeded Browser Default Member').first()).toBeVisible();
  await expect(page.getByText('Missed repayment seeded for the S53 browser contract.')).toBeVisible();

  await page.getByRole('button', { name: 'Grace Period / Extension' }).click();
  await expect(page.getByText('Seeded crop loss assessment.')).toBeVisible();
  await expect(page.getByText('Seeded one-year extension evidence.')).toBeVisible();

  await page.getByRole('button', { name: 'Non-Payment Note' }).click();
  await expect(page.getByText('Frozen seeded non-payment reason.')).toBeVisible();
  await expect(page.getByText('Seeded grace expired unpaid.')).toBeVisible();
  await expect(page.getByText('Browser Credit Assessor')).toBeVisible();
  const nonPaymentNote = page.getByRole('region', { name: 'Note for Non-Payment' });
  await expect(nonPaymentNote).toBeVisible();
  await expect(nonPaymentNote.getByRole('textbox')).toHaveCount(0);
  await expect(nonPaymentNote.getByRole('button')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Recovery Approval' })).toBeEnabled();
  await expect(page.getByRole('button', { name: 'Security Invocation' })).toBeDisabled();
  await page.screenshot({
    path: path.join(evidenceDir, 'default-case-workbench.png'),
    fullPage: true,
    animations: 'disabled',
  });
  await page.getByRole('button', { name: 'Recovery Approval' }).click();
  await expect(page.getByText('Browser Committee Approver')).toHaveCount(2);
  await expect(page.getByText('Browser CFO Approver')).toHaveCount(2);
  await expect(page.getByText('Invoke Sh4').first()).toBeVisible();
  await page.getByLabel('Decision reason').fill('Browser approval reason retained by the backend.');
  await page.getByRole('button', { name: 'Record Recovery Decision' }).click();
  await expect(page.getByText('Recovery decision recorded from canonical backend state.')).toBeVisible();
  await expect(page.getByText('Browser approval reason retained by the backend.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Security Invocation' })).toBeEnabled();
  await page.getByRole('button', { name: 'Security Invocation' }).click();
  await expect(page.getByText('Approved recovery execution available')).toBeVisible();
  await expect(page.getByText('Ready To Initiate')).toBeVisible();
  expect(mutations).toEqual([
    'POST /api/v1/default-cases/default-browser-011pa/recovery-decision/',
  ]);
  await page.screenshot({
    path: path.join(evidenceDir, 'recovery-approval-decision.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('S58-S61 show named server readiness blockers and keep NOC blocked', async ({ page }) => {
  const mutations: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Closure & Archive' }).click();
  await expect(page.getByRole('heading', { name: 'Loan Closure & Archive' })).toBeVisible();
  await expect(page.getByText('LN-BROWSER-CLOSURE-001', { exact: true })).toBeVisible();
  await expect(page.getByText('Interest Paid Or Approved Adjustment')).toBeVisible();
  await expect(page.getByText('Ledger Reconciled')).toBeVisible();
  await expect(page.getByText('Security Tasks Identified')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Close Loan Financially' })).toBeDisabled();
  await page.getByRole('button', { name: 'NOC Generation' }).click();
  await expect(page.getByText('NOC remains blocked until the backend creates a financially-closed loan identity.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Issue NOC' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Security Return / Unpledge' }).click();
  await expect(page.getByText('Security return remains blocked until the backend creates a financially-closed loan identity.')).toBeVisible();
  await page.getByRole('button', { name: 'Archive', exact: true }).click();
  await expect(page.getByText('Archive remains blocked until financial closure is recorded.')).toBeVisible();
  expect(mutations).toEqual([]);
  await page.screenshot({
    path: path.join(evidenceDir, 'closure-readiness-blockers.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('S62-S67 show canonical compliance trackers and keep auditor access read-only', async ({ page }) => {
  await page.unroute('**/api/v1/auth/me/');
  await page.route('**/api/v1/auth/me/', route => ok(route, internalAuditor));
  const mutations: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Compliance' }).click();
  await expect(page.getByRole('heading', { name: 'Compliance Dashboard' })).toBeVisible();
  await expect(page.getByText('₹1,02,00,000.00').first()).toBeVisible();
  await expect(page.getByText('₹22,00,000.00')).toBeVisible();
  await expect(page.getByText('33.3333%')).toBeVisible();
  await expect(page.getByText('12.5000%')).toBeVisible();
  await expect(page.getByText('Seeded Browser Re-KYC Member')).toBeVisible();
  await expect(page.getByText('FY2026-27 · Maharashtra')).toBeVisible();
  await expect(page.getByText('APP-BROWSER-STAMP-011PD')).toBeVisible();
  await expect(page.getByText('Member-only lending control')).toBeVisible();
  await expect(page.getByRole('button', { name: /Review Section 186|Review NBFC Test|Review Evidence/ })).toHaveCount(0);
  expect(mutations).toEqual([]);
  await page.screenshot({
    path: path.join(evidenceDir, 'compliance-trackers.png'),
    fullPage: true,
    animations: 'disabled',
  });
});

test('S68 resolves a canonical grievance and reads archive manifests without mutation controls', async ({ page }) => {
  await page.unroute('**/api/v1/auth/me/');
  await page.route('**/api/v1/auth/me/', route => ok(route, companySecretary));
  const mutations: string[] = [];
  let archiveDetailReads = 0;
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname === '/api/v1/loan-closures/closure-browser-011pe/archive/') {
      archiveDetailReads += 1;
    }
    if (url.pathname.includes('/api/v1/') && request.method() !== 'GET') {
      mutations.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Grievances' }).click();
  await expect(page.getByRole('heading', { name: 'Grievances' })).toBeVisible();
  await expect(page.getByText('GRV-BROWSER-011PE')).toBeVisible();
  await expect(page.getByText('Recovery conduct complaint')).toBeVisible();
  await expect(page.getByText('Recovery-related complaints require CS review.')).toBeVisible();
  await page.getByRole('button', { name: 'Resolve GRV-BROWSER-011PE' }).click();
  await page.getByRole('button', { name: 'Submit Resolution' }).click();
  await expect(page.getByText('Resolution status is required.')).toBeVisible();
  await expect(page.getByText('Resolution reason is required.')).toBeVisible();
  await page.getByLabel('Resolution status').selectOption('resolved');
  await page.getByLabel('Resolution reason').fill('Browser grievance resolution retained by the backend.');
  await page.getByRole('button', { name: 'Submit Resolution' }).click();
  await expect(page.getByText('Grievance resolved from canonical backend state.')).toBeVisible();
  await expect(page.getByText('Browser grievance resolution retained by the backend.')).toBeVisible();
  await page.screenshot({
    path: path.join(evidenceDir, 'grievance-resolution.png'),
    fullPage: true,
    animations: 'disabled',
  });

  await page.getByRole('button', { name: 'Audit & Archive' }).click();
  await expect(page.getByRole('heading', { name: 'Audit & Archive' })).toBeVisible();
  await expect(page.getByText('archive-browser-011pe')).toBeVisible();
  await expect(page.getByText('Archive Room / Browser Rack / Box 11')).toBeVisible();
  await expect(page.getByText('Read-only access — archive records cannot be edited.')).toBeVisible();
  await expect(page.getByRole('button', { name: /archive file|record destruction|delete|edit/i })).toHaveCount(0);
  const downloadStarted = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Download manifest archive-browser-011pe' }).click();
  const manifestDownload = await downloadStarted;
  expect(manifestDownload.suggestedFilename()).toBe('archive-manifest-archive-browser-011pe.json');
  await expect(page.getByText('Archive manifest downloaded through the audited read endpoint.')).toBeVisible();
  expect(archiveDetailReads).toBe(1);
  expect(mutations).toEqual([
    'POST /api/v1/grievances/grievance-browser-011pe/resolve/',
  ]);
});

async function openDefaultWorkbench(page: Page) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Default & Recovery' }).click();
}

const ok = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    meta: { request_id: 'default-browser-contract' },
  }),
});

const listOk = (route: Route, data: unknown[]) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({
    success: true,
    data,
    pagination: {
      page: 1,
      page_size: 100,
      total_count: data.length,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
    meta: { request_id: 'default-browser-list-contract' },
  }),
});

const creditManager = {
  user_id: 'credit-manager-browser',
  full_name: 'Browser Credit Manager',
  email: 'credit-manager-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }],
  teams: [{ team_code: 'credit_assessment', team_name: 'Credit Assessment Team' }],
  role_codes: ['credit_manager'],
  team_codes: ['credit_assessment'],
  permissions: [
    'finance.loan_account.read',
    'defaults.case.read',
    'defaults.assessment.create',
    'defaults.extension.grant',
    'recovery.decision.create',
    'closure.readiness.read',
    'closure.loan.close',
  ],
  available_actions: [],
};

const internalAuditor = {
  user_id: 'auditor-browser-011pd',
  full_name: 'Browser Internal Auditor',
  email: 'auditor-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'internal_auditor', role_name: 'Internal Auditor' }],
  teams: [{ team_code: 'audit', team_name: 'Internal Audit' }],
  role_codes: ['internal_auditor'],
  team_codes: ['audit'],
  permissions: [
    'compliance.control.read',
    'compliance.task.read',
    'compliance.evidence.review',
    'compliance.section186.read',
    'compliance.nbfc_test.read',
    'reports.compliance.read',
  ],
  available_actions: [],
};

const companySecretary = {
  user_id: 'company-secretary-browser-011pe',
  full_name: 'Browser Company Secretary',
  email: 'company-secretary-browser@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'company_secretary', role_name: 'Company Secretary' }],
  teams: [{ team_code: 'compliance', team_name: 'Compliance Team' }],
  role_codes: ['company_secretary'],
  team_codes: ['compliance'],
  permissions: [
    'compliance.grievance.read',
    'compliance.grievance.resolve',
    'closure.archive.read',
  ],
  available_actions: [],
};

const defaultCase = {
  default_case_id: 'default-browser-011pa',
  loan_account_id: 'loan-browser-011pa',
  loan_account_number: 'LN-BROWSER-DEFAULT-001',
  member_id: 'member-browser-011pa',
  borrower_name: 'Seeded Browser Default Member',
  principal_outstanding: '300000.00',
  interest_outstanding: '45000.00',
  total_outstanding: '345000.00',
  trigger_event: 'missed_principal_repayment',
  scheduled_due_date: '2025-04-15',
  repayment_schedule_id: 'schedule-browser-011pa',
  default_case_status: 'non_payment_under_review',
  grace_period_start_date: '2025-04-15',
  grace_period_end_date: '2025-07-15',
  grace_state: 'expired',
  reason: 'Missed repayment seeded for the S53 browser contract.',
  current_assessment: {
    default_assessment_id: 'assessment-browser-011pa',
    default_case_id: 'default-browser-011pa',
    assessment_type: 'post_grace',
    payment_failure_classification: 'non_intentional',
    reason_summary: 'Seeded crop loss assessment.',
    evidence_document_ids: ['assessment-browser-document'],
    borrower_interaction_summary: 'Seeded borrower contact evidence.',
    recommended_action: 'grant_extension',
    assessed_by_user_id: 'assessor-browser-011pa',
    assessed_at: '2025-07-16T10:00:00Z',
  },
  extension_note: {
    extension_note_id: 'extension-browser-011pa',
    default_case_id: 'default-browser-011pa',
    loan_account_id: 'loan-browser-011pa',
    extension_reason: 'Seeded one-year extension evidence.',
    extension_start_date: '2025-07-16',
    extension_end_date: '2026-07-15',
    document_id: 'extension-browser-document',
    prepared_by_user_id: 'manager-browser-011pa',
    approved_by_user_id: 'approver-browser-011pa',
    status: 'active',
  },
  non_payment_note: {
    non_payment_note_id: 'note-browser-011pa',
    default_case_id: 'default-browser-011pa',
    loan_account_id: 'loan-browser-011pa',
    reason_for_non_payment: 'Frozen seeded non-payment reason.',
    intentionality_assessment: 'non_intentional',
    outstanding_principal_amount: '300000.00',
    outstanding_interest_amount: '45000.00',
    recommended_recovery_action: 'invoke_sh4',
    evidence_document_ids: ['note-browser-evidence'],
    frozen_case_facts: {
      borrower_name: 'Seeded Browser Default Member',
      original_due_date: '2025-04-15',
      grace_outcome_summary: 'Seeded grace expired unpaid.',
      extension_outcome_summary: 'Seeded extension expired unpaid.',
      prepared_by_name: 'Browser Credit Assessor',
    },
    document_id: 'note-browser-document',
    prepared_by_user_id: 'assessor-browser-011pa',
    status: 'submitted',
    approval_case_id: 'approval-browser-011pb',
    submitted_to_sanction_committee_at: '2026-07-19T10:00:00Z',
    available_actions: [],
  },
  recovery_decision: null,
  recovery_decision_control: {
    action_code: 'record_recovery_decision',
    enabled: true,
    disabled_reason: null,
    approval_case_id: 'approval-browser-011pb',
    decision: 'invoke_sh4',
  },
  recovery_action: null,
  available_actions: [],
};

const approvalCase = {
  approval_case_id: 'approval-browser-011pb',
  approval_type: 'recovery',
  related_entity_type: 'non_payment_note',
  related_entity_id: 'note-browser-011pa',
  current_status: 'approved',
  decision_date: '2026-07-20',
  reason_for_approval: 'invoke_sh4',
  conflict_block_reason: null,
  required_approvers: [
    { role_code: 'sanction_committee_member', user_id: 'approver-browser-1', full_name: 'Browser Committee Approver', decision: 'approved', acted_at: '2026-07-20T10:00:00Z' },
    { role_code: 'cfo', user_id: 'approver-browser-2', full_name: 'Browser CFO Approver', decision: 'approved', acted_at: '2026-07-20T10:05:00Z' },
  ],
  approval_actions: [
    { approval_action_id: 'approval-action-browser-1', role_code: 'sanction_committee_member', user_id: 'approver-browser-1', full_name: 'Browser Committee Approver', decision: 'approved', comments: 'Approved.', acted_at: '2026-07-20T10:00:00Z' },
    { approval_action_id: 'approval-action-browser-2', role_code: 'cfo', user_id: 'approver-browser-2', full_name: 'Browser CFO Approver', decision: 'approved', comments: 'Approved.', acted_at: '2026-07-20T10:05:00Z' },
  ],
  excluded_approvers: [],
  available_actions: [],
};

const approvedDecision = {
  recovery_decision_id: 'decision-browser-011pb',
  default_case_id: 'default-browser-011pa',
  non_payment_note_id: 'note-browser-011pa',
  approval_case_id: 'approval-browser-011pb',
  decision: 'invoke_sh4',
  decision_reason: 'Browser approval reason retained by the backend.',
  status: 'approved',
  approval_evidence: {
    approval_case_status: 'approved',
    approved_action: 'invoke_sh4',
    required_approvers: approvalCase.required_approvers,
    approval_actions: approvalCase.approval_actions.map(action => ({
      approval_action_id: action.approval_action_id,
      approver_user_id: action.user_id,
      approver_role_code: action.role_code,
      approver_display_name: action.full_name,
      decision: action.decision,
      acted_at: action.acted_at,
    })),
    closed_at: '2026-07-20T10:05:00Z',
  },
  decided_by_user_id: 'credit-manager-browser',
  decided_by_role_code: 'cfo',
  decided_at: '2026-07-20T10:10:00Z',
  available_actions: [{ action_code: 'execute_recovery', action_type: 'invoke_sh4', required_permission: 'recovery.action.initiate' }],
};

const decidedDefaultCase = {
  ...defaultCase,
  default_case_status: 'recovery_approved',
  recovery_decision: approvedDecision,
  recovery_decision_control: null,
};

const closureAccount = {
  loan_account_id: 'loan-browser-011pc', loan_account_number: 'LN-BROWSER-CLOSURE-001',
  loan_application_id: 'application-browser-011pc', application_reference_number: 'APP-BROWSER-011PC',
  member: { member_id: 'member-browser-011pc', display_name: 'Seeded Closure Browser Member' },
  sap_customer_code: 'SAP-BROWSER-011PC', loan_type: 'term_loan', facility_type: 'term_loan',
  interest_rate_type: 'fixed', current_interest_rate: '8.5000', sanctioned_amount: '500000.00',
  disbursed_amount: '500000.00', principal_outstanding: '0.00', interest_outstanding: '125.00',
  charges_outstanding: '0.00', total_outstanding: '125.00', loan_account_status: 'partially_repaid',
  tenure_start_date: '2025-01-01', tenure_end_date: '2026-07-25', repayment_date: '2026-07-25',
  tenure_months: 18, created_at: '2025-01-01T10:00:00Z', activated_at: '2025-01-02T10:00:00Z',
};

const blockedClosureReadiness = {
  loan_account_id: closureAccount.loan_account_id, ready_for_closure: false,
  checks: [
    { code: 'principal_paid', status: 'pass' },
    { code: 'interest_paid_or_approved_adjustment', status: 'fail' },
    { code: 'charges_paid', status: 'pass' },
    { code: 'ledger_reconciled', status: 'fail' },
    { code: 'recovery_clear', status: 'pass' },
    { code: 'security_tasks_identified', status: 'pass', security_return_required: true },
  ],
  principal_outstanding: '0.00', interest_outstanding: '125.00', charges_outstanding: '0.00',
  total_outstanding: '125.00', interest_adjustment_applied: false, security_return_required: true,
  physical_share_return_required: true, demat_unpledge_required: false,
  blank_cheque_return_required: true, poa_release_required: false,
};

const complianceControl = {
  compliance_control_id: 'control-browser-011pd',
  control_code: 'MEMBER_ONLY_LENDING',
  control_name: 'Member-only lending control',
  control_area: 'producer_company',
  legal_basis: 'Producer Company member lending requirement.',
  control_type: 'preventive',
  frequency: 'ongoing',
  owner_role_code: 'company_secretary',
  owner_user_id: 'owner-browser-011pd',
  reviewer_user_id: 'auditor-browser-011pd',
  first_due_date: '2026-04-01',
  evidence_required: 'Loan and membership register.',
  risk_if_missed: 'Non-member lending.',
  status: 'active',
  available_actions: [],
};

const complianceTask = {
  compliance_task_id: 'task-browser-011pd',
  compliance_control_id: complianceControl.compliance_control_id,
  control_code: complianceControl.control_code,
  task_period: 'ongoing',
  due_date: '2026-07-31',
  assigned_to_user_id: 'owner-browser-011pd',
  reviewer_user_id: 'auditor-browser-011pd',
  task_status: 'evidence_submitted',
  remarks: 'Register reconciled.',
  closed_at: null,
  compliance_evidence_id: 'evidence-browser-011pd',
  available_actions: [],
};

const section186 = {
  section_186_tracker_id: 'section-browser-011pd',
  financial_year: 'FY2026-27',
  quarter: 'Q1',
  paid_up_capital_amount: '10000000.00',
  free_reserves_amount: '5000000.00',
  securities_premium_amount: '2000000.00',
  limit_60_percent_basis_amount: '10200000.00',
  limit_100_percent_basis_amount: '7000000.00',
  applicable_limit_amount: '10200000.00',
  total_loans_exposure_amount: '8000000.00',
  headroom_amount: '2200000.00',
  within_limit_flag: true,
  special_resolution_required_flag: false,
  compliance_task_id: 'task-section-browser-011pd',
  compliance_evidence_id: 'evidence-section-browser-011pd',
  review_status: 'pending',
  review_comments: '',
  presented_to_board_flag: false,
  available_actions: [],
};

const nbfcTest = {
  nbfc_principal_test_id: 'nbfc-browser-011pd',
  financial_year: 'FY2026-27',
  quarter: 'Q1',
  financial_assets_amount: '20000000.00',
  total_assets_amount: '60000000.00',
  financial_asset_ratio: '33.3333',
  financial_income_amount: '1000000.00',
  gross_income_amount: '8000000.00',
  financial_income_ratio: '12.5000',
  early_warning_threshold_ratio: '40.0000',
  registration_triggered_flag: false,
  one_ratio_above_statutory_flag: false,
  early_warning_flag: false,
  presented_to_board_flag: false,
  compliance_task_id: 'task-nbfc-browser-011pd',
  compliance_evidence_id: 'evidence-nbfc-browser-011pd',
  review_status: 'pending',
  review_comments: '',
  available_actions: [],
};

const kycReview = {
  kyc_review_id: 'kyc-browser-011pd',
  member_id: 'member-browser-011pd',
  member_name: 'Seeded Browser Re-KYC Member',
  member_type: 'individual',
  member_status: 'active',
  kyc_status: 'verified',
  risk_rating: 'medium',
  due_date: '2026-07-20',
  days_overdue: 5,
  status: 'overdue',
  assigned_to_user_id: 'owner-browser-011pd',
  completeness: { complete: true, pan_status: 'verified', ckyc_consent_status: 'available' },
  available_actions: [],
};

const moneyLendingReview = {
  money_lending_law_review_id: 'money-browser-011pd',
  financial_year: 'FY2026-27',
  state: 'Maharashtra',
  applicability: 'exempt',
  exemption_applicable_flag: true,
  compliance_task_id: 'task-money-browser-011pd',
  compliance_evidence_id: 'evidence-money-browser-011pd',
  reviewed_by_user_id: 'secretary-browser-011pd',
  reviewed_at: '2026-03-15T10:00:00Z',
};

const stampDutyRecord = {
  stamp_duty_record_id: 'stamp-browser-011pd',
  loan_document_id: 'document-browser-011pd',
  document_type: 'loan_agreement',
  loan_application_id: 'application-browser-011pd',
  application_reference_number: 'APP-BROWSER-STAMP-011PD',
  member_id: 'member-browser-011pd',
  borrower_name: 'Seeded Browser Stamp Member',
  stamp_paper_amount: '500.00',
  stamp_type: 'physical',
  stamp_number: 'STAMP-BROWSER-011PD',
  stamp_purchase_date: '2026-06-01',
  executed_date: '2026-06-02',
  status: 'adequate',
  notarisation_status: 'completed',
};

const grievance = {
  grievance_id: 'grievance-browser-011pe',
  grievance_reference: 'GRV-BROWSER-011PE',
  member_id: 'member-browser-011pe',
  loan_account_id: 'loan-browser-011pe',
  loan_application_id: null,
  default_case_id: 'default-browser-011pa',
  recovery_action_id: 'recovery-action-browser-011pe',
  grievance_category: 'recovery_conduct_issue',
  subject: 'Recovery conduct complaint',
  description: 'Borrower requested fair-practice review of a recovery interaction.',
  received_date: '2026-07-20',
  received_channel: 'phone',
  assigned_to_user_id: companySecretary.user_id,
  resolution_due_date: '2026-07-24',
  status: 'open',
  tat_days: 4,
  days_overdue: 1,
  is_overdue: true,
  resolution_summary: '',
  closed_at: null,
  borrower_informed: false,
  borrower_acknowledged: false,
  supporting_document_ids: [],
  resolution_document_id: null,
  internal_notes: '',
  borrower_acknowledgement: '',
  escalation_count: 1,
  notice_communication_id: null,
  notice_delivery_status: null,
  history: [],
  available_actions: ['resolve'],
};

const resolvedGrievance = {
  ...grievance,
  status: 'resolved',
  days_overdue: 0,
  is_overdue: false,
  resolution_summary: 'Browser grievance resolution retained by the backend.',
  closed_at: '2026-07-25T11:00:00Z',
  borrower_informed: true,
  available_actions: [],
};

const archiveRecord = {
  archive_record_id: 'archive-browser-011pe',
  loan_closure_id: 'closure-browser-011pe',
  loan_account_id: 'loan-browser-011pe',
  file_location_physical: 'Archive Room / Browser Rack / Box 11',
  file_location_digital: 'governed://archive/browser-011pe',
  retention_start_date: '2026-07-25',
  retention_until_date: '2034-07-25',
  archived_by_user_id: companySecretary.user_id,
  archived_by_role_code: 'company_secretary',
  archived_at: '2026-07-25T10:00:00Z',
  destruction_eligible: false,
  destruction_certificate_id: null,
  idempotency_replayed: false,
  available_actions: [],
};
