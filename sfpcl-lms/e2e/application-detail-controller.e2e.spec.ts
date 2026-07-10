import { expect, test, type Page, type Route } from '@playwright/test';

const application = {
  loan_application_id: 'app-controller-1',
  application_reference_number: null,
  member: {
    member_id: 'member-1',
    display_name: 'Controller Test Member',
    member_type: 'individual_farmer',
    folio_number: 'FOL-CONTROLLER',
    membership_status: 'active',
    kyc_status: 'verified',
  },
  application_date: '2026-07-10',
  required_loan_amount: '250000.00',
  requested_tenure_months: 12,
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  application_status: 'draft',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
  assigned_owner: null,
  nominee: {
    nominee_id: 'nominee-safe-1',
    nominee_name: 'Safe Nominee',
    age_at_application: 42,
    minor_flag: false,
    kyc_status: 'verified',
    relationship_to_borrower: 'Spouse',
    signature_required_flag: true,
  },
  available_actions: [{
    action_code: 'submit',
    label: 'Submit Application',
    enabled: true,
    disabled_reason: null,
    required_permission: 'applications.loan_application.submit',
  }],
};

test.describe('ApplicationDetail production controller', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
        accessToken: 'controller-access',
        refreshToken: 'controller-refresh',
      }));
    });
    await page.route('**/api/v1/auth/me/', route => json(route, currentUser));
    await page.route('**/api/v1/loan-request-register/**', route => json(route, [], pagination));
  });

  test('renders loading and success, then submits and refreshes through mocked HTTP', async ({ page }) => {
    let detailReads = 0;
    await page.route('**/api/v1/loan-applications/**', async route => {
      const request = route.request();
      const path = new URL(request.url()).pathname;
      if (path.endsWith('/document-checklist/')) return json(route, { loan_application_id: application.loan_application_id, items: [] });
      if (path.endsWith('/deficiencies/')) return json(route, { loan_application_id: application.loan_application_id, items: [] });
      if (path.endsWith('/submit/')) return json(route, { ...application, application_status: 'submitted', available_actions: [] });
      if (path === '/api/v1/loan-applications/') return json(route, [application], pagination);
      detailReads += 1;
      await new Promise(resolve => setTimeout(resolve, 250));
      return json(route, detailReads === 1 ? application : { ...application, application_status: 'submitted', available_actions: [] });
    });

    await openApplication(page);
    await expect(page.getByText('Loading application details from the staff API.')).toBeVisible();
    await expect(page.getByText('Controller Test Member').first()).toBeVisible();
    await expect(page.getByText('Owner:').locator('..')).toContainText('—');
    await page.getByRole('button', { name: 'Submit Application' }).click();
    await expect(page.getByText('Loading application details from the staff API.')).toBeVisible();
    await expect(page.getByText('Submitted', { exact: true }).first()).toBeVisible();
    await expect(page.getByRole('button', { name: 'Submit Application' })).toHaveCount(0);
    expect(detailReads).toBe(2);
  });

  test('renders the production error state when detail HTTP fails', async ({ page }) => {
    await page.route('**/api/v1/loan-applications/**', route => {
      const path = new URL(route.request().url()).pathname;
      if (path === '/api/v1/loan-applications/') return json(route, [application], pagination);
      if (path.endsWith('/document-checklist/')) return json(route, { loan_application_id: application.loan_application_id, items: [] });
      if (path.endsWith('/deficiencies/')) return json(route, { loan_application_id: application.loan_application_id, items: [] });
      return route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ success: false, error: { code: 'UNAVAILABLE', message: 'Controller detail unavailable.' } }),
      });
    });

    await openApplication(page);
    await expect(page.getByText('Application unavailable')).toBeVisible();
    await expect(page.getByText('Controller detail unavailable.')).toBeVisible();
  });
});

async function openApplication(page: Page) {
  await page.goto('/');
  await expect(page.getByRole('button', { name: 'Applications' })).toBeVisible();
  await page.getByRole('button', { name: 'Applications' }).click();
  await page.getByText('Controller Test Member').click();
}

const json = (route: Route, data: unknown, extra: Record<string, unknown> = {}) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data, ...extra }),
});

const pagination = {
  pagination: {
    page: 1,
    page_size: 20,
    total_count: 1,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  },
};

const currentUser = {
  user_id: 'staff-controller-1',
  full_name: 'Controller Test Staff',
  email: 'controller@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }],
  teams: [],
  role_codes: ['credit_manager'],
  team_codes: [],
  permissions: [
    'applications.loan_application.read',
    'applications.loan_application.submit',
  ],
  available_actions: [],
};
