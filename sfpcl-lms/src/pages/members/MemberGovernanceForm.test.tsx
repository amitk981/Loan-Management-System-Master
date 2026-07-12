// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import * as memberApi from '../../services/memberProfileApi';
import MemberGovernanceForm from './MemberGovernanceForm';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('MemberGovernanceForm', () => {
  it('submits the institution create variant without individual identity/profile fields', async () => {
    const create = vi.spyOn(memberApi, 'createMember').mockResolvedValueOnce({ ...profile, member_type: 'fpc' });
    render(<MemberGovernanceForm onSaved={vi.fn()} />);

    await userEvent.selectOptions(screen.getByLabelText('Member Type'), 'fpc');
    await userEvent.type(screen.getByLabelText('Legal Name'), 'Synthetic Producer Company');
    await userEvent.type(screen.getByLabelText('Display Name'), 'Synthetic Producer');
    await userEvent.type(screen.getByLabelText('Folio Number'), 'FOL-SYNTHETIC');
    await userEvent.type(screen.getByLabelText('PAN'), 'ABCDE1234F');
    await userEvent.type(screen.getByLabelText('Authorised Signatory'), 'Synthetic Signatory');
    await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

    expect(create).toHaveBeenCalledTimes(1);
    const payload = create.mock.calls[0][0];
    expect(payload).toEqual(expect.objectContaining({
      member_type: 'fpc',
      pan: 'ABCDE1234F',
      producer_institution_profile: expect.objectContaining({ authorised_signatory_name: 'Synthetic Signatory' }),
    }));
    expect(payload).not.toHaveProperty('aadhaar');
    expect(payload).not.toHaveProperty('individual_profile');
  });

  it('renders verified identity values read-only and exposes only the resource-enabled reverification path', async () => {
    render(<MemberGovernanceForm profile={profile} canReverify onSaved={vi.fn()} />);

    expect(screen.getByText('Verified identity locked')).toBeTruthy();
    expect(screen.getByLabelText('PAN')).toHaveProperty('readOnly', true);
    expect(screen.getByLabelText('Aadhaar')).toHaveProperty('readOnly', true);
    await userEvent.click(screen.getByRole('button', { name: 'Correct verified identity' }));
    expect(screen.getByLabelText('Reverification Reason')).toBeTruthy();
    expect(screen.getByLabelText('PAN')).toHaveProperty('readOnly', false);
    expect(screen.getByRole('button', { name: 'Request identity change' })).toBeTruthy();
  });

  it('sends the current version once and renders authoritative backend field errors inline', async () => {
    const update = vi.spyOn(memberApi, 'updateMember').mockRejectedValueOnce(
      new AuthSessionError('VALIDATION_ERROR', 'Correct the highlighted fields.', 400, { email: 'Enter a valid email address.' }),
    );
    render(<MemberGovernanceForm profile={{ ...profile, kyc_status: 'pending' }} onSaved={vi.fn()} />);

    await userEvent.clear(screen.getByLabelText('Email'));
    await userEvent.type(screen.getByLabelText('Email'), 'bad@example.test');
    await userEvent.click(screen.getByRole('button', { name: 'Save member' }));

    expect(update).toHaveBeenCalledTimes(1);
    expect(update).toHaveBeenCalledWith('member-1', expect.objectContaining({ version: 7, email: 'bad@example.test' }));
    expect(await screen.findByText('Enter a valid email address.')).toBeTruthy();
  });
});

const profile: memberApi.MemberProfileDetail = {
  version: 7, member_id: 'member-1', member_number: 'MEM-1', member_type: 'individual_farmer',
  legal_name: 'Synthetic Member', display_name: 'Synthetic Member', folio_number: 'FOL-1',
  membership_start_date: '2026-01-01', membership_status: 'active', kyc_status: 'verified',
  rekyc_due_date: null, default_status: 'no_default', mobile_number: null, email: 'member@example.test',
  pan: { masked: '******234F', can_view_full: false }, aadhaar: { masked: '********1234', can_view_full: false },
  registered_address: { line1: null, line2: null, village_city: null, district: null, state: null, pincode: null },
  share_summary: { number_of_shares: 1, holding_mode: 'physical', available_share_count: 1 },
  active_member_status: { status: 'active', verified_at: null },
  individual_profile: { first_name: 'Synthetic', middle_name: null, last_name: 'Member', gender: null, date_of_birth: null, occupation: null, land_area_under_cultivation_acres: null, primary_crop: null, services_availed_flag: false, employment_or_service_years: null },
  producer_institution_profile: null,
  available_actions: [],
};
