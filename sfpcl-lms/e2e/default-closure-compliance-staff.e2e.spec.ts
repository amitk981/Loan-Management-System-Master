import fs from 'fs';
import path from 'path';
import { expect, test, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) {
  throw new Error('RALPH_EVIDENCE_DIR is required for the 011PA staff acceptance contract');
}
fs.mkdirSync(evidenceDir, { recursive: true });

test.beforeEach(async ({ page }) => {
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
    return ok(route, defaultCase);
  });
});

test('S53-S55 render server evidence while S56-S57 remain unavailable', async ({ page }) => {
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
  await expect(page.getByRole('button', { name: 'Recovery Approval' })).toBeDisabled();
  await expect(page.getByRole('button', { name: 'Security Invocation' })).toBeDisabled();
  expect(mutations).toEqual([]);

  await page.getByRole('button', { name: /All Cases/ }).click();
  await expect(page.getByText('Missed repayment seeded for the S53 browser contract.')).toBeVisible();
  await page.screenshot({
    path: path.join(evidenceDir, 'default-case-workbench.png'),
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
    'defaults.case.read',
    'defaults.assessment.create',
    'defaults.extension.grant',
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
    recommended_recovery_action: 'present_to_sanction_committee',
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
    status: 'draft',
    approval_case_id: null,
    submitted_to_sanction_committee_at: null,
    available_actions: [],
  },
  recovery_decision: {
    recovery_decision_id: 'decision-browser-011pa',
    decision: 'invoke_sh4',
    status: 'approved',
    available_actions: [{ action_code: 'execute_recovery' }],
  },
  recovery_action: null,
  available_actions: [],
};
