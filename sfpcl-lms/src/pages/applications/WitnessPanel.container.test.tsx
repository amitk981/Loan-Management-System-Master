// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as api from '../../services/applicationIntakeApi';
import { WitnessPanel } from './ApplicationDetail';

const action = (action_code: string) => ({ action_code, label: action_code, enabled: true, disabled_reason: null, required_permission: `members.witness.${action_code}`, required_role: null });
const witness: api.ApplicationWitness = {
  witness_id: 'witness-1', loan_application_id: 'application-1', member_id: 'member-1',
  verification_shareholding_id: 'share-1', folio_number: 'FOL-1', witness_name: 'Witness One',
  address: 'Village Road', mobile: '9876543210',
  pan: { masked: '******234F', can_view_full: false }, aadhaar: { masked: '********1234', can_view_full: false },
  shareholder_verified_flag: true, verification_status: 'verified', verified_at: '2026-07-12T10:00:00Z',
  version: 1, actions: [action('update')],
};

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('mounted witness resource actions', () => {
  it('captures with the exact body and refetches the canonical collection once', async () => {
    const fetch = vi.spyOn(api, 'fetchApplicationWitnesses')
      .mockResolvedValueOnce({ items: [], actions: [action('create')] })
      .mockResolvedValueOnce({ items: [witness], actions: [action('create')] });
    const create = vi.spyOn(api, 'createApplicationWitness').mockResolvedValue(witness);
    render(<WitnessPanel applicationId="application-1" />);
    await screen.findByRole('button', { name: 'Capture Witness' });
    await userEvent.type(screen.getByLabelText(/member id/i), 'member-1');
    await userEvent.type(screen.getByLabelText(/witness name/i), 'Witness One');
    await userEvent.type(screen.getByLabelText(/^pan$/i), 'ABCDE1234F');
    await userEvent.type(screen.getByLabelText(/^aadhaar$/i), '123412341234');
    await userEvent.type(screen.getByLabelText(/^address$/i), 'Village Road');
    await userEvent.type(screen.getByLabelText(/^mobile$/i), '9876543210');
    await userEvent.click(screen.getByRole('button', { name: 'Capture Witness' }));
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
    expect(create).toHaveBeenCalledWith('application-1', { member_id: 'member-1', witness_name: 'Witness One', pan: 'ABCDE1234F', aadhaar: '123412341234', address: 'Village Road', mobile: '9876543210' });
  });

  it('corrects with current version and never exposes a control when the resource action is absent', async () => {
    vi.spyOn(api, 'fetchApplicationWitnesses')
      .mockResolvedValueOnce({ items: [witness], actions: [] })
      .mockResolvedValueOnce({ items: [{ ...witness, witness_name: 'Corrected', version: 2 }], actions: [] });
    const update = vi.spyOn(api, 'updateApplicationWitness').mockResolvedValue({ ...witness, witness_name: 'Corrected', version: 2 });
    const view = render(<WitnessPanel applicationId="application-1" />);
    await userEvent.click(await screen.findByRole('button', { name: 'Correct Witness' }));
    const name = screen.getByLabelText(/correction witness name/i);
    await userEvent.clear(name);
    await userEvent.type(name, 'Corrected');
    await userEvent.click(screen.getByRole('button', { name: 'Save Witness Correction' }));
    await waitFor(() => expect(update).toHaveBeenCalledWith('application-1', 'witness-1', { version: 1, witness_name: 'Corrected', address: 'Village Road', mobile: '9876543210' }));
    view.unmount();
    vi.spyOn(api, 'fetchApplicationWitnesses').mockResolvedValue({ items: [{ ...witness, actions: [] }], actions: [] });
    render(<WitnessPanel applicationId="application-1" />);
    await screen.findByText('Witness One');
    expect(screen.queryByRole('button', { name: 'Correct Witness' })).toBeNull();
  });

  it('shows the authoritative disabled reason and cannot invoke a correction', async () => {
    const update = vi.spyOn(api, 'updateApplicationWitness');
    const denied = { ...action('update'), enabled: false, disabled_reason: 'Missing witness update permission.' };
    vi.spyOn(api, 'fetchApplicationWitnesses').mockResolvedValue({ items: [{ ...witness, actions: [denied] }], actions: [] });
    render(<WitnessPanel applicationId="application-1" />);
    expect(await screen.findByText('Missing witness update permission.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Correct Witness' })).toBeNull();
    expect(update).not.toHaveBeenCalled();
  });
});
