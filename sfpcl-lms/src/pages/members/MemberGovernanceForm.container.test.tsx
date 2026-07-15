// @vitest-environment jsdom
import React from 'react';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import type { MemberProfileDetail } from '../../services/memberProfileApi';
import App from '../../App';
import MemberGovernanceForm from './MemberGovernanceForm';
import MemberProfile from './MemberProfile';

beforeEach(() => {
  vi.stubGlobal('localStorage', window.localStorage);
  storedAuthSession({ accessToken: 'mounted-access', refreshToken: 'mounted-refresh' });
});

afterEach(() => {
  cleanup();
  clearStoredAuthSession();
  window.localStorage.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('MemberGovernanceForm production container', { sequential: true, timeout: 15_000 }, () => {
  it('routes Directory registration into canonical Profile readback with the exact create ledger', async () => {
    const mutationCreate = { ...profile, member_id: 'member-routed', display_name: 'Mutation create leak', pan: { masked: '******LEAK', can_view_full: false } };
    const canonicalCreate = { ...profile, member_id: 'member-routed', display_name: 'Canonical created member', mobile_number: '********3210', available_actions: [updateAction] };
    const memberResponses = [mutationCreate, canonicalCreate];
    const memberRequests: Array<{ url: string; method: string; body?: unknown }> = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.endsWith('/api/v1/auth/me/')) return response(200, { success: true, data: backendUser });
      if (url.endsWith('/api/v1/dashboard/')) return response(200, { success: true, data: { role_context: 'credit_manager', cards: [], tasks: [] } });
      if (url.includes('/api/v1/members/')) {
        memberRequests.push({ url, method, body: init?.body ? JSON.parse(String(init.body)) : undefined });
        if (method === 'GET' && new URL(url).pathname === '/api/v1/members/') return response(200, { success: true, data: [], pagination: { page: 1, page_size: 20, total_items: 0, total_pages: 0 } });
        return response(200, { success: true, data: memberResponses.shift() });
      }
      return response(200, { success: true, data: { items: [], counts: {}, pagination: { page: 1, page_size: 20, total_items: 0, total_pages: 0 } } });
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: 'Members & Borrowers' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Register Member' }));
    await fillCompleteCreate('individual_farmer');
    await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

    expect(await screen.findByRole('heading', { name: 'Canonical created member' })).toBeTruthy();
    expect(screen.queryByText('Mutation create leak')).toBeNull();
    expect(memberRequests.map(({ url, method }) => [method, new URL(url).pathname])).toEqual([
      ['GET', '/api/v1/members/'], ['POST', '/api/v1/members/'], ['GET', '/api/v1/members/member-routed/'],
    ]);
    expect(memberRequests[1].body).toEqual(JSON.parse(JSON.stringify(completeBody('individual_farmer'))));
  });

  it('performs one ordinary human-like update before canonical Profile readback with the exact update ledger', async () => {
    const typeSpy = vi.spyOn(userEvent, 'type');
    const canonicalCreate = { ...profile, member_id: 'member-routed', display_name: 'Canonical created member', mobile_number: '********3210', available_actions: [updateAction] };
    const mutationUpdate = { ...canonicalCreate, version: 8, display_name: 'Mutation update leak' };
    const canonicalUpdate = { ...canonicalCreate, version: 8, display_name: 'Canonical updated member' };
    const memberResponses = [canonicalCreate, mutationUpdate, canonicalUpdate];
    const memberRequests: Array<{ url: string; method: string; body?: unknown }> = [];
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? 'GET';
      if (url.includes('/api/v1/members/')) {
        memberRequests.push({ url, method, body: init?.body ? JSON.parse(String(init.body)) : undefined });
        return response(200, { success: true, data: memberResponses.shift() });
      }
      return response(200, { success: true, data: { items: [], counts: {}, pagination: { page: 1, page_size: 20, total_items: 0, total_pages: 0 } } });
    });
    vi.stubGlobal('fetch', fetchMock);
    render(<MemberProfile memberId="member-routed" onBack={vi.fn()} />);

    expect(await screen.findByRole('heading', { name: 'Canonical created member' })).toBeTruthy();
    await replace('Display Name', 'Requested display name');
    await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

    expect(await screen.findByRole('heading', { name: 'Canonical updated member' })).toBeTruthy();
    expect(screen.queryByText('Mutation update leak')).toBeNull();
    expect(memberRequests.map(({ url, method }) => [method, new URL(url).pathname])).toEqual([
      ['GET', '/api/v1/members/member-routed/'], ['PATCH', '/api/v1/members/member-routed/'],
      ['GET', '/api/v1/members/member-routed/'],
    ]);
    expect(memberRequests[1].body).toEqual({
      version: 7,
      legal_name: canonicalCreate.legal_name,
      display_name: 'Requested display name',
      membership_start_date: canonicalCreate.membership_start_date,
      registered_address: canonicalCreate.registered_address,
      email: canonicalCreate.email,
    });
    expect(typeSpy).toHaveBeenCalledTimes(1);
  });

  it.each(['individual_farmer', 'fpc', 'producer_institution'] as const)(
    'submits the complete %s body through the shared HTTP transport', async memberType => {
      const canonical = { ...profile, member_type: memberType };
      const fetchMock = vi.fn()
        .mockResolvedValueOnce(response(200, { success: true, data: canonical }))
        .mockResolvedValueOnce(response(200, { success: true, data: canonical }));
      vi.stubGlobal('fetch', fetchMock);
      render(<RegistrationJourney />);
      await fillCompleteCreate(memberType);

      await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

      expect(await screen.findByText('******234F')).toBeTruthy();
      expect(screen.getByText('********1234')).toBeTruthy();
      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(fetchMock.mock.calls[0][0]).toBe('http://127.0.0.1:8000/api/v1/members/');
      expect(JSON.parse(String((fetchMock.mock.calls[0][1] as RequestInit).body))).toEqual(JSON.parse(JSON.stringify(completeBody(memberType))));
      expect(fetchMock.mock.calls[1][0]).toBe('http://127.0.0.1:8000/api/v1/members/member-1/');
      expect((fetchMock.mock.calls[1][1] as RequestInit).method).toBe('GET');
    },
  );

  it('posts only the protected identity delta through the shared HTTP transport', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response(200, { success: true, data: {
      identity_change_request_id: 'request-1', member_id: profile.member_id, status: 'pending', member_version: 7,
    } }));
    vi.stubGlobal('fetch', fetchMock);
    render(<MemberGovernanceForm profile={profile} canReverify onSaved={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Correct verified identity' }));
    await userEvent.type(screen.getByLabelText('PAN'), 'ABCDE9999F');
    await userEvent.type(screen.getByLabelText('Reverification Reason'), 'Correct protected identity');
    await userEvent.click(screen.getByRole('button', { name: 'Request identity change' }));

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/member-1/identity-change-requests/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ version: 7, pan: 'ABCDE9999F', reason: 'Correct protected identity' }),
      }),
    );
  });

  it('renders the backend stale-conflict reason verbatim after one PATCH and no refetch', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(response(409, {
      success: false,
      error: { code: 'STALE_WRITE', message: 'Version 7 is stale; current member version is 8.' },
    }));
    vi.stubGlobal('fetch', fetchMock);
    const onSaved = vi.fn();
    render(<MemberGovernanceForm profile={{ ...profile, kyc_status: 'pending' }} onSaved={onSaved} />);

    await userEvent.clear(screen.getByLabelText('Display Name'));
    await userEvent.type(screen.getByLabelText('Display Name'), 'Changed display');
    await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

    expect(await screen.findByText('Version 7 is stale; current member version is 8.')).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/members/member-1/',
      expect.objectContaining({ method: 'PATCH' }),
    );
    expect(onSaved).not.toHaveBeenCalled();
  });

  it.each([
    ['create', 400, 'VALIDATION_ERROR'], ['create', 403, 'PERMISSION_DENIED'], ['create', 409, 'CONFLICT'],
    ['update', 400, 'VALIDATION_ERROR'], ['update', 403, 'OBJECT_ACCESS_DENIED'], ['update', 409, 'STALE_WRITE'],
    ['request', 400, 'VALIDATION_ERROR'], ['request', 403, 'PERMISSION_DENIED'], ['request', 409, 'STALE_WRITE'],
  ] as const)('%s preserves the backend %s %s facts after one mutation and no GET', async (action, status, code) => {
    const reason = `${action} ${code} server reason`;
    const fetchMock = vi.fn().mockResolvedValueOnce(response(status, {
      success: false,
      error: { code, message: reason, field_errors: status === 400 ? { legal_name: 'Server legal-name fact.' } : {} },
    }));
    vi.stubGlobal('fetch', fetchMock);
    const onSaved = vi.fn();
    render(<MemberGovernanceForm
      profile={action === 'create' ? undefined : { ...profile, kyc_status: action === 'request' ? 'verified' : 'pending' }}
      canReverify={action === 'request'}
      onSaved={onSaved}
    />);

    if (action === 'request') {
      await userEvent.click(screen.getByRole('button', { name: 'Correct verified identity' }));
      await userEvent.type(screen.getByLabelText('PAN'), 'ABCDE9999F');
      await userEvent.type(screen.getByLabelText('Reverification Reason'), 'Correct protected identity');
      await userEvent.click(screen.getByRole('button', { name: 'Request identity change' }));
    } else {
      await userEvent.click(screen.getByRole('button', { name: 'Save member' }));
    }

    expect(await screen.findByText(reason)).toBeTruthy();
    if (status === 400) expect(screen.getByText('Server legal-name fact.')).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect((fetchMock.mock.calls[0][1] as RequestInit).method).toBe(action === 'update' ? 'PATCH' : 'POST');
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes('/api/v1/members/') && (fetchMock.mock.calls[0][1] as RequestInit).method === 'GET')).toBe(false);
    expect(onSaved).not.toHaveBeenCalled();
  });
});

const RegistrationJourney = () => {
  const [memberId, setMemberId] = React.useState<string | null>(null);
  return memberId
    ? <MemberProfile memberId={memberId} onBack={() => setMemberId(null)} />
    : <MemberGovernanceForm onSaved={saved => setMemberId(saved.member_id)} />;
};

async function replace(label: string, value: string) {
  const input = screen.getByLabelText(label);
  await userEvent.clear(input);
  await userEvent.type(input, value);
}

function replaceFixture(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

async function fillCompleteCreate(memberType: 'individual_farmer' | 'fpc' | 'producer_institution') {
  if (memberType !== 'individual_farmer') await userEvent.selectOptions(screen.getByLabelText('Member Type'), memberType);
  const common = completeBody(memberType);
  const address = common.registered_address;
  for (const [label, value] of [
    ['Legal Name', common.legal_name], ['Display Name', common.display_name], ['Folio Number', common.folio_number],
    ['Membership Start Date', common.membership_start_date], ['Mobile Number', common.mobile_number], ['Email', common.email], ['PAN', common.pan],
    ['Address Line 1', address.line1], ['Address Line 2', address.line2], ['Village / City', address.village_city],
    ['District', address.district], ['State', address.state], ['Pincode', address.pincode],
  ]) replaceFixture(label, value);
  if (memberType === 'individual_farmer') {
    const individual = common.individual_profile!;
    for (const [label, value] of [['First Name', individual.first_name], ['Middle Name', individual.middle_name], ['Last Name', individual.last_name], ['Gender', individual.gender], ['Date of Birth', individual.date_of_birth], ['Occupation', individual.occupation], ['Cultivation Area (acres)', individual.land_area_under_cultivation_acres], ['Primary Crop', individual.primary_crop], ['Services Availed', 'true'], ['Employment / Service Years', individual.employment_or_service_years], ['Aadhaar', common.aadhaar!]]) replaceFixture(label, String(value));
  } else {
    const institution = common.producer_institution_profile!;
    for (const [label, value] of [['Institution Type', institution.institution_type], ['Registration Number', institution.registration_number], ['Authorised Signatory', institution.authorised_signatory_name], ['Signatory PAN', institution.authorised_signatory_pan], ['Signatory Aadhaar', institution.authorised_signatory_aadhaar], ['Board Resolution Required', 'true'], ['Services Availed', 'true'], ['Produce Supply Years', institution.produce_supply_years]]) replaceFixture(label, String(value));
  }
}

function completeBody(memberType: 'individual_farmer' | 'fpc' | 'producer_institution') {
  const common = {
    member_type: memberType, legal_name: `Complete ${memberType}`, display_name: `Display ${memberType}`,
    folio_number: `FOL-${memberType}`, membership_start_date: '2024-04-01', pan: 'ABCDE1234F',
    registered_address: { line1: 'Registry Road', line2: 'Evidence Block', village_city: 'Nashik', district: 'Nashik', state: 'Maharashtra', pincode: '422001' },
    mobile_number: '+919100001234', email: `${memberType}@example.test`,
  };
  return memberType === 'individual_farmer' ? { ...common, aadhaar: '123456781234', individual_profile: {
    first_name: 'Complete', middle_name: 'Mounted', last_name: 'Farmer', gender: 'female', date_of_birth: '1980-01-15', occupation: 'Farmer', land_area_under_cultivation_acres: '5.25', primary_crop: 'grapes', services_availed_flag: true, employment_or_service_years: '7',
  }, producer_institution_profile: undefined } : { ...common, aadhaar: undefined, individual_profile: undefined, producer_institution_profile: {
    institution_type: 'farmer_producer_company', registration_number: 'REG-1234', authorised_signatory_name: 'Mounted Signatory', authorised_signatory_pan: 'ZBCDE1234Y', authorised_signatory_aadhaar: '876543211234', board_resolution_required_flag: true, services_availed_flag: true, produce_supply_years: '6',
  } };
}

function response(status: number, body: unknown): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
}

const profile: MemberProfileDetail = {
  version: 7, member_id: 'member-1', member_number: 'MEM-1', member_type: 'individual_farmer',
  legal_name: 'Synthetic Member', display_name: 'Synthetic Member', folio_number: 'FOL-1',
  membership_start_date: '2026-01-01', membership_status: 'active', kyc_status: 'verified',
  rekyc_due_date: null, default_status: 'no_default', mobile_number: '+919876543210', email: 'member@example.test',
  pan: { masked: '******234F', can_view_full: false }, aadhaar: { masked: '********1234', can_view_full: false },
  registered_address: { line1: 'Line 1', line2: 'Line 2', village_city: 'Nashik', district: 'Nashik', state: 'Maharashtra', pincode: '422001' },
  share_summary: { number_of_shares: 1, holding_mode: 'physical', available_share_count: 1 },
  active_member_status: { status: 'active', verified_at: null },
  individual_profile: { first_name: 'Synthetic', middle_name: null, last_name: 'Member', gender: null, date_of_birth: null, occupation: null, land_area_under_cultivation_acres: null, primary_crop: null, services_availed_flag: false, employment_or_service_years: null },
  producer_institution_profile: null, available_actions: [],
};

const backendUser = {
  user_id: 'staff-1', full_name: 'Mounted Finance', email: 'mounted@example.test', status: 'active',
  roles: [{ role_code: 'credit_manager', role_name: 'Credit Manager' }], teams: [],
  permissions: ['members.member.read', 'members.member.create', 'members.member.update'], available_actions: [],
};

const updateAction = {
  action_code: 'members.member.update', label: 'Update member', enabled: true, disabled_reason: null,
  required_permission: 'members.member.update', required_role: null,
};
