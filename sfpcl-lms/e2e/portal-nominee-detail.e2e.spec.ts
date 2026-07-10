import { expect, test, type Route } from '@playwright/test';

test('portal detail renders every safe nominee fact and no sensitive controls', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
      accessToken: 'portal-detail-access',
      refreshToken: 'portal-detail-refresh',
    }));
  });
  await page.route('**/api/v1/auth/me/', route => json(route, portalCurrentUser));
  await page.route('**/api/v1/portal/dashboard/', route => json(route, {
    member: portalApplication.member,
    application_counts: {},
    loan_counts: { active: 0 },
    pending_actions: {},
    notices: [],
  }));
  await page.route('**/api/v1/portal/applications/', route => json(route, { items: [portalApplication] }));
  await page.route('**/api/v1/portal/applications/app-portal-safe/', route => json(route, portalApplication));

  await page.goto('/');
  await page.getByRole('button', { name: 'My Applications' }).click();
  await page.getByText('PORTAL-SAFE').click();
  await page.getByRole('button', { name: 'Submitted Data & Deficiencies' }).click();

  for (const value of [
    'nominee-safe-portal-1',
    'Safe Portal Nominee',
    'Spouse',
    '42',
    'Adult',
    'verified',
    'Required',
  ]) {
    await expect(page.getByText(value, { exact: true }).first()).toBeVisible();
  }
  await expect(page.getByText(/Nominee PAN/i)).toHaveCount(0);
  await expect(page.getByText(/Nominee Aadhaar/i)).toHaveCount(0);
  await expect(page.getByText(/token|hash|reveal/i)).toHaveCount(0);

  const evidenceDir = process.env.RALPH_EVIDENCE_DIR;
  if (evidenceDir) {
    await page.screenshot({ path: `${evidenceDir}/portal-nominee-detail.png`, fullPage: true });
  }
});

const json = (route: Route, data: unknown) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ success: true, data }),
});

const portalApplication = {
  loan_application_id: 'app-portal-safe',
  application_reference_number: null,
  display_reference: 'PORTAL-SAFE',
  application_date: '2026-07-10',
  submitted_at: '2026-07-10T08:00:00Z',
  required_loan_amount: '250000.00',
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  loan_type_requested: 'short_term',
  requested_tenure_months: 12,
  application_status: 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
  pending_with: 'SFPCL',
  borrower_action: 'No action required',
  open_deficiency_count: 0,
  created_at: '2026-07-10T07:00:00Z',
  updated_at: '2026-07-10T08:00:00Z',
  member: {
    member_id: 'member-portal-1',
    member_number: 'MEM-PORTAL-1',
    member_type: 'individual_farmer',
    display_name: 'Portal Member',
    folio_number: 'FOL-PORTAL-1',
    membership_status: 'active',
    kyc_status: 'verified',
    default_status: 'no_default',
    share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 },
    active_member_status: { status: 'active', verified_at: null },
  },
  nominee: {
    nominee_id: 'nominee-safe-portal-1',
    nominee_name: 'Safe Portal Nominee',
    age_at_application: 42,
    minor_flag: false,
    kyc_status: 'verified',
    relationship_to_borrower: 'Spouse',
    signature_required_flag: true,
  },
  timeline: [],
  deficiencies: [],
};

const portalCurrentUser = {
  user_id: 'portal-user-1',
  full_name: 'Portal Member',
  email: 'portal.member@sfpcl.example',
  status: 'active',
  roles: [{ role_code: 'borrower_portal_user', role_name: 'Borrower Portal User' }],
  teams: [],
  role_codes: ['borrower_portal_user'],
  team_codes: [],
  permissions: ['portal.loan_application.read_own'],
  available_actions: [],
  member_id: 'member-portal-1',
  portal_account_id: 'portal-account-1',
  portal_role: 'borrower_member',
  member_display_name: 'Portal Member',
};
