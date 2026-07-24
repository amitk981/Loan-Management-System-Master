import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for the 011PB/011PC staff acceptance contract');
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
});

test('S56 records the server-fixed recovery decision and canonical S57 availability', async ({ page }) => {
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
  await page.getByRole('button', { name: 'Recovery Approval' }).click();
  await expect(page.getByText('Browser Committee Approver')).toHaveCount(2);
  await expect(page.getByText('Browser CFO Approver')).toHaveCount(2);
  await expect(page.getByText('Invoke Sh4').first()).toBeVisible();
  await page.getByLabel('Decision reason').fill('Browser approval reason retained by the backend.');
  await page.getByRole('button', { name: 'Record Recovery Decision' }).click();
  await expect(page.getByText('Recovery decision recorded from canonical backend state.')).toBeVisible();
  await expect(page.getByText('Browser approval reason retained by the backend.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Security Invocation' })).toBeEnabled();
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
  expect(mutations).toEqual([]);
  await page.screenshot({
    path: path.join(evidenceDir, 'closure-readiness-blockers.png'),
    fullPage: true,
    animations: 'disabled',
  });
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
