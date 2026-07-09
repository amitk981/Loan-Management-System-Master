import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { MP03DashboardView } from './MP03_Dashboard';
import { MP04ProfileView } from './MP04_MyProfile';
import { MP09ApplicationsView } from './applications/MP09_MyApplications';
import { MP22ProduceSupplyView } from './supply/MP22_ProduceSupply';
import type { PortalApplication, PortalDashboard, PortalProduceSupply, PortalProfile } from '../../../services/portalApi';

describe('member portal backend-backed views', () => {
  it('renders MP03 dashboard counts and pending actions from the portal API', () => {
    const html = renderToStaticMarkup(<MP03DashboardView summary={dashboard} onNavigate={vi.fn()} />);

    expect(html).toContain('Ganesh Thorat');
    expect(html).toContain('FOL-005FB');
    expect(html).toContain('Open deficiencies');
    expect(html).toContain('1');
    expect(html).not.toContain('LO00000042');
  });

  it('renders MP04 profile tabs with masked sensitive values from the portal API', () => {
    const html = renderToStaticMarkup(<MP04ProfileView profile={profile} />);

    expect(html).toContain('Ganesh Thorat');
    expect(html).toContain('******234F');
    expect(html).toContain('********9012');
    expect(html).toContain('Suman Thorat');
    expect(html).not.toContain('123456789012');
  });

  it('renders MP22 produce supply empty shell when the backend model is not implemented', () => {
    const html = renderToStaticMarkup(<MP22ProduceSupplyView supply={produceSupply} />);

    expect(html).toContain('Produce Supply History');
    expect(html).toContain('No produce supply records are available yet.');
    expect(html).toContain('model not implemented');
  });

  it('renders MP09 loading, empty, error, and returned-incomplete application states', () => {
    expect(renderToStaticMarkup(
      <MP09ApplicationsView applications={[]} loading error={null} onNavigateToApplication={vi.fn()} onNavigateToNew={vi.fn()} />
    )).toContain('Loading applications');

    expect(renderToStaticMarkup(
      <MP09ApplicationsView applications={[]} loading={false} error={null} onNavigateToApplication={vi.fn()} onNavigateToNew={vi.fn()} />
    )).toContain('No loan applications have been started yet.');

    expect(renderToStaticMarkup(
      <MP09ApplicationsView applications={[]} loading={false} error="Portal access denied." onNavigateToApplication={vi.fn()} onNavigateToNew={vi.fn()} />
    )).toContain('Portal access denied.');

    const html = renderToStaticMarkup(
      <MP09ApplicationsView applications={[returnedApplication]} loading={false} error={null} onNavigateToApplication={vi.fn()} onNavigateToNew={vi.fn()} />
    );
    expect(html).toContain('Action Needed');
    expect(html).toContain('Review deficiencies');
    expect(html).toContain('APP-RETURN');
  });
});

const member = {
  member_id: 'member-1',
  member_number: 'M-005FB',
  member_type: 'individual_farmer',
  legal_name: 'Ganesh Thorat',
  display_name: 'Ganesh Thorat',
  folio_number: 'FOL-005FB',
  membership_status: 'active',
  kyc_status: 'verified',
  default_status: 'no_default',
  mobile_number: '******0042',
  email: 'ganesh@sfpcl.example',
  pan: { masked: '******234F', can_view_full: false },
  aadhaar: { masked: '********9012', can_view_full: false },
  share_summary: { number_of_shares: 5, holding_mode: 'physical', available_share_count: 5 },
  active_member_status: { status: 'active', verified_at: '2026-07-09T10:00:00Z' },
  individual_profile: { primary_crop: 'grapes', land_area_under_cultivation_acres: '4.50' },
};

const dashboard: PortalDashboard = {
  member,
  application_counts: { total: 1, draft: 0, submitted: 0, incomplete_returned: 1 },
  loan_counts: { active: 0 },
  pending_actions: { open_deficiencies: 1, signature_pending: 0, repayment_due: 0, kyc_update_due: 0 },
  notices: [],
};

const profile: PortalProfile = {
  member,
  nominees: [{ nominee_name: 'Suman Thorat', relationship_to_borrower: 'spouse', pan: { masked: '******678K' }, aadhaar: { masked: '********1234' }, kyc_status: 'verified' }],
  shareholdings: [{ folio_number: 'FOL-005FB', number_of_shares: 5, holding_mode: 'physical', available_share_count: 5, status: 'active' }],
  land_holdings: [{ survey_number: '123/4', village: 'Niphad', area_acres: '4.50', verification_status: 'verified' }],
  crop_plans: [{ season: 'Kharif 2026', crop_type: 'grapes', planned_area_acres: '2.50', verification_status: 'verified' }],
  bank_accounts: [{ account_holder_name: 'Ganesh Thorat', account_number: { masked: '********9012' }, ifsc: 'SBIN0001234', bank_name: 'State Bank of India', branch_name: 'Nashik Main', verification_status: 'verified' }],
  cancelled_cheques: [],
  kyc_profile: { kyc_status: 'verified', rekyc_due_date: '2027-06-22', risk_rating: 'low' },
};

const produceSupply: PortalProduceSupply = {
  member_id: 'member-1',
  records: [],
  summary: {},
  source_status: 'model_not_implemented',
};

const returnedApplication: PortalApplication = {
  loan_application_id: 'app-returned',
  application_reference_number: null,
  display_reference: 'APP-RETURN',
  application_date: '2026-07-10',
  submitted_at: '2026-07-10T08:00:00Z',
  required_loan_amount: '250000.00',
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  loan_type_requested: 'short_term',
  application_status: 'incomplete_returned',
  current_stage: 'initial_loan_request',
  completeness_status: 'incomplete',
  pending_with: 'Borrower',
  borrower_action: 'Review deficiencies',
  open_deficiency_count: 1,
  created_at: '2026-07-10T07:00:00Z',
  updated_at: '2026-07-10T09:00:00Z',
};
