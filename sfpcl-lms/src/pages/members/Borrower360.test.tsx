import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import {
  fetchMemberBankAccounts,
  fetchMemberCancelledCheques,
  type KycProfileDetail,
  type MemberBankAccountDetail,
  type MemberCancelledChequeDetail,
  type MemberCropPlanDetail,
  type MemberLandHoldingDetail,
  type MemberNomineeDetail,
  type MemberProfileDetail,
  type MemberShareholdingDetail,
} from '../../services/memberProfileApi';
import { Borrower360View } from './Borrower360';

const storage = new Map<string, string>();

beforeEach(() => {
  vi.stubGlobal('localStorage', {
    getItem: vi.fn((key: string) => storage.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => storage.set(key, value)),
    removeItem: vi.fn((key: string) => storage.delete(key)),
  });
  storage.clear();
  storedAuthSession({ accessToken: 'access-token-1', refreshToken: 'refresh-token-1' });
});

afterEach(() => {
  clearStoredAuthSession();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('borrower 360 API client additions', () => {
  it('loads bank and cancelled-cheque metadata from 004J endpoints without full account numbers', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(listOk([apiBankAccount]))
      .mockResolvedValueOnce(listOk([cancelledCheque]));
    vi.stubGlobal('fetch', fetchMock);

    const accounts = await fetchMemberBankAccounts('member-1');
    const cheques = await fetchMemberCancelledCheques('member-1');

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/members/member-1/bank-accounts/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/members/member-1/cancelled-cheques/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(accounts.items[0].account_number).toEqual({
      masked: '********9012',
      last4: '9012',
      can_view_full: false,
    });
    expect(accounts.items[0].account_holder_name).toBe('Ramesh Patil');
    expect(cheques.items[0].account_number.masked).toBe('********9012');
    expect(JSON.stringify(accounts)).not.toContain('123456789012');
    expect(JSON.stringify(cheques)).not.toContain('123456789012');
  });
});

describe('Borrower360View', () => {
  it('renders API-backed borrower, KYC, shareholding, land, crop, nominee, and bank metadata without mock remnants', () => {
    const html = [0, 1, 2, 3, 4, 6].map(activeTabIndex => renderBorrower360({ activeTabIndex })).join('\n');

    expect(html).toContain('Ramesh Patil');
    expect(html).toContain('Member 360');
    expect(html).toContain('******234F');
    expect(html).toContain('********9012');
    expect(html).toContain('borrower-pan.pdf');
    expect(html).toContain('FOL-456');
    expect(html).toContain('123/4');
    expect(html).toContain('grapes');
    expect(html).toContain('Sita Patil');
    expect(html).toContain('Kiran Bank Holder');
    expect(html).toContain('State Bank of India');
    expect(html).toContain('********9012');
    expect(html).toContain('No loan records are available from the backend yet.');
    expect(html).toContain('No produce supply records are available.');
    expect(html).not.toContain('Sudha Patil');
    expect(html).not.toContain('ABCDE1234F');
    expect(html).not.toContain('123456789012');
    expect(html).not.toContain('Duplicate bank account');
    expect(html).not.toContain('Payment initiation');
    expect(html).not.toContain('Disbursement readiness');
  });

  it('renders reveal controls only for backend-revealable fields and does not offer bank reveal controls', () => {
    const html = renderBorrower360({
      profile: {
        ...member,
        pan: { ...member.pan, can_view_full: true },
        aadhaar: { ...member.aadhaar, can_view_full: false },
      },
    });

    expect(html).toContain('Reason to reveal PAN');
    expect(html).toContain('Reveal');
    expect(html).not.toContain('Reason to reveal Aadhaar');
    expect(html).not.toContain('Reason to reveal Bank Account');
    expect(html).not.toContain('Reason to reveal Cancelled Cheque');
  });

  it('renders loading, empty, forbidden, and error states through the borrower layout', () => {
    expect(renderBorrower360({ status: 'loading', profile: null })).toContain('Loading borrower 360');
    expect(renderBorrower360({ status: 'empty', profile: null, message: 'Member was not found.' })).toContain('Member was not found.');
    expect(renderBorrower360({ status: 'forbidden', profile: null, message: 'You do not have permission.' })).toContain('You do not have permission.');
    expect(renderBorrower360({ status: 'error', profile: null, message: 'Borrower could not be loaded.' })).toContain('Borrower could not be loaded.');
  });
});

const member: MemberProfileDetail = {
  member_id: 'member-1',
  member_number: 'MEM-00125',
  member_type: 'individual_farmer',
  legal_name: 'Ramesh Patil',
  display_name: 'Ramesh Patil',
  folio_number: 'FOL-456',
  membership_start_date: '2021-04-01',
  membership_status: 'active',
  kyc_status: 'verified',
  rekyc_due_date: '2027-06-22',
  default_status: 'no_default',
  mobile_number: '******7890',
  email: 'ramesh@example.com',
  pan: { masked: '******234F', can_view_full: false },
  aadhaar: { masked: '********9012', can_view_full: false },
  registered_address: {
    line1: 'Village Road',
    line2: 'Near Market',
    village_city: 'Nashik',
    district: 'Nashik',
    state: 'Maharashtra',
    pincode: '422001',
  },
  share_summary: { number_of_shares: 100, holding_mode: 'physical', available_share_count: 85 },
  active_member_status: { status: 'active', verified_at: '2026-06-22T10:30:00Z' },
  individual_profile: {
    first_name: 'Ramesh',
    middle_name: null,
    last_name: 'Patil',
    gender: 'male',
    date_of_birth: '1980-01-15',
    occupation: 'Farmer',
    land_area_under_cultivation_acres: '5.00',
    primary_crop: 'grapes',
    services_availed_flag: true,
    employment_or_service_years: '12.50',
  },
  producer_institution_profile: null,
  available_actions: [],
};

const shareholding: MemberShareholdingDetail = {
  shareholding_id: 'shareholding-1',
  folio_number: 'FOL-456',
  number_of_shares: 100,
  holding_mode: 'physical',
  valuation_per_share: '2000.00',
  valuation_effective_date: '2026-04-01',
  pledged_share_count: 15,
  available_share_count: 85,
  future_shares_pledge_flag: true,
  status: 'active',
};

const landHolding: MemberLandHoldingDetail = {
  land_holding_id: 'land-1',
  document_type: '7_12_extract',
  survey_number: '123/4',
  village: 'Village Name',
  taluka: 'Niphad',
  district: 'Nashik',
  state: 'Maharashtra',
  area_acres: '5.00',
  document_id: '11111111-1111-4111-8111-111111111111',
  verification_status: 'pending',
  verified_by_user_id: null,
  verified_at: null,
  created_at: '2026-07-09T05:55:00Z',
};

const cropPlan: MemberCropPlanDetail = {
  crop_plan_id: 'crop-1',
  loan_application_id: null,
  crop_type: 'grapes',
  season: 'FY2026 Kharif',
  planned_area_acres: '5.00',
  estimated_cost_amount: '100000.00',
  loan_purpose_alignment: 'agriculture_aligned',
  document_id: '33333333-3333-4333-8333-333333333333',
  verification_status: 'pending',
  verified_by_user_id: null,
  verified_at: null,
  created_at: '2026-07-09T05:56:00Z',
};

const nominee: MemberNomineeDetail = {
  nominee_id: 'nominee-1',
  nominee_name: 'Sita Patil',
  date_of_birth: '1985-05-20',
  age_at_application: 41,
  gender: 'female',
  relationship_to_borrower: 'Spouse',
  pan: { masked: '******234F', can_view_full: false },
  aadhaar: { masked: '********1234', can_view_full: false },
  kyc_status: 'pending',
  minor_flag: false,
  signature_required_flag: true,
  created_at: '2026-07-09T05:55:00Z',
};

const kycProfile: KycProfileDetail = {
  kyc_profile_id: 'kyc-profile-1',
  party_type: 'member',
  party_id: 'member-1',
  kyc_status: 'pending',
  ckyc_consent_flag: true,
  beneficial_ownership_verified_flag: false,
  risk_rating: 'low',
  last_verified_at: null,
  last_verified_by_user_id: null,
  rekyc_due_date: '2028-07-09',
  rejection_reason: null,
  documents: [{
    kyc_document_id: 'kyc-document-1',
    kyc_profile_id: 'kyc-profile-1',
    document_type: 'pan',
    document_id: '44444444-4444-4444-8444-444444444444',
    file_name: 'borrower-pan.pdf',
    mime_type: 'application/pdf',
    file_size_bytes: 128,
    sensitivity_level: 'restricted',
    self_attested_flag: true,
    verification_status: 'verified',
    verified_by_user_id: null,
    verified_at: '2026-07-09T08:00:00Z',
    remarks: null,
    created_at: '2026-07-09T08:00:00Z',
  }],
};

const bankAccount: MemberBankAccountDetail = {
  bank_account_id: 'bank-1',
  account_holder_name: 'Kiran Bank Holder',
  account_number: { masked: '********9012', last4: '9012', can_view_full: false },
  ifsc: 'SBIN0001234',
  bank_name: 'State Bank of India',
  branch_name: 'Nashik Branch',
  verification_status: 'verified',
  cancelled_cheque_id: 'cheque-1',
  signature_verified_flag: true,
  status: 'active',
  created_at: '2026-07-09T08:00:00Z',
};

const apiBankAccount: MemberBankAccountDetail = {
  ...bankAccount,
  account_holder_name: 'Ramesh Patil',
};

const cancelledCheque: MemberCancelledChequeDetail = {
  cancelled_cheque_id: 'cheque-1',
  loan_application_id: null,
  document_id: '55555555-5555-4555-8555-555555555555',
  account_number: { masked: '********9012', last4: '9012', can_view_full: false },
  ifsc: 'SBIN0001234',
  branch_name: 'Nashik Branch',
  verification_status: 'verified',
  signature_mismatch_flag: false,
  created_at: '2026-07-09T08:00:00Z',
};

const renderBorrower360 = (overrides: Partial<React.ComponentProps<typeof Borrower360View>> = {}) => renderToStaticMarkup(
  <Borrower360View
    status="success"
    message=""
    profile={member}
    shareholdings={[shareholding]}
    landHoldings={[landHolding]}
    cropPlans={[cropPlan]}
    nominees={[nominee]}
    kycProfile={kycProfile}
    bankAccounts={[bankAccount]}
    cancelledCheques={[cancelledCheque]}
    onBack={vi.fn()}
    onOpenApplication={vi.fn()}
    onOpenLoanAccount={vi.fn()}
    {...overrides}
  />,
);

function listOk(data: unknown[]): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      success: true,
      data,
      pagination: {
        page: 1,
        page_size: 20,
        total_count: data.length,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
