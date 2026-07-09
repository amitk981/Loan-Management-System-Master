import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import {
  createMemberCropPlan,
  createMemberLandHolding,
  createMemberShareholding,
  createMemberNominee,
  fetchMemberCropPlans,
  fetchMemberLandHoldings,
  fetchMemberNominees,
  fetchMemberProfile,
  fetchMemberShareholdings,
  type KycDocumentDetail,
  type KycProfileDetail,
  type MemberCropPlanDetail,
  type MemberLandHoldingDetail,
  type MemberNomineeDetail,
  type MemberProfileDetail,
  type MemberShareholdingDetail,
} from '../../services/memberProfileApi';
import { MemberProfileView } from './MemberProfile';

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

describe('member profile API client', () => {
  it('loads a member profile detail from the backend with the stored bearer token', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(ok(member));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchMemberProfile('member-1');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/member-1/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(result.pan).toEqual({ masked: '******234F', can_view_full: false });
  });

  it.each([['AUTH_REQUIRED', 401], ['PERMISSION_DENIED', 403], ['NOT_FOUND', 404]])(
    'surfaces %s without substituting mock profile data',
    async (code, status) => {
      vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(error(status, code)));
      await expect(fetchMemberProfile('member-1')).rejects.toMatchObject({ code, status });
    },
  );

  it('loads member nominees through the source-backed nominee endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(listOk([nominee]));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchMemberNominees('member-1');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/member-1/nominees/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(result.items[0].pan.masked).toBe('******234F');
    expect(result.items[0].aadhaar.masked).toBe('********1234');
  });

  it('creates member nominees without falling back to mock data and surfaces validation fields', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(nominee))
      .mockResolvedValueOnce(error(400, 'INVALID_PAN_FORMAT', { pan: 'PAN must match the source-defined format.' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createMemberNominee('member-1', nomineeRequest)).resolves.toMatchObject({
      nominee_name: 'Sita Patil',
      pan: { masked: '******234F', can_view_full: false },
    });
    await expect(createMemberNominee('member-1', { ...nomineeRequest, pan: 'bad-pan' })).rejects.toMatchObject({
      code: 'INVALID_PAN_FORMAT',
      fieldErrors: { pan: 'PAN must match the source-defined format.' },
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/members/member-1/nominees/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(nomineeRequest),
      }),
    );
  });

  it('loads member shareholdings through the source-backed shareholding endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(listOk([shareholding]));
    vi.stubGlobal('fetch', fetchMock);

    const result = await fetchMemberShareholdings('member-1');

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/member-1/shareholdings/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(result.items[0]).toMatchObject({
      folio_number: 'FOL-456',
      number_of_shares: 100,
      pledged_share_count: 15,
      available_share_count: 85,
    });
  });

  it('creates member shareholdings and surfaces validation fields', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(shareholding))
      .mockResolvedValueOnce(error(400, 'VALIDATION_ERROR', { pledged_share_count: 'Pledged shares cannot exceed total shares.' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createMemberShareholding('member-1', shareholdingRequest)).resolves.toMatchObject({
      folio_number: 'FOL-456',
      available_share_count: 85,
    });
    await expect(createMemberShareholding('member-1', {
      ...shareholdingRequest,
      pledged_share_count: 101,
    })).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      fieldErrors: { pledged_share_count: 'Pledged shares cannot exceed total shares.' },
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/members/member-1/shareholdings/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(shareholdingRequest),
      }),
    );
  });

  it('loads land holdings and crop plans through source-backed endpoints', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(listOk([landHolding]))
      .mockResolvedValueOnce(listOk([cropPlan]));
    vi.stubGlobal('fetch', fetchMock);

    const landResult = await fetchMemberLandHoldings('member-1');
    const cropResult = await fetchMemberCropPlans('member-1');

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/members/member-1/land-holdings/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/members/member-1/crop-plans/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({ Authorization: 'Bearer access-token-1' }),
      }),
    );
    expect(landResult.items[0]).toMatchObject({ survey_number: '123/4', area_acres: '5.00' });
    expect(cropResult.items[0]).toMatchObject({ crop_type: 'grapes', planned_area_acres: '5.00' });
  });

  it('creates land holdings and crop plans and surfaces validation fields', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(ok(landHolding))
      .mockResolvedValueOnce(error(400, 'VALIDATION_ERROR', { area_acres: 'Value must be greater than zero.' }))
      .mockResolvedValueOnce(ok(cropPlan))
      .mockResolvedValueOnce(error(400, 'VALIDATION_ERROR', { planned_area_acres: 'Value must be greater than zero.' }));
    vi.stubGlobal('fetch', fetchMock);

    await expect(createMemberLandHolding('member-1', landHoldingRequest)).resolves.toMatchObject({
      survey_number: '123/4',
      area_acres: '5.00',
    });
    await expect(createMemberLandHolding('member-1', {
      ...landHoldingRequest,
      area_acres: '0',
    })).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      fieldErrors: { area_acres: 'Value must be greater than zero.' },
    });
    await expect(createMemberCropPlan('member-1', cropPlanRequest)).resolves.toMatchObject({
      crop_type: 'grapes',
      planned_area_acres: '5.00',
    });
    await expect(createMemberCropPlan('member-1', {
      ...cropPlanRequest,
      planned_area_acres: '0',
    })).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      fieldErrors: { planned_area_acres: 'Value must be greater than zero.' },
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/members/member-1/land-holdings/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(landHoldingRequest),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      'http://127.0.0.1:8000/api/v1/members/member-1/crop-plans/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(cropPlanRequest),
      }),
    );
  });

});

describe('MemberProfileView', () => {
  it('renders API-backed overview data, masked identifiers, and no reveal controls', () => {
    const html = renderProfile('success', member, 0);

    expect(html).toContain('Ramesh Patil');
    expect(html).toContain('MEM-00125');
    expect(html).toContain('******234F');
    expect(html).toContain('********9012');
    expect(html).toContain('Village Road');
    expect(html).toContain('Start Application');
    expect(html).not.toContain('Reveal');
    expect(html).not.toContain('ABCDE1234F');
    expect(html).not.toContain('Ganesh Thorat');
  });

  it('renders individual farmer profile details from the API', () => {
    const html = renderProfile('success', member, 0);

    expect(html).toContain('Individual Farmer Details');
    expect(html).toContain('Ramesh');
    expect(html).toContain('Patil');
    expect(html).toContain('15/1/1980');
    expect(html).toContain('Farmer');
    expect(html).toContain('12.50 years');
  });

  it('renders producer institution details without sensitive signatory identifiers', () => {
    const html = renderProfile('success', producerMember, 0);

    expect(html).toContain('Producer Institution Details');
    expect(html).toContain('farmer producer company');
    expect(html).toContain('U00000MH2021PTC000000');
    expect(html).toContain('Authorised Person');
    expect(html).toContain('2.00 years');
    expect(html).not.toContain('Signatory PAN');
    expect(html).not.toContain('Signatory Aadhaar');
  });

  it('uses the existing empty-value treatment when the type-specific profile is missing', () => {
    const html = renderProfile('success', { ...producerMember, producer_institution_profile: null }, 0);

    expect(html).toContain('Producer Institution Details');
    expect(html).toContain('Profile details are not available from the backend yet.');
  });

  it('renders deferred tab empty states instead of synthetic mock rows', () => {
    const html = [6, 7, 8, 9].map(tab => renderProfile('success', member, tab)).join('\n');

    expect(html).toContain('No loan records are available from the backend yet.');
    expect(html).toContain('No communication records are available from the backend yet.');
    expect(html).toContain('No audit trail records are available from the backend yet.');
    expect(html).not.toContain('APP-');
    expect(html).not.toContain('Overdue repayment reminder');
  });

  it('renders shareholding tab list and create states from the API', () => {
    expect(renderProfile('success', member, 1, '', { shareholdingStatus: 'loading' })).toContain('Loading shareholding records');
    expect(renderProfile('success', member, 1, '', { shareholdingStatus: 'empty', shareholdings: [] })).toContain('No shareholding records are available from the backend yet.');
    expect(renderProfile('success', member, 1, '', { shareholdingStatus: 'error', shareholdingMessage: 'Shareholdings could not be loaded.' })).toContain('Shareholdings could not be loaded.');
    const html = renderProfile('success', member, 1, '', {
      shareholdingStatus: 'success',
      shareholdings: [shareholding],
      shareholdingCreateMessage: 'Shareholding saved.',
    });

    expect(html).toContain('Shareholding Details');
    expect(html).toContain('FOL-456');
    expect(html).toContain('Physical');
    expect(html).toContain('100');
    expect(html).toContain('85');
    expect(html).toContain('Shareholding saved.');
    expect(html).not.toContain('mockData');
  });

  it('renders shareholding validation errors without falling back to profile summary rows', () => {
    const html = renderProfile('success', member, 1, '', {
      shareholdingStatus: 'success',
      shareholdings: [],
      shareholdingCreateFieldErrors: { pledged_share_count: 'Pledged shares cannot exceed total shares.' },
    });

    expect(html).toContain('Pledged shares cannot exceed total shares.');
    expect(html).not.toContain('Share certificate details are not available from the backend yet.');
  });

  it('renders nominee tab list and masked identifiers from the API', () => {
    const html = renderProfile('success', member, 7, '', {
      nomineeStatus: 'success',
      nominees: [nominee],
    });

    expect(html).toContain('Nominee Details');
    expect(html).toContain('Sita Patil');
    expect(html).toContain('Spouse');
    expect(html).toContain('******234F');
    expect(html).toContain('********1234');
    expect(html).toContain('Pending');
    expect(html).not.toContain('ABCDE1234F');
    expect(html).not.toContain('123412341234');
    expect(html).not.toContain('Sudha Patil');
  });

  it('renders nominee empty, loading, error, forbidden, validation, and success states', () => {
    expect(renderProfile('success', member, 7, '', { nomineeStatus: 'loading' })).toContain('Loading nominee records');
    expect(renderProfile('success', member, 7, '', { nomineeStatus: 'empty', nominees: [] })).toContain('No nominee records are available from the backend yet.');
    expect(renderProfile('success', member, 7, '', { nomineeStatus: 'error', nomineeMessage: 'Nominees could not be loaded.' })).toContain('Nominees could not be loaded.');
    expect(renderProfile('success', member, 7, '', { nomineeStatus: 'forbidden', nomineeMessage: 'You do not have permission to read nominees.' })).toContain('You do not have permission to read nominees.');
    expect(renderProfile('success', member, 7, '', {
      nomineeStatus: 'success',
      nominees: [],
      nomineeCreateFieldErrors: { pan: 'PAN must match the source-defined format.' },
    })).toContain('PAN must match the source-defined format.');
    expect(renderProfile('success', member, 7, '', {
      nomineeStatus: 'success',
      nominees: [nominee],
      nomineeCreateMessage: 'Nominee saved.',
    })).toContain('Nominee saved.');
  });

  it('renders land and crop tab list, loading, empty, error, validation, and success states from the API', () => {
    expect(renderProfile('success', member, 4, '', { landCropStatus: 'loading' })).toContain('Loading land and crop records');
    expect(renderProfile('success', member, 4, '', { landCropStatus: 'empty', landHoldings: [], cropPlans: [] })).toContain('No land or crop records are available from the backend yet.');
    expect(renderProfile('success', member, 4, '', { landCropStatus: 'error', landCropMessage: 'Land and crop records could not be loaded.' })).toContain('Land and crop records could not be loaded.');
    const html = renderProfile('success', member, 4, '', {
      landCropStatus: 'success',
      landHoldings: [landHolding],
      cropPlans: [cropPlan],
      landCreateMessage: 'Land holding saved.',
      cropCreateMessage: 'Crop plan saved.',
    });

    expect(html).toContain('Land &amp; Crop Evidence');
    expect(html).toContain('123/4');
    expect(html).toContain('5.00 acres');
    expect(html).toContain('7_12_extract');
    expect(html).toContain('grapes');
    expect(html).toContain('FY2026 Kharif');
    expect(html).toContain('100000.00');
    expect(html).toContain('Land holding saved.');
    expect(html).toContain('Crop plan saved.');
    expect(html).not.toContain('Per-acre scale of finance');
    expect(html).not.toContain('Land-based eligible amount');
  });

  it('renders land and crop validation errors without falling back to profile summary rows', () => {
    const html = renderProfile('success', member, 4, '', {
      landCropStatus: 'success',
      landHoldings: [],
      cropPlans: [],
      landCreateFieldErrors: { document_id: 'This field is required.' },
      cropCreateFieldErrors: { planned_area_acres: 'Value must be greater than zero.' },
    });

    expect(html).toContain('This field is required.');
    expect(html).toContain('Value must be greater than zero.');
    expect(html).not.toContain('Land Area Under Cultivation');
    expect(html).not.toContain('Primary Crop');
  });

  it('renders KYC tab loading, empty, error, validation, success, and document metadata states from the API', () => {
    expect(renderProfile('success', member, 5, '', { kycStatus: 'loading' })).toContain('Loading KYC records');
    expect(renderProfile('success', member, 5, '', { kycStatus: 'empty', kycProfile: null })).toContain('No KYC profile is available from the backend yet.');
    expect(renderProfile('success', member, 5, '', { kycStatus: 'error', kycMessage: 'KYC records could not be loaded.' })).toContain('KYC records could not be loaded.');
    const html = renderProfile('success', member, 5, '', {
      kycStatus: 'success',
      kycProfile,
      kycCreateMessage: 'KYC profile saved.',
      kycDocumentMessage: 'KYC document uploaded.',
      kycVerifyMessage: 'KYC document verified.',
    });

    expect(html).toContain('KYC Profile');
    expect(html).toContain('CKYC Consent');
    expect(html).toContain('Low');
    expect(html).toContain('borrower-pan.pdf');
    expect(html).toContain('Self Attested');
    expect(html).toContain('KYC profile saved.');
    expect(html).toContain('KYC document uploaded.');
    expect(html).toContain('KYC document verified.');
    expect(html).not.toContain('KYC document records are not available from the backend yet.');
    expect(html).not.toContain('ABCDE1234F');
    expect(html).not.toContain('123412341234');

    const validationHtml = renderProfile('success', member, 5, '', {
      kycStatus: 'success',
      kycProfile,
      kycCreateFieldErrors: { ckyc_consent_flag: 'This field is required.' },
      kycDocumentFieldErrors: { self_attested_flag: 'Self-attestation is required for PAN and Aadhaar.' },
      kycVerifyFieldErrors: { verification_status: 'Must be verified or rejected.' },
    });
    expect(validationHtml).toContain('This field is required.');
    expect(validationHtml).toContain('Self-attestation is required for PAN and Aadhaar.');
    expect(validationHtml).toContain('Must be verified or rejected.');
  });

  it('renders loading, empty, and auth/error states using existing profile layout patterns', () => {
    expect(renderProfile('loading', null, 0)).toContain('Loading member profile');
    expect(renderProfile('empty', null, 0)).toContain('Member profile unavailable');
    expect(renderProfile('unauthorized', null, 0, 'Please sign in to continue.')).toContain('Please sign in to continue.');
    expect(renderProfile('forbidden', null, 0, 'You do not have permission.')).toContain('You do not have permission.');
    expect(renderProfile('error', null, 0, 'Member could not be loaded.')).toContain('Member could not be loaded.');
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
  share_summary: { number_of_shares: 100, holding_mode: 'physical', available_share_count: 100 },
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
  available_actions: [{
    action_code: 'create_loan_application',
    label: 'Start Application',
    enabled: true,
    disabled_reason: null,
    required_permission: 'applications.loan_application.create',
  }],
};

const producerMember: MemberProfileDetail = {
  ...member,
  member_id: 'member-2',
  member_number: 'MEM-00126',
  member_type: 'fpc',
  legal_name: 'ABC Farmer Producer Company Limited',
  display_name: 'ABC FPC',
  folio_number: 'FOL-789',
  individual_profile: null,
  producer_institution_profile: {
    institution_type: 'farmer_producer_company',
    registration_number: 'U00000MH2021PTC000000',
    authorised_signatory_name: 'Authorised Person',
    board_resolution_required_flag: true,
    services_availed_flag: true,
    produce_supply_years: '2.00',
  },
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

const nomineeRequest = {
  nominee_name: 'Sita Patil',
  date_of_birth: '1985-05-20',
  gender: 'female',
  relationship_to_borrower: 'Spouse',
  pan: 'ABCDE1234F',
  aadhaar: '123412341234',
  signature_required_flag: true,
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

const shareholdingRequest = {
  folio_number: 'FOL-456',
  number_of_shares: 100,
  holding_mode: 'physical',
  valuation_per_share: '2000.00',
  valuation_effective_date: '2026-04-01',
  pledged_share_count: 15,
  future_shares_pledge_flag: true,
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
  loan_application_id: '22222222-2222-4222-8222-222222222222',
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

const landHoldingRequest = {
  document_type: '7_12_extract',
  survey_number: '123/4',
  village: 'Village Name',
  taluka: 'Niphad',
  district: 'Nashik',
  state: 'Maharashtra',
  area_acres: '5.00',
  document_id: '11111111-1111-4111-8111-111111111111',
};

const cropPlanRequest = {
  loan_application_id: '22222222-2222-4222-8222-222222222222',
  crop_type: 'grapes',
  season: 'FY2026 Kharif',
  planned_area_acres: '5.00',
  estimated_cost_amount: '100000.00',
  loan_purpose_alignment: 'agriculture_aligned',
  document_id: '33333333-3333-4333-8333-333333333333',
};

const kycDocument: KycDocumentDetail = {
  kyc_document_id: 'kyc-document-1',
  kyc_profile_id: 'kyc-profile-1',
  document_type: 'pan',
  document_id: '44444444-4444-4444-8444-444444444444',
  file_name: 'borrower-pan.pdf',
  mime_type: 'application/pdf',
  file_size_bytes: 128,
  sensitivity_level: 'restricted',
  self_attested_flag: true,
  verification_status: 'pending',
  verified_by_user_id: null,
  verified_at: null,
  remarks: null,
  created_at: '2026-07-09T08:00:00Z',
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
  rekyc_due_date: null,
  rejection_reason: null,
  documents: [kycDocument],
};

const renderProfile = (
  status: React.ComponentProps<typeof MemberProfileView>['status'],
  profile: MemberProfileDetail | null,
  activeTab: number,
  message = '',
  overrides: Partial<React.ComponentProps<typeof MemberProfileView>> = {},
) => renderToStaticMarkup(
  <MemberProfileView
    status={status}
    message={message}
    profile={profile}
    activeTab={activeTab}
    onTabChange={vi.fn()}
    onBack={vi.fn()}
    onCreateNominee={vi.fn()}
    onCreateShareholding={vi.fn()}
    onCreateLandHolding={vi.fn()}
    onCreateCropPlan={vi.fn()}
    onCreateKycProfile={vi.fn()}
    onUpdateKycProfile={vi.fn()}
    onUploadKycDocument={vi.fn()}
    onVerifyKycDocument={vi.fn()}
    {...overrides}
  />,
);

function ok(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, meta: { api_version: 'v1' } }),
  } as Response;
}

function error(status: number, code: string, fieldErrors: Record<string, string> = {}): Response {
  return {
    ok: false,
    status,
    json: async () => ({
      success: false,
      error: {
        code,
        message: code === 'PERMISSION_DENIED' ? 'You do not have permission.' : 'Request failed.',
        field_errors: fieldErrors,
      },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}

function listOk(data: unknown[]): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, pagination: { page: 1, page_size: 20, total_count: data.length, total_pages: 1, has_next: false, has_previous: false }, meta: { api_version: 'v1' } }),
  } as Response;
}
