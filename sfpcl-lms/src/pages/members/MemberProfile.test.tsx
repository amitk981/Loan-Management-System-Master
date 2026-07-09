import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import { fetchMemberProfile, type MemberProfileDetail } from '../../services/memberProfileApi';
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
    expect(html).toContain('No nominee records are available from the backend yet.');
    expect(html).toContain('No communication records are available from the backend yet.');
    expect(html).toContain('No audit trail records are available from the backend yet.');
    expect(html).not.toContain('APP-');
    expect(html).not.toContain('Sudha Patil');
    expect(html).not.toContain('Overdue repayment reminder');
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

const renderProfile = (
  status: React.ComponentProps<typeof MemberProfileView>['status'],
  profile: MemberProfileDetail | null,
  activeTab: number,
  message = '',
) => renderToStaticMarkup(
  <MemberProfileView
    status={status}
    message={message}
    profile={profile}
    activeTab={activeTab}
    onTabChange={vi.fn()}
    onBack={vi.fn()}
  />,
);

function ok(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => ({ success: true, data, meta: { api_version: 'v1' } }),
  } as Response;
}

function error(status: number, code: string): Response {
  return {
    ok: false,
    status,
    json: async () => ({
      success: false,
      error: { code, message: code === 'PERMISSION_DENIED' ? 'You do not have permission.' : 'Request failed.' },
      meta: { api_version: 'v1' },
    }),
  } as Response;
}
