import fs from 'fs';
import path from 'path';
import { expect, test, type Locator, type Page, type Route } from '@playwright/test';

const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
if (!evidenceDir) throw new Error('RALPH_EVIDENCE_DIR is required for register/settings visual acceptance');
fs.mkdirSync(evidenceDir, { recursive: true });

test('S23/S25/S70/S71 preserve scoped contracts through routed app-shell navigation', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  let actor: 'reader' | 'manager' = 'reader';
  const observedApiRequests: string[] = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.pathname.startsWith('/api/v1/')) observedApiRequests.push(`${request.method()} ${url.pathname}${url.search}`);
  });

  await page.addInitScript(() => localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({ accessToken: 'settings-access', refreshToken: 'settings-refresh' })));
  await page.route('**/api/v1/auth/me/', route => json(route, user(actor)));
  await page.route('**/api/v1/dashboard/', route => json(route, { role_context: 'auditor', cards: [], tasks: [] }));
  await page.route('**/api/v1/credit-sanction-register/**', route => {
    const url = new URL(route.request().url());
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('20');
    const fullyFiltered = url.searchParams.get('financial_year') === 'FY2026-27' && url.searchParams.get('decision') === 'sanctioned';
    return paginated(route, fullyFiltered ? [sanctionRow] : [], 20);
  });
  await page.route('**/api/v1/exception-register/**', route => {
    const url = new URL(route.request().url());
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('20');
    const fullyFiltered = url.searchParams.get('status') === 'approved' && url.searchParams.get('exception_type') === 'exceeds_loan_limit';
    return paginated(route, fullyFiltered ? [exceptionRow] : [], 20);
  });
  await page.route('**/api/v1/approval-matrix-rules/**', route => {
    if (route.request().method() === 'PATCH') return json(route, proposal);
    const url = new URL(route.request().url());
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('100');
    return paginated(route, matrixRules, 100);
  });
  await page.route('**/api/v1/config/loan-policy/**', route => json(route, policyVersions));

  await page.goto('/');
  await page.getByRole('button', { name: /^Registers$/ }).click();
  await page.getByLabel('Financial year').fill('FY2026-27');
  await page.getByRole('button', { name: 'Apply financial year' }).click();
  await page.getByLabel('Sanction decision').selectOption('sanctioned');
  await expect(page.getByText('Browser Scoped Borrower')).toBeVisible();
  await expect(page.getByText('CSR-BROWSER-001')).toBeVisible();
  await expect(page.getByText('FOL-BROWSER-001')).toBeVisible();
  await expect(page.getByText('Browser Director source comment.')).toBeVisible();
  await expect(page.getByText('1 record')).toBeVisible();
  await captureReviewable(page, page.getByTestId('sanction-source-evidence'), 'credit-sanction-register-source-fields.png');

  await page.getByRole('button', { name: 'Exception register' }).click();
  await page.getByLabel('Exception status').selectOption('approved');
  await page.getByLabel('Exception type').selectOption('exceeds_loan_limit');
  await expect(page.getByText('Browser exception business reason')).toBeVisible();
  await expect(page.getByText('browser-support.pdf')).toBeVisible();
  await expect(page.getByRole('button', { name: /download/i })).toHaveCount(0);
  await capture(page, 'exception-register-scoped.png');

  await page.getByRole('button', { name: /^Settings$/ }).click();
  await page.getByRole('button', { name: 'Approval Matrix' }).click();
  await expect(page.getByText('Server: CFO + two Directors')).toBeVisible();
  await expect(page.getByRole('button', { name: /Edit AM-BROWSER-2/ })).toHaveCount(0);
  await expect(page.getByText(/until slice 012EA/)).toBeVisible();
  await capture(page, 'approval-matrix-read-only.png');

  actor = 'manager';
  await page.reload();
  await page.getByRole('button', { name: /^Settings$/ }).click();
  await page.getByRole('button', { name: 'Approval Matrix' }).click();
  await page.getByRole('button', { name: 'Edit AM-BROWSER-2' }).click();
  await page.getByLabel('Successor version').fill('AM-BROWSER-3');
  await page.getByLabel('Effective from').fill('2027-04-01');
  await page.getByLabel('Change reason').fill('Browser governed successor proof.');
  await page.getByRole('button', { name: 'Submit for Approval' }).click();
  await expect(page.getByText('Configuration proposal pending approval')).toBeVisible();
  await expect(page.getByText('proposal-browser-1')).toBeVisible();
  await capture(page, 'approval-matrix-successor-pending.png');

  actor = 'reader';
  await page.reload();
  await page.getByRole('button', { name: /^Settings$/ }).click();
  await expect(page.getByRole('heading', { name: 'Policy Version Summary' })).toBeVisible();
  await expect(page.getByText('Read-only access')).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
  await capture(page, 'loan-policy-read-only.png');

  await page.getByRole('button', { name: 'Approval Matrix' }).click();
  await expect(page.getByText(/until slice 012EA/)).toBeVisible();
  await page.getByRole('button', { name: 'Template Management' }).click();
  await expect(page.getByText(/until slice 008A/)).toBeVisible();
  await expect(page.getByRole('button', { name: /upload|activate|retire/i })).toHaveCount(0);
  await capture(page, 'settings-deferred-panels.png');

  expect(observedApiRequests.some(value => value.includes('/approval-cases/'))).toBe(false);
  expect(observedApiRequests.some(value => value.includes('/document-files/'))).toBe(false);
  expect(observedApiRequests.some(value => value.includes('/activate/'))).toBe(false);
});

const user = (actor: 'reader' | 'manager') => ({
  user_id: `settings-${actor}`, full_name: actor === 'manager' ? 'Settings Manager' : 'Settings Reader',
  email: `${actor}@sfpcl.example`, status: 'active', roles: [{ role_code: 'internal_auditor', role_name: 'Internal Auditor' }],
  teams: [], role_codes: ['internal_auditor'], team_codes: [],
  permissions: [
    'approvals.sanction_register.read', 'approvals.exception_register.read', 'approvals.matrix.read',
    'config.loan_policy.read', ...(actor === 'manager' ? ['approvals.matrix.manage', 'config.loan_policy.manage'] : []),
  ],
  available_actions: [],
});

const sanctionRow = {
  credit_sanction_register_entry_id: 'register-browser-1', approval_case_id: 'case-browser-1', loan_application_id: 'application-browser-1',
  sanction_decision_id: 'decision-browser-1', workflow_event_id: 'event-browser-1', application_number: 'LO-BROWSER-001',
  entry_number: 'CSR-BROWSER-001', folio_number: 'FOL-BROWSER-001', loan_type: 'short_term',
  borrower_name: 'Browser Scoped Borrower', borrower_type: 'individual_farmer', requested_amount: '500000.00', eligible_amount: '450000.00',
  recommended_amount: '440000.00', sanctioned_amount: '440000.00', approval_authority: 'CFO + one Director',
  approver_names: ['Browser CFO', 'Browser Director'], approval_date: '2026-07-14', decision: 'sanctioned',
  approver_decisions: [{ approval_action_id: 'action-browser-2', role_code: 'director', user_id: 'director-browser', full_name: 'Browser Director', decision: 'approved', comments: 'Browser Director source comment.', acted_at: '2026-07-14T03:00:00Z' }],
  purpose: { category: 'crop_production', description: 'Browser crop production' }, risk: { overall_risk_rating: 'medium' },
  rejection_reason: null, conditions: 'Complete browser legal documents.', communication: { communication_id: 'communication-browser-1', status: 'pending', sent_at: null },
  reasons: 'Browser frozen sanction reason', exception_reference: null, conflict_abstention_details: [],
  general_meeting_approval_reference: null, recorded_at: '2026-07-14T03:00:00Z',
};

const exceptionRow = {
  exception_register_entry_id: 'exception-browser-1', loan_application_id: 'application-browser-1', loan_account_id: null,
  approval_case_id: 'case-browser-1', cycle_number: 1, exception_type: 'exceeds_loan_limit',
  description: 'Browser frozen exception description', business_reason: 'Browser exception business reason', risk_assessment: 'Medium',
  borrower_name: 'Browser Scoped Borrower', financial_impact: '440000.00', requested_by: { user_id: 'requester-browser', full_name: 'Browser Requester' }, decision_date: '2026-07-14',
  status: 'approved', case_status: 'approved', conflict_block_reason: null, authority_applied_summary: 'CFO + two Directors',
  route_approvers: [], required_approvers: [], approval_actions: [{ approval_action_id: 'action-browser-1', role_code: 'cfo', user_id: 'cfo-browser', full_name: 'Browser CFO', decision: 'approved', comments: 'Browser immutable approval comment.', acted_at: '2026-07-14T03:00:00Z' }],
  supporting_documents: [{ document_id: 'document-browser-1', file_name: 'browser-support.pdf', mime_type: 'application/pdf', file_size_bytes: 2048, sensitivity_level: 'restricted', uploaded_at: '2026-07-14T02:00:00Z' }],
  created_at: '2026-07-14T02:00:00Z', closed_at: '2026-07-14T03:00:00Z',
};

const matrixRules = [{
  approval_matrix_rule_id: 'rule-browser-2', decision_type: 'loan_sanction', amount_min: '500000.01', amount_max: null,
  condition_code: null, required_approver_roles: ['cfo', 'director'], required_director_count: 2,
  authority_summary: 'Server: CFO + two Directors', minimum_approver_count: 3, joint_approval_required_flag: true,
  register_required: 'credit_sanction_register', effective_from: '2026-04-01', effective_to: null, status: 'active', version_number: 'AM-BROWSER-2',
}];

const proposal = {
  approval_configuration_proposal_id: 'proposal-browser-1', proposal_type: 'rule_supersede', target_entity_id: 'rule-browser-2',
  payload: {}, reason: 'Browser governed successor proof.', status: 'pending', version: 1, made_by_user_id: 'settings-manager',
  decided_by_user_id: null, decided_at: null, rejection_reason: null, available_actions: [],
};

const policyVersions = [{
  loan_policy_config_id: 'policy-browser-active', policy_name: 'Browser Board Policy', policy_version: 'LP-BROWSER-1',
  effective_from: '2026-04-01', effective_to: null, short_term_duration_months: 12, min_secured_loan_months: 12,
  max_secured_loan_years: 3, approval_threshold_amount: '500000.00', default_scale_of_finance_per_acre_amount: '20000.00',
  share_limit_percentage: '10.0000', per_share_cap_amount: '200.00', interest_rate_type: 'floating',
  interest_benchmark: 'Browser Board benchmark', penal_interest_rate: null, rekyc_frequency_months: 24,
  record_retention_years: 8, grace_period_months: 3, non_intentional_extension_months: 12,
  board_approval_reference: 'BOARD-BROWSER-1', status: 'active',
}];

const json = (route: Route, data: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data }) });
const paginated = (route: Route, data: unknown[], pageSize: number) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ success: true, data, pagination: { page: 1, page_size: pageSize, total_count: data.length, total_pages: 1, has_next: false, has_previous: false } }) });
const capture = (page: Page, fileName: string) => page.screenshot({ path: path.join(evidenceDir, fileName), fullPage: true, animations: 'disabled' });

const captureReviewable = async (page: Page, evidence: Locator, fileName: string) => {
  await evidence.scrollIntoViewIfNeeded();
  const box = await evidence.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.y).toBeGreaterThanOrEqual(0);
  expect(box!.y + box!.height).toBeLessThanOrEqual(720);
  const screenshot = await page.screenshot({ path: path.join(evidenceDir, fileName), animations: 'disabled' });
  const stats = await page.evaluate(async dataUrl => {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.width; canvas.height = image.height;
    const context = canvas.getContext('2d')!;
    context.drawImage(image, 0, 0);
    const pixels = context.getImageData(0, 0, image.width, image.height).data;
    let opaqueDark = 0;
    const buckets = new Set<number>();
    for (let index = 0; index < pixels.length; index += 16) {
      const red = pixels[index]; const green = pixels[index + 1]; const blue = pixels[index + 2];
      if (red < 12 && green < 12 && blue < 12) opaqueDark += 1;
      buckets.add((red >> 5) * 64 + (green >> 5) * 8 + (blue >> 5));
    }
    const tileSize = 64;
    const columns = Math.ceil(image.width / tileSize);
    const rows = Math.ceil(image.height / tileSize);
    const uniform = Array<boolean>(columns * rows).fill(false);
    for (let tileY = 0; tileY < rows; tileY += 1) {
      for (let tileX = 0; tileX < columns; tileX += 1) {
        let min = 255; let max = 0;
        for (let y = tileY * tileSize; y < Math.min((tileY + 1) * tileSize, image.height); y += 4) {
          for (let x = tileX * tileSize; x < Math.min((tileX + 1) * tileSize, image.width); x += 4) {
            const offset = (y * image.width + x) * 4;
            for (let channel = 0; channel < 3; channel += 1) {
              min = Math.min(min, pixels[offset + channel]); max = Math.max(max, pixels[offset + channel]);
            }
          }
        }
        uniform[tileY * columns + tileX] = max - min <= 4;
      }
    }
    const visited = Array<boolean>(uniform.length).fill(false);
    let largestUniformRegion = 0;
    for (let start = 0; start < uniform.length; start += 1) {
      if (!uniform[start] || visited[start]) continue;
      const queue = [start]; visited[start] = true; let size = 0;
      while (queue.length) {
        const current = queue.pop()!; size += 1;
        const x = current % columns; const y = Math.floor(current / columns);
        for (const next of [x > 0 ? current - 1 : -1, x + 1 < columns ? current + 1 : -1, y > 0 ? current - columns : -1, y + 1 < rows ? current + columns : -1]) {
          if (next >= 0 && uniform[next] && !visited[next]) { visited[next] = true; queue.push(next); }
        }
      }
      largestUniformRegion = Math.max(largestUniformRegion, size);
    }
    return { width: image.width, height: image.height, darkRatio: opaqueDark / (pixels.length / 16), colorBuckets: buckets.size, largestUniformRegionRatio: largestUniformRegion / uniform.length };
  }, `data:image/png;base64,${screenshot.toString('base64')}`);
  expect(stats).toMatchObject({ width: 1280, height: 720 });
  expect(stats.darkRatio).toBeLessThan(0.2);
  expect(stats.colorBuckets).toBeGreaterThan(16);
  expect(stats.largestUniformRegionRatio).toBeLessThan(0.3);
};
